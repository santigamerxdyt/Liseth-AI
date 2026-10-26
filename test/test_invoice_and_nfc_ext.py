"""
Unit tests for Liseth Digital Invoicing and Extended NFC Ecosystem.
Tests DIAN pro-forma electronic invoices, CUFE SHA-384 hashes, tax math, currency converter,
Stark security key proximity unlock, and action dispatching.
"""

import pytest
from app.services.invoice_service import InvoiceService, invoice_service
from app.services.nfc_service import nfc_service
from app.actions.nfc_action import nfc_action


def test_invoice_service_status():
    st = invoice_service.get_status()
    assert st["status"] == "ONLINE"
    assert "CUFE SHA-384" in st["standards"]


def test_generate_invoice_calculations_and_cufe():
    inv = invoice_service.generate_invoice(
        client_name="Agroindustrias del Valle S.A.S.",
        client_id="900123456-7",
        items=[
            {"description": "Asesoría Financiera WACC y Valoración", "quantity": 2, "unit_price": 100000.0},
            {"description": "Estructuración de Flujo de Caja Libre", "quantity": 1, "unit_price": 50000.0}
        ],
        tax_rate=0.19,
        retefuente_rate=0.04,
        currency="COP"
    )

    assert inv["id"].startswith("FAC-")
    assert inv["subtotal"] == 250000.0
    assert inv["tax_iva"] == 47500.0   # 19% of 250,000
    assert inv["retefuente"] == 10000.0  # 4% of 250,000
    assert inv["total"] == 287500.0      # 250k + 47.5k - 10k
    assert len(inv["cufe_hash"]) == 96   # SHA-384 is 96 hex characters
    assert "catalogo-vpfe.dian.gov.co" in inv["dian_qr"]

    # Markdown representation
    md = invoice_service.format_invoice_markdown(inv)
    assert "Factura Electrónica Pro-Forma" in md
    assert "Agroindustrias del Valle S.A.S." in md
    assert "$287,500.00 COP" in md
    assert inv["cufe_hash"] in md


def test_nfc_currency_and_crypto_converter():
    # Test USD to COP
    res_usd = nfc_service.convert_currency(100.0, from_curr="USD", to_curr="COP")
    assert res_usd["converted_amount"] == 415000.0

    # Test COP to USD
    res_cop = nfc_service.convert_currency(415000.0, from_curr="COP", to_curr="USD")
    assert res_cop["converted_amount"] == 100.0

    # Test Crypto (BTC to COP)
    res_btc = nfc_service.convert_currency(1.0, from_curr="BTC", to_curr="COP")
    assert res_btc["converted_amount"] == 278000000.0


def test_nfc_security_badge_proximity_unlock():
    # Verify default Stark master key
    ver = nfc_service.verify_security_badge("04:STARK:KEY:01")
    assert ver["authorized"] is True

    # Enroll a new custom NFC card
    enroll_res = nfc_service.enroll_security_badge("04:UNAL:STUDENT:88", label="Carné Estudiantil UNAL")
    assert enroll_res["id"] == "04:UNAL:STUDENT:88"

    # Verify newly enrolled card
    ver_new = nfc_service.verify_security_badge("04:UNAL:STUDENT:88")
    assert ver_new["authorized"] is True
    assert "Carné Estudiantil UNAL" in ver_new["message"]

    # Unknown card should fail
    ver_unknown = nfc_service.verify_security_badge("04:UNKNOWN:CARD:99")
    assert ver_unknown["authorized"] is False


def test_nfc_action_invoicing_and_converter():
    # Test invoice action
    res_inv = nfc_action({
        "action": "invoice",
        "client": "Constructora Bolívar",
        "amount": 75000,
        "concept": "Auditoría de Procesos"
    })
    assert "Factura Electrónica Pro-Forma" in res_inv
    assert "Constructora Bolívar" in res_inv
    assert "CUFE" in res_inv

    # Test convert action
    res_conv = nfc_action({
        "action": "convert",
        "amount": 50,
        "from": "USD",
        "to": "COP"
    })
    assert "Conversión de Divisas" in res_conv
    assert "207,500.0000 COP" in res_conv

    # Test badge action
    res_badge = nfc_action({
        "action": "badge",
        "uid": "04:STARK:KEY:01"
    })
    assert "Verificación de credencial NFC" in res_badge
    assert "True" in res_badge
