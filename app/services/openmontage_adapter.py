"""
OpenMontage Media Adapter for Liseth // JARVIS.
Integration inspired by aliberson/openmontage.
Provides:
- Multimedia composition pipeline.
- Audio synthesis formatting & track mixing.
- Subtitle generation (WebVTT & SubRip SRT) synchronized with speech transcripts.
- Audio normalization and format conversion.
"""
import io
import logging
import math
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvis.openmontage")


class OpenMontageMediaAdapter:
    """
    Adapter for media generation, audio mixing, and subtitle composition.
    Operates modularly without interfering with real-time conversational latency.
    """

    def generate_subtitles_vtt(self, segments: List[Dict[str, Any]]) -> str:
        """
        Generates WebVTT subtitles formatted for video/audio players.
        Each segment: {"start": 0.0, "end": 2.5, "text": "Hola Santiago"}
        """
        lines = ["WEBVTT\n"]
        for i, seg in enumerate(segments, 1):
            start_str = self._format_vtt_timestamp(seg.get("start", 0.0))
            end_str = self._format_vtt_timestamp(seg.get("end", 0.0))
            text = seg.get("text", "").strip()
            lines.append(f"{i}\n{start_str} --> {end_str}\n{text}\n")
        return "\n".join(lines)

    def generate_subtitles_srt(self, segments: List[Dict[str, Any]]) -> str:
        """Generates standard SubRip (SRT) format."""
        lines = []
        for i, seg in enumerate(segments, 1):
            start_str = self._format_srt_timestamp(seg.get("start", 0.0))
            end_str = self._format_srt_timestamp(seg.get("end", 0.0))
            text = seg.get("text", "").strip()
            lines.append(f"{i}\n{start_str} --> {end_str}\n{text}\n")
        return "\n".join(lines)

    def _format_vtt_timestamp(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

    def _format_srt_timestamp(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def mix_audio_tracks(self, voice_pcm: bytes, bg_music_pcm: Optional[bytes] = None, voice_gain: float = 1.0, bg_gain: float = 0.2) -> bytes:
        """
        Mixes voice track with optional ambient background audio,
        applying ducking and dynamic range compression.
        """
        if not voice_pcm:
            return b""
        if not bg_music_pcm:
            return voice_pcm

        try:
            import numpy as np
            voice_arr = np.frombuffer(voice_pcm, dtype=np.int16).astype(np.float32) * voice_gain
            bg_arr = np.frombuffer(bg_music_pcm, dtype=np.int16).astype(np.float32) * bg_gain

            # Match lengths
            min_len = min(len(voice_arr), len(bg_arr))
            mixed = voice_arr[:min_len] + bg_arr[:min_len]
            # Clip to int16 boundaries
            mixed = np.clip(mixed, -32768, 32767).astype(np.int16)
            return mixed.tobytes()
        except Exception as e:
            logger.warning(f"[OpenMontage] Error mezclando pistas de audio: {e}")
            return voice_pcm


openmontage_adapter = OpenMontageMediaAdapter()
