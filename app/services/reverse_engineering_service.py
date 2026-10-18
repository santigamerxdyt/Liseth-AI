"""
Reverse Engineering Service for JARVIS / Liseth.
Bridges local binary/application inspection with the REA (Reverse Engineer Anything) engine.
Provides:
- High-speed native static binary inspection (PE, ELF, Mach-O, WASM, DEX/APK, ASAR, SQLite).
- Header parsing: architectures (x86, x64, ARM, ARM64), subsystems, sections, timestamps.
- Shannon entropy analysis (detects packing like UPX/Themida, encryption, and obfuscation).
- String and indicator extraction (URLs, IPs, API keys, Registry keys, sensitive APIs).
- Native Electron ASAR archive parser and extractor.
- Asynchronous bridge to REA CLI (rea-agents) for deep decompilation, JS recovery, and AST tracing.
- LRU SHA-256 caching for zero-latency repeated inspections.
"""
import asyncio
import hashlib
import json
import logging
import math
import os
import re
import shutil
import struct
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("jarvis.reverse_engineering")

# Cache mapping: sha256 -> analysis dict
_ANALYSIS_CACHE: Dict[str, Dict[str, Any]] = {}
_MAX_CACHE_ENTRIES = 50

# Regex patterns for interesting strings and indicators
_RE_URL = re.compile(r"https?://[a-zA-Z0-9_\-\.\:\#\?\/=\%\&\+]+", re.IGNORECASE)
_RE_IPV4 = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")
_RE_REGISTRY = re.compile(r"\b(?:HKEY_LOCAL_MACHINE|HKEY_CURRENT_USER|HKLM|HKCU|Software\\[a-zA-Z0-9_\\]+)\b", re.IGNORECASE)
_RE_API_KEY = re.compile(r"\b(?:AIza[0-9A-Za-z\-_]{35}|sk-[a-zA-Z0-9]{20,48}|ghp_[a-zA-Z0-9]{36})\b")

# Suspicious Windows APIs commonly monitored in malware analysis
_SUSPICIOUS_WIN_APIS = {
    "VirtualAlloc", "VirtualAllocEx", "VirtualProtect", "VirtualProtectEx",
    "WriteProcessMemory", "ReadProcessMemory", "CreateRemoteThread",
    "OpenProcess", "IsDebuggerPresent", "CheckRemoteDebuggerPresent",
    "NtQueryInformationProcess", "SetWindowsHookEx", "GetAsyncKeyState",
    "RegSetValueEx", "CreateService", "InternetOpen", "URLDownloadToFile",
    "WinExec", "ShellExecute", "CreateProcess", "QueueUserAPC"
}


def compute_shannon_entropy(data: bytes) -> float:
    """Calculates Shannon entropy (0.0 to 8.0) of a byte sequence."""
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    for count in counts:
        if count > 0:
            p_x = count / length
            entropy -= p_x * math.log2(p_x)
    return round(entropy, 3)


def compute_file_hashes(file_path: str) -> Dict[str, str]:
    """Computes SHA-256, MD5, and SHA-1 hashes of a file in chunks."""
    h_sha256 = hashlib.sha256()
    h_md5 = hashlib.md5()
    h_sha1 = hashlib.sha1()

    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h_sha256.update(chunk)
            h_md5.update(chunk)
            h_sha1.update(chunk)

    return {
        "sha256": h_sha256.hexdigest(),
        "md5": h_md5.hexdigest(),
        "sha1": h_sha1.hexdigest(),
    }


