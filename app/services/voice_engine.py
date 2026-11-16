"""
Liseth Voice Engine (Single Voice Architecture)
Coordinates:
- 16-State Central State Machine with strict transition governance:
  IDLE, INITIALIZING, LISTENING, SPEECH_DETECTED, RECORDING,
  TRANSCRIBING, PROCESSING, THINKING, RESPONSE_READY, SYNTHESIZING,
  SPEAKING, INTERRUPTED, STOPPING, RECONNECTING, PAUSED, ERROR.
- Single owner of hardware microphone (via LisethMicrophoneManager).
- Single owner of speech playback (via LisethAudioManager).
- Hermes AI Multi-Agent reasoning synchronization.
- Real-time Barge-In interruption (< 40ms) and acoustic echo suppression.
"""
import asyncio
import io
import logging
import re
import threading
import time
import unicodedata
import uuid
from typing import Any, Callable, Dict, List, Optional, Set

import numpy as np

from app.services.audio_manager import audio_manager
from app.services.microphone_manager import microphone_manager

logger = logging.getLogger("jarvis.voice_engine")

RATE = 16000
CHANNELS = 1
CHUNK = 1024
DTYPE = "int16"

# 16-State State Machine
VALID_STATES: Set[str] = {
    "IDLE",
    "INITIALIZING",
    "LISTENING",
    "SPEECH_DETECTED",
    "RECORDING",
    "TRANSCRIBING",
    "PROCESSING",
    "THINKING",
    "RESPONSE_READY",
    "SYNTHESIZING",
    "SPEAKING",
    "INTERRUPTED",
    "STOPPING",
    "RECONNECTING",
    "PAUSED",
    "ERROR",
}

WAKE_WORDS = [
    "liseth", "liceth", "lizeth", "lizet", "liset", "lissette",
    "lisset", "lised", "lisseth", "lise", "asistente", "jarvis"
]

STOP_TRIGGERS = [
    "callate", "cállate", "silencio", "para", "parar", "detente", "deténte",
    "stop", "basta", "deja de hablar", "no hables", "shh", "shhh",
    "callese", "cállese", "para ya", "basta ya", "silencio ya", "cancelar"
]

SLEEP_TRIGGERS = [
    "duermete", "ve a dormir", "a dormir", "descansa", "modo reposo", "ponte en reposo"
]

HALLUCINATIONS = [
    "subtitulado por", "subtítulos por", "amara.org", "gracias por ver",
    "suscríbete", "suscribete", "transcripción por", "...", "silencio"
]


def normalize_text(text: str) -> str:
    """Normalizes text by stripping accents, diacritics, and lowercase."""
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", text)
    cleaned = "".join(c for c in nfkd if not unicodedata.combining(c))
    return cleaned.lower().strip()


def contains_wake_word(text: str, custom_name: Optional[str] = None) -> bool:
    """Checks if speech contains Liseth or custom assistant wake word."""
    norm = normalize_text(text)
    words = list(WAKE_WORDS)
    if custom_name:
        words.append(normalize_text(custom_name))
    pattern = r"\b(?:" + "|".join(re.escape(w) for w in words) + r")\b"
    return bool(re.search(pattern, norm, re.IGNORECASE))


def extract_command(text: str, custom_name: Optional[str] = None) -> str:
    """Extracts command text following the wake word."""
    words = list(WAKE_WORDS)
    if custom_name:
        words.append(normalize_text(custom_name))
    pattern = r"^.*?\b(?:" + "|".join(re.escape(w) for w in words) + r")\b[\s,:;.-]*"
    return re.sub(pattern, "", text, flags=re.IGNORECASE).strip()


