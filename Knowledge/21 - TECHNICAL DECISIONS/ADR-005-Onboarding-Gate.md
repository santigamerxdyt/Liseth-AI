---
type: adr
status: approved
priority: critical
created: 2026-11-12
updated: 2026-11-15
author: 'Software Architect & SaaS Lead'
tags:
  - adr
  - onboarding
  - security
  - saas
verified: true
---

# 🏛️ ADR-005: Puerta Obligatoria de Activación (Firebase + API Key + Plan Pagado)

## Estado
**APROBADO E IMPLEMENTADO**

## Contexto y Problema
El Señor Santiago requirió explícitamente que la plataforma sea un producto comercial sostenible. Se identificó el riesgo de que usuarios creen cuentas vacías y consuman recursos del servidor, o naveguen por la aplicación sin haber vinculado su cuenta en Firebase, sin haber suministrado su propia API Key de cerebros y sin haber contratado un plan comercial.

## Alternativas Evaluadas
1. **Acceso Libre Inicial (Freemium no restringido):** Alto consumo de infraestructura por usuarios no monetizables.
2. **Onboarding Guiado No Bloqueante:** Los usuarios pueden cerrar el modal y utilizar la interfaz sin completar los requisitos.
3. **Onboarding Gate Estricto y Hermético:** La interfaz bloquea el cierre del modal de bienvenida/planes y el backend rechaza peticiones a los endpoints cognitivos hasta que el usuario cumpla los 3 requisitos:
   - Crear / enlazar cuenta en Google Firebase.
   - Guardar su API Key de IA cifrada.
   - Activar un plan de pago o suscripción formal.

## Decisión Tomada
Se implementó el **Onboarding Gate Guard** en dos capas:
1. **Frontend:** El modal ciberpunk de planes (`saas-pricing-modal`) no puede cerrarse mediante clics fuera del contenedor ni con la tecla Escape si `has_completed_onboarding == false`.
2. **Backend:** El endpoint `/api/brain/chat` y los módulos HUD validan el estado de activación del tenant. Los administradores no-creators tienen denegado modificar las reglas de Firebase.

## Justificación
Cumple 100% con la directiva de negocio del Señor Santiago: rentabilidad directa, costo de inferencia cubierto por el usuario y control centralizado del creador.

## Consecuencias y Verificación
- **Validación:** Validado en el flujo completo del Cyber-HUD y cubierto por las pruebas de integración.
- **Archivo Fuente:** [app/routers/saas_router.py](file:///c:/Users/Usuario/Desktop/MI%20LISEHT/app/routers/saas_router.py) y [index.html](file:///c:/Users/Usuario/Desktop/MI%20LISEHT/index.html)
