"""
SlopMonster & Deslop Service for JARVIS / Liseth.
AI writing pattern detector, copy humanizer, and anti-slop editor:
- Evaluates drafts against 5 core AI writing categories (0 to 5 score).
- Detects robotic buzzwords, formulaic constructions, triadic lists, and em-dash overuse.
- Dual-language support: English and Spanish AI pattern catalogues.
- Autonomous humanizer engine: strips AI filler, throat-clearing openers, and pompous jargon,
  producing direct, authoritative, executive human prose.
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger("jarvis.slopmonster")

# ── English AI Tells Catalogue (from SlopMonster) ───────────────────────────
_VOCAB_EN = [
    'delve', 'leverage', 'seamless', 'elevate', 'robust', 'unlock', 'unleash',
    'empower', 'streamline', 'cutting-edge', 'state-of-the-art', 'game-changer',
    'game-changing', 'revolutionize', 'revolutionise', 'transformative',
    'transformation', 'innovate', 'holistic', 'synergy', 'synergies', 'paradigm', 'bespoke',
    'meticulous', 'tapestry', 'testament', 'beacon', 'unparalleled', 'supercharge',
    'turbocharge', 'effortless', 'next-level', 'pivotal', 'foster', 'showcase',
    'compelling', 'intuitive', 'world-class', 'best-in-class'
]

_VOCAB_EXACT_EN = [
    'crafted', 'curated', 'harnessing', 'harness the power', 'journey', 'realm', 'landscape',
    'navigate the', 'in the world of', "in today's", 'ever-evolving', 'fast-paced',
    'look no further', 'dive in', "let's dive", 'deep dive', 'embark',
    'unlock the power', 'buckle up', 'the secret sauce', 'level up'
]

_PHRASES_EN = [
    (r"(?:\bnot|n['’]t)\s+(?:just|only|merely|simply)\b[^.!?]{0,80}\bbut\b", "Construcción 'not just X, but Y'"),
    (r"\bwhether you(?:'?re| are)\b[^.!?]{0,40}\bor\b", "Apertura fórmula 'whether you're X or Y'"),
    (r"\bmore than just\b", "Frase comodín 'more than just'"),
    (r"\b(that|this)(?:'?s| is) where\b[^.!?]{0,30}\bcomes? in\b", "Transición 'that's where X comes in'"),
    (r"\bsay goodbye to\b", "Cliché publicitario 'say goodbye to'"),
    (r"\bimagine (a|an|the)\b", "Apertura teatral 'imagine a...'"),
    (r"\bin conclusion\b|\bto sum up\b|\bultimately\b", "Conclusión escolar de ensayo ('in conclusion')"),
    (r"\bwhen it comes to\b", "Relleno 'when it comes to'"),
    (r"\bat the end of the day\b", "Cliché 'at the end of the day'"),
    (r"\bthe key is\b|\bthe truth is\b|\bhere'?s the thing\b", "Apertura innecesaria ('here's the thing')"),
    (r"\bhelps? you to\b|\bcan help you\b", "Promesa vaga ('helps you to...')"),
    (r"\bvery unique\b|\bquite literally\b", "Intensificador inflado ('very unique')"),
]

# ── Spanish AI Tells Catalogue (Adaptado para español) ────────────────────────
_VOCAB_ES = [
    'adentrarse', 'profundizar', 'tapiz', 'testimonio de', 'piedra angular',
    'sin fisuras', 'vibrante', 'revolucionar', 'revolucionario', 'desbloquear',
    'empoderar', 'optimizar', 'vanguardista', 'de ultima generacion', 'transformador',
    'holistico', 'sinergia', 'paradigma', 'a medida', 'meticuloso', 'sin precedentes',
    'sobrecargar', 'intuitivo', 'de clase mundial', 'crucial', 'fundamental'
]

_VOCAB_EXACT_ES = [
    'en el vertiginoso mundo actual', 'en un mundo en constante evolucion',
    'no busques mas', 'sumergirse en', 'dar el salto', 'llevar al siguiente nivel',
    'el ingrediente secreto', 'en el panorama actual', 'un viaje hacia',
    'desatar el poder de', 'aprovechar al maximo'
]

_PHRASES_ES = [
    (r"\bno\s+solo\b[^.!?]{0,80}\bsino\s+tambi[eé]n\b", "Construcción típica 'no solo X, sino también Y'"),
    (r"\bya\s+seas\s+(?:un|una)\b[^.!?]{0,40}\bo\b", "Apertura cliché 'ya seas X o Y'"),
    (r"\ben\s+conclusi[oó]n\b|\ben\s+resumen\b|\ben\s+[uú]ltima\s+instancia\b", "Conclusión artificial de IA ('en conclusión / en última instancia')"),
    (r"\bcabe\s+destacar\s+que\b|\bes\s+importante\s+(?:recordar|mencionar)\s+que\b", "Apertura de relleno ('cabe destacar que...')"),
    (r"\bdicho\s+esto\b", "Muletilla de transición ('dicho esto')"),
    (r"\bdile\s+adi[oó]s\s+a\b", "Cliché publicitario ('dile adiós a...')"),
    (r"\bimagina\s+(?:un|una|el|la)\b", "Apertura artificial ('imagina un...')"),
    (r"\ba\s+fin\s+de\s+cuentas\b", "Frase hecha ('a fin de cuentas')"),
]


class SlopMonsterService:
    """Manages AI copy evaluation, scoring, pattern hunting, and text humanization."""

    def __init__(self):
        self._skills_dir = Path("c:/Users/Usuario/Desktop/MI LISEHT/.agents/skills/slopmonster")

    def deslop_text(self, text: str, file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyzes a piece of text or document for AI tells across 5 categories:
        1. Vocabulary (Robotic buzzwords)
        2. Sentence Patterns (Cliché constructions)
        3. Punctuation (Em-dashes, excessive colons/questions)
        4. Rhythm & Triadic Lists (Three-item repetitions)
        5. Unsupported Proof & Empty Conclusions
        Returns a score out of 5.0 and exact line-level matches.
        """
        if not text or not text.strip():
            return {
                "score": 0.0,
                "human_score": "0 / 5",
                "human_percentage": 0,
                "status": "FALLÓ (Texto vacío)",
                "total_violations": 0,
                "findings": []
            }

        lines = text.split("\n")
        findings: List[Dict[str, Any]] = []

        failed_categories = set()

        # 1. Category 1: Vocabulary Tells (EN & ES)
        for idx, line in enumerate(lines, start=1):
            lower_line = line.lower()
            # English root matching
            for word in _VOCAB_EN:
                pattern = rf"\b{re.escape(word)}(?:s|ed|ing|tion|tions|tive|ly)?\b"
                for m in re.finditer(pattern, lower_line):
                    failed_categories.add("Vocabulario")
                    findings.append({
                        "category": "Vocabulario IA",
                        "line": idx,
                        "match": m.group(0),
                        "context": line.strip()[:90],
                        "issue": f"Palabra trillada de IA: '{m.group(0)}'",
                        "fix": "Reemplace por un verbo directo y concreto (ej. 'use', 'haga', 'cree')."
                    })
            # English exact
            for word in _VOCAB_EXACT_EN:
                if word in lower_line:
                    failed_categories.add("Vocabulario")
                    findings.append({
                        "category": "Vocabulario IA",
                        "line": idx,
                        "match": word,
                        "context": line.strip()[:90],
                        "issue": f"Frase trillada de marketing IA: '{word}'",
                        "fix": "Elimine la metáfora y exprese la idea de forma literal."
                    })
            # Spanish vocabulary
            for word in _VOCAB_ES:
                if re.search(rf"\b{re.escape(word)}\b", lower_line):
                    failed_categories.add("Vocabulario")
                    findings.append({
                        "category": "Vocabulario IA (Español)",
                        "line": idx,
                        "match": word,
                        "context": line.strip()[:90],
                        "issue": f"Término artificial de IA: '{word}'",
                        "fix": "Utilice vocabulario natural y ejecutivo sin adornos innecesarios."
                    })
            for word in _VOCAB_EXACT_ES:
                if word in lower_line:
                    failed_categories.add("Vocabulario")
                    findings.append({
                        "category": "Vocabulario IA (Español)",
                        "line": idx,
                        "match": word,
                        "context": line.strip()[:90],
                        "issue": f"Cliché típico de IA en español: '{word}'",
                        "fix": "Vaya directo al grano sin introducciones genéricas."
                    })

        # 2. Category 2: Sentence Patterns & Cliché Constructions
        for idx, line in enumerate(lines, start=1):
            for pattern, desc in _PHRASES_EN:
                if re.search(pattern, line, re.IGNORECASE):
                    failed_categories.add("Patrones de Oración")
                    findings.append({
                        "category": "Patrón de Oración IA",
                        "line": idx,
                        "match": desc,
                        "context": line.strip()[:90],
                        "issue": f"Construcción sintáctica robótica: {desc}",
                        "fix": "Divida en dos oraciones claras o exprese la afirmación sin rodeos."
                    })
            for pattern, desc in _PHRASES_ES:
                if re.search(pattern, line, re.IGNORECASE):
                    failed_categories.add("Patrones de Oración")
                    findings.append({
                        "category": "Patrón de Oración IA (Español)",
                        "line": idx,
                        "match": desc,
                        "context": line.strip()[:90],
                        "issue": f"Construcción sintáctica robótica: {desc}",
                        "fix": "Reescriba de forma concisa sin muletillas de transición."
                    })

        # 3. Category 3: Punctuation Clichés (Em-dash abuse)
        for idx, line in enumerate(lines, start=1):
            em_dashes = line.count("—") + line.count(" - ")
            if em_dashes >= 2:
                failed_categories.add("Puntuación")
                findings.append({
                    "category": "Puntuación Robótica",
                    "line": idx,
                    "match": "Múltiples guiones largos (—)",
                    "context": line.strip()[:90],
                    "issue": "Abuso de guiones largos (em-dash), muletilla típica de modelos LLM.",
                    "fix": "Reemplace los guiones por puntos seguidos, comas o paréntesis discretos."
                })

        # 4. Category 4: Rhythm & Triadic Lists
        for idx, line in enumerate(lines, start=1):
            # Detects "X, Y, and Z" or "X, Y y Z"
            if re.search(r"\b[a-zA-ZáéíóúÁÉÍÓÚ]+\s*,\s*[a-zA-ZáéíóúÁÉÍÓÚ]+\s+(?:and|y|e)\s+[a-zA-ZáéíóúÁÉÍÓÚ]+\b", line):
                if any(k in line.lower() for k in ["rápido", "seguro", "escalable", "fast", "reliable", "secure", "simple", "potente", "powerful", "innovador"]):
                    failed_categories.add("Ritmo y Listas")
                    findings.append({
                        "category": "Ritmo y Listas de Tres",
                        "line": idx,
                        "match": "Tríada de adjetivos",
                        "context": line.strip()[:90],
                        "issue": "Lista trillada de 3 adjetivos publicitarios de IA.",
                        "fix": "Enfoque en el beneficio principal en lugar de apilar adjetivos vacíos."
                    })

        # 5. Category 5: Empty Proof & Conclusions
        for idx, line in enumerate(lines, start=1):
            if re.search(r"^(?:en conclusi[oó]n|en resumen|in conclusion|to sum up|ultimately)\b", line.strip(), re.IGNORECASE):
                failed_categories.add("Conclusiones Vacías")
                findings.append({
                    "category": "Conclusiones Vacías",
                    "line": idx,
                    "match": line.strip()[:40],
                    "context": line.strip()[:90],
                    "issue": "Cierre formulaico de IA sin valor factual adicional.",
                    "fix": "Finalice con el siguiente paso práctico o la llamada a la acción concreta."
                })

        # Score calculation: 5 minus 1 for each failed category
        score = max(0.0, 5.0 - len(failed_categories))
        human_pct = int((score / 5.0) * 100)

        return {
            "target": file_name or "Texto analizado",
            "score": score,
            "human_score": f"{score:.1f} / 5.0",
            "human_percentage": human_pct,
            "failed_categories": list(failed_categories),
            "total_violations": len(findings),
            "is_clean": score >= 4.5,
            "findings": findings
        }

    def humanize_text(self, text: str) -> Dict[str, Any]:
        """
        Rewrites robotic AI draft into direct, punchy, human executive prose.
        Removes throat-clearing, replaces buzzwords, and restructures cliché sentences.
        """
        original = text
        cleansed = text
        changes: List[str] = []

        # Replacements table (Robotic phrase -> Direct human equivalent)
        replacements = [
            (r"\bIn today's fast-paced digital world,?\s*", ""),
            (r"\bEn el vertiginoso mundo actual,?\s*", ""),
            (r"\bEn un mundo en constante evoluci[oó]n,?\s*", ""),
            (r"\bAt its core,?\s*", ""),
            (r"\bEn su n[uú]cleo,?\s*", ""),
            (r"\bCabe destacar que\s+", ""),
            (r"\bEs importante recordar que\s+", ""),
            (r"\bIt is important to remember that\s+", ""),
            (r"\bDicho esto,?\s*", "Sin embargo, "),
            (r"\bdelve into\b", "examine"),
            (r"\bprofundizar en\b", "analizar"),
            (r"\badentrarse en\b", "explorar"),
            (r"\bleverage\b", "use"),
            (r"\baprovechar al m[aá]ximo\b", "usar"),
            (r"\bseamlessly\b", "directly"),
            (r"\bsin fisuras\b", "de forma fluida"),
            (r"\belevate\b", "improve"),
            (r"\brevolucionar\b", "transformar"),
            (r"\bcutting-edge\b", "modern"),
            (r"\bde [uú]ltima generaci[oó]n\b", "actual"),
            (r"\btapestry of\b", "mix of"),
            (r"\bun tapiz de\b", "una combinación de"),
            (r"\btestament to\b", "proof of"),
            (r"\bun testimonio de\b", "prueba de"),
            (r"\bpiedra angular\b", "base"),
            (r"\bcornerstone\b", "basis"),
            (r"\bin conclusion,?\s*", ""),
            (r"\ben conclusi[oó]n,?\s*", ""),
            (r"\bto sum up,?\s*", ""),
            (r"\ben resumen,?\s*", ""),
        ]

        for pattern, replacement in replacements:
            if re.search(pattern, cleansed, re.IGNORECASE):
                cleansed, count = re.subn(pattern, replacement, cleansed, flags=re.IGNORECASE)
                if count > 0:
                    changes.append(f"Eliminado cliché o reemplazado término: '{pattern}'")

        # Replace excessive em-dashes with commas or periods
        if "—" in cleansed:
            cleansed = cleansed.replace(" — ", ", ").replace("—", ", ")
            changes.append("Normalizados guiones largos (—) a puntuación natural.")

        # Re-score after cleansing
        re_audit = self.deslop_text(cleansed)

        return {
            "original_length": len(original),
            "cleansed_length": len(cleansed),
            "changes_made": len(changes),
            "change_log": changes,
            "new_score": re_audit["score"],
            "new_human_score": re_audit["human_score"],
            "cleansed_text": cleansed.strip()
        }

    def format_deslop_report(self, res: Dict[str, Any]) -> str:
        """Formats the Deslop audit report for Señor Santiago."""
        score = res.get("score", 0.0)
        pct = res.get("human_percentage", 0)
        total = res.get("total_violations", 0)
        target = res.get("target", "Documento")

        status_badge = "🟢 TEXTO HUMANO AUTÉNTICO" if score >= 4.5 else ("🟡 TEXTO CON HUELLAS DE IA" if score >= 3.0 else "🔴 TEXTO ALTAMENTE ROBÓTICO (SLOP)")

        lines = [
            f"### 🧽 Análisis Anti-Slop de Redacción AI (SlopMonster)",
            f"- **Objetivo Evaluado**: `{target}`",
            f"- **Puntuación de Humanidad**: **{score:.1f} / 5.0** (`{pct}%`)",
            f"- **Diagnóstico**: **{status_badge}**",
            f"- **Categorías con Tell de IA**: {', '.join(res.get('failed_categories', [])) or 'Ninguna (Limpio)'}",
            f"- **Total de Patrones Detectados**: `{total}`",
            ""
        ]

        if res.get("is_clean"):
            lines.append("🎉 **¡Redacción Impecable!** El texto suena natural, directo y libre de la verborrea característica de los modelos de lenguaje.")
            return "\n".join(lines)

        lines.append("#### 🔍 Patrones y Frases de IA Encontrados:")
        for idx, f in enumerate(res.get("findings", [])[:12], start=1):
            lines.append(f"**{idx}. [{f['category']}] Línea {f['line']}**")
            lines.append(f"> **Detectado**: `{f['match']}`")
            lines.append(f"> **Contexto**: *\"{f['context']}\"*")
            lines.append(f"> **Recomendación**: {f['fix']}\n")

        lines.append("> **💡 Consejo**: Puede pedirme *'humaniza este texto'* o *'deslop este archivo'* para reescribirlo automáticamente eliminando todos los clichés.")
        return "\n".join(lines)

    def format_humanize_report(self, res: Dict[str, Any]) -> str:
        """Formats the humanized rewrite output."""
        lines = [
            f"### ✨ Texto Humanizado (De-slopped por SlopMonster)",
            f"- **Nueva Calificación Humana**: `{res.get('new_human_score')}`",
            f"- **Ajustes Realizados**: `{res.get('changes_made')}` mejoras editoriales",
            "",
            "#### 📝 Versión Limpia y Ejecutiva:",
            "```text",
            res.get("cleansed_text", ""),
            "```",
            ""
        ]
        if res.get("change_log"):
            lines.append("#### 🛠️ Resumen de Correcciones Aplicadas:")
            for ch in res["change_log"][:6]:
                lines.append(f"- {ch}")

        return "\n".join(lines)

    def get_status(self) -> Dict[str, Any]:
        """Returns the status of the SlopMonster service."""
        return {
            "engine": "SlopMonster & Deslop Engine (v1.0)",
            "languages_supported": ["Español", "English"],
            "categories_evaluated": [
                "1. Vocabulario Artificial (Pompous Buzzwords)",
                "2. Patrones de Oración y Fórmulas Cliché ('No solo X, sino Y')",
                "3. Puntuación Forzada (Abuso de guiones em-dash)",
                "4. Ritmo y Tríadas de Adjetivos Vacíos",
                "5. Conclusiones Escolares y Afirmaciones sin Evidencia"
            ],
            "skills_path": str(self._skills_dir)
        }

    def format_status_report(self, st: Dict[str, Any]) -> str:
        """Formats the SlopMonster status report."""
        cats = "\n".join([f"  - {c}" for c in st.get("categories_evaluated", [])])
        return (
            "### 🧽 Motor Anti-Slop y Humanizador de Textos (SlopMonster)\n"
            f"- **Versión**: {st.get('engine')}\n"
            f"- **Idiomas Soportados**: {', '.join(st.get('languages_supported', []))}\n"
            f"- **Categorías Evaluadas**:\n{cats}\n"
            f"- **Directorio de Habilidad**: `{st.get('skills_path')}`\n\n"
            "El sistema está listo para auditar y transformar cualquier ensayo, correo, informe universitario o propuesta en texto humano, directo y convincente, señor Santiago."
        )


# Global Singleton Instance
slopmonster_service = SlopMonsterService()
