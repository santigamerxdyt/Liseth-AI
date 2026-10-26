"""
Stark Vault Action for JARVIS / Liseth.
Entrypoint for cryptographic password generation, entropy analysis, and secret packaging.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.services.stark_vault_service import stark_vault_service

logger = logging.getLogger("jarvis.stark_vault_action")


def stark_vault_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    params = parameters or {}
    action = str(params.get("action") or "generate").lower().strip()

    try:
        if action in ["generate", "generar", "crear_clave", "password"]:
            length = int(params.get("length") or 18)
            mode = str(params.get("mode") or "complex").lower()
            res = stark_vault_service.generate_password(length=length, mode=mode)
            return (
                f"### 🛡️ Credencial Criptográfica Stark Generada\n"
                f"- **Contraseña Generada**: `{res['password']}`\n"
                f"- **Longitud**: `{res['length']} caracteres` | **Modo**: `{res['mode']}`\n"
                f"- **Entropía de Shannon**: `{res['entropy_bits']} bits`\n"
                f"- **Puntuación de Seguridad**: `{res['score']}%` ({res['rating']})\n"
                f"- **Tiempo Estimado de Fuerza Bruta**: `{res['crack_time']}`\n\n"
                f"Copie y guarde esta credencial de forma segura, señor Santiago."
            )

        if action in ["audit", "analizar", "entropia", "strength"]:
            pwd = str(params.get("password") or params.get("text") or "")
            if not pwd:
                return "Señor Santiago, indique la contraseña o cadena a evaluar."
            audit = stark_vault_service.evaluate_password_strength(pwd)
            return (
                f"### 🔍 Auditoría Criptográfica de Contraseña\n"
                f"- **Nivel de Seguridad**: `{audit['score']}%` - **{audit['rating']}**\n"
                f"- **Entropía**: `{audit['entropy_bits']} bits` (Espacio muestral: {audit['pool_size']} caracteres)\n"
                f"- **Resistencia al Ataque**: `{audit['crack_time']}`"
            )

        if action in ["package_nfc", "nfc_beam", "compartir_secreto"]:
            secret = str(params.get("secret") or params.get("text") or "STARK-SECRET-2026")
            label = str(params.get("label") or "Credencial Protegida")
            pkg = stark_vault_service.package_secret_for_nfc(secret, label=label)
            return f"✓ Secreto '{pkg['label']}' empaquetado y listo para transmisión NFC (Checksum: `{pkg['checksum']}`)."

        return f"Acción Stark Vault '{action}' no reconocida. Opciones: 'generate', 'audit', 'package_nfc'."

    except Exception as e:
        logger.error(f"Error in stark_vault_action: {e}", exc_info=True)
        return f"Error en bóveda Stark: {str(e)}"
