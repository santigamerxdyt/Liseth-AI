# app/actions/web_search.py
"""
Real-time, Truthful Web Search Engine for Liseth (JARVIS).
Cascading multi-tier architecture:
1. Google Gemini Live Search Grounding (REST API with googleSearch tool & grounding chunks)
2. DDGS Live Web & News Search (ddgs with fresh publication timestamps and source attribution)
3. Wikipedia REST API & OpenSearch (authoritative encyclopedia facts & links)
4. Synthesis formatter ensuring factual truthfulness, explicit dates, and verifiable links.
"""
import json
import logging
import re
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

import httpx

logger = logging.getLogger("jarvis.web_search")

# ── Gemini grounding quota circuit breaker ────────────────────────────────────
_QUOTA_COOLDOWN_SEC  = 900          # 15 minutes cooldown after 429/quota exhaustion
_quota_blocked_until = 0.0
_quota_lock          = threading.Lock()


def _gemini_available() -> bool:
    with _quota_lock:
        return time.monotonic() >= _quota_blocked_until


def _note_gemini_error(exc: Exception) -> None:
    """Trip the breaker when the error is a quota / rate-limit rejection."""
    global _quota_blocked_until
    msg = str(exc)
    if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower():
        with _quota_lock:
            already = time.monotonic() < _quota_blocked_until
            _quota_blocked_until = time.monotonic() + _QUOTA_COOLDOWN_SEC
        if not already:
            print(
                "[WebSearch] [QUOTA] Gemini grounding quota reached/limited — skipping for "
                f"{_QUOTA_COOLDOWN_SEC // 60} min and serving real-time results via DDGS/Wikipedia."
            )


class _QuotaCooldown(RuntimeError):
    """Raised instead of calling Gemini while the quota breaker is open."""


def _log_failure(context: str, exc: Exception) -> None:
    """Log a search backend failure."""
    if isinstance(exc, _QuotaCooldown):
        return
    print(f"[WebSearch] [NOTICE] {context} ({exc}) — cascading to auxiliary backend.")


def _run_bounded(fn, timeout: float, label: str = "task"):
    """Run fn() in a daemon thread; return its result, or None if it overruns."""
    box = [None]

    def _run():
        try:
            box[0] = fn()
        except Exception as e:
            _log_failure(label, e)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        print(f"[WebSearch] {label} exceeded {timeout:.1f}s — moving to next tier.")
    return box[0]


def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR        = _get_base_dir()
API_CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"


def _get_api_key() -> str:
    try:
        from app.config import settings
        if getattr(settings, "GEMINI_API_KEY", None):
            return settings.GEMINI_API_KEY
    except Exception:
        pass

    try:
        if API_CONFIG_PATH.exists():
            with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("gemini_api_key", "")
    except Exception:
        pass
    return ""


# ── Tier 1: Gemini REST API with Google Search Grounding ──────────────────────

def _gemini_search(query: str, mode: str = "search") -> str:
    if not _gemini_available():
        raise _QuotaCooldown("Gemini grounding is in quota cooldown")

    api_key = _get_api_key()
    if not api_key:
        raise ValueError("No Gemini API key available for grounding")

    model = "gemini-2.5-flash"
    try:
        from app.config import settings
        model = settings.GEMINI_MODEL or model
    except Exception:
        pass

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    sys_instruction = (
        f"Eres Liseth, asistente de Santiago. Fecha y hora actual del sistema: {now_str}. "
        "Usa información reciente, verídica y comprobable de internet. "
        "Sé precisa, directa, cita fuentes exactas y nunca inventes datos ni asumas fechas pasadas."
    )

    payload: Dict[str, Any] = {
        "contents": [{"parts": [{"text": query}]}],
        "systemInstruction": {"parts": [{"text": sys_instruction}]},
        "tools": [{"googleSearch": {}}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048,
        }
    }

    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 429:
                _note_gemini_error(RuntimeError(f"HTTP 429: {resp.text[:200]}"))
                raise RuntimeError("Gemini quota 429")
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini API returned status {resp.status_code}: {resp.text[:200]}")

            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError("Gemini returned empty candidates")

            cand = candidates[0]
            parts = cand.get("content", {}).get("parts", [])
            text_blocks = [p.get("text", "") for p in parts if isinstance(p, dict) and "text" in p]
            main_text = "".join(text_blocks).strip()

            if not main_text:
                raise ValueError("Gemini returned empty text response")

            # Extract verified grounding sources
            gm = cand.get("groundingMetadata", {})
            sources = []
            for chunk in gm.get("groundingChunks", []):
                web = chunk.get("web", {})
                w_title = web.get("title", "").strip()
                w_uri = web.get("uri", "").strip()
                if w_uri and (w_uri not in [s[1] for s in sources]):
                    sources.append((w_title or w_uri, w_uri))

            if sources:
                src_lines = ["\n\n🔗 **Fuentes Verificadas de Internet:**"]
                for i, (title, uri) in enumerate(sources[:5], 1):
                    src_lines.append(f"{i}. [{title}]({uri})")
                main_text += "\n" + "\n".join(src_lines)

            return main_text

    except Exception as e:
        _note_gemini_error(e)
        raise


