# 👑 GUÍA MAESTRA DE LISETH • ASISTENTE PERSONAL & COPILOTO EJECUTIVO
**Para: Señor Santiago Huérfano López (Superadmin CREATOR)**

Liseth ha sido consolidada con una arquitectura de **Voz Única Oficial (Salomé es-CO)**, orquestación silenciosa **Hermes AI**, integración de **Bóveda de Conocimiento Obsidian (Vault Engine)**, plataforma comercial **SaaS Multi-Tenant** vinculada a Google Firebase (`liseth-saas-ai`), **Código de Verificación de Inicio (2FA)** obligatorio y optimización responsiva completa para teléfonos móviles.

---

## 🎙️ 1. ARQUITECTURA DE VOZ ÚNICA OFICIAL (`es-CO-SalomeNeural`)

Para garantizar una experiencia auditiva pura y sin interferencias:
- **Identidad Vocal Inmutable:** Liseth cuenta con una **sola voz oficial**: `es-CO-SalomeNeural` (Microsoft Edge-TTS en español colombiano), dulce, cálida, respetuosa y con acústica de alta fidelidad.
- **Controlador Centralizado de Audio (`LisethAudioManager`):** Singleton con bloqueo de canal por Mutex. Serializa todas las locuciones y aplica deduplicación por hash en ventana de 2.0 segundos para impedir repeticiones o ecos.
- **Eliminación de Motores Duplicados:** Se han neutralizado y eliminado las rutas secundarias del navegador (`window.speechSynthesis` y Windows SAPI) para que nunca hablen dos voces al mismo tiempo.
- **Hermes AI Silencioso:** El orquestador NousResearch Hermes Agent y sus 8 Named Bots razonan en segundo plano en silencio absoluto; delegan la síntesis vocal exclusivamente a Liseth.
- **Interrupción Instantánea (Barge-In < 40ms):** Puedes interrumpir a Liseth en cualquier momento diciendo *"Liseth para"* o *"espera"*; el canal se libera al instante.

---

## 🛡️ 2. CÓDIGO DE VERIFICACIÓN DE INICIO & ACCESO OBLIGATORIO

Para garantizar que nadie ajeno acceda a Liseth:
- **Verificación en App y Web:** Siempre que abras la aplicación de escritorio (`desktop_app.py` / `iniciar_liseth.bat`) o la interfaz web, el sistema solicitará formalmente tu inicio de sesión y tu código de verificación.
- **Código de Verificación de Inicio (`launch_code`):**
  - **Para el Señor Santiago (Creador):** Ingresa tu PIN maestro (`JARVIS_ACCESS_PIN` en `.env`), validado criptográficamente en tiempo constante.
  - **Para usuarios registrados:** Ingresan su correo, contraseña y el código de seguridad personal configurado al crear su cuenta.
- **Sin Auto-Bypass:** La sesión se bloquea al iniciar o recargar la página hasta validar credenciales y código de verificación.

---

## 📱 3. EXPERIENCIA MÓVIL EN CELULARES (SMARTPHONES)

Liseth está completamente optimizada para iPhone (iOS Safari) y Android (Chrome):
- **Cero Zoom Molesto en iOS:** Todos los campos de texto e inputs tienen `font-size: 16px !important;`, evitando el auto-zoom de pantalla al tocar para escribir.
- **Layout Adaptable de 1 Columna:** Las tarjetas de planes y los modales se organizan verticalmente en pantallas de 320px a 480px, sin desbordamiento horizontal.
- **Touch Targets de 44px:** Botones, pestañas y controles cumplen con el estándar táctil ergonómico de Apple y Google.
- **Desbloqueo de Audio:** El motor de audio se desbloquea proactivamente en el primer toque de pantalla (`touchstart`).
- **Permisos de Micrófono:** En celulares, el micrófono requiere conexión HTTPS o localhost por seguridad del navegador; si se accede por HTTP en red local, el sistema te lo indica amigablemente permitiéndote chatear por texto sin cuelgues.

---

## 🧠 4. BÓVEDA DE CONOCIMIENTO OBSIDIAN (VAULT ENGINE)

La carpeta raíz del proyecto funciona como un Vault Inteligente para Obsidian:
- **Centro de Mando:** [`Knowledge/00 - HOME/PROJECT COMMAND CENTER.md`](Knowledge/00%20-%20HOME/PROJECT%20COMMAND%20CENTER.md) enlaza toda la arquitectura técnica, modelos de IA, monetización, seguridad y tareas pendientes.
- **Mapas de Contenido (MOCs):** 
  - `PROJECT ARCHITECTURE MAP`
  - `AI ECOSYSTEM MAP`
  - `BUSINESS AND REVENUE MAP`
  - `SECURITY AND PRIVACY MAP`
- **Contexto Progresivo:** Antigravity consulta únicamente los documentos necesarios (Nivel 1 al 5), ahorrando tokens y acelerando las respuestas.

---

## 💎 5. PLATAFORMA SAAS & VINCULACIÓN CON GOOGLE FIREBASE

- **Proyecto Firebase Oficial:** Todas las cuentas se vinculan al Google Firebase del Señor Santiago (`liseth-saas-ai`, #353398586852).
- **Control Soberano CREATOR:** Solo el Señor Santiago puede editar la configuración del proyecto Firebase usando su PIN de Creador.
- **Cerebros de IA Propios:** Cada usuario debe ingresar su propia API Key de Google Gemini, Groq, OpenAI o Claude al crear su cuenta, garantizando autosuficiencia y rentabilidad sin costes de inferencia para el Creador.
- **Planes Comerciales:** STARTER ($10 USD / mes), PRO ($25 USD / mes), BUSINESS ($50 USD / mes) y ENTERPRISE ($150 USD / mes) con soporte de pagos múltiples (Stripe, Wompi, Bold, Nequi, Daviplata, PSE).

---

## 💾 6. CÓMO INICIAR A LISETH CON UN CLIC

1. **Aplicación Nativa de Escritorio:**
   - Haz doble clic en **`iniciar_liseth.bat`** o **`INICIAR_ESCRITORIO.bat`**.
   - Se abrirá la ventana de escritorio con aceleración gráfica, micrófono en segundo plano y voz oficial Salomé.
2. **Acceso Web Local:**
   - Haz doble clic en **`INICIAR_WEB.bat`** o corre `python run.py`.
   - Abre tu navegador en **`http://localhost:3000`**.
3. **Acceso desde Celular (Misma Red Wi-Fi):**
   - En el navegador de tu teléfono ingresa la IP local de tu PC (ejemplo: `http://192.168.1.10:3000`).

---

## 📄 7. MANUAL EJECUTIVO COMPLETO EN PDF

Para consultar la referencia técnica detallada con los 48 módulos tácticos, matrices financieras, auditorías y atajos:
- 📄 **[`Manual_Liseth.pdf`](Manual_Liseth.pdf)** *(Recompilado dinámicamente con `python tools/generate_manual_pdf.py`)*.

---
*Liseth AI • Asistente Personal Ejecutivo y Plataforma SaaS de Santiago Huérfano López.*
