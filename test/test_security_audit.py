"""
Automated Test Suite for Security Audit Enterprise Service in Liseth.
Verifies static vulnerability analysis, secret detection, action dispatching,
and brain router intent classification.
"""

import pytest
from app.services.security_audit_service import SecurityAuditService, security_audit_service
from app.actions.security_audit_action import security_audit_action
from app.services.action_dispatcher import action_dispatcher
from app.services.brain_router import detect_direct_intent


class TestSecurityAuditService:
    """Tests for SecurityAuditService primitives."""

    def test_status_structure(self):
        st = security_audit_service.get_status()
        assert isinstance(st, dict)
        assert "Security Audit" in st["engine"]
        assert len(st["detection_vectors"]) >= 5

    def test_detect_secrets_and_api_keys(self):
        vulnerable_code = """
        API_KEY = "AIzaSyD-1234567890abcdefghijklmnopqrstuvw"
        AWS_SECRET = "AKIA1234567890ABCDEF"
        DB_URL = "mongodb+srv://admin:SuperSecretPassword123@cluster.mongodb.net/prod"
        """
        audit = security_audit_service.audit_code_snippet(vulnerable_code, "config.py")
        assert audit["total_findings"] >= 3
        assert audit["risk_level"] in ["CRÍTICO", "ALTO"]
        cwes = [f.get("cwe") for f in audit["findings"]]
        assert "CWE-798" in cwes

    def test_detect_sql_and_command_injection(self):
        vulnerable_code = """
        import os
        import subprocess

        def run_query(user_id):
            query = "SELECT * FROM users WHERE id = '" + user_id + "'"
            return db.execute(query)

        def execute_user_script(script):
            subprocess.run("python " + script, shell=True)
            eval(user_input)
        """
        audit = security_audit_service.audit_code_snippet(vulnerable_code, "handler.py")
        assert audit["total_findings"] >= 3
        cwes = [f.get("cwe") for f in audit["findings"]]
        assert "CWE-89" in cwes   # SQLi
        assert "CWE-78" in cwes   # Command Injection
        assert "CWE-95" in cwes   # Eval code injection
        assert audit["security_score"] < 50

    def test_clean_code_security_score(self):
        clean_code = """
        import os
        from sqlalchemy import text

        def get_user_safe(db, user_id: int):
            stmt = text("SELECT id, name FROM users WHERE id = :user_id")
            return db.execute(stmt, {"user_id": user_id}).fetchone()

        def safe_hash(data: bytes) -> str:
            import hashlib
            return hashlib.sha256(data).hexdigest()
        """
        audit = security_audit_service.audit_code_snippet(clean_code, "safe.py")
        assert audit["total_findings"] == 0
        assert audit["security_score"] == 100
        assert audit["risk_level"] == "SEGURO"


class TestSecurityAuditAction:
    """Tests for security_audit_action wrapper."""

    def test_action_status(self):
        out = security_audit_action({"action": "status"})
        assert "Security Audit Enterprise" in out
        assert "OWASP" in out

    def test_action_audit_code(self):
        code = "os.system('rm -rf ' + user_path)"
        out = security_audit_action({"action": "audit", "code": code})
        assert "Informe de Auditoría de Ciberseguridad" in out

    def test_action_audit_path(self):
        out = security_audit_action({"action": "audit", "path": "."})
        assert "Informe de Auditoría de Ciberseguridad" in out


class TestBrainRouterSecurityIntegration:
    """Tests zero-latency intent classification for Security Audit in brain_router."""

    def test_status_intent(self):
        res = detect_direct_intent("Liseth como esta el estado de seguridad")
        assert res is not None
        tool, args, prompt = res
        assert tool == "security_audit"
        assert args.get("action") == "status"

    def test_audit_codebase_intent(self):
        res = detect_direct_intent("audita la seguridad de este proyecto")
        assert res is not None
        tool, args, prompt = res
        assert tool == "security_audit"
        assert args.get("action") == "audit"

    def test_audit_file_intent(self):
        res = detect_direct_intent("escanea vulnerabilidades en 'app/main.py'")
        assert res is not None
        tool, args, prompt = res
        assert tool == "security_audit"
        assert "main.py" in args.get("path", "")


@pytest.mark.asyncio
async def test_action_dispatcher_security_integration():
    """Verifies action_dispatcher dispatches security_audit calls."""
    res = await action_dispatcher.execute_tool("security_audit", {"action": "status"})
    assert "Security Audit Enterprise" in res
