"""
Reverse Engineering Action for JARVIS / Liseth.
Exposes binary inspection, entropy verification, string extraction, and REA commands
to the action dispatcher and brain router.
"""
import os
import asyncio
from pathlib import Path
from typing import Any, Dict, Optional
from app.services.reverse_engineering_service import reverse_engineering_service


def reverse_engineering_action(parameters: Optional[Dict[str, Any]] = None) -> str:
    """
    Synchronous entrypoint for reverse engineering tool execution.
    Can be run in a background executor thread without blocking the event loop.
    """
    params = parameters or {}
    action = params.get("action", "inspect").lower().strip()
    target_path = params.get("target_path") or params.get("path") or params.get("file") or ""

    if not target_path and action not in ["status", "engines"]:
        return (
            "Señor Santiago, debe especificar la ruta del archivo o binario a analizar "
            "(ejemplo: target_path='C:\\Windows\\notepad.exe')."
        )

    # 1. Status query
    if action in ["status", "engines", "rea_status"]:
        return (
            "### 🛡️ Motor de Ingeniería Inversa de Liseth (REA v6.7.0)\n"
            "- **Estado del Motor**: ONLINE y vinculado a Antigravity y Liseth.\n"
            "- **Capacidades Activas**:\n"
            "  - Inspección estática nativa (PE, ELF, Mach-O, WASM, APK, SQLite).\n"
            "  - Análisis de entropía de Shannon (detección de empaquetadores y cifrado).\n"
            "  - Extracción de cadenas e indicadores de compromiso (APIs, URLs, IPs, Registros).\n"
            "  - Desempaquetado nativo de archivos Electron ASAR.\n"
            "  - Puente CLI a `rea-agents` para descompilación y recuperación de código fuente.\n"
            "- **Lanzamiento**: Soporta comandos de voz directos con respuesta de latencia 0 ms."
        )

    resolved_path = os.path.abspath(os.path.expanduser(target_path.strip('"\'')))

    if not os.path.exists(resolved_path):
        return f"Señor Santiago, el archivo indicado no existe en la ruta: `{resolved_path}`."

    # 2. String extraction only
    if action in ["strings", "cadenas"]:
        inspection = reverse_engineering_service.inspect_file(resolved_path)
        ind = inspection.get("indicators", {})
        lines = [
            f"### 🔍 Extracción de Cadenas e Indicadores: `{os.path.basename(resolved_path)}`",
            f"- **APIs Críticas**: {', '.join(ind.get('suspicious_apis', [])) or 'Ninguna detectada'}",
            f"- **URLs**: {', '.join(ind.get('urls', [])) or 'Ninguna detectada'}",
            f"- **IPs**: {', '.join(ind.get('ips', [])) or 'Ninguna detectada'}",
            f"- **Claves de Registro**: {', '.join(ind.get('registry_keys', [])) or 'Ninguna detectada'}",
            f"- **Claves API**: {', '.join(ind.get('api_keys', [])) or 'Ninguna detectada'}",
        ]
        return "\n".join(lines)

    # 3. Entropy analysis only
    if action in ["entropy", "entropia"]:
        inspection = reverse_engineering_service.inspect_file(resolved_path)
        ent = inspection.get("shannon_entropy", 0.0)
        pack = inspection.get("packing_assessment", "")
        return (
            f"### 📊 Análisis de Entropía de Shannon: `{os.path.basename(resolved_path)}`\n"
            f"- **Entropía Calculada**: `{ent} / 8.0`\n"
            f"- **Diagnóstico**: {pack}\n"
            f"- **Detalle**: Una entropía superior a 7.15 indica que el archivo probablemente está comprimido con UPX, Themida o protegido con algoritmos criptográficos."
        )

    # 4. ASAR extraction
    if action in ["asar", "extract_asar"]:
        inspection = reverse_engineering_service.inspect_file(resolved_path)
        asar = inspection.get("asar_details", {})
        if asar.get("error"):
            return f"❌ Error en archivo ASAR: {asar['error']}"
        files = asar.get("file_tree_sample", [])
        return (
            f"### 📦 Archivo Electron ASAR: `{os.path.basename(resolved_path)}`\n"
            f"- **Total de archivos indexados**: {asar.get('total_files', 0)}\n"
            f"- **Archivos clave identificados**:\n" +
            "\n".join([f"  - `{f}`" for f in files[:15]])
        )

    # 5. Full Inspection (default)
    data = reverse_engineering_service.inspect_file(resolved_path)
    return reverse_engineering_service.format_inspection_report(data)
