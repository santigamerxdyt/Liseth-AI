"""
TTS API Router for JARVIS / Liseth.
Streams MP3 audio for requested text and voice configurations.
"""
import logging
from fastapi import APIRouter, HTTPException, Query, Response
from app.services.tts_service import synthesize_speech

logger = logging.getLogger("jarvis.tts_router")

router = APIRouter(prefix="/api", tags=["tts"])


@router.get("/tts")
async def tts_endpoint(
    text: str = Query(..., min_length=1, max_length=2000, description="Texto a sintetizar"),
    voice: str = Query("es-CO-SalomeNeural", description="Identificador de voz Edge/Neuronal"),
    rate: str = Query("+0%", description="Velocidad de locución"),
    pitch: str = Query("+10Hz", description="Tono / afinación"),
    provider: str = Query("edge", description="Proveedor TTS"),
):
    """
    Synthesizes and returns MP3 audio for speech output.
    """
    try:
        audio_bytes = await synthesize_speech(
            text=text,
            voice=voice,
            rate=rate,
            pitch=pitch,
        )
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="No se generó audio para el texto proporcionado.")

        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Type": "audio/mpeg",
                "Cache-Control": "public, max-age=86400",
                "Accept-Ranges": "bytes",
            },
        )
    except Exception as e:
        logger.warning(f"Fallo en endpoint /api/tts: {e}")
        raise HTTPException(status_code=500, detail=f"Error sintetizando voz: {str(e)}")
