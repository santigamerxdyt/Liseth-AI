"""
Diffin Binary Analysis Service for Liseth // JARVIS.
Experimental integration inspired by diffin/diffin.
Provides:
- Binary artifact inspection and byte-level diff analysis.
- Cryptographic hash verification (SHA-256 / SHA-1 / MD5).
- Audio and binary file header structural validation.
"""
import hashlib
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvis.diffin")


class DiffinService:
    """
    Experimental binary and artifact inspection utility.
    Used for build verification, release integrity checks, and audio artifact validation.
    """

    def compute_hashes(self, file_path_or_bytes: Any) -> Dict[str, str]:
        """Calculates cryptographic digests for an artifact."""
        if isinstance(file_path_or_bytes, str) and os.path.isfile(file_path_or_bytes):
            with open(file_path_or_bytes, "rb") as f:
                data = f.read()
        elif isinstance(file_path_or_bytes, (bytes, bytearray)):
            data = file_path_or_bytes
        else:
            return {"error": "Invalid input for binary hash computation"}

        return {
            "size_bytes": str(len(data)),
            "sha256": hashlib.sha256(data).hexdigest(),
            "sha1": hashlib.sha1(data).hexdigest(),
            "md5": hashlib.md5(data).hexdigest(),
        }

    def compare_binary_artifacts(self, artifact_a: bytes, artifact_b: bytes) -> Dict[str, Any]:
        """
        Compares two binary artifacts at the byte level,
        detecting identical match, byte differences, and offset changes.
        """
        len_a = len(artifact_a)
        len_b = len(artifact_b)
        hash_a = hashlib.sha256(artifact_a).hexdigest()
        hash_b = hashlib.sha256(artifact_b).hexdigest()

        if hash_a == hash_b:
            return {
                "identical": True,
                "size_match": True,
                "differing_bytes": 0,
                "similarity_ratio": 1.0,
                "sha256": hash_a
            }

        diff_count = 0
        min_len = min(len_a, len_b)
        for i in range(min_len):
            if artifact_a[i] != artifact_b[i]:
                diff_count += 1
        diff_count += abs(len_a - len_b)

        max_len = max(len_a, len_b)
        similarity = 1.0 - (diff_count / max_len) if max_len > 0 else 1.0

        return {
            "identical": False,
            "size_match": len_a == len_b,
            "size_a": len_a,
            "size_b": len_b,
            "differing_bytes": diff_count,
            "similarity_ratio": round(similarity, 4),
            "sha256_a": hash_a,
            "sha256_b": hash_b,
        }

    def inspect_audio_header(self, audio_bytes: bytes) -> Dict[str, Any]:
        """Inspects headers of audio artifacts (WAV/RIFF, MP3, OGG)."""
        if len(audio_bytes) < 12:
            return {"valid": False, "error": "Buffer too short"}

        header = audio_bytes[:12]
        format_detected = "unknown"

        if header[:4] == b"RIFF" and header[8:12] == b"WAVE":
            format_detected = "WAV/RIFF"
        elif header[:3] == b"ID3" or header[:2] in (b"\xff\xfb", b"\xff\xf3"):
            format_detected = "MP3"
        elif header[:4] == b"OggS":
            format_detected = "OGG/Opus"

        return {
            "valid": format_detected != "unknown",
            "format": format_detected,
            "header_bytes_hex": header.hex(),
            "total_bytes": len(audio_bytes)
        }


diffin_service = DiffinService()
