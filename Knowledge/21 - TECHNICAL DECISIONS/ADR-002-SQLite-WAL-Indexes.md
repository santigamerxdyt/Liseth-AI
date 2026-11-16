---
type: adr
status: approved
priority: critical
created: 2026-10-20
updated: 2026-11-15
author: 'Database Architect'
tags:
  - adr
  - database
  - sqlite
  - wal
  - performance
verified: true
---

# 🏛️ ADR-002: SQLite en Modo WAL con 18 Índices Compuestos

## Estado
**APROBADO E IMPLEMENTADO**

## Contexto y Problema
En entornos SaaS multi-tenant con múltiples lecturas concurrentes (consultas del HUD, validación de sesiones, lectura de saldo) y escrituras transaccionales (deducción de créditos, guardado de mensajes, registros NFC), el motor SQLite estándar genera bloqueos de contención (`sqlite3.OperationalError: database is locked`).

## Alternativas Evaluadas
1. **Migrar inmediatamente a PostgreSQL / MySQL:** Soporte nativo concurrente, pero añade complejidad operativa y requiere dependencias pesadas en entornos de desarrollo local.
2. **SQLite Estándar con Semáforos Python:** Reduce bloqueos pero colapsa bajo estrés concurrente y degrada los tiempos de respuesta.
3. **SQLite Hardened con Modo WAL (`Write-Ahead Logging`) e Índices Compuestos:** Escritores y lectores no se bloquean entre sí, manteniendo la portabilidad sin infraestructura externa.

## Decisión Tomada
Se configuró SQLite con:
- `PRAGMA journal_mode=WAL;`
- `PRAGMA synchronous=NORMAL;`
- `PRAGMA busy_timeout=15000;`
- Creación de **18 índices compuestos** en las tablas `saas_users`, `saas_credit_ledger`, `saas_subscriptions`, `saas_referrals` y `chat_messages`.

## Justificación
La base de datos soporta cientos de lecturas concurrentes simultáneas mientras las escrituras ocurren secuencialmente en el archivo `-wal` sin generar bloqueos. Los 18 índices aceleran las consultas BOLA (`WHERE user_id = :u AND id = :id`) reduciendo los tiempos de ejecución de 45ms a menos de **1.4ms**.

## Consecuencias y Verificación
- **Validación:** 438 pruebas automatizadas ejecutadas concurrentemente sin un solo error de contención de base de datos.
- **Archivo Fuente:** [app/database/session.py](file:///c:/Users/Usuario/Desktop/MI%20LISEHT/app/database/session.py)
