"""
Admin Privilege Management for JARVIS / Liseth.
Ensures the assistant runs with Windows Administrator privileges (elevated)
to grant full access to hardware, network, system files, and process controls.
"""
import logging
import os
import sys

logger = logging.getLogger("jarvis.admin")


def is_admin() -> bool:
    """Checks whether the current process is running with Administrator privileges."""
    if sys.platform != "win32":
        # Unix root check
        return os.geteuid() == 0 if hasattr(os, "geteuid") else False
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        logger.debug(f"[AdminCheck] Error al verificar privilegios: {e}")
        return False


def ensure_admin(force: bool = True) -> bool:
    """
    Verifies Administrator rights. If not elevated, requests Windows UAC elevation
    and relaunches the process cleanly.
    Returns True if already admin.
    """
    if is_admin():
        logger.info("[ADMIN] Proceso ejecutándose con privilegios completos de Administrador.")
        return True

    if sys.platform != "win32":
        logger.warning("[ADMIN] No es Windows; omitiendo elevación UAC.")
        return False

    if not force:
        return False

    logger.warning("[ADMIN] Privilegios insuficientes. Solicitando elevación de Administrador a Windows...")
    try:
        import ctypes
        # Format arguments
        params = " ".join(f'"{arg}"' for arg in sys.argv)
        # ShellExecute with 'runas' verb triggers the standard Windows UAC prompt
        hinstance = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            params,
            os.getcwd(),
            1  # SW_SHOWNORMAL
        )
        if hinstance > 32:
            logger.info("[ADMIN] Instancia elevada lanzada con éxito. Finalizando proceso actual sin privilegios.")
            sys.exit(0)
        else:
            logger.error(f"[ADMIN] El usuario canceló la elevación UAC (código: {hinstance}).")
            return False
    except Exception as e:
        logger.error(f"[ADMIN] Fallo al invocar ShellExecute 'runas': {e}", exc_info=True)
        return False


def get_elevation_status() -> dict:
    """Returns human-readable privilege status for telemetry and logs."""
    admin = is_admin()
    return {
        "is_admin": admin,
        "mode": "ADMINISTRADOR (Acceso Total al Sistema)" if admin else "USUARIO ESTANDAR (Privilegios Limitados)",
        "can_access_hardware": admin,
        "can_manage_services": admin,
    }
