---
type: moc
status: active
priority: critical
created: 2026-11-15
updated: 2026-11-15
author: 'Senior Full Stack Lead'
tags:
  - moc
  - development
  - codebase
  - tests
  - git
verified: true
---

# 💻 DEVELOPMENT AND CODEBASE MAP (MOC)

> **PROPÓSITO:** Mapa completo de la estructura del código fuente, directrices de ingeniería, convenciones de nomenclatura, organización de pruebas y flujos de integración continua.

---

## 📁 MAPA DEL ÁRBOL DEL PROYECTO

```
c:/Users/Usuario/Desktop/MI LISEHT
├── .obsidian/               <- Configuración y plugins del Vault de Obsidian
├── app/                     <- Núcleo del Backend FastAPI
│   ├── core/                <- Configuración, autenticación, seguridad y hashing
│   ├── database/            <- Conexión SQLAlchemy asíncrona, migraciones y WAL
│   ├── models/              <- Modelos ORM (saas.py, brain.py, users.py)
│   ├── routers/             <- Controladores de rutas REST (auth, saas, brain, nfc)
│   ├── schemas/             <- Esquemas Pydantic V2 de validación de entrada/salida
│   ├── services/            <- Lógica de negocio (saas_service, brain_service, etc.)
│   └── static/              <- Assets frontend desplegados
├── core/                    <- Módulos legacy de utilidades y orquestación
├── data/                    <- Bases de datos locales SQLite (app.db) y ChromaDB
├── Knowledge/               <- VAULT MAESTRO DE CONOCIMIENTO (26 carpetas especializadas)
│   ├── 00 - HOME/           <- PROJECT COMMAND CENTER.md
│   ├── 01 a 25/             <- Dominios técnicos del sistema
│   └── 99 - TEMPLATES/      <- Plantillas YAML reutilizables
├── test/                    <- Suite automatizada de pruebas con Pytest (438 tests)
│   ├── test_saas_features.py<- Pruebas de suscripciones, BOLA, créditos y gates
│   ├── test_auth.py         <- Pruebas de hashing, tokens, rate limits
│   └── test_brain.py        <- Pruebas de cascada multi-cerebro y memoria
├── index.html               <- Cyber-HUD Frontend Principal (Three.js WebGL AI Orb)
├── jarvis.html              <- Réplica exacta con paridad SHA-256
├── package.json             <- Dependencias de herramientas y plugins frontend
├── requirements.txt         <- Dependencias Python de backend (FastAPI, SQLAlchemy, etc.)
└── pytest.ini               <- Configuración del motor de pruebas
```

---

## 🧪 SUITE DE PRUEBAS AUTOMATIZADAS (438 TESTS PASSED)

El proyecto cuenta con una cobertura integral de pruebas que valida:
- **Cero Regresiones:** Ningún cambio de código es aceptado si reduce el recuento de 438 tests aprobados.
- **Aislamiento Multi-Tenant:** Verificación explícita de ataques BOLA donde un usuario intenta acceder a recursos de otro.
- **Transaccionalidad Financiera:** Validación de integridad en cobros, ledger contable y mitigación de condiciones de carrera (Race Conditions).
- **Protección del Onboarding Gate:** Comprobación de que usuarios sin cuenta Firebase o sin plan pagado sean interceptados antes de interactuar con el sistema.

Para ejecutar la suite completa en la terminal de Antigravity:
```powershell
python -m pytest test/ -q
# Salida esperada: 438 passed in ~45-50s
```

Ver [[test_suite_overview]] y [[security_test_matrix]].

---

## 📜 CONVENCIONES DE CÓDIGO
- **Python Backend:** Cumplimiento de PEP 8, tipado estricto con `typing`, modelos asíncronos (`async`/`await`) con SQLAlchemy 2.0 y validaciones declarativas con Pydantic V2.
- **Frontend:** Vanilla JavaScript modular y eficiente sin frameworks pesados, minimizando re-renders en el canvas de Three.js para sostener 60 FPS estables.
- **Documentación Obsidian:** Cada nuevo módulo debe crearse a partir de las plantillas en `Knowledge/99 - TEMPLATES/` con metadatos YAML obligatorios.
