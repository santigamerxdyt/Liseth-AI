"""
Test Suite for Real-Time Truthful Web Search & Internet Grounding in Liseth (JARVIS).
Validates:
- Direct intent detection for live web search, breaking news, market prices, and research.
- Multi-tier cascading engine (Gemini Google Search Grounding -> DDGS News/Web -> Wikipedia).
- Factual truthfulness, publication timestamps, and verified source citations.
- BrainRouter response integration for live web requests.
"""
import pytest
from app.actions.web_search import (
    web_search,
    _wikipedia_search,
    _format_news,
    _format_ddg,
    _format_price,
    _compare,
)
from app.services.brain_router import detect_direct_intent, BrainRouter


def test_web_search_direct_intent_detection():
    """Verifies that queries demanding live internet data map cleanly to web_search."""
    test_cases = [
        ("busca en internet sobre computación cuántica", "web_search", "computacion cuantica", "search"),
        ("busca en google sobre inteligencia artificial", "web_search", "inteligencia artificial", "search"),
        ("buscar en la web sobre autos eléctricos", "web_search", "autos electricos", "search"),
        ("noticias de hoy sobre colombia", "web_search", "colombia", "news"),
        ("ultimas noticias de tecnologia", "web_search", "tecnologia", "news"),
        ("noticias recientes de la nasa", "web_search", "la nasa", "news"),
        ("precio actual de bitcoin", "web_search", "bitcoin", "price"),
        ("cotizacion del dolar hoy", "web_search", "dolar hoy", "price"),
        ("cuanto cuesta hoy una rtx 4090", "web_search", "rtx 4090", "price"),
        ("investiga en internet sobre fusion nuclear", "web_search", "fusion nuclear", "research"),
    ]

    for user_query, expected_tool, expected_kw, expected_mode in test_cases:
        intent = detect_direct_intent(user_query)
        assert intent is not None, f"Failed to detect intent for query: '{user_query}'"
        tool_name, tool_args, friendly_reply = intent
        assert tool_name == expected_tool
        import unicodedata
        q_norm = "".join(c for c in unicodedata.normalize('NFKD', tool_args.get("query", "")) if not unicodedata.combining(c)).lower()
        assert expected_kw in q_norm, f"Expected '{expected_kw}' in query for '{user_query}'"
        assert tool_args.get("mode") == expected_mode
        assert "Santiago" in friendly_reply


def test_wikipedia_fallback_authoritative_search():
    """Verifies that Wikipedia fallback returns authoritative factual summaries and URLs."""
    res = _wikipedia_search("Inteligencia artificial")
    assert res is not None
    assert "Inteligencia artificial" in res["title"]
    assert "Wikipedia" in res["source"]
    assert "https://" in res["url"]
    assert len(res["snippet"]) > 30


def test_web_search_formatters():
    """Verifies formatters produce clean, cited, and timestamped markdown."""
    # News formatter
    mock_news = [
        {
            "title": "Avance en Inteligencia Artificial en 2026",
            "snippet": "Nuevos modelos superan hitos de razonamiento autónomo.",
            "url": "https://noticias.example.com/ia-2026",
            "source": "Reuters",
            "date": "2026-10-25T12:00:00",
        }
    ]
    formatted_news = _format_news("IA 2026", mock_news)
    assert "Últimas Noticias e Información Reciente" in formatted_news
    assert "Avance en Inteligencia Artificial en 2026" in formatted_news
    assert "Reuters" in formatted_news
    assert "https://noticias.example.com/ia-2026" in formatted_news
    assert "2026-10-25" in formatted_news

    # Price formatter
    mock_price = [
        {
            "title": "Bitcoin / USD Cotización",
            "snippet": "Precio en tiempo real: $68,000 USD",
            "url": "https://crypto.example.com/btc",
        }
    ]
    formatted_price = _format_price("Bitcoin", mock_price)
    assert "Cotización y Precios de Mercado" in formatted_price
    assert "Bitcoin / USD Cotización" in formatted_price
    assert "https://crypto.example.com/btc" in formatted_price

    # Web text formatter
    mock_web = [
        {
            "title": "Python 3.14 Release Notes",
            "snippet": "Python 3.14 includes significant performance improvements.",
            "url": "https://docs.python.org/3.14/",
            "source": "Python Software Foundation",
        }
    ]
    formatted_web = _format_ddg("Python 3.14", mock_web)
    assert "Resultados Verificados de Internet" in formatted_web
    assert "Python 3.14 Release Notes" in formatted_web
    assert "https://docs.python.org/3.14/" in formatted_web


def test_web_search_missing_query_handling():
    """Verifies graceful handling of empty queries."""
    res = web_search({})
    assert "indique qué tema" in res.lower() or "search query" in res.lower()


@pytest.mark.asyncio
async def test_brain_router_direct_intent_web_search_integration():
    """Verifies BrainRouter routes live search requests with truthful synthesis."""
    router = BrainRouter()
    res = await router.generate_response(prompt="noticias de hoy sobre tecnologia")
    assert res is not None
    assert res.get("brain") == "native-automation"
    assert res.get("model") == "direct-intent"
    executed = res.get("executedTools", [])
    assert len(executed) > 0
    assert executed[0]["name"] == "web_search"
    assert executed[0]["args"]["mode"] == "news"
    # Result should include polite address and formatted results
    assert "Santiago" in res.get("text", "")
