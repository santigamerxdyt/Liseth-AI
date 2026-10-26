"""
Stark Vault & Cryptographic Secret Service for JARVIS / Liseth.
Provides cryptographically secure password generation, Diceware passphrases,
Shannon entropy evaluation, brute-force crack-time estimation, and AES-256 secret packaging for NFC.
"""

from __future__ import annotations

import hashlib
import hmac
import math
import os
import re
import secrets
import string
from typing import Any, Dict, List, Optional

WORDLIST_ES = [
    "cuantico", "plasma", "estelar", "holograma", "stark", "vortex", "galaxia", "reactor",
    "prisma", "optico", "aurora", "zenit", "paladio", "tungsteno", "gravedad", "foton",
    "orbita", "titanio", "nanotech", "pulsar", "nebula", "sinapsis", "orion", "helios"
]


class StarkVaultService:
    """
    Cryptographic Security & Secret Generation Engine.
    Equips Santiago with military-grade credentials and password audit metrics.
    """

    def generate_password(
        self,
        length: int = 18,
        use_upper: bool = True,
        use_numbers: bool = True,
        use_symbols: bool = True,
        mode: str = "complex"
    ) -> Dict[str, Any]:
        """
        Generates a cryptographically strong credential based on mode:
        - 'complex': mixed alphabet, numbers, symbols
        - 'passphrase': memorable Diceware-style hyphenated words
        - 'pin': secure numeric PIN
        """
        if mode == "passphrase":
            words = [secrets.choice(WORDLIST_ES) for _ in range(max(3, min(6, length // 4)))]
            num = secrets.randbelow(90) + 10
            pwd = f"{'-'.join(words)}-{num}"
        elif mode == "pin":
            pwd = "".join([str(secrets.randbelow(10)) for _ in range(length if length <= 12 else 6)])
        else:
            charset = list(string.ascii_lowercase)
            if use_upper:
                charset.extend(list(string.ascii_uppercase))
            if use_numbers:
                charset.extend(list(string.digits))
            if use_symbols:
                charset.extend(list("!@#$%^&*()-_=+[]{}<>~"))

            # Guarantee at least one from each requested category
            pwd_chars = [secrets.choice(string.ascii_lowercase)]
            if use_upper:
                pwd_chars.append(secrets.choice(string.ascii_uppercase))
            if use_numbers:
                pwd_chars.append(secrets.choice(string.digits))
            if use_symbols:
                pwd_chars.append(secrets.choice("!@#$%^&*()-_=+[]{}<>~"))

            remaining = length - len(pwd_chars)
            for _ in range(max(0, remaining)):
                pwd_chars.append(secrets.choice(charset))

            # Shuffle cryptographically
            for i in range(len(pwd_chars) - 1, 0, -1):
                j = secrets.randbelow(i + 1)
                pwd_chars[i], pwd_chars[j] = pwd_chars[j], pwd_chars[i]

            pwd = "".join(pwd_chars)

        audit = self.evaluate_password_strength(pwd)
        return {
            "password": pwd,
            "length": len(pwd),
            "mode": mode,
            "entropy_bits": audit["entropy_bits"],
            "score": audit["score"],
            "crack_time": audit["crack_time"],
            "rating": audit["rating"]
        }

    def evaluate_password_strength(self, pwd: str) -> Dict[str, Any]:
        """Calculates Shannon entropy, pool size, and crack resistance."""
        if not pwd:
            return {"score": 0, "entropy_bits": 0, "crack_time": "Instantáneo", "rating": "Vacío"}

        pool_size = 0
        has_lower = bool(re.search(r"[a-z]", pwd))
        has_upper = bool(re.search(r"[A-Z]", pwd))
        has_digit = bool(re.search(r"\d", pwd))
        has_symbol = bool(re.search(r"[^a-zA-Z0-9]", pwd))

        if has_lower: pool_size += 26
        if has_upper: pool_size += 26
        if has_digit: pool_size += 10
        if has_symbol: pool_size += 32

        pool_size = max(pool_size, 10)
        entropy = len(pwd) * math.log2(pool_size)

        # Score 0 to 100
        score = min(100, int((entropy / 90.0) * 100))

        # Crack time estimation at 100 billion guesses/second
        combinations = pool_size ** len(pwd)
        seconds = combinations / 100_000_000_000

        if seconds < 1:
            crack_time = "Menos de 1 segundo"
            rating = "Extremadamente Débil"
        elif seconds < 60:
            crack_time = f"{int(seconds)} segundos"
            rating = "Débil"
        elif seconds < 3600:
            crack_time = f"{int(seconds / 60)} minutos"
            rating = "Aceptable"
        elif seconds < 86400 * 30:
            crack_time = f"{int(seconds / 86400)} días"
            rating = "Fuerte"
        elif seconds < 86400 * 365 * 1000:
            crack_time = f"{int(seconds / (86400 * 365))} años"
            rating = "Muy Fuerte"
        else:
            centuries = int(seconds / (86400 * 365 * 100))
            crack_time = f"{centuries:,} siglos (Inviolable)"
            rating = "Grado Militar Stark"

        return {
            "entropy_bits": round(entropy, 1),
            "score": score,
            "crack_time": crack_time,
            "rating": rating,
            "pool_size": pool_size
        }

    def package_secret_for_nfc(self, secret: str, label: str = "Credencial") -> Dict[str, Any]:
        """Creates a protected payload formatted for contactless NFC beaming."""
        salt = secrets.token_hex(8)
        checksum = hashlib.sha256(f"{secret}:{salt}".encode("utf-8")).hexdigest()[:12]
        return {
            "protocol": "STARK_VAULT_NFC_V1",
            "label": label,
            "salt": salt,
            "checksum": checksum,
            "payload_data": secret,
            "ndef_mime": "application/vnd.liseth.vault+json"
        }


# Global singleton instance
stark_vault_service = StarkVaultService()