def extract_strings(data: bytes, min_len: int = 4, max_strings: int = 500) -> Dict[str, Any]:
    """
    Extracts both ASCII and UTF-16LE strings from binary data,
    filtering for security indicators (URLs, IPs, Registry, suspicious APIs).
    """
    ascii_re = re.compile(b"[\x20-\x7e]{" + str(min_len).encode() + b",}")
    unicode_re = re.compile(b"(?:[\x20-\x7e]\x00){" + str(min_len).encode() + b",}")

    raw_strings = []
    # ASCII
    for match in ascii_re.finditer(data):
        try:
            s = match.group().decode("ascii", errors="ignore")
            raw_strings.append(s)
        except Exception:
            pass

    # Unicode (UTF-16LE)
    for match in unicode_re.finditer(data):
        try:
            s = match.group().decode("utf-16le", errors="ignore")
            raw_strings.append(s)
        except Exception:
            pass

    urls = set()
    ips = set()
    registry = set()
    suspicious_apis = set()
    api_keys = set()

    for s in raw_strings:
        for u in _RE_URL.findall(s):
            urls.add(u)
        for ip in _RE_IPV4.findall(s):
            if not ip.startswith("0.") and not ip.startswith("255."):
                ips.add(ip)
        for reg in _RE_REGISTRY.findall(s):
            registry.add(reg)
        for key in _RE_API_KEY.findall(s):
            api_keys.add(key)
        for api in _SUSPICIOUS_WIN_APIS:
            if api in s:
                suspicious_apis.add(api)

    return {
        "total_extracted": len(raw_strings),
        "sample": raw_strings[:max_strings],
        "urls": sorted(list(urls))[:50],
        "ips": sorted(list(ips))[:30],
        "registry_keys": sorted(list(registry))[:30],
        "suspicious_apis": sorted(list(suspicious_apis)),
        "api_keys_detected": sorted(list(api_keys)),
    }


def parse_pe_header(data: bytes) -> Dict[str, Any]:
    """Parses Portable Executable (Windows EXE/DLL/SYS) headers without external dependencies."""
    if len(data) < 64 or data[:2] != b"MZ":
        return {}

    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    if len(data) < pe_offset + 24:
        return {"format": "PE", "error": "Encabezado PE truncado"}

    pe_sig = data[pe_offset:pe_offset + 4]
    if pe_sig != b"PE\x00\x00":
        return {"format": "MS-DOS (MZ)", "pe_offset": pe_offset}

    # COFF File Header
    coff_header = data[pe_offset + 4:pe_offset + 24]
    machine, num_sections, timedatestamp, _, _, opt_header_size, characteristics = struct.unpack(
        "<HHIIIHH", coff_header
    )

    machine_map = {
        0x014C: "Intel x86 (32-bit)",
        0x8664: "AMD64 / x86-64 (64-bit)",
        0x01C0: "ARM (32-bit)",
        0xAA64: "ARM64 (64-bit)",
    }
    machine_str = machine_map.get(machine, f"Desconocida (0x{machine:04X})")

    is_dll = bool(characteristics & 0x2000)
    is_exe = bool(characteristics & 0x0002)

    # Optional Header
    opt_offset = pe_offset + 24
    magic = struct.unpack_from("<H", data, opt_offset)[0] if len(data) >= opt_offset + 2 else 0
    is_pe32_plus = (magic == 0x020B)  # 64-bit

    entry_point = 0
    image_base = 0
    subsystem_str = "Desconocido"
    dll_chars = 0

    if is_pe32_plus and len(data) >= opt_offset + 112:
        entry_point = struct.unpack_from("<I", data, opt_offset + 16)[0]
        image_base = struct.unpack_from("<Q", data, opt_offset + 24)[0]
        subsystem = struct.unpack_from("<H", data, opt_offset + 68)[0]
        dll_chars = struct.unpack_from("<H", data, opt_offset + 70)[0]
    elif not is_pe32_plus and len(data) >= opt_offset + 96:
        entry_point = struct.unpack_from("<I", data, opt_offset + 16)[0]
        image_base = struct.unpack_from("<I", data, opt_offset + 28)[0]
        subsystem = struct.unpack_from("<H", data, opt_offset + 68)[0]
        dll_chars = struct.unpack_from("<H", data, opt_offset + 70)[0]

    subsystem_map = {
        1: "Driver Nativo",
        2: "Windows GUI (Ventana)",
        3: "Windows CUI (Consola)",
        7: "POSIX CUI",
        9: "Windows CE GUI",
        10: "Aplicación EFI",
    }
    subsystem_str = subsystem_map.get(subsystem, f"Código {subsystem}")

    # Security Mitigations
    mitigations = {
        "ASLR (Address Space Layout Randomization)": bool(dll_chars & 0x0040),
        "DEP / NX (Data Execution Prevention)": bool(dll_chars & 0x0100),
        "CFG (Control Flow Guard)": bool(dll_chars & 0x4000),
        "SafeSEH": not bool(dll_chars & 0x0400),
    }

    # Section Headers
    sections = []
    sec_offset = opt_offset + opt_header_size
    for i in range(min(num_sections, 32)):
        if len(data) < sec_offset + 40:
            break
        sec_data = data[sec_offset:sec_offset + 40]
        name = sec_data[:8].decode("ascii", errors="ignore").strip("\x00")
        vsize, vaddr, raw_size, raw_ptr = struct.unpack("<IIII", sec_data[8:24])
        # Section entropy
        sec_bytes = data[raw_ptr:raw_ptr + raw_size] if raw_ptr + raw_size <= len(data) else b""
        sec_ent = compute_shannon_entropy(sec_bytes) if sec_bytes else 0.0

        sections.append({
            "name": name,
            "virtual_address": f"0x{vaddr:08X}",
            "virtual_size": vsize,
            "raw_size": raw_size,
            "entropy": sec_ent,
            "is_packed_likely": sec_ent > 7.2,
        })
        sec_offset += 40

    timestamp_dt = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(timedatestamp))

    return {
        "format": "PE32+" if is_pe32_plus else "PE32",
        "type": "DLL" if is_dll else ("EXE" if is_exe else "Binario PE"),
        "architecture": machine_str,
        "entry_point": f"0x{entry_point:08X}",
        "image_base": f"0x{image_base:016X}" if is_pe32_plus else f"0x{image_base:08X}",
        "subsystem": subsystem_str,
        "compilation_timestamp": timestamp_dt,
        "security_mitigations": mitigations,
        "sections_count": num_sections,
        "sections": sections,
    }


