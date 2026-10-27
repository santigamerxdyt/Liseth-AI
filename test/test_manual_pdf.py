"""
Unit tests for Liseth's dynamic PDF manual generator.
"""
import os
import tempfile
import pytest
from tools.generate_manual_pdf import generate_manual_pdf


def test_generate_manual_pdf_produces_valid_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_pdf = os.path.join(tmpdir, "test_manual.pdf")
        res_path = generate_manual_pdf(out_pdf)

        assert os.path.exists(res_path)
        assert os.path.getsize(res_path) > 10000  # Detailed multi-page PDF

        # Verify PDF specification conformity
        with open(res_path, "rb") as f:
            content = f.read()
            assert content.startswith(b"%PDF-1.")
            assert b"%%EOF" in content[-128:]
            # Verify that key sections are embedded in the stream objects
            assert b"LISETH AI" in content
            assert b"Administracion" in content or b"Business" in content or b"Financiera" in content
            assert b"APA" in content
            assert b"VAN" in content or b"NPV" in content
            assert b"Segundo Plano" in content or b"Background" in content
            assert b"Formulario 490" in content or b"Impuestos DIAN" in content
            assert b"Accesibilidad" in content or b"WCAG" in content
            assert b"Unit Economics" in content or b"9-Box" in content or b"TRM" in content
            assert b"ESG" in content or b"Factoring" in content or b"KTNO" in content
