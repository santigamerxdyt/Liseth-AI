"""
JARVIS / Liseth - Unified Launcher Script.
Performs pre-flight checks, auto-generates secure encryption keys if missing,
validates dependencies, and starts the server or native desktop window.
"""
import argparse
import os
import re
import secrets
import socket
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent


def get_local_lan_ip() -> str:
    """Attempts to discover LAN IP address for mobile PWA access."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def check_and_harden_env():
    """
    Checks .env file, creates it from .env.example if missing,
    and automatically replaces default MASTER_ENCRYPTION_KEY with a secure key.
    """
    env_file = BASE_DIR / ".env"
    example_file = BASE_DIR / ".env.example"

    if not env_file.exists():
        if example_file.exists():
            print("[*] Creando .env inicial a partir de .env.example...")
            content = example_file.read_text(encoding="utf-8")
        else:
            content = "PORT=3000\nHOST=127.0.0.1\nJARVIS_ACCESS_PIN=1234\n"
        env_file.write_text(content, encoding="utf-8")

    content = env_file.read_text(encoding="utf-8")
    modified = False

    # Check for default or empty MASTER_ENCRYPTION_KEY
    forbidden_keys = [
        "jarvis-secret-key-32-chars-change-me",
        "jarvis-liseth-default-secure-key-32b",
        "",
    ]

    key_match = re.search(r"^MASTER_ENCRYPTION_KEY=(.*)$", content, re.MULTILINE)
    current_key = key_match.group(1).strip() if key_match else ""

    if current_key in forbidden_keys:
        new_key = secrets.token_urlsafe(32)
        print("[!] ATENCIÓN: Detectada MASTER_ENCRYPTION_KEY por defecto.")
        print("[+] Generando clave criptográfica segura aleatoria para tu instalación...")
        if key_match:
            content = re.sub(
                r"^MASTER_ENCRYPTION_KEY=.*$",
                f"MASTER_ENCRYPTION_KEY={new_key}",
                content,
                flags=re.MULTILINE,
            )
        else:
            content += f"\nMASTER_ENCRYPTION_KEY={new_key}\n"
        modified = True

    # Check for SESSION_SECRET
    if "SESSION_SECRET=" not in content:
        session_secret = secrets.token_hex(32)
        content += f"\nSESSION_SECRET={session_secret}\n"
        modified = True

    if modified:
        env_file.write_text(content, encoding="utf-8")
        print("[+] Archivo .env asegurado y actualizado correctamente.")

    # Check PIN
    pin_match = re.search(r"^JARVIS_ACCESS_PIN=(.*)$", content, re.MULTILINE)
    current_pin = pin_match.group(1).strip() if pin_match else ""
    if current_pin in ["1234", "0000", "1111", ""]:
        print("\n" + "=" * 65)
        print(" [!] AVISO DE SEGURIDAD (PIN DE ACCESO):")
        print(f" Tu JARVIS_ACCESS_PIN actual es '{current_pin or 'VACÍO'}'.")
        print(" Por favor cámbialo en tu archivo .env por un PIN seguro.")
        print("=" * 65 + "\n")


def check_dependencies():
    """Checks required python libraries."""
    required = ["fastapi", "uvicorn", "sqlalchemy", "aiosqlite", "cryptography", "httpx"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"[!] Faltan dependencias necesarias: {', '.join(missing)}")
        print("Instálalas ejecutando: python -m pip install -r requirements.txt")
        sys.exit(1)


def find_available_port(preferred_port: int, host: str = "127.0.0.1") -> int:
    """Autonomously finds an open port if preferred port is in use."""
    candidates = [preferred_port, 3001, 3002, 8000, 8080]
    for port in candidates:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                return port
        except OSError:
            continue
    return preferred_port


def main():
    parser = argparse.ArgumentParser(description="Lanzador de JARVIS / Liseth")
    parser.add_argument("--desktop", action="store_true", help="Abrir como aplicación nativa de escritorio")
    parser.add_argument("--host", type=str, default=None, help="Host a enlazar (ej. 127.0.0.1 o 0.0.0.0)")
    parser.add_argument("--port", type=int, default=None, help="Puerto a enlazar (ej. 3000 u 8000)")
    args = parser.parse_args()

    # Pre-flight security and env check
    check_and_harden_env()
    check_dependencies()

    from app.config import settings

    host = args.host or settings.HOST
    requested_port = args.port or settings.PORT
    port = find_available_port(requested_port, host)
    settings.PORT = port
    if f"http://127.0.0.1:{port}" not in settings.ALLOWED_ORIGINS:
        settings.ALLOWED_ORIGINS.extend([f"http://127.0.0.1:{port}", f"http://localhost:{port}"])
    if port != requested_port:
        print(f"[!] Puerto {requested_port} ocupado. Conmutando autónomamente al puerto {port}...")

    lan_ip = get_local_lan_ip()

    banner = f"""
  +-----------------------------------------------------------+
  |              LISETH - ASISTENTE INTELIGENTE               |
  |                  Arquitectura Python 2.0                  |
  +-----------------------------------------------------------+
  [+] Estado Backend  : ONLINE
  [+] Base de Datos   : SQLite WAL (data/jarvis.db)
  [+] Acceso Local    : http://127.0.0.1:{port}
  [+] Acceso LAN / PWA: http://{lan_ip}:{port}
  [+] Modo Escritorio : {'ACTIVADO' if args.desktop else 'DESACTIVADO (Navegador)'}
  -------------------------------------------------------------
"""
    try:
        print(banner)
    except Exception:
        pass

    if args.desktop:
        import desktop_app
        desktop_app.main()
    else:
        import uvicorn
        uvicorn.run("app.main:app", host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
