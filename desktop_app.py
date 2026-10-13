"""
JARVIS / Liseth - Native Windows Desktop Application (pywebview).
Launches FastAPI backend in a background thread and opens a native application window.
"""
import os
import sys
import threading
import time
import uvicorn
import webview
from app.config import settings

def start_backend():
    """Starts the FastAPI backend inside a background thread."""
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=settings.PORT,
        log_level="warning",
        access_log=False,
    )

def main():
    print(f"[*] Iniciando backend de Liseth en http://127.0.0.1:{settings.PORT}...")
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
        url=f"http://127.0.0.1:{settings.PORT}",
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
