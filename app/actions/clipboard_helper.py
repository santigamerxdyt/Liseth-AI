"""
Smart Clipboard Assistant for Liseth.
Safely inspects the Windows clipboard, detects errors/tracebacks, code snippets,
URLs or JSON, and provides automated analysis or bug fixing.
"""
from __future__ import annotations
import json
import logging
import re
from typing import Tuple, Dict, Any

logger = logging.getLogger("Liseth.Clipboard")

_RE_TRACEBACK = re.compile(
    r"(?:Traceback \(most recent call last\)|Error:|Exception:|NullPointerException|SyntaxError:|TypeError:|ValueError:|KeyError:|IndexError:|AttributeError:|RuntimeError:|OperationalError:|AssertionError:)",
    re.IGNORECASE
)
_RE_URL = re.compile(r"^https?://[^\s]+$")
_RE_CODE_KEYWORDS = re.compile(
    r"\b(?:def |class |import |from |function |const |let |var |async |await |return |public |private |struct |impl |fn |select\s+.*\s+from)\b"
)


def get_clipboard_text() -> str:
    """
    Safely retrieves text from the Windows OS clipboard without external dependencies.
    Uses Win32 user32/kernel32 APIs, with pyperclip/tkinter fallbacks.
    """
    # 1. Native Windows Win32 API via ctypes
    try:
        import ctypes
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        CF_UNICODETEXT = 13

        if user32.OpenClipboard(None):
            try:
                h_data = user32.GetClipboardData(CF_UNICODETEXT)
                if h_data:
                    p_data = kernel32.GlobalLock(h_data)
                    if p_data:
                        try:
                            text = ctypes.c_wchar_p(p_data).value
                            if text is not None:
                                return str(text)
                        finally:
                            kernel32.GlobalUnlock(h_data)
            finally:
                user32.CloseClipboard()
    except Exception as e:
        logger.debug(f"[Clipboard] ctypes Win32 read failed: {e}")

    # 2. Pyperclip fallback if installed
    try:
        import pyperclip
        return pyperclip.paste() or ""
    except Exception:
        pass

    # 3. Tkinter fallback
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        text = root.clipboard_get()
        root.destroy()
        return text or ""
    except Exception:
        pass

    return ""


def detect_clipboard_kind(text: str) -> str:
    """Categorizes clipboard contents into error, json, code, url, or general text."""
    if not text or not text.strip():
        return "empty"

    stripped = text.strip()

    # URL check
    if _RE_URL.match(stripped):
        return "url"

    # Error / Traceback check
    if _RE_TRACEBACK.search(text):
        return "error"

    # JSON check
    if (stripped.startswith("{") and stripped.endswith("}")) or (stripped.startswith("[") and stripped.endswith("]")):
        try:
            json.loads(stripped)
            return "json"
        except Exception:
            pass

    # Code check
    if _RE_CODE_KEYWORDS.search(text) or "\n    " in text or "\n\t" in text:
        return "code"

    return "text"


async def smart_clipboard_action(parameters: dict = None) -> str:
    """
    Analyzes, summarizes, or suggests fixes for the content currently in the clipboard.
    """
    params = parameters or {}
    action = params.get("action", "analyze").lower()
    custom_query = params.get("query", "").strip()

    raw_text = get_clipboard_text()
    if not raw_text or not raw_text.strip():
        return "Su portapapeles está vacío en este momento, señor Santiago. Copie algún texto, código o error primero."

    kind = detect_clipboard_kind(raw_text)
    preview = raw_text[:500] + ("..." if len(raw_text) > 500 else "")

    if action in ["read", "leer", "mostrar", "contenido"]:
        return f"En su portapapeles ({kind}) tiene copiado lo siguiente:\n\n{preview}"

    # Analysis or Fix requested
    prompt_intent = custom_query or "Analiza y explica lo que tengo copiado en el portapapeles"

    # Specialized prompt depending on type
    if kind == "error":
        instruction = (
            f"El usuario Santiago copió un mensaje de error o traceback en su portapapeles:\n```\n{raw_text}\n```\n"
            f"Pregunta/Petición: '{prompt_intent}'.\n"
            "Identifica la causa raíz del error, explica qué significa con precisión y proporciona la solución paso a paso de forma dulce y profesional."
        )
    elif kind == "json":
        instruction = (
            f"El usuario Santiago copió una estructura JSON en su portapapeles:\n```json\n{raw_text}\n```\n"
            f"Pregunta/Petición: '{prompt_intent}'.\n"
            "Valida si es un JSON correcto, resume su estructura o campos principales y explica su utilidad."
        )
    elif kind == "code":
        instruction = (
            f"El usuario Santiago copió este fragmento de código en su portapapeles:\n```\n{raw_text}\n```\n"
            f"Pregunta/Petición: '{prompt_intent}'.\n"
            "Explica qué hace este código, si tiene alguna vulnerabilidad o bug potencial, y cómo mejorarlo."
        )
    else:
        instruction = (
            f"El usuario Santiago copió el siguiente texto en su portapapeles:\n\"\"\"{raw_text}\"\"\"\n"
            f"Petición: '{prompt_intent}'. Proporciona un análisis conciso, claro y profesional."
        )

    try:
        from app.services.brain_router import brain_router
        res = await brain_router.call_gemini(
            contents=[{"role": "user", "parts": [{"text": instruction}]}],
            tools=[]
        )
        return res.get("text", f"He analizado el contenido de su portapapeles ({kind}), señor Santiago:\n{preview}")
    except Exception as e:
        logger.debug(f"[Clipboard] LLM call fallback: {e}")
        # Deterministic offline fallback
        if kind == "error":
            return f"He detectado un error en su portapapeles:\n{preview}\n\nLe sugiero revisar la línea indicada y verificar las variables o sintaxis relacionadas."
        elif kind == "json":
            return f"Su portapapeles contiene datos estructurados JSON:\n{preview}"
        elif kind == "code":
            return f"Su portapapeles contiene código fuente ({len(raw_text.splitlines())} líneas):\n{preview}"
        else:
            return f"Contenido actual de su portapapeles:\n{preview}"
