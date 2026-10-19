"""
Automated Test Suite for Vercel Labs Agent Skills in Liseth.
Verifies framework detection, packaging, React best practices auditing,
Web Interface Guidelines compliance, action dispatching, and brain routing.
"""

import json
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.services.vercel_skills_service import VercelSkillsService, vercel_skills_service
from app.actions.vercel_skills_action import vercel_skills_action
from app.services.action_dispatcher import action_dispatcher
from app.services.brain_router import detect_direct_intent


class TestVercelSkillsService:
    """Tests for the VercelSkillsService primitives."""

    def test_status_structure(self):
        st = vercel_skills_service.get_status()
        assert isinstance(st, dict)
        assert "Vercel Labs" in st["engine"]
        assert len(st["skills_installed"]) >= 3

    def test_detect_framework_package_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_file = Path(tmpdir) / "package.json"
            pkg_file.write_text(json.dumps({
                "name": "my-next-app",
                "dependencies": {"next": "14.2.0", "react": "18.3.1"}
            }), encoding="utf-8")
            res = vercel_skills_service.detect_framework(tmpdir)
            assert res["framework"] == "Next.js"
            assert res["has_package_json"] is True

    def test_detect_framework_static_html(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "index.html").write_text("<h1>Hello World</h1>", encoding="utf-8")
            res = vercel_skills_service.detect_framework(tmpdir)
            assert res["framework"] == "Static HTML"
            assert res["has_index_html"] is True

    def test_create_project_tarball(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir)
            (p / "index.html").write_text("<h1>Test App</h1>", encoding="utf-8")
            (p / "node_modules").mkdir()
            (p / "node_modules" / "heavy.js").write_text("console.log('heavy')", encoding="utf-8")

            tar_path, size = vercel_skills_service.create_project_tarball(tmpdir)
            assert os.path.exists(tar_path)
            assert size > 0

            # Verify node_modules was excluded
            import tarfile
            with tarfile.open(tar_path, "r:gz") as tar:
                names = tar.getnames()
                assert any("index.html" in n for n in names)
                assert not any("node_modules" in n for n in names)

    def test_audit_react_code_detects_barrel_and_waterfalls(self):
        bad_react_code = """
        import React, { useState } from 'react';
        import { Check, X, Menu } from 'lucide-react';

        export function BadComponent({ items }) {
            const [count, setCount] = useState(0);

            async function loadData() {
                const user = await fetchUser();
                const posts = await fetchPosts();
                const comments = await fetchComments();
            }

            return (
                <div style={{ padding: 20 }}>
                    {items.length && <span>Hay {items.length} elementos</span>}
                    <button onClick={() => setCount(count + 1)}>Incrementar</button>
                </div>
            );
        }
        """
        audit = vercel_skills_service.audit_react_code(bad_react_code, "BadComponent.tsx")
        assert audit["total_findings"] >= 3
        rule_ids = [f["rule_id"] for f in audit["findings"]]
        assert "bundle-barrel-imports" in rule_ids
        assert "async-parallel" in rule_ids
        assert "rendering-conditional-render" in rule_ids
        assert audit["score"] < 80

    def test_audit_react_code_clean_component(self):
        clean_code = """
        import React, { useCallback, useMemo } from 'react';
        import Check from 'lucide-react/dist/esm/icons/check';

        export function CleanComponent({ items, onAction }) {
            const count = useMemo(() => items.length, [items]);
            const handleClick = useCallback(() => {
                onAction();
            }, [onAction]);

            return (
                <div className="p-4">
                    {count > 0 ? <span>Total: {count}</span> : null}
                    <button type="button" onClick={handleClick}>Acción</button>
                </div>
            );
        }
        """
        audit = vercel_skills_service.audit_react_code(clean_code, "CleanComponent.tsx")
        assert audit["score"] >= 95
        assert audit["grade"] in ["A+", "A"]

    def test_audit_web_design_detects_a11y_issues(self):
        bad_html = """
        <div class="card">
            <img src="/logo.png">
            <div onClick="navigate()">Ir al panel</div>
            <button class="icon-btn"><svg></svg></button>
            <input type="email" placeholder="Correo">
            <style>
                .input { outline: none; }
            </style>
        </div>
        """
        audit = vercel_skills_service.audit_web_design(bad_html, "dashboard.html")
        assert audit["total_findings"] >= 3
        cats = [f["category"] for f in audit["findings"]]
        assert any("Accesibilidad" in c for c in cats)
        assert any("Formularios" in c for c in cats)
        assert any("Estados de Enfoque" in c for c in cats)


class TestVercelSkillsAction:
    """Tests for vercel_skills_action wrapper."""

    def test_action_status(self):
        out = vercel_skills_action({"action": "status"})
        assert "Vercel Labs" in out
        assert "react-best-practices" in out

    def test_action_detect_framework(self):
        out = vercel_skills_action({"action": "framework", "path": "."})
        assert "Framework" in out

    def test_action_unknown(self):
        out = vercel_skills_action({"action": "desconocida"})
        assert "no se reconoció la acción" in out.lower()

    def test_action_audit_react_inline_code(self):
        code = "import { Check } from 'lucide-react'; export default () => <div style={{ margin: 0 }}></div>;"
        out = vercel_skills_action({"action": "audit_react", "code": code})
        assert "Auditoría de Rendimiento React" in out
        assert "bundle-barrel-imports" in out

    def test_action_audit_design_inline_code(self):
        code = "<img src='pic.jpg'><input type='text'>"
        out = vercel_skills_action({"action": "audit_design", "code": code})
        assert "Auditoría de Interfaz Web" in out
        assert "Accesibilidad" in out


class TestBrainRouterVercelIntegration:
    """Tests zero-latency intent classification for Vercel Skills in brain_router."""

    def test_status_intent(self):
        res = detect_direct_intent("Liseth como esta el estado de vercel")
        assert res is not None
        tool, args, prompt = res
        assert tool == "vercel_skills"
        assert args.get("action") == "status"

    def test_deploy_preview_intent(self):
        res = detect_direct_intent("despliega mi aplicacion a vercel")
        assert res is not None
        tool, args, prompt = res
        assert tool == "vercel_skills"
        assert args.get("action") == "deploy"
        assert args.get("prod") is False

    def test_deploy_production_intent(self):
        res = detect_direct_intent("despliega mi aplicacion a vercel en produccion")
        assert res is not None
        tool, args, prompt = res
        assert tool == "vercel_skills"
        assert args.get("action") == "deploy"
        assert args.get("prod") is True

    def test_audit_react_intent(self):
        res = detect_direct_intent("audita este componente react 'src/components/Header.tsx'")
        assert res is not None
        tool, args, prompt = res
        assert tool == "vercel_skills"
        assert args.get("action") == "audit_react"
        assert "Header.tsx" in args.get("path", "")

    def test_audit_design_intent(self):
        res = detect_direct_intent("revisa el diseño web de mi pagina 'index.html'")
        assert res is not None
        tool, args, prompt = res
        assert tool == "vercel_skills"
        assert args.get("action") == "audit_design"
        assert "index.html" in args.get("path", "")


def test_action_dispatcher_vercel_integration():
    """Verifies vercel_skills_action returns status."""
    res = vercel_skills_action({"action": "status"})
    assert "Vercel Labs" in res
    assert "react-best-practices" in res

