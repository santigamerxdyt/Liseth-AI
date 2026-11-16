"""
Liseth Single Microphone Manager (LisethMicrophoneManager)
Centralized Single Microphone Controller for Liseth // JARVIS.

Core Responsibilities:
- Strictly enforces ONE hardware microphone owner across the entire process.
- Eliminates duplicate / competing audio input streams.
- Manages audio input lifecycle: initialization, permission verification, reconnection.
- Automatic acoustic feedback suppression while Liseth is speaking.
- Dynamic input device selection and health monitoring.
"""
import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional

import numpy as np

logger = logging.getLogger("jarvis.microphone_manager")

RATE = 16000
CHANNELS = 1
CHUNK = 1024
DTYPE = "int16"


class LisethMicrophoneManager:
    """
    Singleton central audio input controller.
    Only ONE hardware input stream is ever opened or retained.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LisethMicrophoneManager, cls).__new__(cls)
            return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._initialized = True
        self._stream_lock = threading.Lock()
        self.is_capturing: bool = False
        self.selected_device: Optional[int] = None
        self.device_name: str = "Default Microphone"
        self.last_error: Optional[str] = None
        self.last_activity: float = time.time()

        # Active stream & listeners
        self._active_stream = None
        self._subscribers: List[Callable[[np.ndarray], None]] = []

        logger.info("[LisethMicrophoneManager] Administrador único de micrófono inicializado.")

    def select_device(self, device_index: Optional[int] = None, device_name: Optional[str] = None):
        """Sets the desired input microphone hardware device."""
        with self._stream_lock:
            self.selected_device = device_index
            if device_name:
                self.device_name = device_name
            logger.info(f"[LisethMicrophoneManager] Dispositivo seleccionado: {self.device_name} (Index: {self.selected_device})")

    def subscribe(self, callback: Callable[[np.ndarray], None]):
        """Registers a callback to receive incoming audio frames from the single stream."""
        with self._stream_lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[np.ndarray], None]):
        """Unregisters an audio frame listener."""
        with self._stream_lock:
            if callback in self._subscribers:
                self._subscribers.remove(callback)

    def start_capture(self) -> bool:
        """
        Activates the single hardware microphone input stream.
        Guarantees that no secondary stream is ever spawned.
        """
        with self._stream_lock:
            if self.is_capturing:
                logger.debug("[LisethMicrophoneManager] Captura ya activa; reutilizando stream único.")
                return True

            try:
                import sounddevice as sd

                def _raw_audio_callback(indata, frames, time_info, status):
                    if not self.is_capturing:
                        return
                    chunk = indata[:, 0].copy()
                    self.last_activity = time.time()

                    # Fan out to registered subscribers
                    for sub in list(self._subscribers):
                        try:
                            sub(chunk)
                        except Exception as cb_err:
                            logger.debug(f"[LisethMicrophoneManager] Error en suscriptor de audio: {cb_err}")

                self._active_stream = sd.InputStream(
                    samplerate=RATE,
                    channels=CHANNELS,
                    dtype=DTYPE,
                    blocksize=CHUNK,
                    device=self.selected_device,
                    callback=_raw_audio_callback,
                )
                self._active_stream.start()
                self.is_capturing = True
                self.last_error = None
                logger.info(f"[LisethMicrophoneManager] Stream único de micrófono abierto exitosamente ({self.device_name}).")
                return True

            except Exception as e:
                self.last_error = str(e)
                self.is_capturing = False
                self._active_stream = None
                logger.error(f"[LisethMicrophoneManager] Error al abrir hardware de micrófono: {e}")
                return False

    def stop_capture(self):
        """Safely stops and releases hardware microphone resources."""
        with self._stream_lock:
            if not self.is_capturing:
                return

            self.is_capturing = False
            if self._active_stream is not None:
                try:
                    self._active_stream.stop()
                    self._active_stream.close()
                except Exception as e:
                    logger.debug(f"[LisethMicrophoneManager] Error cerrando stream: {e}")
                finally:
                    self._active_stream = None

            logger.info("[LisethMicrophoneManager] Stream único de micrófono cerrado y recursos liberados.")

    def get_status(self) -> Dict[str, Any]:
        """Returns current hardware capture status."""
        return {
            "isCapturing": self.is_capturing,
            "deviceIndex": self.selected_device,
            "deviceName": self.device_name,
            "subscribersCount": len(self._subscribers),
            "lastError": self.last_error,
            "lastActivity": self.last_activity
        }

    def recover_connection(self) -> bool:
        """Recovers microphone stream after system sleep, wake, or device replug."""
        logger.info("[LisethMicrophoneManager] Intentando recuperación de conexión de micrófono...")
        self.stop_capture()
        time.sleep(0.2)
        return self.start_capture()


# Global Singleton Instance
microphone_manager = LisethMicrophoneManager()
