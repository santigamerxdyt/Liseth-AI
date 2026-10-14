"""
VoiceEngine for JARVIS / Liseth.
Provides native, continuous hardware voice capture and wake-word detection using
sounddevice, speech_recognition, and edge-tts, ported from Mark-XXXIX.

Modes:
- "off": Voice engine paused/idle.
- "standby": Modo Reposo. Continually monitors microphone with low CPU overhead.
             When wake word ("Liseth", "Liceth", "Jarvis") is spoken, activates immediately.
- "active": Modo Activo. Fluid conversation. Listens to instructions without needing name.
            Auto-sends upon speech pause. After 20 seconds of inactivity, drops to "standby".

Acoustic Echo Protection:
- Microphone input is automatically muted while Liseth is speaking or processing.
"""
import asyncio
import io
import logging
import re
import threading
import time
import unicodedata
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import sounddevice as sd
import speech_recognition as sr
from app.config import settings

logger = logging.getLogger("jarvis.voice_engine")

RATE = 16000
CHANNELS = 1
CHUNK = 1024
DTYPE = "int16"

WAKE_WORDS = [
    "liseth", "liceth", "lizeth", "lizet", "liset", "lissette",
    "lisset", "lised", "lisseth", "lise", "asistente", "jarvis"
]


def normalize_text(text: str) -> str:
    """Normalizes text by removing accents, diacritics, and symbols."""
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
    def __init__(self):
        self.state: str = "off"  # "off" | "standby" | "active"
        self.is_running: bool = False
        self.is_speaking: bool = False
        self.is_thinking: bool = False
        self._thread: Optional[threading.Thread] = None
        self._recognizer = sr.Recognizer()
        self._recognizer.energy_threshold = 300
        self._recognizer.dynamic_energy_threshold = True

        self.last_transcript: str = ""
        self.last_role: str = ""
        self.last_activity_time: float = time.time()
        self.speech_end_time: float = 0.0

        # Event subscribers for real-time SSE/WebSocket
        self._subscribers: List[asyncio.Queue] = []
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        # Lock for safe thread operations
        self._lock = threading.Lock()

    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    def subscribe(self) -> asyncio.Queue:
        """Subscribes an async SSE queue to receive real-time voice events."""
        q = asyncio.Queue(maxsize=50)
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        if q in self._subscribers:
            self._subscribers.remove(q)

    def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """Dispatches an event safely to all connected clients."""
        payload = {"type": event_type, "timestamp": time.time(), **data}
        if self._loop and self._loop.is_running():
            for q in list(self._subscribers):
                try:
                    self._loop.call_soon_threadsafe(
                        lambda queue, item: queue.put_nowait(item) if not queue.full() else None,
                        q, payload
                    )
                except Exception:
                    pass

    def set_state(self, new_state: str, play_chime: bool = True):
        """Switches voice assistant state ('off', 'standby', 'active')."""
        with self._lock:
            old_state = self.state
            if old_state == new_state:
                return
            self.state = new_state
            self.last_activity_time = time.time()
            logger.info(f"[VoiceEngine] Estado cambiado: {old_state} -> {new_state}")

        self.broadcast_event("state_change", {"state": new_state})

        if new_state == "active" and play_chime:
            threading.Thread(target=self._play_tone, args=(740, 0.15), daemon=True).start()
        elif new_state == "standby" and play_chime:
            threading.Thread(target=self._play_tone, args=(440, 0.2), daemon=True).start()

    def start(self):
        """Starts background hardware microphone listener thread."""
        if self.is_running:
            return
        self.is_running = True
        self.set_state("standby", play_chime=False)
        self._thread = threading.Thread(target=self._run_loop, name="LisethVoiceThread", daemon=True)
        self._thread.start()
        logger.info("[VoiceEngine] Hilo nativo de captura de audio iniciado.")

    def stop(self):
        """Stops background microphone listener."""
        self.is_running = False
        self.set_state("off", play_chime=False)
        logger.info("[VoiceEngine] Hilo nativo de captura de audio detenido.")

    def speak(self, text: str, voice: str = "es-CO-SalomeNeural"):
        """Speaks text asynchronously using high-fidelity edge-tts and pygame mixer."""
        threading.Thread(target=self._speak_blocking, args=(text, voice), daemon=True).start()

    def _speak_blocking(self, text: str, voice: str = "es-CO-SalomeNeural"):
        if not text or not text.strip():
            return
        self.is_speaking = True
        self.broadcast_event("speaking", {"isSpeaking": True, "text": text})
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            import edge_tts
            communicate = edge_tts.Communicate(text=text, voice=voice, rate="+5%", pitch="+15Hz")

            # Stream into in-memory MP3 buffer
            async def get_audio_bytes():
                chunks = []
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        chunks.append(chunk["data"])
                return b"".join(chunks)

            # Run coroutine safely
            audio_bytes = asyncio.run(get_audio_bytes())
            if audio_bytes:
                mp3_fp = io.BytesIO(audio_bytes)
                pygame.mixer.music.load(mp3_fp)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() and self.is_running:
                    time.sleep(0.08)
        except Exception as e:
            logger.warning(f"[VoiceEngine] Error reproduciendo voz con pygame: {e}")
        finally:
            self.speech_end_time = time.time()
            self.is_speaking = False
            self.broadcast_event("speaking", {"isSpeaking": False})

    def _play_tone(self, freq: int = 580, duration: float = 0.15):
        """Plays a gentle procedural notification tone."""
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

    def _run_loop(self):
        """Continuous hardware audio acquisition loop with sounddevice."""
        logger.info("[VoiceEngine] Escuchando dispositivo de audio predeterminado...")

        speech_buffer = []
        is_recording_speech = False
        silence_start_time = 0.0
        energy_threshold = 450

        def audio_callback(indata, frames, time_info, status):
            nonlocal is_recording_speech, silence_start_time

            # Acoustic echo protection: discard input if Liseth is speaking or cooling down
            if self.is_speaking or (time.time() - self.speech_end_time < 0.45):
                return

            if self.state == "off":
                return

            chunk = indata[:, 0]
            # RMS amplitude
            rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))

            if rms > energy_threshold:
                if not is_recording_speech:
                    is_recording_speech = True
                    speech_buffer.clear()
                speech_buffer.append(chunk.copy())
                silence_start_time = 0.0
            elif is_recording_speech:
                speech_buffer.append(chunk.copy())
                if silence_start_time == 0.0:
                    silence_start_time = time.time()

        try:
            with sd.InputStream(
                samplerate=RATE,
                channels=CHANNELS,
                dtype=DTYPE,
                blocksize=CHUNK,
                callback=audio_callback,
            ):
                while self.is_running:
                    time.sleep(0.05)

                    # 1. Check for silence completion of spoken phrase
                    if is_recording_speech and silence_start_time > 0.0:
                        # Required silence duration: 1.0s in active, 1.2s in standby
                        silence_needed = 1.0 if self.state == "active" else 1.2
                        if time.time() - silence_start_time > silence_needed:
                            is_recording_speech = False
                            silence_start_time = 0.0
                            if len(speech_buffer) > 8:  # At least ~0.5s of audio
                                collected = np.concatenate(speech_buffer)
                                speech_buffer.clear()
                                self._process_speech(collected)
                            else:
                                speech_buffer.clear()

                    # 2. Check 20-second inactivity timeout in active mode
                    if self.state == "active":
                        if time.time() - self.last_activity_time > 20.0 and not is_recording_speech and not self.is_speaking and not self.is_thinking:
                            logger.info("[VoiceEngine] 20 segundos de inactividad: pasando a Modo Reposo (standby).")
                            self.set_state("standby", play_chime=True)

        except Exception as e:
            logger.error(f"[VoiceEngine] Error fatal en captura de micrófono: {e}", exc_info=True)
            self.is_running = False

    def _process_speech(self, pcm_array: np.ndarray):
        """Transcribes PCM audio buffer and executes commands or wakes up."""
        try:
            raw_bytes = pcm_array.tobytes()
            audio_data = sr.AudioData(raw_bytes, RATE, 2)

            # Transcribe via Google STT (es-CO)
            try:
                transcript = self._recognizer.recognize_google(audio_data, language="es-CO")
            except sr.UnknownValueError:
                # Inaudible / background noise
                return
            except sr.RequestError as re_err:
                logger.warning(f"[VoiceEngine] Reconocimiento falló ({re_err})")
                return

            transcript = transcript.strip()
            if not transcript:
                return

            logger.info(f"[VoiceEngine] Transcripción ({self.state}): '{transcript}'")
            self.broadcast_event("transcript", {"text": transcript, "role": "user"})

            # --- CASO 1: EN MODO REPOSO (STANDBY) ---
            if self.state == "standby":
                if contains_wake_word(transcript):
                    logger.info(f"[VoiceEngine] Wake word detectada: '{transcript}'")
                    self.set_state("active", play_chime=True)
                    cmd = extract_command(transcript)
                    if cmd and len(cmd) >= 2:
                        self._execute_user_command(cmd)
                    else:
                        self.speak("¿Sí, Santiago? Le escucho atentamente.")
                return

            # --- CASO 2: EN MODO ACTIVO (CONVERSACIÓN FLUIDA) ---
            if self.state == "active":
                self.last_activity_time = time.time()
                self._execute_user_command(transcript)

        except Exception as e:
            logger.error(f"[VoiceEngine] Error procesando habla: {e}", exc_info=True)

    def _execute_user_command(self, text: str):
        """Sends command to BrainRouter, executes tools, and speaks response."""
        self.is_thinking = True
        self.broadcast_event("thinking", {"text": text})

        def run_async():
            try:
                from app.services.brain_router import brain_router
                from app.services.soul_service import soul_service

                sys_instruction = soul_service.build_system_instruction()

                # Call brain router with system automation tools enabled
                res = asyncio.run(
                    brain_router.generate_response(
                        prompt=text,
                        system_prompt=sys_instruction,
                    )
                )

                response_text = res.get("text", "")
                executed_tools = res.get("executedTools", [])

                logger.info(f"[VoiceEngine] Respuesta de Liseth: '{response_text[:80]}...'")
                self.broadcast_event("response", {
                    "text": response_text,
                    "executedTools": executed_tools,
                    "role": "assistant"
                })

                # Speak response with sweet female voice
                self.speak(response_text)
                self.last_activity_time = time.time()

            except Exception as e:
                logger.error(f"[VoiceEngine] Error procesando orden: {e}", exc_info=True)
                err_msg = f"Inconveniente procesando la orden: {str(e)}"
                self.broadcast_event("response", {"text": err_msg, "role": "assistant"})
                self.speak("Disculpe, Santiago, hubo un inconveniente al procesar la instrucción.")
            finally:
                self.is_thinking = False

        threading.Thread(target=run_async, daemon=True).start()


voice_engine = VoiceEngine()
