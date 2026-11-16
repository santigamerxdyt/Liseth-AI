# LISETH AI — Copiloto Autónomo, Plataforma SaaS & Asistente Personal Ejecutivo v3.0
> **Exclusivo para Señor Santiago Huérfano López (Superadmin CREATOR)**  
> Plataforma de inteligencia artificial multi-inquilino de escritorio y web, con arquitectura de voz única colombiana (`es-CO-SalomeNeural`), integración de Bóveda Obsidian, orquestación Hermes AI, vinculación soberana a Google Firebase, verificación de identidad en inicio (2FA) y optimización ergonómica completa para smartphones.

---

## 🌟 Visión General

**Liseth AI** es un ecosistema autónomo de inteligencia artificial desarrollado en **Python 3.10+** (con backend de alto rendimiento **FastAPI** / **Uvicorn** y frontend interactivo de escritorio / web). Integra arquitecturas multi-cerebro (**Google Gemini 3.5**, **Anthropic Claude 3.5**, **Groq LLaMA 3.3**, **OpenAI GPT-4o**), síntesis de voz neuronal oficial en tiempo real, 48 módulos tácticos HUD y un vault estructurado de conocimiento compatible con Obsidian.

Para una guía detallada de todas las capacidades, consulte los documentos oficiales:
- 📄 **[`Manual_Liseth.pdf`](Manual_Liseth.pdf)** — Manual Ejecutivo Integral (43 secciones, recompilado dinámicamente).
- 📘 **[`GUIA_USO_LISEHT.md`](GUIA_USO_LISEHT.md)** — Guía Rápida de Operación, Voz y Despliegue Móvil.
- 🏛️ **[`Knowledge/00 - HOME/PROJECT COMMAND CENTER.md`](Knowledge/00%20-%20HOME/PROJECT%20COMMAND%20CENTER.md)** — Centro de Mando del Vault Obsidian.

---

## 🚀 Capacidades y Módulos Principales del Sistema

| Módulo / Subsistema | Motor / Componente | Descripción Operativa |
|---|---|---|
| **1. Arquitectura de Voz Única Oficial** | `app/services/audio_manager.py` | Voz oficial inmutable `es-CO-SalomeNeural` (Microsoft Edge-TTS en español colombiano) con Mutex singleton, deduplicación de audio y neutralización de motores redundantes. |
| **2. Control Central de Micrófono** | `app/services/microphone_manager.py` | Posesión exclusiva del hardware de audio (`sounddevice`), prevención de colisiones de captura y supresión de eco acústico. |
| **3. Orquestación Silenciosa Hermes AI** | `app/services/hermes_orchestrator.py` | Integración del orquestador NousResearch Hermes Agent y sus 8 Named Bots; razonan en segundo plano en silencio y canalizan la respuesta hablada por Liseth. |
| **4. Seguridad de Inicio (Launch Code 2FA)** | `app/routers/auth_router.py` | Verificación de identidad obligatoria al iniciar la app o web. Valida contra PIN maestro (Señor Santiago) o código de seguridad personal (usuarios). |
| **5. Plataforma SaaS & Firebase Soberano** | `app/services/saas_service.py` | Multi-inquilino comercial vinculado a Google Firebase (`liseth-saas-ai`). Usuarios colocan sus propias API Keys de IA y adquieren planes activos. |
| **6. Pasarelas de Pago Múltiples** | `app/routers/saas_router.py` | Checkout integrado para Colombia e internacional (Stripe, Wompi, Bold, Nequi, Daviplata, PSE, Cripto) con libro mayor de créditos inmutable. |
| **7. Optimización Móvil Ergonómica** | `index.html` & `app/static/` | Viewport dinámico (`interactive-widget=resizes-content`), prevención de auto-zoom en iOS Safari (`font-size: 16px !important;`), touch targets de 44px y layout vertical. |
| **8. Bóveda de Conocimiento Obsidian** | `Knowledge/` & `.obsidian/` | Vault inteligente con MOCs de Arquitectura, IA, Monetización y Seguridad. Protocolo de contexto progresivo de 5 niveles para Antigravity. |
| **9. Automatización de Windows y PC** | `app/actions/computer_*.py` | Control de volumen, brillo, teclado, ratón, ventanas y atajos con 0 ms de latencia y autoelevación UAC a Administrador. |
| **10. Cerebros en Cascada y Auto-Heal** | `app/services/brain_router.py` | Conmutación instantánea ante cuotas agotadas: Gemini 3.5 -> Claude 3.5 -> Groq LLaMA 3.3 -> OpenAI GPT-4o. |
| **11. Ecosistema NFC y Pagos por Contacto** | `app/routers/nfc_router.py` | Emisión de tarjetas virtuales vCard, lectura de credenciales y simulación de transacciones sin contacto. |
| **12. Auditoría Integral SAST & Ciberseguridad**| `app/services/security_audit_service.py` | Análisis de vulnerabilidades OWASP Top 10, CWE Top 25, prevención de inyecciones y control estricto de roles (RBAC). |

