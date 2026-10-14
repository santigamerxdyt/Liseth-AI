"""
TTS Service for JARVIS / Liseth.
Synthesizes speech using edge-tts with in-memory caching for low latency.
"""
import io
import logging
from typing import Dict, Optional

logger = logging.getLogger("jarvis.tts")

# In-memory audio cache for frequent phrases
_audio_cache: Dict[str, bytes] = {}
MAX_CACHE_ITEMS = 60


async def synthesize_speech(
    text: str,
    voice: str = "es-MX-DaliaNeural",
    rate: str = "+5%",
    pitch: str = "+15Hz",
) -> bytes:
    """
    Synthesizes speech to MP3 audio bytes using edge-tts.
    Checks memory cache first.
    """
    clean_text = text.strip()
    if not clean_text:
        return b""

    # Cache key
    cache_key = f"{voice}|{rate}|{pitch}|{clean_text}"
    if cache_key in _audio_cache:
        return _audio_cache[cache_key]

    try:
        import edge_tts

        communicate = edge_tts.Communicate(
            text=clean_text,
            voice=voice,
            rate=rate,
            pitch=pitch,
        )

        audio_chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])

        audio_bytes = b"".join(audio_chunks)

        if audio_bytes and len(_audio_cache) < MAX_CACHE_ITEMS:
            _audio_cache[cache_key] = audio_bytes

        return audio_bytes
    except Exception as e:
        logger.warning(f"Error sintetizando voz neuronal con edge-tts: {e}")
        raise e
