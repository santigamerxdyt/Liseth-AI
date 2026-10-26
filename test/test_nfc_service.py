"""
Unit tests for Liseth's NFC and Contactless Payment Engine.
Tests NDEF payload generation, tokenized payments, vCards, tap processing, and tool action dispatch.
"""

import json
import pytest
from app.services.nfc_service import NFCService, nfc_service
from app.actions.nfc_action import nfc_action


def test_nfc_service_status():
    st = nfc_service.get_status()
    assert st["status"] == "ONLINE"
    assert "Bre-B Interoperable (Colombia)" in st["payment_methods"]
    assert "NFC Forum Type 2/4/5" in st["supported_protocols"]
    report = nfc_service.format_status_report(st)
    assert "Ecosistema NFC" in report


def test_create_payment_payload():
    tx = nfc_service.create_payment_payload(
        amount=50000.0,
        currency="COP",
        concept="Consultoría Estratégica",
        recipient="Santiago",
        method="bre_b"
    )
    assert tx["id"].startswith("TX-NFC-")
    assert tx["amount"] == 50000.0
    assert tx["currency"] == "COP"
    assert tx["status"] == "pending_tap"
    assert len(tx["signature"]) == 16
    assert "breb://pay" in tx["deep_link"]
    assert len(tx["ndef_records"]) == 3
    # Check mime record
    mime_rec = tx["ndef_records"][0]
    assert mime_rec["mediaType"] == "application/vnd.liseth.payment+json"
    pdata = json.loads(mime_rec["data"])
    assert pdata["protocol"] == "LISETH_NFC_PAY_V1"
    assert pdata["amount"] == 50000.0


def test_create_vcard_payload():
    vcard = nfc_service.create_vcard_payload(
        name="Santiago",
        role="Administrador de Empresas / CEO",
        organization="UNAL Palmira",
        phone="+57 300 123 4567",
        email="santiago@unal.edu.co"
    )
    assert vcard["type"] == "vcard"
    assert "BEGIN:VCARD" in vcard["vcard_text"]
    assert "FN:Santiago" in vcard["vcard_text"]
    assert "TITLE:Administrador de Empresas / CEO" in vcard["vcard_text"]
    assert "ORG:UNAL Palmira" in vcard["vcard_text"]
    assert "END:VCARD" in vcard["vcard_text"]


def test_incoming_tap_processing():
    # Emulate incoming payment tap
    records = [
        {
            "recordType": "mime",
            "mediaType": "application/vnd.liseth.payment+json",
            "data": json.dumps({
                "protocol": "LISETH_NFC_PAY_V1",
                "amount": 15000,
                "currency": "COP",
                "recipient": "Café Gourmet",
                "concept": "Capuchino y Repostería"
            })
        }
    ]
    res = nfc_service.process_incoming_tap(
        serial_number="04:A1:B2:C3:D4:E5:F6",
        records=records,
        simulated=False
    )
    assert res["type"] == "payment"
    assert res["status"] == "completed"
    assert res["extracted_data"]["payment"]["amount"] == 15000

    # Ledger check
    ledger = nfc_service.get_ledger(limit=5)
    assert len(ledger) > 0
    assert any(it["id"] == res["id"] for it in ledger)


def test_nfc_action_dispatcher():
    # Test status
    res_st = nfc_action({"action": "status"})
    assert "Ecosistema NFC" in res_st

    # Test payment creation
    res_pay = nfc_action({
        "action": "payment_request",
        "amount": 32000,
        "currency": "COP",
        "concept": "Materiales de estudio",
        "recipient": "Santiago"
    })
    assert "Solicitud de Cobro Contactless Generada" in res_pay
    assert "32,000.00" in res_pay

    # Test vcard beaming
    res_vcard = nfc_action({
        "action": "beam_vcard",
        "name": "Santiago",
        "role": "CEO"
    })
    assert "Tarjeta de Contacto Digital (vCard)" in res_vcard

    # Test history
    res_hist = nfc_action({"action": "history"})
    assert "Historial de Transacciones Contactless" in res_hist

    # Test clear history
    res_clear = nfc_action({"action": "clear_history"})
    assert "Operación completada" in res_clear