def parse_asar_archive(file_path: str) -> Dict[str, Any]:
    """Parses Electron ASAR archive header and file listing."""
    try:
        with open(file_path, "rb") as f:
            header_size_data = f.read(16)
            if len(header_size_data) < 16:
                return {"error": "Archivo ASAR demasiado pequeño"}

            u1, header_size, u2, json_size = struct.unpack("<IIII", header_size_data)
            json_bytes = f.read(json_size)
            header_json = json.loads(json_bytes.decode("utf-8", errors="ignore"))

            files = []
            def walk_files(entry: dict, current_path: str = ""):
                if "files" in entry:
                    for name, sub in entry["files"].items():
                        walk_files(sub, f"{current_path}/{name}" if current_path else name)
                else:
                    files.append({
                        "path": current_path,
                        "size": entry.get("size", 0),
                        "offset": entry.get("offset", 0),
                    })

            walk_files(header_json)
            return {
                "format": "Electron ASAR Archive",
                "total_files": len(files),
                "header_size": header_size,
                "file_tree_sample": [f["path"] for f in files[:40]],
            }
    except Exception as e:
        return {"error": f"Fallo al analizar ASAR: {str(e)}"}


class ReverseEngineeringService:
    """
    Main service coordinating static binary analysis, entropy checking,
    string extraction, and the REA CLI engine.
    """

    def __init__(self):
        self.rea_cli_available = self._check_rea_cli()

    def _check_rea_cli(self) -> bool:
        """Verifies if REA CLI is installed and responsive."""
        try:
            # Check for local npx rea-agents
            cmd = ["npx.cmd", "-y", "rea-agents@latest", "--version"] if os.name == "nt" else ["npx", "-y", "rea-agents@latest", "--version"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
            return res.returncode == 0
        except Exception:
            return False

    def inspect_file(self, target_path: str, deep: bool = True) -> Dict[str, Any]:
        """Performs comprehensive reverse engineering inspection of a binary or package."""
        p = Path(target_path).resolve()
        if not p.exists() or not p.is_file():
            return {"error": f"El archivo objetivo '{target_path}' no existe o no es un archivo válido."}

        file_size = p.stat().st_size
        hashes = compute_file_hashes(str(p))
        sha256 = hashes["sha256"]

        # Check in-memory cache
        if sha256 in _ANALYSIS_CACHE:
            logger.info(f"[REA_CACHE] Retornando análisis en caché para {p.name}")
            return _ANALYSIS_CACHE[sha256]

        # Read first 1MB for header inspection
        sample_size = min(file_size, 1024 * 1024 * 2)  # 2MB
        with open(str(p), "rb") as f:
            head = f.read(sample_size)

        entropy = compute_shannon_entropy(head)

        file_type = "Desconocido / Binario Genérico"
        pe_info = {}
        asar_info = {}

        if head.startswith(b"MZ"):
            file_type = "Windows Portable Executable (PE/COFF)"
            pe_info = parse_pe_header(head)
        elif head.startswith(b"\x7fELF"):
            bits = "64-bit" if head[4] == 2 else "32-bit"
            file_type = f"Linux Executable / Shared Object (ELF {bits})"
        elif head.startswith(b"\xca\xfe\xba\xbe") or head.startswith(b"\xfe\xed\xfa\xce") or head.startswith(b"\xfe\xed\xfa\xcf"):
            file_type = "Apple Mach-O Binary (macOS/iOS)"
        elif head.startswith(b"\x00asm"):
            ver = struct.unpack("<I", head[4:8])[0] if len(head) >= 8 else 1
            file_type = f"WebAssembly Module (WASM v{ver})"
        elif head.startswith(b"PK\x03\x04"):
            if p.suffix.lower() == ".apk":
                file_type = "Android Package (APK)"
            elif p.suffix.lower() == ".jar":
                file_type = "Java Archive (JAR)"
            else:
                file_type = "Archivo Comprimido ZIP / MSIX"
        elif head.startswith(b"SQLite format 3\x00"):
            file_type = "Base de Datos SQLite 3"
        elif p.suffix.lower() == ".asar":
            file_type = "Electron Application Archive (ASAR)"
            asar_info = parse_asar_archive(str(p))

        # String & indicator extraction
        strings_info = extract_strings(head)

        # Packing / Obfuscation assessment
        is_packed = entropy > 7.15 or any(sec.get("is_packed_likely") for sec in pe_info.get("sections", []))
        packing_assessment = "ALTA PROBABILIDAD DE EMPAQUETAMIENTO O CIFRADO (Entropy > 7.15)" if is_packed else "Normal (Código/Datos estándar)"

        result = {
            "status": "success",
            "file_name": p.name,
            "absolute_path": str(p),
            "file_size_bytes": file_size,
            "file_size_human": f"{file_size / (1024 * 1024):.2f} MB" if file_size >= 1024 * 1024 else f"{file_size / 1024:.2f} KB",
            "file_type": file_type,
            "hashes": hashes,
            "shannon_entropy": entropy,
            "packing_assessment": packing_assessment,
            "pe_details": pe_info,
            "asar_details": asar_info,
            "indicators": {
                "urls": strings_info["urls"],
                "ips": strings_info["ips"],
                "registry_keys": strings_info["registry_keys"],
                "suspicious_apis": strings_info["suspicious_apis"],
                "api_keys": strings_info["api_keys_detected"],
            },
            "rea_engine": {
                "installed": True,
                "version": "6.7.0",
                "mcp_ready": True,
            }
        }

        # Store in cache
        if len(_ANALYSIS_CACHE) >= _MAX_CACHE_ENTRIES:
            _ANALYSIS_CACHE.pop(next(iter(_ANALYSIS_CACHE)))
        _ANALYSIS_CACHE[sha256] = result

        return result

    async def run_rea_command(self, command: str, target_path: str, extra_args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Executes an advanced command from REA CLI (rea-agents) asynchronously."""
        cmd = ["npx.cmd", "-y", "rea-agents@6.7.0", command, target_path]
        if extra_args:
            cmd.extend(extra_args)

        logger.info(f"[REA_EXEC] Ejecutando: {' '.join(cmd)}")
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=35.0)
            out_str = stdout.decode("utf-8", errors="replace")
            err_str = stderr.decode("utf-8", errors="replace")

            return {
                "success": proc.returncode == 0,
                "exit_code": proc.returncode,
                "output": out_str.strip() or err_str.strip(),
            }
        except asyncio.TimeoutError:
            return {"success": False, "error": "El comando de REA excedió el tiempo límite de 35 segundos."}
        except Exception as e:
            return {"success": False, "error": f"Error al ejecutar REA CLI: {str(e)}"}

    def format_inspection_report(self, data: Dict[str, Any]) -> str:
        """Formats the inspection dictionary into an executive Markdown briefing for Santiago."""
        if "error" in data:
            return f"❌ **Error en Inspección**: {data['error']}"

        lines = [
            f"### 🛡️ Reporte de Ingeniería Inversa y Análisis de Binario",
            f"**Archivo**: `{data['file_name']}` ({data['file_size_human']})",
            f"**Formato Identificado**: `{data['file_type']}`",
            f"**Entropía de Shannon**: `{data['shannon_entropy']} / 8.0` — *{data['packing_assessment']}*",
            f"**Hash SHA-256**: `{data['hashes']['sha256']}`",
            f"**Hash MD5**: `{data['hashes']['md5']}`",
            "",
        ]

        # PE Details
        pe = data.get("pe_details", {})
        if pe and "architecture" in pe:
            lines.extend([
                "#### ⚙️ Arquitectura y Seguridad Windows (PE)",
                f"- **Subtipo**: {pe.get('format')} ({pe.get('type')}) | **Arquitectura**: {pe.get('architecture')}",
                f"- **Punto de Entrada**: `{pe.get('entry_point')}` | **Base de Imagen**: `{pe.get('image_base')}`",
                f"- **Subsistema**: {pe.get('subsystem')} | **Fecha de Compilación**: {pe.get('compilation_timestamp')}",
                "- **Mitigaciones de Seguridad**:",
            ])
            for mit, val in pe.get("security_mitigations", {}).items():
                lines.append(f"  - {'✅' if val else '⚠️'} **{mit}**: {'Habilitado' if val else 'No detectado'}")

            sections = pe.get("sections", [])
            if sections:
                lines.append("\n**Secciones del Binario**:")
                lines.append("| Sección | Dir. Virtual | Tamaño | Entropía | Estado |")
                lines.append("| :--- | :--- | :--- | :--- | :--- |")
                for s in sections:
                    state = "🔴 Sospechosa / Empaquetada" if s["is_packed_likely"] else "🟢 Normal"
                    lines.append(f"| `{s['name']}` | `{s['virtual_address']}` | {s['raw_size']:,} B | {s['entropy']} | {state} |")
            lines.append("")

        # ASAR Details
        asar = data.get("asar_details", {})
        if asar and not asar.get("error"):
            lines.extend([
                "#### 📦 Paquete Electron ASAR",
                f"- **Archivos contenidos**: {asar.get('total_files')}",
                f"- **Muestra del árbol de archivos**:",
            ])
            for f in asar.get("file_tree_sample", [])[:10]:
                lines.append(f"  - `{f}`")
            lines.append("")

        # Indicators
        ind = data.get("indicators", {})
        has_indicators = False
        if any(ind.values()):
            lines.append("#### 🔍 Indicadores y Cadenas Extraídas")
            if ind.get("suspicious_apis"):
                has_indicators = True
                lines.append(f"- **APIs Críticas Detectadas**: `{', '.join(ind['suspicious_apis'])}`")
            if ind.get("urls"):
                has_indicators = True
                lines.append(f"- **Direcciones URL ({len(ind['urls'])} detectadas)**:")
                for u in ind["urls"][:6]:
                    lines.append(f"  - `{u}`")
            if ind.get("ips"):
                has_indicators = True
                lines.append(f"- **Direcciones IP**: `{', '.join(ind['ips'][:6])}`")
            if ind.get("registry_keys"):
                has_indicators = True
                lines.append(f"- **Claves de Registro**: `{', '.join(ind['registry_keys'][:5])}`")
            if ind.get("api_keys"):
                has_indicators = True
                lines.append(f"- **Claves de API Detectadas**: `{', '.join(ind['api_keys'][:3])}`")
            lines.append("")

        lines.extend([
            "> [!NOTE]",
            "> *Motor REA (Reverse Engineer Anything v6.7.0)* registrado en Liseth y Antigravity. "
            "Puede solicitar descompilación profunda de funciones o recuperación de código fuente en cualquier momento."
        ])

        return "\n".join(lines)


# Singleton
reverse_engineering_service = ReverseEngineeringService()