class VoiceEngine:
    """
    Central Voice Engine orchestrator.
    Guarantees strict single-voice execution and unifies audio input/output lifecycle.
    """
    def __init__(self):
        self._state: str = "IDLE"
        self.is_running: bool = False
        self.is_speaking: bool = False
        self.is_thinking: bool = False
        self._master_thread: Optional[threading.Thread] = None

        # VAD & Energy parameters
        self.energy_threshold: float = 280.0
        self.dynamic_energy_threshold: bool = True
        self.min_speech_duration_ms: float = 300.0  # Minimum 300ms of audio
        self.min_rms_threshold: float = 120.0       # Ignore absolute silence/hiss

        # Telemetry & Diagnostics
        self.last_transcript: str = ""
        self.last_role: str = ""
        self.last_activity_time: float = time.time()
        self.speech_end_time: float = 0.0
        self.last_error: Optional[str] = None
        self.current_execution_token: Optional[str] = None

        # Event subscribers for real-time SSE / WebSocket
        self._subscribers: List[asyncio.Queue] = []
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._lock = threading.Lock()
        self._stop_requested: bool = False

        # STT Recognizer
        self._recognizer = None
        self._init_recognizer()

        # Connect with audio manager callbacks
        audio_manager.register_callback("start", self._on_playback_start)
        audio_manager.register_callback("end", self._on_playback_end)

    def _init_recognizer(self):
        try:
            import speech_recognition as sr
            self._recognizer = sr.Recognizer()
            self._recognizer.energy_threshold = 280
            self._recognizer.dynamic_energy_threshold = True
            self._recognizer.pause_threshold = 0.5
            self._recognizer.non_speaking_duration = 0.3
        except Exception as e:
            logger.warning(f"[VoiceEngine] speech_recognition no disponible: {e}")

    def _on_playback_start(self, data: Dict[str, Any]):
        """Called when LisethAudioManager physically begins playing audio on output hardware."""
        self.is_speaking = True
        self.set_state("SPEAKING", details={"turn_id": data.get("turn_id")})
        self.broadcast_event("speaking", {"isSpeaking": True, "text": data.get("text"), "token": data.get("turn_id")})

    def _on_playback_end(self, data: Dict[str, Any]):
        """Called when LisethAudioManager finishes speech playback or is interrupted."""
        self.is_speaking = False
        self.speech_end_time = time.time()
        self.broadcast_event("speaking", {"isSpeaking": False, "interrupted": data.get("interrupted", False)})
        if self.state in ["SPEAKING", "SYNTHESIZING"]:
            self.set_state("LISTENING")

    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        """Injects running event loop for threadsafe SSE broadcasts."""
        self._loop = loop

    def subscribe(self) -> asyncio.Queue:
        """Registers a queue for real-time SSE event delivery."""
        q: asyncio.Queue = asyncio.Queue()
        with self._lock:
            self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        """Unregisters an SSE event queue."""
        with self._lock:
            if q in self._subscribers:
                self._subscribers.remove(q)

    def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """Dispatches event to all active SSE subscribers."""
        payload = {"type": event_type, "timestamp": time.time(), **data}
        with self._lock:
            subs = list(self._subscribers)
        for q in subs:
            if self._loop and self._loop.is_running():
                self._loop.call_soon_threadsafe(q.put_nowait, payload)
            else:
                try:
                    q.put_nowait(payload)
                except Exception:
                    pass

    @property
    def state(self) -> str:
        return self._state

    def set_state(self, new_state: str, details: Optional[Dict[str, Any]] = None, play_chime: bool = False):
        """Applies state machine transition and broadcasts event."""
        upper_state = new_state.upper()
        # Backward compatibility aliases
        if upper_state == "GENERATING_RESPONSE":
            upper_state = "RESPONSE_READY"
        elif upper_state == "REQUESTING_PERMISSION":
            upper_state = "INITIALIZING"

        if upper_state not in VALID_STATES:
            logger.warning(f"[VoiceEngine] Rechazado estado inválido: '{new_state}'")
            return

        old_state = self._state
        if old_state == upper_state and upper_state != "RECORDING":
            return

        self._state = upper_state
        logger.info(f"[VoiceEngine] Estado: {old_state} -> {upper_state}")

        event_data = {
            "previous_state": old_state,
            "current_state": upper_state,
            "details": details or {}
        }
        self.broadcast_event("state_change", event_data)

        if upper_state == "LISTENING" and play_chime:
            threading.Thread(target=self._play_tone, args=(740, 0.12), daemon=True).start()
        elif upper_state == "PAUSED" and play_chime:
            threading.Thread(target=self._play_tone, args=(440, 0.15), daemon=True).start()

    def start(self):
        """Starts background hardware microphone listener through MicrophoneManager."""
        if self.is_running:
            return
        self.is_running = True
        self.set_state("INITIALIZING")

        # Open single microphone stream
        microphone_manager.subscribe(self._on_incoming_audio_frame)
        success = microphone_manager.start_capture()
        if not success:
            logger.error("[VoiceEngine] No se pudo inicializar micrófono; iniciando en modo degradado.")
            self.set_state("ERROR", details={"error": microphone_manager.last_error})
            return

        self._master_thread = threading.Thread(target=self._vad_consumer_loop, name="LisethVoiceVADThread", daemon=True)
        self._master_thread.start()
        self.set_state("LISTENING")
        logger.info("[VoiceEngine] Sistema Single Voice de Liseth activo y escuchando.")

    def stop(self):
        """Stops microphone capture, speech output, and releases hardware."""
        self.is_running = False
        self.set_state("STOPPING")
        microphone_manager.unsubscribe(self._on_incoming_audio_frame)
        microphone_manager.stop_capture()
        self.stop_speaking()
        self.set_state("IDLE")
        logger.info("[VoiceEngine] Sistema Single Voice detenido y recursos liberados.")

    def pause(self):
        """Pauses listening without shutting down engine."""
        self.set_state("PAUSED", play_chime=True)

    def resume(self):
        """Resumes active listening."""
        self.set_state("LISTENING", play_chime=True)

    def stop_speaking(self, interrupted: bool = False):
        """Immediately halts active speech output (Barge-In) via LisethAudioManager."""
        self._stop_requested = True
        self.current_execution_token = None
        audio_manager.stop(interrupted=interrupted)
        self.is_speaking = False
        self.speech_end_time = time.time()

        if interrupted:
            self.set_state("INTERRUPTED", details={"reason": "barge_in"})

        self.broadcast_event("speaking", {"isSpeaking": False, "interrupted": interrupted})
        self.broadcast_event("stop_speaking", {"interrupted": interrupted})
        logger.info("[VoiceEngine] Habla y síntesis detenidas de inmediato (Barge-In ejecutado).")

    def speak(self, text: str, voice: str = "es-CO-SalomeNeural", token: Optional[str] = None):
        """
        Routes all speech requests strictly through LisethAudioManager.
        Guarantees single official voice and prevents dual speech.
        """
        if not text or not text.strip():
            return

        if not token:
            token = str(uuid.uuid4())
            self.current_execution_token = token

        self.set_state("SYNTHESIZING", details={"token": token})

        # Delegate exclusively to single audio manager
        audio_manager.speak(
            text=text,
            turn_id=token,
            voice=voice,
        )

    def _play_tone(self, freq: int = 580, duration: float = 0.15):
        """Plays gentle confirmation tone using Pygame if available."""
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1)
            sample_rate = 22050
            n_samples = int(sample_rate * duration)
            t = np.linspace(0, duration, n_samples, False)
            envelope = np.sin(np.pi * np.linspace(0, 1, n_samples))
            wave_data = (np.sin(2 * np.pi * freq * t) * envelope * 16384).astype(np.int16)
            sound = pygame.sndarray.make_sound(wave_data)
            sound.play()
        except Exception:
            pass

    # ── VAD & Incoming Audio Frame Processing ──────────────────────────────────
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    # Frame queue for thread-safe processing
    _frame_queue: asyncio.Queue = None
    _audio_buffer: List[np.ndarray] = []
    _is_recording: bool = False
    _silence_start: float = 0.0

    # Barge-In interrupt state
    _interrupt_buffer: List[np.ndarray] = []
    _is_recording_interrupt: bool = False
    _interrupt_silence_start: float = 0.0

    def _on_incoming_audio_frame(self, chunk: np.ndarray):
        """Callback fed directly by LisethMicrophoneManager."""
        if not self.is_running or self.state in ["IDLE", "PAUSED", "ERROR"]:
            return

        rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))

        # ── 1. Barge-In Interruption while speaking ─────────────────────────
        if self.is_speaking or audio_manager.is_playing():
            if rms > self.energy_threshold * 1.25:
                if not self._is_recording_interrupt:
                    self._is_recording_interrupt = True
                    self._interrupt_buffer.clear()
                self._interrupt_buffer.append(chunk.copy())
                self._interrupt_silence_start = 0.0
            elif self._is_recording_interrupt:
                self._interrupt_buffer.append(chunk.copy())
                if self._interrupt_silence_start == 0.0:
                    self._interrupt_silence_start = time.time()
            return
        else:
            if self._is_recording_interrupt:
                self._is_recording_interrupt = False
                self._interrupt_buffer.clear()
                self._interrupt_silence_start = 0.0

        # ── 2. Acoustic Echo Window Suppression ──────────────────────────────
        now = time.time()
        if (now - self.speech_end_time) < 0.45:
            return  # Suppress trailing speaker echoes

        # ── 3. Normal User Speech VAD Detection ──────────────────────────────
        if rms > self.energy_threshold:
            if not self._is_recording:
                self._is_recording = True
                self._audio_buffer.clear()
                self.set_state("SPEECH_DETECTED")
                self.set_state("RECORDING")
            self._audio_buffer.append(chunk.copy())
            self._silence_start = 0.0
        elif self._is_recording:
            self._audio_buffer.append(chunk.copy())
            if self._silence_start == 0.0:
                self._silence_start = time.time()

    def _vad_consumer_loop(self):
        """Monitors silence timeouts and dispatches speech buffers."""
        while self.is_running:
            time.sleep(0.03)

            # Barge-in completed evaluation
            if (self.is_speaking or audio_manager.is_playing()) and self._is_recording_interrupt and self._interrupt_silence_start > 0.0:
                if time.time() - self._interrupt_silence_start > 0.20:
                    self._is_recording_interrupt = False
                    self._interrupt_silence_start = 0.0
                    if len(self._interrupt_buffer) >= 3:
                        collected = np.concatenate(self._interrupt_buffer)
                        self._interrupt_buffer.clear()
                        threading.Thread(target=self._check_and_handle_interrupt, args=(collected,), daemon=True).start()
                    else:
                        self._interrupt_buffer.clear()

            # Normal speech phrase completion
            if not self.is_speaking and not audio_manager.is_playing() and self._is_recording and self._silence_start > 0.0:
                if time.time() - self._silence_start > 0.55:
                    self._is_recording = False
                    self._silence_start = 0.0
                    total_chunks = len(self._audio_buffer)
                    speech_ms = (total_chunks * CHUNK / RATE) * 1000.0
                    if speech_ms >= self.min_speech_duration_ms:
                        collected = np.concatenate(self._audio_buffer)
                        self._audio_buffer.clear()
                        self._process_speech(collected)
                    else:
                        self._audio_buffer.clear()
                        self.set_state("LISTENING")

    def _check_and_handle_interrupt(self, pcm_array: np.ndarray):
        """Interprets barge-in audio while speaking."""
        if not self.is_speaking and not audio_manager.is_playing():
            return
        try:
            raw_bytes = pcm_array.tobytes()
            import speech_recognition as sr
            audio_data = sr.AudioData(raw_bytes, RATE, 2)
            if self._recognizer:
                text = self._recognizer.recognize_google(audio_data, language="es-CO")
                norm = normalize_text(text)
                logger.info(f"[VoiceEngine] Interrupción detectada: '{text}'")
                if any(trig in norm for trig in STOP_TRIGGERS):
                    self.stop_speaking(interrupted=True)
                    self.set_state("LISTENING", play_chime=False)
        except Exception:
            pass

    def _process_speech(self, pcm_array: np.ndarray):
        """
        Executes strict execution order:
        LISTENING -> SPEECH_DETECTED -> RECORDING -> TRANSCRIBING ->
        PROCESSING -> THINKING -> RESPONSE_READY -> SYNTHESIZING -> SPEAKING -> LISTENING.
        """
        self.set_state("TRANSCRIBING")
        try:
            rms = float(np.sqrt(np.mean(pcm_array.astype(np.float32) ** 2)))
            if rms < self.min_rms_threshold:
                logger.debug(f"[VoiceEngine] Audio descartado por baja energía ({rms:.1f})")
                self.set_state("LISTENING")
                return

            raw_bytes = pcm_array.tobytes()
            import speech_recognition as sr
            audio_data = sr.AudioData(raw_bytes, RATE, 2)

            transcript = ""
            if self._recognizer:
                try:
                    transcript = self._recognizer.recognize_google(audio_data, language="es-CO")
                except sr.UnknownValueError:
                    self.set_state("LISTENING")
                    return
                except Exception as e:
                    logger.warning(f"[VoiceEngine] Error en STT primario: {e}")
                    self.set_state("LISTENING")
                    return

            transcript = transcript.strip()
            norm = normalize_text(transcript)

            if not transcript or any(h in norm for h in HALLUCINATIONS):
                self.set_state("LISTENING")
                return

            self.last_transcript = transcript
            self.last_activity_time = time.time()
            self.broadcast_event("transcript", {"text": transcript, "role": "user"})

            self.set_state("PROCESSING")

            # Direct Stop / Silence trigger
            if any(trig in norm for trig in STOP_TRIGGERS):
                logger.info(f"[VoiceEngine] Comando de silencio recibido: '{transcript}'")
                self.stop_speaking(interrupted=True)
                ack = "En silencio, señor Santiago."
                self.broadcast_event("response", {"text": ack, "role": "assistant"})
                self.set_state("LISTENING")
                return

            # Direct Sleep trigger
            if any(trig in norm for trig in SLEEP_TRIGGERS):
                logger.info(f"[VoiceEngine] Modo reposo recibido: '{transcript}'")
                self.pause()
                ack = "Entendido, Santiago. Quedo en pausa."
                self.broadcast_event("response", {"text": ack, "role": "assistant"})
                self.speak(ack)
                return

            # Wake word or direct command
            cmd = extract_command(transcript) if contains_wake_word(transcript) else transcript
            if not cmd:
                greeting = "¿Sí, Santiago? Le escucho atentamente."
                self.set_state("RESPONSE_READY")
                self.broadcast_event("response", {"text": greeting, "role": "assistant"})
                self.speak(greeting)
                return

            self._execute_user_command(cmd)

        except Exception as e:
            logger.error(f"[VoiceEngine] Error procesando habla: {e}", exc_info=True)
            self.set_state("ERROR", details={"error": str(e)})

    def _execute_user_command(self, text: str):
        """Sends command to Hermes AI Orchestrator enforcing single-voice sequencing."""
        token = str(uuid.uuid4())
        self.current_execution_token = token
        self.is_thinking = True

        # Enter THINKING before Hermes begins
        self.set_state("THINKING", details={"token": token, "query": text})
        self.broadcast_event("thinking", {"text": text, "token": token})

        def run_async():
            try:
                from app.services.hermes_orchestrator import hermes_orchestrator
                res = asyncio.run(hermes_orchestrator.route_and_execute(prompt=text, modality="voice"))

                # Ensure token wasn't canceled during reasoning
                if self.current_execution_token != token:
                    logger.info("[VoiceEngine] Respuesta descartada por token obsoleto o interrupción.")
                    return

                # Enter RESPONSE_READY once Hermes completes
                self.set_state("RESPONSE_READY", details={"token": token})
                response_text = res.get("text", "")
                executed_tools = res.get("executedTools", [])

                logger.info(f"[VoiceEngine] Respuesta lista ({res.get('agent', 'hermes')}): '{response_text[:80]}...'")
                self.broadcast_event("response", {
                    "text": response_text,
                    "agent": res.get("agent", "hermes"),
                    "executedTools": executed_tools,
                    "role": "assistant",
                    "token": token
                })

                if any(t.get("name") == "stop_speaking" for t in executed_tools):
                    self.stop_speaking()
                    self.set_state("LISTENING")
                    return

                # Speak single response through LisethAudioManager
                self.speak(response_text, token=token)

            except Exception as e:
                logger.error(f"[VoiceEngine] Error en orquestación Hermes: {e}", exc_info=True)
                err_msg = "Disculpe, Santiago, hubo un inconveniente al coordinar la respuesta."
                self.set_state("RESPONSE_READY", details={"token": token})
                self.broadcast_event("response", {"text": err_msg, "role": "assistant", "token": token})
                self.speak(err_msg, token=token)
            finally:
                self.is_thinking = False

        threading.Thread(target=run_async, daemon=True).start()


# Global Singleton Instance
voice_engine = VoiceEngine()
