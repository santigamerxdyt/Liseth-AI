---
type: overview
status: active
priority: critical
created: 2026-11-15
updated: 2026-11-15
author: 'Software Architect'
tags:
  - tech-stack
  - inventory
  - dependencies
verified: true
---

# 🛠️ INVENTARIO MAESTRO DEL STACK TECNOLÓGICO

| Capa Tecnológica | Tecnología / Herramienta | Versión / Especificación | Propósito en el Proyecto |
| :--- | :--- | :--- | :--- |
| **Backend Core** | Python + FastAPI | 3.12+ / FastAPI 0.115+ | Framework asíncrono para endpoints REST, WebSocket y seguridad. |
| **Servidor ASGI** | Uvicorn | Standard Worker | Servidor HTTP de alto rendimiento para FastAPI. |
| **Persistencia ORM** | SQLAlchemy + aiosqlite | SQLAlchemy 2.0 Async | Acceso concurrente no bloqueante a la base de datos relacional. |
| **Motor de Base de Datos**| SQLite 3 (Modo WAL) | WAL Mode + PRAGMAs | Almacenamiento local ultrarrápido con 18 índices compuestos. |
| **Base de Datos Vectorial**| ChromaDB | Local Vector Store | Memoria semántica a largo plazo y recuperación RAG de conversaciones. |
| **Criptografía** | Cryptography / hashlib | AES-256-GCM / PBKDF2 / scrypt | Hashing de credenciales y cifrado simétrico autenticado de API keys. |
| **Frontend UI/UX** | Vanilla JS (ES2024) + CSS3| Cyberpunk HUD | Interfaz gráfica futurista, reactiva y sin frameworks pesados. |
| **Renderizado 3D** | Three.js WebGL | r128 | Esfera holográfica de partículas que reacciona a la voz y a la IA. |
| **Hardware Contactless** | W3C Web NFC API | `window.NDEFReader` | Lectura y escritura de tarjetas NFC físicas a 13.56 MHz. |
| **Suite de Pruebas** | Pytest + pytest-asyncio | 8.0+ | 438 pruebas unitarias, de integración y de ciberseguridad. |
