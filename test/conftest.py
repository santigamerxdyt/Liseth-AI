import os

# Prevent background internet polling during tests in sandboxed environment
os.environ["TELEGRAM_BOT_TOKEN"] = ""

from app.services.heartbeat_service import heartbeat_service
from app.services.telegram_service import telegram_service

heartbeat_service.start = lambda: None
telegram_service.start = lambda: None