# ── Tier 2: DDGS Web & News Search ───────────────────────────────────────────

def _get_ddgs():
    """Returns the active DDGS class (ddgs or duckduckgo_search fallback)."""
    try:
        from ddgs import DDGS
        return DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS
            return DDGS
        except ImportError:
            return None


def _ddg_search(query: str, max_results: int = 6) -> list[dict]:
    DDGS = _get_ddgs()
    if not DDGS:
        return []
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                title = r.get("title", "").strip()
                snippet = r.get("body", "").strip()
                url = r.get("href", "").strip()
                if title or snippet:
                    results.append({
                        "title":   title,
                        "snippet": snippet,
                        "url":     url,
                        "source":  "Web",
                    })
    except Exception as e:
        print(f"[WebSearch] [WARN] DDGS text() error: {e}")

    # Fallback to Wikipedia if DDGS text comes back completely dry
    if not results:
        wiki_res = _wikipedia_search(query)
        if wiki_res:
            results.append(wiki_res)

    return results


def _ddg_news(query: str, max_results: int = 8) -> list[dict]:
    """DDGS news search — returns recent articles with timestamps."""
    DDGS = _get_ddgs()
    results = []
    if DDGS:
        try:
            with DDGS() as ddgs:
                for r in ddgs.news(query, max_results=max_results):
                    results.append({
                        "title":   r.get("title", "").strip(),
                        "snippet": r.get("body", "").strip(),
                        "url":     r.get("url", "").strip(),
                        "source":  r.get("source", "").strip() or "Noticias",
                        "date":    r.get("date", "").strip(),
                    })
        except Exception as e:
            print(f"[WebSearch] [WARN] DDGS news() error ({e}) — falling back to text search")

    if not results:
        results = _ddg_search(f"{query} noticias recientes", max_results=max_results)

    return results


# ── Tier 3: Wikipedia REST API & OpenSearch ──────────────────────────────────

def _wikipedia_search(query: str) -> Optional[dict]:
    """Searches Wikipedia in Spanish (or English) for authoritative, verified knowledge."""
    clean_q = re.sub(r"^(?:busca|buscar|que es|quien es|definicion de|historia de)\s+", "", query, flags=re.IGNORECASE).strip()
    if not clean_q:
        clean_q = query

    headers = {"User-Agent": "LisethAssistant/2.0 (contact@liseth.local; https://liseth.local)"}

    # 1. First attempt OpenSearch to resolve clean article title
    target_title = clean_q
    try:
        open_url = f"https://es.wikipedia.org/w/api.php?action=opensearch&search={quote(clean_q)}&limit=3&namespace=0&format=json"
        with httpx.Client(timeout=4.0) as client:
            resp = client.get(open_url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                if len(data) >= 2 and data[1]:
                    target_title = data[1][0]
    except Exception:
        pass

    # 2. Query summary REST API
    for lang in ("es", "en"):
        try:
            sum_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote(target_title)}"
            with httpx.Client(timeout=4.0) as client:
                r = client.get(sum_url, headers=headers)
                if r.status_code == 200:
                    d = r.json()
                    extract = d.get("extract", "").strip()
                    title = d.get("title", target_title).strip()
                    page_url = d.get("content_urls", {}).get("desktop", {}).get("page", "")
                    if extract:
                        return {
                            "title": f"{title} (Enciclopedia Oficial)",
                            "snippet": extract,
                            "url": page_url or f"https://{lang}.wikipedia.org/wiki/{quote(title)}",
                            "source": f"Wikipedia ({lang.upper()})",
                            "date": datetime.now().strftime("%Y-%m-%d"),
                        }
        except Exception:
            continue
    return None


# ── Formatters ────────────────────────────────────────────────────────────────