---

## 📱 Experiencia en Dispositivos Móviles (Celulares)

Liseth puede ser utilizada directamente desde cualquier teléfono inteligente (iPhone o Android):
1. Inicie Liseth en su computadora mediante `iniciar_liseth.bat` o `INICIAR_WEB.bat`.
2. En el navegador del celular (Safari / Chrome), abra la dirección de red local de la PC (ejemplo: `http://192.168.1.15:3000`).
3. La interfaz se adaptará automáticamente a una sola columna vertical con botones de fácil pulsación (touch targets >= 44px), sin auto-zoom en campos de texto y con desbloqueo proactivo de audio.

---

## 🛠️ Instalación y Puesta en Marcha

### 1. Requisitos Previos
- **Sistema Operativo:** Windows 10 u 11 (64-bit).
- **Python:** Versión 3.10 o superior (recomendado Python 3.12+ o 3.14).
- **Git:** Para clonar el repositorio.

### 2. Clonar el Repositorio
```bash
git clone https://github.com/santigamerxdyt/Liseth-AI.git
cd Liseth-AI
```

### 3. Crear el Entorno Virtual e Instalar Dependencias
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Copie el archivo de plantilla `.env.example` a `.env`:
```bash
copy .env.example .env
```
Abra `.env` y agregue su clave de Google Gemini (`GEMINI_API_KEY`), el PIN de acceso maestro (`JARVIS_ACCESS_PIN`) y opcionalmente las claves de Anthropic, Groq u OpenAI.

### 5. Iniciar la Aplicación
Liseth incluye lanzadores rápidos con autoelevación de privilegios de Administrador:

- **Modo Escritorio (Ventana Nativa con voz y hardware):**
  ```bash
  iniciar_liseth.bat
  ```
  *o alternativamente:*
  ```bash
  INICIAR_ESCRITORIO.bat
  ```

- **Modo Servidor Web (Dashboard navegador en http://localhost:3000):**
  ```bash
  INICIAR_WEB.bat
  ```

- **Ejecución directa por comando:**
  ```bash
  python desktop_app.py
  ```

---

## 🧪 Pruebas Unitarias y Calidad de Código

El repositorio cuenta con una suite completa de pruebas automatizadas con cobertura total:

```bash
python -m pytest test/ -v
```

Todas las pruebas pasan al 100%:
- `test_single_voice_architecture.py` (Arquitectura de voz única, mutex singleton, supresión de duplicaciones y sincronización Hermes).
- `test_mobile_and_launch_auth.py` (Código de verificación 2FA, inicio obligatorio en app/web y salvaguardas móviles).
- `test_saas_platform.py` (Multi-inquilino, aislamiento de datos, planes, pasarelas de pago y vinculación Firebase).
- `test_user_brain_keys.py` (Almacenamiento cifrado de API keys propias de usuarios).
- `test_manual_pdf.py` (Generación dinámica del manual PDF ejecutivo de 43 secciones).

---

## 📄 Licencia y Propiedad

© 2026 **Santiago Huérfano López**. Todos los derechos reservados.  
Propiedad intelectual y tecnológica protegida bajo los términos de `LEGAL_TERMS_AND_COPYRIGHT.md`.


## Modo de uso libre

Activado por solicitud del propietario. `access-mode.js` es el interruptor compartido
por las interfaces y los servidores Python y Node: `freeAccess: true` permite usar
el asistente sin cuenta, inicio de sesi?n ni compra de planes. El portal SaaS,
los registros (incluido Firebase), pagos, recargas, referidos y webhooks comerciales
quedan deshabilitados. No se crean cuentas ni se eliminan datos existentes.
Las herramientas de an?lisis financiero del asistente siguen disponibles.

Las operaciones administrativas del servidor Python conservan la protecci?n para
accesos remotos; el uso local no requiere PIN. Las claves y los costes propios de
los proveedores de IA siguen dependiendo de la configuraci?n del propietario.

Mantener este modo hasta que el propietario solicite reactivarlo. Para reactivar,
cambiar `true` a `false` en `access-mode.js`, reiniciar el servidor y recargar la
interfaz. Reiniciar y recargar tambi?n es necesario al activar el modo libre.
