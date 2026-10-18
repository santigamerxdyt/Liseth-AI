"""
System Shutdown Action for JARVIS / Liseth.
Gracefully stops all background services (voice engine, heartbeat sentinel, telegram bot)
and closes the application window and process when requested by Señor Santiago.
"""
from __future__ import annotations
import logging
import os
import sys
import threading
import time
from typing import Optional

logger = logging.getLogger("Liseth.Shutdown")


def _terminate_process_tree():
    """Stops all running services and terminates the application process."""
    logger.info("[SHUTDOWN] Deteniendo servicios de Liseth...")

    # 1. Close webview desktop windows if running
    try:
        import webview
        for win in getattr(webview, "windows", []):
            try:
                win.destroy()
            except Exception as w_err:
                logger.debug(f"[SHUTDOWN] Error cerrando ventana webview: {w_err}")
    except Exception:
        pass

    # 2. Stop native voice engine
    try:
        from app.services.voice_engine import voice_engine
        voice_engine.stop()
        logger.info("[SHUTDOWN] Motor de voz detenido.")
    except Exception as ve_err:
        logger.debug(f"[SHUTDOWN] Error deteniendo voice_engine: {ve_err}")

    # 3. Stop heartbeat sentinel
    try:
        from app.services.heartbeat_service import heartbeat_service
        heartbeat_service.stop()
        logger.info("[SHUTDOWN] Centinela de heartbeat detenido.")
    except Exception as hb_err:
        logger.debug(f"[SHUTDOWN] Error deteniendo heartbeat_service: {hb_err}")

    # 4. Stop telegram bot
    try:
        from app.services.telegram_service import telegram_service
        telegram_service.stop()
        logger.info("[SHUTDOWN] Bot de Telegram detenido.")
    except Exception as tg_err:
        logger.debug(f"[SHUTDOWN] Error deteniendo telegram_service: {tg_err}")

    # 5. Flush and exit process
    logger.info("[SHUTDOWN] Proceso finalizado. ¡Hasta luego, señor Santiago!")
    time.sleep(0.3)
    os._exit(0)


def shutdown_liseth(delay_seconds: float = 2.0, execute_exit: bool = True) -> str:
    """
    Initiates graceful shutdown of Liseth.
    Allows delay_seconds for audio response to speak and HTTP/SSE reply to dispatch.
    If execute_exit is False (e.g. during unit tests), returns without killing the test runner.
    """
    farewell = (
        "Hasta luego, señor Santiago. Ha sido un placer asistirle hoy. "
        "Cerrando la aplicación y deteniendo todos los servicios..."
    )

    if execute_exit:
        def _delayed():
            time.sleep(max(0.5, float(delay_seconds)))
            _terminate_process_tree()

        t = threading.Thread(target=_delayed, daemon=True, name="LisethShutdownThread")
        t.start()

    return farewell