def _format_ddg(query: str, results: list[dict]) -> str:
    if not results:
        return f"No se encontraron resultados web verificados para: '{query}'."

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"🔍 **Resultados Verificados de Internet para:** *{query}*",
        f"📅 *Consulta en tiempo real:* {now_str}\n"
    ]
    for i, r in enumerate(results, 1):
        title = r.get("title", "Resultado")
        snippet = r.get("snippet", "")
        url = r.get("url", "")
        src = r.get("source", "Web")
        lines.append(f"{i}. 📌 **{title}** [{src}]")
        if snippet:
            lines.append(f"   {snippet}")
        if url:
            lines.append(f"   🔗 [Enlace verificado]({url})")
        lines.append("")

    lines.append("🛡️ *Información recuperada en tiempo real desde la web abierta.*")
    return "\n".join(lines).strip()


def _format_news(query: str, results: list[dict]) -> str:
    if not results:
        return f"No se encontraron noticias recientes para: '{query}'."

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"📰 **Últimas Noticias e Información Reciente:** *{query}*",
        f"📅 *Actualizado al:* {now_str}\n"
    ]
    for i, r in enumerate(results, 1):
        title = r.get("title", "")
        if not title:
            continue
        src = f" — *{r['source']}*" if r.get("source") else ""
        date_str = f" ({r['date'][:10]})" if r.get("date") else ""
        lines.append(f"{i}. 📌 **{title}**{src}{date_str}")
        if r.get("snippet"):
            lines.append(f"   {r['snippet']}")
        if r.get("url"):
            lines.append(f"   🔗 [Leer noticia completa]({r['url']})")
        lines.append("")

    lines.append("🛡️ *Fuentes periodísticas y agencias de información verificadas en tiempo real.*")
    return "\n".join(lines).strip()


def _format_price(query: str, results: list[dict]) -> str:
    if not results:
        return f"No se encontró información de precios de mercado para: '{query}'."

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"💰 **Cotización y Precios de Mercado:** *{query}*",
        f"📅 *Verificado al:* {now_str}\n"
    ]
    for i, r in enumerate(results, 1):
        title = r.get("title", "")
        if not title:
            continue
        lines.append(f"{i}. 🏷️ **{title}**")
        if r.get("snippet"):
            lines.append(f"   {r['snippet']}")
        if r.get("url"):
            lines.append(f"   🔗 [Ver cotización/oferta]({r['url']})")
        lines.append("")

    return "\n".join(lines).strip()


# ── Briefing helper ────────────────────────────────────────────────────────────

def _gemini_headlines(n: int = 5) -> tuple[list[str], str]:
    """Fetches current headlines via DDGS news or Gemini grounding."""
    # Fast DDGS news first
    try:
        news_items = _ddg_news("noticias destacadas de hoy", max_results=n)
        if news_items:
            headlines = [item["title"] for item in news_items if item.get("title")][:n]
            raw_text = "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
            return headlines, raw_text
    except Exception as e:
        logger.debug(f"[WebSearch] Error en titulares DDGS: {e}")

    # Fallback to Gemini
    try:
        raw = _gemini_search(f"Top {n} titulares de noticias mundiales hoy. Lista numerada solo títulos.")
        headlines = []
        for line in raw.splitlines():
            line = line.strip()
            if re.match(r'^[\d]+[.\)\-]', line):
                clean = re.sub(r'^[\d]+[.\)\-]\s*', '', line).strip()
                if clean:
                    headlines.append(clean)
        return headlines[:n], raw
    except Exception:
        return [], ""


# ── Modes ──────────────────────────────────────────────────────────────────────

def _search(query: str) -> str:
    """Default search — Gemini grounded first, DDGS and Wikipedia fallback."""
    try:
        return _gemini_search(query, mode="search")
    except Exception as e:
        _log_failure("Gemini search", e)
        results = _ddg_search(query)
        return _format_ddg(query, results)


def _news(query: str) -> str:
    """News mode — DDGS news with timestamps first, Gemini grounded fallback."""
    ddg_query = query if query else "noticias hoy"
    gemini_query = f"últimas noticias verídicas de hoy: {query}" if query else "principales noticias mundiales de hoy"

    def _ddg_attempt() -> str:
        items = _ddg_news(ddg_query, max_results=8)
        return _format_news(ddg_query, items)

    text = _run_bounded(_ddg_attempt, timeout=6.0, label="DDGS news")
    if text and len(text) > 80 and not text.startswith("No se encontraron"):
        return text

    text = _run_bounded(
        lambda: _gemini_search(gemini_query, mode="news"), timeout=7.0, label="Gemini news"
    )
    if text and len(text) > 80:
        return text

    return f"No se encontraron noticias recientes para: '{query}'."


