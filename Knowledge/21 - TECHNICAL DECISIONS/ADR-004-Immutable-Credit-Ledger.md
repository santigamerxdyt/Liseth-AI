---
type: adr
status: approved
priority: critical
created: 2026-11-05
updated: 2026-11-15
author: 'Financial Systems Lead'
tags:
  - adr
  - monetization
  - ledger
  - immutability
verified: true
---

# 🏛️ ADR-004: Libro Mayor Inmutable de Doble Entrada (SaasCreditLedger)

## Estado
**APROBADO E IMPLEMENTADO**

## Contexto y Problema
Modificar directamente la columna `credits` en la tabla de usuarios sin un historial auditable provoca discrepancias financieras, condiciones de carrera (race conditions), imposibilidad de detectar fraudes en reembolsos y falta de trazabilidad en las comisiones de referidos.

## Alternativas Evaluadas
1. **Saldo Simple Mutable (`UPDATE saas_users SET credits = credits - X`):** Propenso a inconsistencias y no auditable.
2. **Tabla de Logs No Transaccional:** Registra eventos pero no garantiza consistencia matemática.
3. **Libro Mayor Inmutable de Doble Entrada (`SaasCreditLedger`):** Cada adición, deducción, pago, transferencia NFC o comisión se almacena como una fila inmutable con `delta`, `balance_after`, `reason` y metadatos JSON.

## Decisión Tomada
Se creó el modelo `SaasCreditLedger`. El saldo del usuario es la suma histórica verificable de sus movimientos y cada operación actualiza el saldo de forma atómica dentro de una transacción asíncrona de base de datos.
- Prohibición estricta de sentencias `DELETE` o `UPDATE` sobre la tabla `saas_credit_ledger`.

## Justificación
Garantiza auditoría financiera absoluta, soporte para disputas de pagos en pasarelas (Stripe/Bre-B/Nequi) y previene la duplicación de recompensas de referidos.

## Consecuencias y Verificación
- **Validación:** Probado en `test_ledger_immutability` y verificado en la suite completa.
- **Archivo Fuente:** [app/models/saas.py](file:///c:/Users/Usuario/Desktop/MI%20LISEHT/app/models/saas.py)
