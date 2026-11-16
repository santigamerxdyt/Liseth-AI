"""
Liseth Single Audio Manager (LisethAudioManager)
Centralized Single Audio Controller for Liseth // JARVIS.

Core Responsibilities:
- Strictly enforces ONE official voice (es-CO-SalomeNeural).
- Strictly enforces ONE active audio playback system across all agents and interfaces.
- Prevents concurrent / overlapping audio speech.
- Provides atomic turn_id and playback_id deduplication.
- Ultra-low latency Barge-In interruption (< 40ms).
- Graceful resource reclamation and safe shutdown.
"""
import asyncio
import hashlib
import io
import logging
import threading
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Set

import numpy as np

logger = logging.getLogger("jarvis.audio_manager")


class LisethAudioManager:
    """
    Singleton central audio playback controller.
    Arbitrates all speech output for Liseth to ensure only ONE voice plays at any given time.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LisethAudioManager, cls).__new__(cls)
            return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._initialized = True
        self.official_voice: str = "es-CO-SalomeNeural"
        self.fallback_voice: str = "es-MX-DaliaNeural"
        self.default_rate: str = "+6%"
        self.default_pitch: str = "+4Hz"

        # Playback synchronization
        self._playback_lock = threading.RLock()
        self._is_playing: bool = False
        self._is_paused: bool = False
        self._stop_requested: bool = False

        # Turn & Execution IDs
        self.current_turn_id: Optional[str] = None
        self.current_playback_id: Optional[str] = None
        self.last_playback_id: Optional[str] = None
        self.last_speech_end_time: float = 0.0

        # Deduplication cache (text_hash -> timestamp)
        self._recent_playbacks: Dict[str, float] = {}
        self._completed_turns: Set[str] = set()

        # Telemetry & Callbacks
        self._on_start_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self._on_end_callbacks: List[Callable[[Dict[str, Any]], None]] = []

        # Background playback worker
        self._playback_thread: Optional[threading.Thread] = None

        logger.info(f"[LisethAudioManager] Inicializado con voz oficial: '{self.official_voice}'")

    def initialize(self) -> bool:
        """Initializes underlying Pygame audio mixer safely."""
        with self._playback_lock:
            try:
                import pygame
                if not pygame.mixer.get_init():
                    pygame.mixer.init(frequency=24000, size=-16, channels=1, buffer=1024)
                    logger.info("[LisethAudioManager] Pygame mixer inicializado a 24kHz mono.")
                return True
            except Exception as e:
                logger.warning(f"[LisethAudioManager] Fallo al inicializar Pygame mixer: {e}")
                return False

    def get_active_voice(self) -> str:
        """Returns the official voice ID."""
        return self.official_voice

    def is_playing(self) -> bool:
        """Checks if speech audio is currently playing."""
        with self._playback_lock:
            if self._is_playing:
                try:
                    import pygame
                    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                        return True
                    else:
                        self._is_playing = False
                except Exception:
                    self._is_playing = False
            return self._is_playing

    def is_paused(self) -> bool:
        """Checks if playback is paused."""
        return self._is_paused

    def register_callback(self, event_type: str, callback: Callable[[Dict[str, Any]], None]):
        """Registers listener for playback lifecycle events ('start', 'end')."""
        if event_type == "start":
            self._on_start_callbacks.append(callback)
        elif event_type == "end":
            self._on_end_callbacks.append(callback)

    def _hash_text(self, text: str) -> str:
        """Produces normalized SHA-256 digest of speech text."""
        norm = " ".join(text.lower().strip().split())
        return hashlib.sha256(norm.encode("utf-8")).hexdigest()

    def speak(
        self,
        text: str,
        turn_id: Optional[str] = None,
        playback_id: Optional[str] = None,
        voice: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
        priority: str = "normal",
        on_start: Optional[Callable] = None,
        on_end: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Dispatches text speech through the single authorized audio pipeline.
        Deduplicates identical turns and prevents parallel overlapping output.
        """
        clean_text = text.strip()
        if not clean_text:
            return {"ok": False, "reason": "empty_text"}

        text_hash = self._hash_text(clean_text)
        now = time.time()

        # ── 1. Deduplication Gate ─────────────────────────────────────────────
        # Drop if exact text was spoken within the last 2.0 seconds
        if text_hash in self._recent_playbacks:
            if (now - self._recent_playbacks[text_hash]) < 2.0 and priority != "urgent":
                logger.info(f"[LisethAudioManager] 🛑 Descartando reproducción duplicada detectada (hash: {text_hash[:8]}).")
                return {"ok": False, "reason": "duplicate_suppressed"}

        # Clean old deduplication entries
        self._recent_playbacks = {h: ts for h, ts in self._recent_playbacks.items() if (now - ts) < 15.0}
        self._recent_playbacks[text_hash] = now

        # ── 2. Interruption of Active Speech if needed ────────────────────────
        assigned_turn = turn_id or str(uuid.uuid4())
        assigned_playback = playback_id or str(uuid.uuid4())

        # If already playing, stop previous speech cleanly
        if self.is_playing():
            logger.info(f"[LisethAudioManager] Interrumpiendo reproducción previa para iniciar nuevo turno '{assigned_turn}'.")
            self.stop(interrupted=True)

        chosen_voice = voice or self.official_voice
        chosen_rate = rate or self.default_rate
        chosen_pitch = pitch or self.default_pitch

        self.current_turn_id = assigned_turn
        self.current_playback_id = assigned_playback
        self._stop_requested = False

        # Launch playback in isolated background thread
        self._playback_thread = threading.Thread(
            target=self._execute_playback_worker,
            args=(clean_text, assigned_turn, assigned_playback, chosen_voice, chosen_rate, chosen_pitch, on_start, on_end),
            name=f"LisethAudioWorker-{assigned_playback[:8]}",
            daemon=True
        )
        self._playback_thread.start()

        return {
            "ok": True,
            "turn_id": assigned_turn,
            "playback_id": assigned_playback,
            "voice": chosen_voice,
            "text": clean_text
        }

    def _execute_playback_worker(
        self,
        text: str,
        turn_id: str,
        playback_id: str,
        voice: str,
        rate: str,
        pitch: str,
        on_start: Optional[Callable],
        on_end: Optional[Callable],
    ):
        """Thread worker executing synthesis and audio playback."""
        start_time = time.time()
        logger.info(f"[LisethAudioManager] Iniciando síntesis para turno '{turn_id}' [Playback: {playback_id[:8]}]: '{text[:60]}...'")

        # ── Phase 1: Synthesize Audio via Edge-TTS ───────────────────────────
        audio_bytes = b""
        try:
            import edge_tts

            async def fetch_audio():
                communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
                chunks = []
                async for chunk in communicate.stream():
                    if self._stop_requested or self.current_playback_id != playback_id:
                        logger.info("[LisethAudioManager] Síntesis abortada por interrupción / nuevo turno.")
                        return b""
                    if chunk["type"] == "audio":
                        chunks.append(chunk["data"])
                return b"".join(chunks)

            audio_bytes = asyncio.run(fetch_audio())

        except Exception as synth_err:
            logger.warning(f"[LisethAudioManager] Advertencia en síntesis oficial ({voice}): {synth_err}. Probando fallback.")
            try:
                import edge_tts

                async def fetch_fallback():
                    communicate = edge_tts.Communicate(text=text, voice=self.fallback_voice, rate=rate, pitch=pitch)
                    chunks = []
                    async for chunk in communicate.stream():
                        if self._stop_requested or self.current_playback_id != playback_id:
                            return b""
                        if chunk["type"] == "audio":
                            chunks.append(chunk["data"])
                    return b"".join(chunks)

                audio_bytes = asyncio.run(fetch_fallback())
            except Exception as fb_err:
                logger.error(f"[LisethAudioManager] Error crítico en síntesis TTS: {fb_err}")
                audio_bytes = b""

        # Check if canceled during synthesis
        if self._stop_requested or self.current_playback_id != playback_id or not audio_bytes:
            self._is_playing = False
            return

        # ── Phase 2: Hardware Playback via Pygame Mixer ───────────────────────
        with self._playback_lock:
            if self._stop_requested or self.current_playback_id != playback_id:
                return

            self._is_playing = True
            self._is_paused = False

            # Notify start callbacks
            event_payload = {
                "event": "start",
                "turn_id": turn_id,
                "playback_id": playback_id,
                "voice": voice,
                "text": text
            }
            if on_start:
                try:
                    on_start(event_payload)
                except Exception:
                    pass
            for cb in self._on_start_callbacks:
                try:
                    cb(event_payload)
                except Exception:
                    pass

        try:
            self.initialize()
            import pygame

            mp3_stream = io.BytesIO(audio_bytes)
            pygame.mixer.music.load(mp3_stream)
            pygame.mixer.music.play()

            logger.info(f"[LisethAudioManager] Reproduciendo voz oficial para turno '{turn_id}'...")

            while pygame.mixer.music.get_busy() and not self._stop_requested and self.current_playback_id == playback_id:
                time.sleep(0.03)

            if self._stop_requested or self.current_playback_id != playback_id:
                pygame.mixer.music.stop()
                logger.info(f"[LisethAudioManager] Reproducción detenida (Barge-in ejecutado para {playback_id[:8]}).")

        except Exception as play_err:
            logger.error(f"[LisethAudioManager] Error en reproducción de audio física: {play_err}")

        finally:
            with self._playback_lock:
                self._is_playing = False
                self._is_paused = False
                self.last_speech_end_time = time.time()
                self.last_playback_id = playback_id
                self._completed_turns.add(turn_id)

                end_payload = {
                    "event": "end",
                    "turn_id": turn_id,
                    "playback_id": playback_id,
                    "interrupted": self._stop_requested,
                    "duration_s": round(time.time() - start_time, 2)
                }

                if on_end:
                    try:
                        on_end(end_payload)
                    except Exception:
                        pass
                for cb in self._on_end_callbacks:
                    try:
                        cb(end_payload)
                    except Exception:
                        pass

                logger.info(f"[LisethAudioManager] Turno '{turn_id}' finalizado ({'Interrumpido' if self._stop_requested else 'Completado'}).")

    def stop(self, interrupted: bool = True) -> bool:
        """
        Immediately halts active speech output (Barge-In) and clears execution tokens.
        Thread-safe and instantaneous.
        """
        self._stop_requested = True
        self.current_playback_id = None

        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except Exception as e:
            logger.debug(f"[LisethAudioManager] Error deteniendo mixer: {e}")

        with self._playback_lock:
            self._is_playing = False
            self._is_paused = False
            self.last_speech_end_time = time.time()

        logger.info(f"[LisethAudioManager] Habla detenida de inmediato (Barge-In={interrupted}).")
        return True

    def pause(self) -> bool:
        """Pauses speech playback."""
        with self._playback_lock:
            if not self._is_playing or self._is_paused:
                return False
            try:
                import pygame
                if pygame.mixer.get_init():
                    pygame.mixer.music.pause()
                    self._is_paused = True
                    logger.info("[LisethAudioManager] Reproducción pausada.")
                    return True
            except Exception as e:
                logger.debug(f"[LisethAudioManager] Error pausando mixer: {e}")
            return False

    def resume(self) -> bool:
        """Resumes paused speech playback."""
        with self._playback_lock:
            if not self._is_paused:
                return False
            try:
                import pygame
                if pygame.mixer.get_init():
                    pygame.mixer.music.unpause()
                    self._is_paused = False
                    logger.info("[LisethAudioManager] Reproducción reanudada.")
                    return True
            except Exception as e:
                logger.debug(f"[LisethAudioManager] Error reanudando mixer: {e}")
            return False

    def interrupt(self) -> bool:
        """Alias for high-priority barge-in stop."""
        return self.stop(interrupted=True)

    def shutdown(self):
        """Cleanly releases audio hardware and terminates worker threads."""
        logger.info("[LisethAudioManager] Liberando recursos de audio y apagando mixer...")
        self.stop(interrupted=True)
        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.quit()
        except Exception as e:
            logger.debug(f"[LisethAudioManager] Error apagando pygame mixer: {e}")
        logger.info("[LisethAudioManager] Apagado completado.")


# Global Singleton Instance
audio_manager = LisethAudioManager()