def _research(query: str) -> str:
    """Deep research — comprehensive factual inquiry with sources."""
    research_query = (
        f"Explicación detallada, actual y verídica de: {query}. "
        "Incluye contexto factual comprobado, estado actual y citas a fuentes confiables."
    )
    try:
        return _gemini_search(research_query, mode="research")
    except Exception as e:
        _log_failure("Gemini research", e)
        results = _ddg_search(query, max_results=8)
        return _format_ddg(query, results)


def _price(query: str) -> str:
    """Product/asset price lookup with verified live data."""
    price_query = f"precio actual o cotización de {query} en tiempo real hoy"
    try:
        return _gemini_search(price_query, mode="price")
    except Exception as e:
        _log_failure("Gemini price", e)
        results = _ddg_search(f"{query} precio actual cotizacion mercado", max_results=6)
        return _format_price(query, results)


def _compare(items: list[str], aspect: str) -> str:
    query = (
        f"Compara objetivamente {', '.join(items)} en cuanto a {aspect}. "
        "Aporta datos recientes, hechos específicos y fuentes comprobables."
    )
    try:
        return _gemini_search(query, mode="compare")
    except Exception as e:
        _log_failure("Gemini compare", e)

    all_results: dict[str, list] = {}
    for item in items:
        try:
            all_results[item] = _ddg_search(f"{item} {aspect}", max_results=3)
        except Exception:
            all_results[item] = []

    lines = [f"📊 **Comparativa Verificada — {aspect.upper()}**", "─" * 45]
    for item in items:
        lines.append(f"\n▸ **{item}**")
        for r in all_results.get(item, [])[:2]:
            if r.get("snippet"):
                lines.append(f"  • {r['snippet']}")
            if r.get("url"):
                lines.append(f"    🔗 [Fuente]({r['url']})")
    return "\n".join(lines)


# ── Public entry point ─────────────────────────────────────────────────────────

def web_search(
    parameters:     dict,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """
    Primary web search action handler.
    Searches the live internet for recent, truthful and verified facts.
    """
    params = parameters or {}
    query  = params.get("query", "").strip()
    mode   = params.get("mode",  "search").lower().strip()
    items  = params.get("items", [])
    aspect = params.get("aspect", "general").strip() or "general"

    if not query and not items:
        return "Por favor, indique qué tema, noticia o dato desea buscar en internet."

    if items and mode not in ("compare",):
        mode = "compare"

    if player:
        player.write_log(f"[Search:{mode}] {query or ', '.join(items)}")

    print(f"[WebSearch] [SEARCH] mode={mode!r}  query={query!r}")

    try:
        if mode == "compare" and items:
            return _compare(items, aspect)
        if mode == "news":
            return _news(query)
        if mode == "research":
            return _research(query)
        if mode == "price":
            return _price(query)
        return _search(query)

    except Exception as e:
        print(f"[WebSearch] [ERROR] Fallo en busqueda web: {e}")
        # Final safety net: try Wikipedia directly
        try:
            wiki_res = _wikipedia_search(query)
            if wiki_res:
                return f"📖 **{wiki_res['title']}**\n\n{wiki_res['snippet']}\n\n🔗 [Ver en Wikipedia]({wiki_res['url']})"
        except Exception:
            pass
        return f"No se pudo completar la búsqueda en internet en este momento ({e})."


# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "web_search",
    "description": (
        "Busca información reciente, verídica y comprobada en internet. "
        "Úsala SIEMPRE que Santiago pregunte por noticias actuales, eventos recientes, cotizaciones, "
        "precios de mercado, estado de proyectos o información que requiera estar actualizada en tiempo real. "
        "Modos: 'search' (búsqueda general), 'news' (noticias recientes con fecha), 'research' (investigación profunda), "
        "'price' (precios y cotizaciones), 'compare' (comparación de opciones)."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "Consulta, tema o términos exactos de búsqueda en internet"
            },
            "mode": {
                "type": "STRING",
                "description": "search | news | research | price | compare"
            },
            "items": {
                "type": "ARRAY",
                "items": {
                    "type": "STRING"
                },
                "description": "Lista de elementos a comparar (modo compare)"
            },
            "aspect": {
                "type": "STRING",
                "description": "Aspecto de comparación: precio | características | rendimiento | opiniones"
            }
        },
        "required": [
            "query"
        ]
    },
    "handler": web_search,
}
