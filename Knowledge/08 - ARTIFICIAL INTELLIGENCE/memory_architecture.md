---
type: ai-doc
status: implemented
priority: high
created: 2026-11-15
updated: 2026-11-15
author: 'AI Architect'
source_paths:
  - core/chroma_memory.py
tags:
  - ai
  - memory
  - chromadb
  - embeddings
verified: true
---

# 🧠 MEMORY ARCHITECTURE // MEMORIA SEMÁNTICA VECTORIAL CON CHROMADB

## 📐 Estrategia de Persistencia de Contexto
- **Memoria a Corto Plazo:** Los últimos 6 mensajes conversacionales cargados directamente desde SQLite en cada turno.
- **Memoria a Largo Plazo (Semántica):** Base de datos vectorial local con ChromaDB ubicada en `data/chroma/`. Indexa conocimientos previos, preferencias del Señor Santiago y fragmentos clave de conversaciones anteriores con embeddings normalizados.
- **Aislamiento por Tenant:** Cada colección en ChromaDB está acoplada al `user_id` impidiendo la mezcla de memorias entre usuarios.
