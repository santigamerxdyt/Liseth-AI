"""
Bidirectional Telegram Service for Liseth.
Supports remote mobile commands (/start, /estado, /agenda, /resumen, /dnd, /pomodoro),
voice note processing, and natural language conversation via BrainRouter.
"""
from __future__ import annotations
import asyncio
import logging
import threading
import time
from typing import Optional, Dict, Any

import httpx

from app.config import settings

logger = logging.getLogger("Liseth.Telegram")


class TelegramService:
    _instance: Optional[TelegramService] = None

    def __new__(cls) -> TelegramService:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_state()
        return cls._instance

    def _init_state(self):
        self.token: str = settings.TELEGRAM_BOT_TOKEN
        self.default_chat_id: str = settings.TELEGRAM_CHAT_ID
        self.is_running: bool = False
        self.offset: int = 0
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def start(self):
        """Starts the Telegram polling daemon if bot token is configured."""
        self.token = settings.TELEGRAM_BOT_TOKEN or self.token
        self.default_chat_id = settings.TELEGRAM_CHAT_ID or self.default_chat_id

        if not self.token:
            logger.info("[Telegram] TELEGRAM_BOT_TOKEN no configurado. Servicio bidireccional en reposo.")
            return

        if self.is_running:
            return

        self.is_running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._poll_loop, daemon=True, name="TelegramPoller")
        self._thread.start()
        logger.info("[Telegram] Centinela bidireccional de Telegram iniciado.")

    def stop(self):
        """Stops the Telegram polling loop."""
        self.is_running = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        logger.info("[Telegram] Centinela bidireccional de Telegram detenido.")

    def _poll_loop(self):
        """Long-polling loop for Telegram updates."""
        logger.info("[Telegram] Iniciando bucle de recepción de mensajes remotos...")
        while self.is_running and not self._stop_event.is_set():
            try:
                url = f"https://api.telegram.org/bot{self.token}/getUpdates"
                params = {"offset": self.offset, "timeout": 20}
                with httpx.Client(timeout=25.0) as client:
                    resp = client.get(url, params=params)
                    if resp.status_code == 200:
                        data = resp.json()
                        updates = data.get("result", [])
                        for u in updates:
                            self.offset = u["update_id"] + 1
                            if "message" in u:
                                asyncio.run(self.handle_message(u["message"]))
                    elif resp.status_code == 401:
                        logger.error("[Telegram] TELEGRAM_BOT_TOKEN inválido (HTTP 401). Deteniendo poller.")
                        self.is_running = False
                        break
            except Exception as e:
                logger.debug(f"[Telegram] Error en sondeo getUpdates: {e}")
                self._stop_event.wait(5.0)

    async def handle_message(self, message: Dict[str, Any]) -> str:
        """Processes an incoming Telegram message (text, voice, or command)."""
        sender_chat_id = str(message.get("chat", {}).get("id", ""))
        chat_id = sender_chat_id or self.default_chat_id
        if sender_chat_id and (not self.default_chat_id or self.default_chat_id == "8820455447"):
            self.default_chat_id = sender_chat_id
            settings.TELEGRAM_CHAT_ID = sender_chat_id
            logger.info(f"[Telegram] Auto-vinculado Chat ID de Santiago: {sender_chat_id}")
            try:
                from app.routers.credentials_router import update_env_file
                update_env_file({"TELEGRAM_CHAT_ID": sender_chat_id})
            except Exception as e:
                logger.debug(f"[Telegram] No se pudo persistir TELEGRAM_CHAT_ID en .env: {e}")

        text = message.get("text", "").strip()
        voice = message.get("voice")

        # 1. Voice Note Handling
        if voice:
            reply = await self._process_voice_note(voice)
            await self.send_message(reply, chat_id=chat_id)
            return reply

        if not text:
            return ""

        # 2. Command Interception
        cmd = text.lower().split()[0].split("@")[0]

        if cmd in ["/start", "/help", "/ayuda"]:
            reply = (
                f"¡Hola, señor Santiago! Soy Liseth, su asistente personal.\n\n"
                f"✓ *Canal seguro sincronizado* (Chat ID: `{chat_id}`).\n\n"
                "Comandos rápidos disponibles:\n"
                "• /estado - Telemetría y estado del sistema\n"
                "• /agenda - Sus reuniones de hoy\n"
                "• /resumen - Resumen ejecutivo de Gmail y pendientes\n"
                "• /dnd - Activar/desactivar Modo No Molestar\n"
                "• /pomodoro - Iniciar trabajo profundo (50 min)\n\n"
                "También puede enviarme cualquier instrucción o nota de voz directamente."
            )

        elif cmd in ["/estado", "/status"]:
            import psutil
            from app.services.heartbeat_service import heartbeat_service
            from app.services.brain_router import brain_router
            ram = psutil.virtual_memory().percent
            cpu = psutil.cpu_percent(interval=None)
            dnd = "Activado 🌙" if heartbeat_service.gatekeeper.dnd_mode else "Desactivado 🔔"
            reply = (
                f"🖥️ *Telemetría del Sistema:*\n"
                f"• CPU: {cpu:.1f}%\n"
                f"• RAM: {ram:.1f}%\n"
                f"• Modo No Molestar: {dnd}\n"
                f"• Modelo Activo: `{brain_router.active_gemini_model}`"
            )

        elif cmd in ["/agenda", "/reuniones"]:
            from app.services.calendar_service import calendar_service
            reply = calendar_service.format_daily_agenda()

        elif cmd in ["/resumen", "/inbox"]:
            from app.connectors.google_workspace import google_connector
            from app.services.commitment_service import commitment_service
            mail_summary = await google_connector.get_smart_inbox_summary(max_results=5)
            commitments = commitment_service.list_commitments(status="pending")
            comm_text = f"\n\n📋 *Compromisos pendientes ({len(commitments)}):*\n" + "\n".join(
                [f"- {c['text']} ({c.get('due_time')})" for c in commitments[:5]]
            ) if commitments else "\n\nNo tiene compromisos pendientes hoy."
            reply = f"{mail_summary}{comm_text}"

        elif cmd in ["/dnd", "/silencio"]:
            from app.services.heartbeat_service import heartbeat_service
            state = heartbeat_service.gatekeeper.toggle_dnd()
            reply = f"Modo No Molestar {'activado 🌙' if state else 'desactivado 🔔'}, señor Santiago."

        elif cmd in ["/pomodoro", "/concentracion", "/deepwork"]:
            from app.actions.deep_work import deep_work_manager
            res = deep_work_manager.start_session(duration_minutes=50, task="Trabajo remoto")
            reply = res["message"]

        else:
            # 3. Natural language query processed by BrainRouter
            try:
                from app.services.brain_router import brain_router
                from app.services.soul_service import soul_service
                sys_inst = soul_service.build_system_instruction(
                    "Estás respondiendo a través de Telegram a tu creador y único administrador, el Señor Santiago. "
                    "Responde siempre con dulzura, calidez, lealtad y elegancia ejecutiva. "
                    "Utiliza formato Markdown limpio y conciso adaptado a la lectura en dispositivos móviles."
                )
                res = await brain_router.generate_response(
                    prompt=text,
                    system_prompt=sys_inst,
                    user_id=f"tg_{chat_id}",
                    platform="telegram"
                )
                reply = res.get("text", "He procesado su solicitud con éxito, señor Santiago.")
            except Exception as e:
                logger.error(f"[Telegram] Error procesando con BrainRouter: {e}")
                reply = f"Lo siento, señor Santiago, ocurrió un error procesando su mensaje: {e}"

        await self.send_message(reply, chat_id=chat_id)
        return reply

    async def _process_voice_note(self, voice_dict: dict) -> str:
        """Fetches voice note file from Telegram and transcribes/processes it."""
        file_id = voice_dict.get("file_id")
        if not file_id or not self.token:
            return "Recibí su nota de voz, pero no fue posible descargar el archivo de audio."

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                info_res = await client.get(f"https://api.telegram.org/bot{self.token}/getFile?file_id={file_id}")
                if info_res.status_code == 200:
                    file_path = info_res.json().get("result", {}).get("file_path", "")
                    if file_path:
                        audio_url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
                        audio_data = await client.get(audio_url)
                        if audio_data.status_code == 200:
                            # Send audio to multi-brain router (Gemini multimodal with Groq/Claude/OpenAI fallback)
                            import base64
                            b64 = base64.b64encode(audio_data.content).decode("utf-8")
                            contents = [{
                                "role": "user",
                                "parts": [
                                    {"inline_data": {"mime_type": "audio/ogg", "data": b64}},
                                    {"text": "El usuario Santiago te envió esta nota de voz por Telegram. Escúchala con atención, responde a lo que pide o necesita con dulzura, elegancia y precisión ejecutiva."}
                                ]
                            }]
                            from app.services.brain_router import brain_router
                            from app.services.soul_service import soul_service
                            sys_inst = soul_service.build_system_instruction("Respuesta por Telegram a nota de voz del Señor Santiago.")
                            res = await brain_router.generate_response(
                                contents=contents,
                                system_prompt=sys_inst,
                                user_id=f"tg_{self.default_chat_id}",
                                platform="telegram"
                            )
                            return res.get("text", "He recibido y procesado su nota de voz, señor Santiago.")
        except Exception as e:
            logger.debug(f"[Telegram] Error descargando/procesando audio: {e}")

        return "He recibido su nota de voz por Telegram, señor Santiago."

    async def send_message(self, text: str, chat_id: Optional[str] = None) -> bool:
        """Sends a text message to Santiago's Telegram chat."""
        target_chat = chat_id or self.default_chat_id or settings.TELEGRAM_CHAT_ID
        bot_tok = self.token or settings.TELEGRAM_BOT_TOKEN

        if not bot_tok or not target_chat:
            logger.debug("[Telegram] Token o Chat ID ausente para envío de mensaje.")
            return False

        try:
            url = f"https://api.telegram.org/bot{bot_tok}/sendMessage"
            payload = {
                "chat_id": target_chat,
                "text": text,
                "parse_mode": "Markdown",
            }
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    return True
                # If markdown parse fails, retry without markdown
                if "can't parse entities" in resp.text.lower() or resp.status_code == 400:
                    payload.pop("parse_mode", None)
                    resp2 = await client.post(url, json=payload)
                    return resp2.status_code == 200
                logger.warning(f"[Telegram] Error enviando mensaje HTTP {resp.status_code}: {resp.text}")
                return False
        except Exception as e:
            logger.debug(f"[Telegram] Error en send_message: {e}")
            return False


telegram_service = TelegramService()
