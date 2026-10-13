"""
Unit tests for app.core.crypto module.
"""
import pytest
from app.core.crypto import (
    encrypt,
    decrypt,
    hash_pin,
    verify_pin,
    generate_secure_key,
    get_master_key,
)


def test_encrypt_and_decrypt():
    secret = "test-encryption-key-for-unit-test-32b"
    sample_texts = [
        "Hola Santiago, soy Liseth.",
        "Token: ya29.a0AfH6SMD...12345",
        "Caracteres especiales: áéíóú ñ ¿?! 🚀🤖",
        "JSON data: {\"oauth\": \"valid\", \"refresh\": \"xyz\"}",
    ]

    for text in sample_texts:
        encrypted = encrypt(text, secret)
        assert encrypted != text
        assert ":" in encrypted
        parts = encrypted.split(":")
        assert len(parts) == 3
        # Ensure parts are valid hex
        assert bytes.fromhex(parts[0])
        assert bytes.fromhex(parts[1])
        assert bytes.fromhex(parts[2])

        decrypted = decrypt(encrypted, secret)
        assert decrypted == text


def test_tamper_detection():
    secret = "test-encryption-key-for-unit-test-32b"
    original = "Confidential Token"
    encrypted = encrypt(original, secret)
    parts = encrypted.split(":")

    # Alter ciphertext by 1 bit
    corrupted_ct = bytearray.fromhex(parts[2])
    corrupted_ct[0] ^= 0x01
    tampered = f"{parts[0]}:{parts[1]}:{corrupted_ct.hex()}"

    # Decrypting tampered text must return None (fail closed)
    assert decrypt(tampered, secret) is None


def test_tampered_tag():
    secret = "test-encryption-key-for-unit-test-32b"
    original = "Confidential Token"
    encrypted = encrypt(original, secret)
    parts = encrypted.split(":")

    corrupted_tag = bytearray.fromhex(parts[1])
    corrupted_tag[0] ^= 0x01
    tampered = f"{parts[0]}:{corrupted_tag.hex()}:{parts[2]}"

    assert decrypt(tampered, secret) is None


def test_scrypt_pin_hashing():
    pin = "8520"
    salt_hex, hash_hex = hash_pin(pin)

    assert len(salt_hex) == 32  # 16 bytes hex
    assert len(hash_hex) == 64  # 32 bytes hex

    # Verify correct PIN
    assert verify_pin(pin, salt_hex, hash_hex) is True

    # Verify incorrect PIN
    assert verify_pin("1234", salt_hex, hash_hex) is False
    assert verify_pin("8521", salt_hex, hash_hex) is False
    assert verify_pin("", salt_hex, hash_hex) is False


def test_node_cross_platform_ciphertext():
    """
    Verifies that a known ciphertext generated with Node.js crypto.js
    decrypts perfectly in Python.
    Node key secret: 'test-secret-key-1234567890123456'
    Node text: 'Hola desde Node!'
    """
    secret = "test-secret-key-1234567890123456"
    node_ciphertext = "bde273fa79438d489a53d7e22a13f811:8423b1ab211882e18bbe13df294f156b:3e2185927d15d48b83cdcc458843efd0"

    decrypted = decrypt(node_ciphertext, secret)
    assert decrypted == "Hola desde Node!"
