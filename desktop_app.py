"""
JARVIS / Liseth - Native Windows Desktop Application (pywebview).
Launches FastAPI backend in a background thread and opens a native application window.
"""
import os
import sys
import threading
import time
import uvicorn
import socket
import webview
from app.config import settings

def find_available_port(preferred_port: int, host: str = "127.0.0.1") -> int:
    candidates = [preferred_port, 3001, 3002, 8000, 8080]
    for port in candidates:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                return port
        except OSError:
            continue
    return preferred_port

ACTIVE_PORT = find_available_port(settings.PORT)

def start_backend():
    """Starts the FastAPI backend inside a background thread."""
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=ACTIVE_PORT,
        log_level="warning",
        access_log=False,
    )

def main():
    print(f"[*] Iniciando backend de Liseth en http://127.0.0.1:{ACTIVE_PORT}...")
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()

    # Wait for backend to be ready
    time.sleep(1.2)

    icon_path = str(settings.STATIC_DIR / "liseth.ico")
    if not os.path.exists(icon_path):
        icon_path = None

    print("[*] Abriendo ventana nativa de escritorio...")
    window = webview.create_window(
        title="Liseth — Asistente Personal de Santiago",
        url=f"http://127.0.0.1:{ACTIVE_PORT}",
        width=1280,
        height=850,
        min_size=(900, 600),
        background_color="#04070d",
        text_select=True,
    )

    webview.start(debug=False)
    print("[*] Ventana cerrada. Liseth finalizada.")

if __name__ == "__main__":
    main()
