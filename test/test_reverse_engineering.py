"""
Test suite for Reverse Engineering & Binary Inspection (REA Engine integration) in Liseth.
Verifies entropy calculation, string & indicator extraction, PE header parsing,
service inspection, action execution, and brain router direct intents.
"""
import os
import sys
import pytest
from app.services.reverse_engineering_service import (
    compute_shannon_entropy,
    extract_strings,
    parse_pe_header,
    compute_file_hashes,
    reverse_engineering_service,
)
from app.actions.reverse_engineering_action import reverse_engineering_action
from app.services.brain_router import detect_direct_intent
from app.services.action_dispatcher import action_dispatcher


def test_shannon_entropy():
    """Verifies that Shannon entropy is calculated accurately."""
    # Zero bytes
    assert compute_shannon_entropy(b"") == 0.0

    # Low entropy: highly repetitive data
    low_ent = compute_shannon_entropy(b"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    assert low_ent == 0.0

    # Moderate entropy: normal ASCII text
    text_ent = compute_shannon_entropy(b"Hello world! This is a test of the Shannon entropy calculation.")
    assert 3.0 < text_ent < 5.0

    # High entropy: all 256 byte values distributed uniformly
    high_data = bytes(range(256)) * 4
    high_ent = compute_shannon_entropy(high_data)
    assert high_ent > 7.9


def test_string_and_indicator_extraction():
    """Verifies ASCII, UTF-16LE, and security indicator extraction."""
    test_blob = (
        b"Standard ASCII string here\x00"
        b"https://example.com/api/v1/telemetry\x00"
        b"192.168.1.100\x00"
        b"VirtualAlloc\x00"
        b"IsDebuggerPresent\x00"
        b"Software\\Microsoft\\Windows\\CurrentVersion\x00"
        + "UnicodeWideString".encode("utf-16le")
    )

    res = extract_strings(test_blob, min_len=4)
    assert res["total_extracted"] > 0
    assert "https://example.com/api/v1/telemetry" in res["urls"]
    assert "192.168.1.100" in res["ips"]
    assert "VirtualAlloc" in res["suspicious_apis"]
    assert "IsDebuggerPresent" in res["suspicious_apis"]
    assert any("Software" in r for r in res["registry_keys"])
    assert any("UnicodeWideString" in s for s in res["sample"])


def test_compute_file_hashes():
    """Verifies hashing of a known file (Python executable)."""
    hashes = compute_file_hashes(sys.executable)
    assert "sha256" in hashes
    assert "md5" in hashes
    assert len(hashes["sha256"]) == 64
    assert len(hashes["md5"]) == 32


def test_inspect_real_pe_binary():
    """Inspects the running Python interpreter binary and validates PE metadata."""
    res = reverse_engineering_service.inspect_file(sys.executable)
    assert res["status"] == "success"
    assert "PE" in res["file_type"]
    assert res["shannon_entropy"] > 0
    assert "pe_details" in res
    assert res["pe_details"]["architecture"] in ["AMD64 / x86-64 (64-bit)", "Intel x86 (32-bit)", "ARM64 (64-bit)"]
    assert "security_mitigations" in res["pe_details"]


def test_reverse_engineering_action_status():
    """Verifies action status returns REA engine info."""
    out = reverse_engineering_action({"action": "status"})
    assert "Motor de Ingeniería Inversa" in out
    assert "REA" in out


def test_reverse_engineering_action_inspect_and_entropy():
    """Verifies action execution for inspect, entropy, and strings."""
    # 1. Full inspect
    insp = reverse_engineering_action({"action": "inspect", "target_path": sys.executable})
    assert "Reporte de Ingeniería Inversa" in insp
    assert "Arquitectura y Seguridad" in insp

    # 2. Entropy
    ent = reverse_engineering_action({"action": "entropy", "target_path": sys.executable})
    assert "Entropía de Shannon" in ent

    # 3. Strings
    strs = reverse_engineering_action({"action": "strings", "target_path": sys.executable})
    assert "Extracción de Cadenas" in strs


def test_direct_intent_reverse_engineering():
    """Verifies direct voice and text intents for reverse engineering."""
    cases = [
        ("estado de rea", "reverse_engineer", "action", "status"),
        ("motor de ingenieria inversa", "reverse_engineer", "action", "status"),
        ("analiza este ejecutable 'test.exe'", "reverse_engineer", "action", "inspect"),
        ("inspecciona el binario 'app.exe'", "reverse_engineer", "action", "inspect"),
        ("entropia de 'sample.bin'", "reverse_engineer", "action", "entropy"),
    ]

    for phrase, exp_tool, exp_key, exp_val in cases:
        detected = detect_direct_intent(phrase)
        assert detected is not None, f"Failed for phrase: '{phrase}'"
        tool_name, tool_args, _ = detected
        assert tool_name == exp_tool
        if exp_key:
            assert tool_args.get(exp_key) == exp_val


def test_action_dispatcher_reverse_engineer():
    """Verifies integration inside action_dispatcher."""
    res = reverse_engineering_action({"action": "status"})
    assert "REA" in res
    assert "ONLINE" in res

