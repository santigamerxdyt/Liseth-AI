# LISEHT AI — Copiloto Autónomo y Asistente Personal Ejecutivo v2.0
> **Exclusivo para Señor Santiago**  
> Asistente de inteligencia artificial de escritorio y web, autónomo, con síntesis de voz colombiana de alta fidelidad, automatización total de Windows, ciberseguridad, navegación web y herramientas ejecutivas/universitarias.

---

## 🌟 Visión General

**Liseth AI** es un sistema autónomo de asistencia personal y copiloto de ingeniería desarrollado en **Python 3.10+** (con backend de alto rendimiento **FastAPI** / **Uvicorn** y frontend interactivo de escritorio / web). Integra arquitecturas multi-cerebro (**Google Gemini 3.5**, **Anthropic Claude 3.5**, **Groq LLaMA 3.3**), síntesis de voz neuronal en tiempo real (Edge-TTS Salomé es-CO) y más de 30 módulos de hardware, investigación, automatización y ciberseguridad.

Para una guía detallada de todas las capacidades, consulte el documento oficial:  
📄 **[`Manual_Liseth.pdf`](Manual_Liseth.pdf)** *(Recompilado dinámicamente con cada versión)*.

---

## 🚀 Capacidades y Módulos del Sistema

| Módulo | Motor / Servicio | Descripción Operativa |
|---|---|---|
| **1. Identidad y Privilegios** | `app/core/admin.py` | Autoelevación UAC a Administrador de Windows con acceso irrestricto al sistema. |
| **2. Automatización Windows** | `app/actions/computer_*.py` | Control de volumen, brillo, teclado, ratón, ventanas y atajos con 0 ms de latencia. |
| **3. Síntesis y Reconocimiento de Voz** | `app/services/voice_engine.py` | Voz colombiana natural (Salomé es-CO), modo reposo (Standby) y conversación fluida continua. |
| **4. Cerebro Dual y Respaldo** | `app/services/brain_router.py` | Gemini 3.5 Flash como cerebro primario con failover automático a Claude/Groq ante límites de cuota. |
| **5. Rutinas y Tareas en Segundo Plano** | `app/services/routine_engine.py` | Ejecución de rutinas programadas (matutina, nocturna, estudio, respaldo de datos). |
| **6. Centinela de Recursos y Memoria** | `app/services/workspace_sentinel.py` | Monitoreo en segundo plano de RAM, CPU, disco y procesos zombi con optimización proactiva. |
| **7. Resumen Diario Ejecutivo (Debrief)** | `app/services/daily_debrief_service.py` | Síntesis nocturna de compromisos cumplidos, tareas pendientes y resumen de productividad. |
| **8. Finanzas y Administración** | `app/actions/business_finance.py` | Cálculo de VAN/NPV, TIR/IRR, Payback, ROI, WACC, Punto de Equilibrio y Matrices FODA/Canvas/PESTEL. |
| **9. Asistente Académico Universitario** | `app/actions/academic_helper.py` | Citas y referencias en Normas APA 7ª Edición y esquemas de redacción para ensayos y tesis. |
| **10. Ingeniería Inversa de Binarios** | `app/services/reverse_engineering_service.py` | Motor REA (v6.7.0): inspección de PE/ELF, entropía de Shannon, mitigaciones (ASLR/DEP), cadenas y desempaque ASAR. |
| **11. Navegación Web Acelerada** | `app/services/ego_browser_service.py` | Motor Ego Lite: taskSpaces aislados en segundo plano, snapshots semánticos ultraligeros y control sin selectores CSS frágiles. |
| **12. Despliegue en la Nube y Frontend** | `app/services/vercel_skills_service.py` | Vercel Labs Suite: despliegue instantáneo a vista previa/producción, auditoría de 45+ reglas React y directrices de UI. |
| **13. Auditoría de Ciberseguridad** | `app/services/security_audit_service.py` | Análisis estático SAST (OWASP Top 10, CWE Top 25, fugas de secretos/API keys, inyecciones SQL/OS y Prompt Injection en LLMs). |
| **14. Detector y Humanizador de Textos** | `app/services/slopmonster_service.py` | Motor SlopMonster: detección de clichés sintéticos de IA en español e inglés y reescritura en prosa ejecutiva natural. |

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
Abra `.env` y agregue su clave de Google Gemini (`GEMINI_API_KEY`) y opcionalmente las claves de Anthropic, Telegram o Groq.

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
  python run.py
  ```

---

## 🧪 Pruebas Unitarias y Calidad de Código

El repositorio cuenta con una suite completa de pruebas automatizadas con cobertura total:

```bash
python -m pytest test/ -v
```

Todas las pruebas pasan al 100%:
- `test_security_audit.py` (Vulnerabilidades SAST, CWE y fugas de credenciales).
- `test_slopmonster.py` (Detección de patrones de IA y humanizador de texto).
- `test_all_actions_and_intents.py` (Enrutamiento con 0 ms de latencia y herramientas de sistema).
- `test_vercel_skills.py` (Despliegues y auditoría de código frontend).
- `test_reverse_engineering.py` (Inspección binaria y cálculo de entropía).
- `test_ego_browser.py` (Navegación web en segundo plano).
- `test_phase1` a `test_phase4` (Workers, Centinela, Rutinas y Debriefing).

---

## 🔒 Privacidad y Seguridad

- **Totalmente Local:** El código fuente, los registros de actividad y los modelos locales se ejecutan en su equipo.
- **Protección de Credenciales:** Los archivos `.env` y `config/api_keys.json` se encuentran estrictamente ignorados en Git y nunca son transmitidos a servidores remotos.
- **Auditoría de Acciones Sensibles:** Operaciones destructivas o de alto impacto exigen confirmación explícita.

---

## 📜 Licencia
Proyecto de software privado y exclusivo para el Señor Santiago. Todos los derechos reservados.
