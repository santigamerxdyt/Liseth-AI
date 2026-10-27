"""
PDF Generator for Liseth's Executive User Manual.
Generates a comprehensive, professional PDF manual containing all capabilities,
modules, and voice/text quick commands for Señor Santiago.

Zero external dependencies (pure Python standard library).
Can be executed at any time to regenerate the manual when new features are added:
    python tools/generate_manual_pdf.py
"""
import datetime
import os
import sys
from typing import List, Tuple


class LisethPDFBuilder:
    """
    Pure Python vector PDF builder (PDF 1.4 specification).
    Renders styled headers, paragraphs, command boxes, tables, and auto-paginates.
    """

    PAGE_WIDTH = 595.28
    PAGE_HEIGHT = 841.89
    MARGIN_LEFT = 42.0
    MARGIN_RIGHT = 42.0
    MARGIN_TOP = 50.0
    MARGIN_BOTTOM = 50.0

    def __init__(self, title: str = "Manual de Liseth"):
        self.doc_title = title
        self.pages_ops: List[List[str]] = []
        self.current_page_ops: List[str] = []
        self.current_y = self.PAGE_HEIGHT - self.MARGIN_TOP
        self.usable_width = self.PAGE_WIDTH - self.MARGIN_LEFT - self.MARGIN_RIGHT
        self._new_page()

    def _new_page(self):
        """Starts a fresh page and resets the cursor."""
        if self.current_page_ops:
            self.pages_ops.append(self.current_page_ops)
        self.current_page_ops = []
        self.current_y = self.PAGE_HEIGHT - self.MARGIN_TOP

        # Draw running top header rule
        self.current_page_ops.append("q")
        self.current_page_ops.append("0.12 0.35 0.55 RG 1.5 w")  # Navy border
        self.current_page_ops.append(f"{self.MARGIN_LEFT} {self.PAGE_HEIGHT - 35} m {self.PAGE_WIDTH - self.MARGIN_RIGHT} {self.PAGE_HEIGHT - 35} l S")
        self.current_page_ops.append("0.3 0.3 0.3 rg")
        self.current_page_ops.append(f"BT /F2 8 Tf {self.MARGIN_LEFT} {self.PAGE_HEIGHT - 30} Td (LISETH AI \\| COPILOTO AUTONOMO EJECUTIVO) Tj ET")
        self.current_page_ops.append(f"BT /F3 8 Tf {self.PAGE_WIDTH - self.MARGIN_RIGHT - 110} {self.PAGE_HEIGHT - 30} Td (EXCLUSIVO PARA SENOR SANTIAGO) Tj ET")
        self.current_page_ops.append("Q")

    def _check_page_break(self, height_needed: float):
        """Creates a new page if the required vertical space is unavailable."""
        if (self.current_y - height_needed) < self.MARGIN_BOTTOM:
            self._new_page()

    def _escape_pdf_str(self, text: str) -> str:
        """Escapes parentheses and backslashes for PDF string literals."""
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    def add_cover_banner(self, title: str, subtitle: str, author_note: str):
        """Renders an executive front cover banner."""
        self._check_page_break(110)
        y = self.current_y

        # Draw filled navy card
        self.current_page_ops.append("q")
        self.current_page_ops.append("0.08 0.22 0.38 rg")  # Deep blue background
        self.current_page_ops.append(f"{self.MARGIN_LEFT} {y - 95} {self.usable_width} 95 re f")

        # Inner cyan accent line
        self.current_page_ops.append("0.0 0.8 0.75 RG 3 w")
        self.current_page_ops.append(f"{self.MARGIN_LEFT + 15} {y - 95} m {self.MARGIN_LEFT + 15} {y} l S")

        # Title text (white)
        self.current_page_ops.append("1 1 1 rg")
        self.current_page_ops.append(f"BT /F2 20 Tf {self.MARGIN_LEFT + 25} {y - 32} Td ({self._escape_pdf_str(title)}) Tj ET")

        # Subtitle
        self.current_page_ops.append("0.85 0.95 0.98 rg")
        self.current_page_ops.append(f"BT /F2 11 Tf {self.MARGIN_LEFT + 25} {y - 54} Td ({self._escape_pdf_str(subtitle)}) Tj ET")

        # Author / Date
        self.current_page_ops.append("0.7 0.8 0.9 rg")
        self.current_page_ops.append(f"BT /F1 9 Tf {self.MARGIN_LEFT + 25} {y - 78} Td ({self._escape_pdf_str(author_note)}) Tj ET")
        self.current_page_ops.append("Q")

        self.current_y = y - 115

    def add_section_header(self, title: str):
        """Renders a major numbered section header."""
        self._check_page_break(45)
        y = self.current_y

        self.current_page_ops.append("q")
        # Pill badge background
        self.current_page_ops.append("0.90 0.94 0.98 rg")
        self.current_page_ops.append(f"{self.MARGIN_LEFT} {y - 24} {self.usable_width} 24 re f")
        # Left accent stripe
        self.current_page_ops.append("0.1 0.4 0.65 rg")
        self.current_page_ops.append(f"{self.MARGIN_LEFT} {y - 24} 5 24 re f")
        # Header text
        self.current_page_ops.append("0.08 0.25 0.45 rg")
        self.current_page_ops.append(f"BT /F2 12 Tf {self.MARGIN_LEFT + 12} {y - 17} Td ({self._escape_pdf_str(title)}) Tj ET")
        self.current_page_ops.append("Q")

        self.current_y = y - 34

    def add_subsection_header(self, title: str):
        """Renders a subsection title."""
        self._check_page_break(25)
        y = self.current_y
        self.current_page_ops.append("q")
        self.current_page_ops.append("0.15 0.25 0.35 rg")
        self.current_page_ops.append(f"BT /F2 10.5 Tf {self.MARGIN_LEFT + 4} {y - 13} Td ({self._escape_pdf_str(title)}) Tj ET")
        self.current_page_ops.append("Q")
        self.current_y = y - 20

    def add_paragraph(self, text: str, font: str = "F1", size: float = 9.0, leading: float = 12.0, color=(0.15, 0.15, 0.15), indent: float = 0.0):
        """Wraps and prints text across multiple lines cleanly."""
        words = text.split()
        if not words:
            return

        # Approx character limit per line based on usable width and font size
        chars_per_line = int((self.usable_width - indent) / (size * 0.52))

        lines = []
        current_line = []
        current_len = 0

        for w in words:
            if current_len + len(w) + 1 <= chars_per_line:
                current_line.append(w)
                current_len += len(w) + 1
            else:
                lines.append(" ".join(current_line))
                current_line = [w]
                current_len = len(w)

        if current_line:
            lines.append(" ".join(current_line))

        for line in lines:
            self._check_page_break(leading + 2)
            y = self.current_y
            r, g, b = color
            self.current_page_ops.append("q")
            self.current_page_ops.append(f"{r} {g} {b} rg")
            self.current_page_ops.append(f"BT /{font} {size} Tf {self.MARGIN_LEFT + indent} {y - size} Td ({self._escape_pdf_str(line)}) Tj ET")
            self.current_page_ops.append("Q")
            self.current_y = y - leading

        self.current_y -= 3  # Gap after paragraph

    def add_command_box(self, voice_command: str, description: str, result_or_shortcut: str = ""):
        """Draws a high-visibility command card for voice/text quick execution."""
        box_height = 36.0 if not result_or_shortcut else 46.0
        self._check_page_break(box_height + 6)
        y = self.current_y

        self.current_page_ops.append("q")
        # Soft background card
        self.current_page_ops.append("0.97 0.98 0.99 rg")
        self.current_page_ops.append(f"{self.MARGIN_LEFT + 6} {y - box_height} {self.usable_width - 12} {box_height} re f")

        # Border
        self.current_page_ops.append("0.85 0.88 0.92 RG 0.75 w")
        self.current_page_ops.append(f"{self.MARGIN_LEFT + 6} {y - box_height} {self.usable_width - 12} {box_height} re S")

        # Command tag (teal box)
        self.current_page_ops.append("0.05 0.55 0.65 rg")
        self.current_page_ops.append(f"{self.MARGIN_LEFT + 12} {y - 18} 65 14 re f")
        self.current_page_ops.append("1 1 1 rg")
        self.current_page_ops.append(f"BT /F2 7.5 Tf {self.MARGIN_LEFT + 16} {y - 13} Td (COMANDO VOZ) Tj ET")

        # Command text
        self.current_page_ops.append("0.1 0.15 0.25 rg")
        self.current_page_ops.append(f"BT /F2 9.5 Tf {self.MARGIN_LEFT + 84} {y - 14} Td (\\\"{self._escape_pdf_str(voice_command)}\\\") Tj ET")

        # Description
        self.current_page_ops.append("0.35 0.38 0.42 rg")
        self.current_page_ops.append(f"BT /F1 8.5 Tf {self.MARGIN_LEFT + 14} {y - 29} Td ({self._escape_pdf_str(description)}) Tj ET")

        # Extra result/shortcut
        if result_or_shortcut:
            self.current_page_ops.append("0.12 0.45 0.35 rg")
            self.current_page_ops.append(f"BT /F4 8 Tf {self.MARGIN_LEFT + 14} {y - 41} Td (-> {self._escape_pdf_str(result_or_shortcut)}) Tj ET")

        self.current_page_ops.append("Q")
        self.current_y = y - box_height - 6

    def compile(self) -> bytes:
        """Compiles vector objects into valid PDF 1.4 binary data."""
        if self.current_page_ops:
            self.pages_ops.append(self.current_page_ops)

        total_pages = len(self.pages_ops)

        # Append page numbers and bottom footers to all pages
        for idx, page_ops in enumerate(self.pages_ops, start=1):
            page_ops.append("q")
            page_ops.append("0.85 0.88 0.92 RG 1 w")
            page_ops.append(f"{self.MARGIN_LEFT} 35 m {self.PAGE_WIDTH - self.MARGIN_RIGHT} 35 l S")
            page_ops.append("0.45 0.48 0.52 rg")
            page_ops.append(f"BT /F1 8 Tf {self.MARGIN_LEFT} 24 Td (Liseth AI \\| Copiloto Personal & Autónomo \\| Documento Dinámico) Tj ET")
            page_ops.append(f"BT /F2 8 Tf {self.PAGE_WIDTH - self.MARGIN_RIGHT - 75} 24 Td (Pagina {idx} de {total_pages}) Tj ET")
            page_ops.append("Q")

        pdf_chunks = []
        pdf_chunks.append(b"%PDF-1.4\n")

        # We will build objects:
        # 1: Catalog
        # 2: Pages tree
        # 3..6: Fonts (F1: Helvetica, F2: Helvetica-Bold, F3: Helvetica-Oblique, F4: Courier)
        # 7 .. 7 + N - 1: Page objects
        # 7 + N .. 7 + 2N - 1: Content stream objects

        num_pages = len(self.pages_ops)
        obj_count = 6 + (2 * num_pages)
        offsets = {}

        def add_object(obj_num: int, body: bytes):
            offsets[obj_num] = sum(len(c) for c in pdf_chunks)
            pdf_chunks.append(f"{obj_num} 0 obj\n".encode("latin1") + body + b"\nendobj\n")

        # 1: Catalog
        add_object(1, b"<< /Type /Catalog /Pages 2 0 R >>")

        # 2: Pages tree
        page_obj_ids = [7 + i for i in range(num_pages)]
        kids_str = " ".join(f"{pid} 0 R" for pid in page_obj_ids)
        add_object(2, f"<< /Type /Pages /Kids [{kids_str}] /Count {num_pages} >>".encode("latin1"))

        # 3..6: Standard 14 Fonts
        add_object(3, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
        add_object(4, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
        add_object(5, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique /Encoding /WinAnsiEncoding >>")
        add_object(6, b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>")

        font_resources = "<< /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R /F4 6 0 R >> >>"

        # Content streams and Pages
        for i in range(num_pages):
            content_obj_id = 7 + num_pages + i
            page_obj_id = 7 + i

            # Stream body
            raw_stream = "\n".join(self.pages_ops[i]).encode("latin1", errors="replace")
            stream_body = f"<< /Length {len(raw_stream)} >>\nstream\n".encode("latin1") + raw_stream + b"\nendstream"
            add_object(content_obj_id, stream_body)

            # Page object
            page_body = (
                f"<< /Type /Page /Parent 2 0 R "
                f"/MediaBox [0 0 {self.PAGE_WIDTH} {self.PAGE_HEIGHT}] "
                f"/Resources {font_resources} "
                f"/Contents {content_obj_id} 0 R >>"
            ).encode("latin1")
            add_object(page_obj_id, page_body)

        # XREF Table
        xref_start = sum(len(c) for c in pdf_chunks)
        total_objs = obj_count + 1
        pdf_chunks.append(f"xref\n0 {total_objs}\n0000000000 65535 f \n".encode("latin1"))
        for obj_id in range(1, total_objs):
            pdf_chunks.append(f"{offsets[obj_id]:010d} 00000 n \n".encode("latin1"))

        # Trailer
        trailer = (
            f"trailer\n<< /Size {total_objs} /Root 1 0 R "
            f"/Info << /Title ({self.doc_title}) /Author (Liseth AI) >> >>\n"
            f"startxref\n{xref_start}\n%%EOF\n"
        ).encode("latin1")
        pdf_chunks.append(trailer)

        return b"".join(pdf_chunks)


def generate_manual_pdf(output_path: str = "Manual_Liseth.pdf") -> str:
    """
    Compiles the complete executive manual for Liseth and writes it to disk.
    Always includes all current features and quick commands.
    """
    builder = LisethPDFBuilder(title="Manual Ejecutivo de Liseth - Senor Santiago")

    # Front cover banner
    today = datetime.datetime.now().strftime("%d de %B de %Y")
    builder.add_cover_banner(
        title="LISETH AI - MANUAL MAESTRO DE USUARIO",
        subtitle="Guia Completa de Funcionalidades, Modos y Comandos Rapidos",
        author_note=f"Copiloto Personal Autónomo de Señor Santiago \\| Edición Dinámica ({today})"
    )

    builder.add_paragraph(
        "Bienvenido a su manual ejecutivo de Liseth. Este documento se actualiza automáticamente con cada nueva "
        "función incorporada a su asistente. En él encontrará la totalidad de herramientas disponibles divididas por "
        "categoría, su sintaxis de voz y texto con respuesta inmediata (latencia 0 ms) y los flujos autónomos en segundo plano.",
        size=9.2, leading=13.0
    )

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 1: IDENTIDAD, PRIVILEGIOS Y MODOS DE OPERACIÓN
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("1. Identidad, Privilegios Elevados y Modos de Operación")
    builder.add_paragraph(
        "Liseth es su asistente personal ejecutiva con personalidad afectuosa, respetuosa, resolutiva y elegante. "
        "Cuenta con síntesis vocal de alta fidelidad (Salomé es-CO) optimizada para responder con cadencia rápida y sin pausas artificiales.",
        size=9.0
    )
    builder.add_subsection_header("Privilegios Elevados de Windows (Modo Administrador Automático):")
    builder.add_paragraph(
        "• Autoelevación UAC Obligatoria: Liseth se ejecuta siempre con privilegios de Administrador de Windows en todos sus lanzadores (`iniciar_liseth.bat`, `INICIAR_ESCRITORIO.bat`, `INICIAR_WEB.bat` y `python run.py`).\n"
        "• Acceso Total al Sistema: Otorga control irrestricto sobre hardware, administración de servicios, control de procesos del sistema y acceso a rutas protegidas sin restricciones de permisos.\n"
        "• Bandera de Bypass: Para entornos de prueba o depuración sin elevación, admite la bandera `--no-admin`.",
        size=8.5, leading=11.5, indent=8.0
    )
    builder.add_subsection_header("Estados del Motor de Voz:")
    builder.add_paragraph(
        "• Modo Reposo (Standby): Monitorea el micrófono con bajo consumo de CPU. Se activa al oír su nombre.\n"
        "• Modo Activo: Conversación fluida directa sin necesidad de repetir su nombre. Tras 20s de inactividad vuelve a reposo.\n"
        "• Modo No Molestar (DND): Silencia cualquier aviso o notificación vocal para no interrumpir su concentración.",
        size=8.5, leading=11.5, indent=8.0
    )
    builder.add_command_box("Liseth / Liceth / Jarvis [instrucción]", "Activa a Liseth desde reposo y ejecuta la orden de inmediato.", "Transición Standby -> Active")
    builder.add_command_box("Ve a dormir / Modo reposo / Silencio", "Pone a Liseth inmediatamente en reposo sin cerrar la aplicación.", "Modo Standby silencioso")
    builder.add_command_box("¿Eres administradora? / Estado de privilegios", "Verifica en tiempo real que Liseth cuente con privilegios elevados de Administrador.", "Admin Privilege Check")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 2: CONTROL DEL PC Y HARDWARE WINDOWS
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("2. Automatización del PC y Control de Windows")
    builder.add_paragraph(
        "Liseth ejecuta comandos de hardware con 0 ms de latencia mediante llamadas Win32 nativas:",
        size=9.0
    )
    builder.add_command_box("Abre [Calculadora / Chrome / Spotify / Bloc de Notas]", "Inicia programas y herramientas del sistema al instante.", "Lanzador de aplicaciones nativo")
    builder.add_command_box("Sube el volumen / Baja el volumen / Silencia", "Ajusta el sonido del sistema en incrementos o mutea el audio.", "Control de volumen Win32")
    builder.add_command_box("Pon el volumen al [50% / 80%]", "Fija el volumen en un porcentaje numérico exacto.", "Set volumen directo")
    builder.add_command_box("Sube el brillo / Baja el brillo", "Ajusta la luminosidad de la pantalla.", "Hardware de pantalla")
    builder.add_command_box("Toma una captura de pantalla / Pantallazo", "Captura la pantalla completa y la guarda en su carpeta de imágenes.", "Captura instantánea")
    builder.add_command_box("Pantalla completa / F11", "Alterna la visualización a pantalla completa de la app activa.", "Toggle fullscreen")
    builder.add_command_box("Muestra el escritorio / Minimiza todo", "Oculta todas las ventanas y despeja la pantalla de trabajo.", "Win + D nativo")
    builder.add_command_box("Maximiza la ventana / Cierra la ventana", "Gestiona la ventana activa sin usar el ratón.", "Gestión de ventanas")
    builder.add_command_box("Pausa la música / Siguiente canción / Anterior", "Control multimedia global sobre Spotify, navegadores o reproductores.", "Teclas virtuales de medios")
    builder.add_command_box("Pon en Spotify [canción o artista]", "Lanza Spotify en segundo plano y reproduce la pista solicitada.", "URI spotify:search")
    builder.add_command_box("Estado de mi PC / Rendimiento del sistema", "Reporte de telemetría: carga de CPU, uso de RAM, disco y temperatura.", "Telemetría en tiempo real")
    builder.add_command_box("Cierra tu aplicación / Apágate Liseth", "Detiene los hilos de fondo y cierra ordenadamente el programa.", "Cierre ordenado y despedida")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 3: AUTONOMÍA COMPLETA Y TAREAS EN SEGUNDO PLANO
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("3. Autonomía Completa y Tareas en Segundo Plano")
    builder.add_paragraph(
        "Liseth puede trabajar de forma autónoma mientras usted se concentra en otras actividades, "
        "reportando únicamente cuando concluye o si se requiere su atención:",
        size=9.0
    )
    builder.add_command_box("Ejecuta en segundo plano [tarea]", "Encola y ejecuta trabajos largos en hilos asíncronos sin bloquear el PC.", "BackgroundWorkerService")
    builder.add_command_box("¿Qué tareas están en segundo plano? / Tareas activas", "Lista las tareas encoladas, en ejecución y recientemente completadas.", "Consulta de cola autónoma")
    builder.add_command_box("Cancela la tarea en segundo plano", "Detiene la tarea autónoma en ejecución o en espera.", "Cancelación de worker")
    builder.add_command_box("¿Cómo están mis proyectos? / Estado del centinela", "Audita el estado de salud de su código fuente en segundo plano.", "WorkspaceSentinel silencioso")
    builder.add_command_box("Escanea mis proyectos / Revisa mi código", "Fuerza un escaneo de sintaxis py_compile en busca de errores o roturas.", "Reporte de centinela")
    builder.add_command_box("Inicia mi rutina de la mañana / Rutina matutina", "Ejecuta cadena: clima de Bogotá, agenda de hoy, salud de proyectos y saludo.", "RoutineEngine: Morning")
    builder.add_command_box("Inicia rutina de trabajo / Modo concentración", "Activa Trabajo Profundo Pomodoro (50m), DND y verificación de código.", "RoutineEngine: Focus")
    builder.add_command_box("Rutina de cierre / Finalizar jornada", "Balance de compromisos, tareas en segundo plano y cierre de jornada.", "RoutineEngine: Wrap-up")
    builder.add_command_box("¿Qué hiciste hoy, Liseth? / Resumen del día", "Reporte ejecutivo consolidado de todas las actividades autónomas del día.", "DailyDebriefService")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 4: ADMINISTRACIÓN DE EMPRESAS Y MODELACIÓN FINANCIERA
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("4. Administración de Empresas y Modelación Financiera")
    builder.add_paragraph(
        "Herramientas financieras y analíticas diseñadas específicamente para su formación gerencial y proyectos de inversión:",
        size=9.0
    )
    builder.add_command_box("Calcula el VAN / Valor Actual Neto", "Evalúa la viabilidad financiera de proyectos según tasa de descuento y flujos.", "Fórmula VAN / NPV con dictamen")
    builder.add_command_box("Calcula la TIR / Tasa Interna de Retorno", "Determina la tasa intrínseca de rendimiento por aproximación Newton-Raphson.", "Cálculo matemático exacto")
    builder.add_command_box("Calcula el ROI / Retorno de Inversión", "Calcula la rentabilidad porcentual y el multiplicador de la inversión.", "Beneficio neto / Inversión")
    builder.add_command_box("Punto de equilibrio / Break-even", "Desglosa costos fijos, precio y costo variable unitario en unidades y dinero.", "Margen de contribución")
    builder.add_command_box("Matriz FODA / Matriz DOFA", "Genera el análisis estratégico cruzado: fortalezas, debilidades, oportunidades y amenazas.", "Estrategias FO, FA, DO, DA")
    builder.add_command_box("Modelo Canvas / Business Model Canvas", "Estructura los 9 módulos clave de un modelo de negocio escalable.", "Lienzo estratégico Osterwalder")
    builder.add_command_box("Análisis PESTEL", "Audita los factores macroentorno: político, económico, social, tecnológico, ecológico y legal.", "Diagnóstico de entorno")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 5: ASISTENCIA UNIVERSITARIA Y NORMAS APA 7
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("5. Asistencia Universitaria y Normas APA 7ª Edición")
    builder.add_paragraph(
        "Soporte integral para sus entregas académicas, monografías y trabajos de investigación:",
        size=9.0
    )
    builder.add_command_box("Normas APA / Formato APA", "Entrega los parámetros oficiales: márgenes 2.54 cm, tipografías válidas e interlineado doble.", "Guía de estilo APA 7")
    builder.add_command_box("Genera cita APA / Referencia APA", "Construye referencias bibliográficas con sangría francesa y citas en el texto.", "Libros, revistas, tesis y web")
    builder.add_command_box("Estructura de ensayo", "Entrega el esquema metodológico con distribución porcentual (introducción, tesis, conclusiones).", "Estructura académica de ensayo")
    builder.add_command_box("Estructura de informe / Informe ejecutivo", "Esquema profesional para casos de estudio, diagnósticos y propuestas empresariales.", "Template de informe gerencial")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 6: PROGRAMACIÓN Y PRODUCTIVIDAD DE DATOS
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("6. Programación y Productividad con Datos")
    builder.add_paragraph(
        "Herramientas para agilizar sus tareas de desarrollo de software y manipulación de datos:",
        size=9.0
    )
    builder.add_command_box("Estadística descriptiva [datos]", "Calcula media, mediana, varianza, desviación estándar y rango de una serie de números.", "Analítica estadística 0 ms")
    builder.add_command_box("Convierte JSON a tabla Markdown", "Transforma listas de objetos JSON en tablas visuales para documentación en GitHub.", "Formateador de datos")
    builder.add_command_box("Genera sentencias SQL desde CSV", "Genera scripts INSERT INTO listos para ejecutar en bases de datos relacionales.", "Conversor de datos a SQL")
    builder.add_command_box("Modo trabajo profundo / Iniciar Pomodoro", "Inicia sesión de concentración de 50 min con silenciado de interrupciones.", "DeepWork / Pomodoro Manager")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 7: VISIÓN MULTIMODAL Y PORTAPAPELES
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("7. Visión Multimodal y Portapapeles Inteligente")
    builder.add_paragraph(
        "Capacidades de análisis visual y depuración de código copiadas en su memoria de portapapeles:",
        size=9.0
    )
    builder.add_command_box("Mira mi pantalla / ¿Qué estoy viendo?", "Captura su monitor y analiza el contenido visual mediante visión multimodal Gemini.", "Inspección de pantalla")
    builder.add_command_box("Analiza mi portapapeles / Explica lo que copié", "Detecta trazas de error, JSON o código en su portapapeles y sugiere la solución.", "Smart Clipboard Debugger")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 8: CONECTIVIDAD EXTERNA (GMAIL Y TELEGRAM)
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("8. Conectividad Externa (Gmail y Telegram)")
    builder.add_paragraph(
        "Integración con sus canales de comunicación externos:",
        size=9.0
    )
    builder.add_command_box("Revisa mi correo / ¿Tengo correos urgentes?", "Filtra su bandeja Gmail separando mensajes de alta prioridad de promociones y boletines.", "Google Workspace Connector")
    builder.add_command_box("Bot de Telegram (@Liseth)", "Control remoto bidireccional vía comandos (/estado, /agenda, /resumen) y notas de voz.", "Telegram Long-Polling Daemon")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 9: INGENIERÍA INVERSA Y ANÁLISIS DE BINARIOS (MOTOR REA)
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("9. Ingeniería Inversa y Análisis de Binarios (Motor REA)")
    builder.add_paragraph(
        "Liseth incorpora el motor REA (Reverse Engineer Anything v6.7.0) junto con un analizador estático nativo "
        "para examinar ejecutables (EXE, DLL, SYS), paquetes (APK, ASAR, ZIP, WASM, JAR) y bases de datos sin necesidad de código fuente:",
        size=9.0
    )
    builder.add_command_box("Analiza este ejecutable [ruta / archivo]", "Inspección completa: arquitectura, mitigaciones (ASLR/DEP), entropía y secciones.", "Inspección de binarios PE/ELF")
    builder.add_command_box("Entropía de [archivo]", "Calcula la entropía de Shannon (0-8) para detectar empaquetadores (UPX/Themida) o cifrado.", "Detección de packers/cifrado")
    builder.add_command_box("Cadenas del ejecutable [archivo]", "Extrae cadenas ASCII y UTF-16LE, URLs, IPs, claves de registro y APIs sospechosas.", "Extracción de IOCs y cadenas")
    builder.add_command_box("Extrae el archivo asar [ruta]", "Desempaqueta y lista el árbol de código fuente de aplicaciones Electron.", "Inspector Electron ASAR")
    builder.add_command_box("Estado de REA / Motor de ingeniería inversa", "Reporta el estado operativo del motor REA y sus 207 herramientas MCP.", "Telemetría de motor REA")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 10: AUTOMATIZACIÓN WEB Y NAVEGACIÓN ACELERADA (MOTOR EGO LITE)
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("10. Automatización Web y Navegación Acelerada (Motor Ego Lite)")
    builder.add_paragraph(
        "Liseth incorpora la arquitectura de navegación autónoma Ego Lite (v2.0). Permite ejecutar flujos web completos "
        "en segundo plano mediante espacios de tarea aislados (taskSpaces) y snapshots semánticos ultraligeros que reducen en un 90% "
        "el consumo de tokens, indexando cada elemento interactivo con identificadores directos ([ref=1], [ref=2]):",
        size=9.0
    )
    builder.add_command_box("Analiza la página [URL] / Snapshot de [URL]", "Extrae un árbol semántico numerado de la web para inspección y control instantáneo.", "Snapshot semántico token-efficient")
    builder.add_command_box("Navega a [URL] con Ego / Entra a [URL]", "Abre y procesa la web en un espacio de tarea aislado sin alterar sus ventanas activas.", "Navegación background taskSpace")
    builder.add_command_box("Haz clic en [ref=N / nombre] con Ego", "Ejecuta un clic sobre el elemento interactivo identificado por su número de referencia.", "Interacción precisa con elementos")
    builder.add_command_box("Escribe [texto] en [ref=N] con Ego", "Rellena formularios, buscadores o campos de texto directamente sin selectores complejos.", "Entrada de datos en formularios")
    builder.add_command_box("Captura pantalla de [URL] con Ego", "Genera una captura en alta resolución de la página web renderizada en segundo plano.", "Captura visual de página")
    builder.add_command_box("Busca en Google con Ego [consulta]", "Extracción limpia de resultados orgánicos sin publicidad ni scripts invasivos.", "Google Search Learner")
    builder.add_command_box("Estadísticas de GitHub [usuario/repo]", "Consulta estrellas, forks, issues y resumen del repositorio de GitHub.", "GitHub Repo Stats Learner")
    builder.add_command_box("Estado de Ego Browser / Espacios de tarea", "Reporta la telemetría del motor, contextos activos y herramientas aprendidas.", "Telemetría de Ego Browser")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 11: DESPLIEGUE EN LA NUBE Y OPTIMIZACIÓN FRONTEND (VERCEL LABS SUITE)
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("11. Despliegue en la Nube y Optimización Frontend (Vercel Labs Suite)")
    builder.add_paragraph(
        "Liseth incorpora el conjunto de herramientas de desarrollo de Vercel Labs para publicar sitios web al instante "
        "y auditar código frontend contra más de 45 reglas de rendimiento de ingeniería de Vercel y 100 directrices de interfaz:",
        size=9.0
    )
    builder.add_command_box("Despliega mi aplicación / Despliega este proyecto", "Publica su proyecto web en Vercel generando URL de vista previa y panel de control.", "Despliegue instantáneo Vercel")
    builder.add_command_box("Despliega a Vercel en producción", "Publica directamente a dominio principal y entorno de producción (--prod).", "Despliegue a Producción")
    builder.add_command_box("Audita este componente React [archivo]", "Evalúa su código contra 45+ reglas Vercel: waterfalls, bundle size, re-renders y micro-optimizaciones.", "Vercel React Best Practices")
    builder.add_command_box("Revisa el diseño web / Audita la interfaz UI", "Audita accesibilidad (A11y), estados de foco, etiquetas de formularios y UX móvil.", "Web Interface Guidelines")
    builder.add_command_box("Detecta el framework del proyecto", "Identifica Next.js, Vite, Astro, React, Vue, Svelte o sitios estáticos HTML.", "Detector de frameworks")
    builder.add_command_box("Estado de Vercel / Vercel Skills", "Muestra la versión de Vercel CLI, rutas de habilidades y reglas activas.", "Telemetría de Vercel Suite")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 12: AUDITORÍA INTEGRAL DE CIBERSEGURIDAD (SECURITY AUDIT ENTERPRISE)
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("12. Auditoría Integral de Ciberseguridad (Security Audit Enterprise)")
    builder.add_paragraph(
        "Liseth incorpora un motor estático de auditoría y análisis de vulnerabilidades alineado con los estándares OWASP Top 10 y CWE Top 25. "
        "Examina repositorios completos, archivos y fragmentos de código (Python, JavaScript, TypeScript, Bash, JSON, YAML y configuraciones), "
        "identificando credenciales expuestas, inyecciones de código (SQLi, Command Injection, NoSQLi), vectores de Prompt Injection en LLMs, "
        "deserializaciones inseguras y configuraciones erróneas de seguridad con guías técnicas de remediación:",
        size=9.0
    )
    builder.add_command_box("Audita la seguridad de este proyecto / Audita la seguridad de [ruta]", "Escaneo estático integral del repositorio con índice de seguridad (0-100), desglose de severidad y clasificación de riesgo.", "Auditoría de ciberseguridad SAST")
    builder.add_command_box("Escanea vulnerabilidades en [archivo]", "Análisis exhaustivo del archivo detectando CWEs específicos, líneas afectadas y sugerencias de remediación.", "Análisis de vulnerabilidades de archivo")
    builder.add_command_box("Busca secretos y credenciales en mi código", "Detección de claves de Google Cloud, AWS, GitHub, OpenAI y cadenas de conexión a bases de datos con ofuscación automática.", "Detector de secretos expuestos")
    builder.add_command_box("Audita vectores OWASP / Seguridad en IA", "Inspección de riesgos en prompts de IA (OWASP-LLM01), deserialización pickle/yaml insegura y políticas CORS permisivas.", "Auditoría OWASP y LLM Security")
    builder.add_command_box("Estado de seguridad / Telemetría de seguridad", "Reporta el estado del motor de ciberseguridad, motores estáticos y vectores de análisis activos.", "Telemetría Security Audit")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 13: DETECTOR Y HUMANIZADOR DE TEXTOS AI (SLOPMONSTER & DESLOP)
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("13. Detector y Humanizador de Textos AI (SlopMonster & Deslop)")
    builder.add_paragraph(
        "Liseth incorpora el motor lingüístico SlopMonster para la detección de patrones sintéticos de inteligencia artificial y su transformación "
        "en prosa humana ejecutiva. Evalúa textos en español e inglés mediante 5 dimensiones de análisis (vocabulario trillado, construcciones cliché, "
        "abuso de guiones largos, listas triádicas y conclusiones vacías), reescribiendo borradores robóticos en redacción natural, persuasiva y con voz de autor:",
        size=9.0
    )
    builder.add_command_box("Humaniza este texto: '[texto]' / Deslop este borrador", "Elimina muletillas y frases hechas de IA ('en el vertiginoso mundo actual', 'tapiz', 'faro'), reescribiendo con cadencia natural y concisa.", "Humanizador y de-slopper")
    builder.add_command_box("Analiza si este texto parece hecho por IA: '[texto]'", "Calcula el Slop Score multidimensional (0 a 5 por categoría), nivel de sospecha de IA y recomendaciones específicas.", "Auditoría de patrones de IA (Slop Score)")
    builder.add_command_box("Reescribe mi ensayo / artículo con tono humano", "Reformula ensayos académicos, correos corporativos o artículos eliminando redundancias y conclusiones artificiales.", "Reescritura humana de textos")
    builder.add_command_box("Estado de SlopMonster / Detector de IA", "Muestra el estado del motor lingüístico, catálogo bilingüe de patrones de IA y umbrales de puntuación.", "Telemetría SlopMonster")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 14: SINCRONIZACIÓN AUTOMÁTICA CON GITHUB Y DESPLIEGUE WEB (GIT SYNC & GITHUB PAGES)
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("14. Sincronización Automática con GitHub y Despliegue Web (Git Sync & GitHub Pages)")
    builder.add_paragraph(
        "Liseth cuenta con un motor nativo de sincronización automática con GitHub y despliegue web público en la nube. "
        "Permite que todas las modificaciones realizadas en el proyecto se suban y respalden en la nube con un solo comando de voz o en segundo plano "
        "mediante su centinela automático, publicando la interfaz para que cualquier persona pueda abrirla y utilizarla directamente desde el navegador, "
        "operando tanto conectada al backend local como de forma 100% autónoma en la nube (con cerebro embebido para finanzas, normas APA y voz sintetizada):",
        size=9.0
    )
    builder.add_command_box("Sincroniza con GitHub / Sube los cambios a GitHub", "Detecta archivos modificados, genera un commit semántico con fecha/hora y sube los cambios a origin main.", "Sincronización Git en la nube")
    builder.add_command_box("Estado de Git / Estado de sincronización", "Reporta la rama activa, archivos pendientes por subir y estado del repositorio remoto.", "Telemetría del repositorio")
    builder.add_command_box("Inicia el centinela de GitHub / Auto sync", "Activa el monitoreo en segundo plano que detecta cambios y los sube a GitHub automáticamente cada 5 minutos.", "Centinela de Auto-Sync")
    builder.add_command_box("Detén el centinela de GitHub", "Pausa la sincronización automática en segundo plano para trabajar sin subir cambios continuos.", "Control del Centinela Git")
    builder.add_command_box("Modo Cloud Autónomo (GitHub Pages)", "https://santigamerxdyt.github.io/Liseth-AI/ \\| Operativo 24/7 sin servidor local: chat cognitivo, voz sintetizada, finanzas y APA.", "Despliegue Autónomo en la Nube")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 15: INVESTIGACIÓN CIENTÍFICA Y ESTADO DEL ARTE (ACADEMIC RESEARCHER)
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("15. Investigación Científica y Estado del Arte (Academic Researcher)")
    builder.add_paragraph(
        "Liseth cuenta con integración directa a las bases de datos abiertas OpenAlex (250M+ publicaciones) y arXiv.org. "
        "Permite buscar literatura revisada por pares, extraer resúmenes, DOIs y PDFs de acceso abierto, sintetizar revisiones bibliográficas "
        "(Estado del Arte) y estructurar citas parentéticas, narrativas y bibliográficas en Normas APA 7ª Edición para sus entregas universitarias:",
        size=9.0
    )
    builder.add_command_box("Busca artículos sobre [tema] / Papers de [tema]", "Recupera publicaciones científicas con autores, año, revista, resumen, métricas de citas y DOI permanente.", "Búsqueda científica OpenAlex/arXiv")
    builder.add_command_box("Estado del arte sobre [tema] / Revisión bibliográfica", "Genera una revisión de literatura completa con tendencias conceptuales, vacíos de investigación y lista de referencias APA 7.", "Estado del Arte Universitario")
    builder.add_command_box("Estado de Academic Research", "Reporta la telemetría del motor de investigación académica, fuentes indexadas y estándar APA activo.", "Telemetría Academic Researcher")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 16: ESTRATEGIA CORPORATIVA Y FINANZAS AVANZADAS (BUSINESS STRATEGIST)
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("16. Estrategia Corporativa y Finanzas Avanzadas (Business Strategist)")
    builder.add_paragraph(
        "Módulo diseñado a la medida para la formación en Administración de Empresas de Santiago. "
        "Estructura matrices de diagnóstico competitivo y modelos financieros cuantitativos para la toma de decisiones gerenciales:",
        size=9.0
    )
    builder.add_command_box("Matriz FODA de [empresa] / Análisis SWOT", "Genera el diagnóstico en 4 cuadrantes y la matriz de cruce estratégico con iniciativas FO, DO, FA y DA.", "Matriz FODA y Cruce Estratégico")
    builder.add_command_box("5 Fuerzas de Porter de [industria]", "Diagnóstico del atractivo del sector: poder de clientes/proveedores, rivalidad, barreras de entrada y sustitutos.", "Fuerzas Competitivas de Porter")
    builder.add_command_box("Modelo Canvas de [negocio] / Business Model Canvas", "Estructura los 9 bloques de Osterwalder: propuesta de valor, clientes, canales, recursos, costos e ingresos.", "Lienzo Business Model Canvas")
    builder.add_command_box("Proyección de flujo de caja / Flujo de caja libre", "Modela el Estado de Resultados y el Flujo de Caja Libre (FCF) proyectado a N períodos con EBITDA y CAPEX.", "Proyección Financiera Pro-Forma")
    builder.add_command_box("Tabla de amortización de préstamo [monto]", "Calcula cronograma de crédito con cuotas mensuales, desglose de capital e intereses en Sistema Francés o Alemán.", "Amortización de Crédito")
    builder.add_command_box("Calcula el WACC / Costo de Capital", "Calcula el Costo Promedio Ponderado de Capital con ponderación de patrimonio/deuda y escudo fiscal para definir la tasa de corte (TIR).", "Cálculo del WACC / CPPC")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 17: CIENCIA DE DATOS Y MACHINE LEARNING (DATA & ML TOOLKIT)
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("17. Ciencia de Datos y Machine Learning (Data & ML Toolkit)")
    builder.add_paragraph(
        "Conjunto de herramientas analíticas para auditar, depurar y modelar información cuantitativa con rigor estadístico. "
        "Permite detectar anomalías en datasets empresariales, calcular modelos de regresión y generar pipelines de código Python listos para producción:",
        size=9.0
    )
    builder.add_command_box("Perfila estos datos [CSV] / Limpia este dataset", "Auditoría de calidad tabular: detección de nulos, duplicados, tipado inferido y outliers mediante rango intercuartil (IQR).", "Perfilamiento y Auto-Limpieza")
    builder.add_command_box("Regresión lineal de X=[...] Y=[...]", "Ajusta recta de mínimos cuadrados OLS, calcula bondad de ajuste (R²), correlación de Pearson, MSE y proyecta valores futuros.", "Regresión Lineal OLS")
    builder.add_command_box("Pronóstico de la serie [valores numéricos]", "Proyección de series temporales con Suavizamiento Exponencial Simple (SES) y medias móviles con detección de tendencia.", "Forecasting de Series de Tiempo")
    builder.add_command_box("Script de Machine Learning para [regresión/clustering]", "Genera código modular y reproducible en Python usando Pandas, NumPy y Scikit-Learn con escalado y evaluación.", "Pipeline ML en Python")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 18: AUTOMATIZACIÓN OFIMÁTICA Y FÓRMULAS AVANZADAS (WORKSPACE AUTOMATION)
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("18. Automatización Ofimática y Fórmulas Avanzadas (Workspace Automation)")
    builder.add_paragraph(
        "Acelera la productividad diaria en la preparación de informes, hojas de cálculo complejas y presentaciones de alto impacto:",
        size=9.0
    )
    builder.add_command_box("Fórmula de Excel para [requerimiento / búsqueda]", "Genera la solución en fórmulas bilingües (BUSCARX/XLOOKUP, SUMAR.SI.CONJUNTO, matrices dinámicas) con control de errores.", "Generador de Fórmulas de Excel/Sheets")
    builder.add_command_box("Estructura de informe de consultoría / Ensayo académico", "Diseña el blueprint estructurado para informes gerenciales ejecutivos (To-Be, ROI, 30-60-90 días) o ensayos universitarios.", "Blueprint de Informes y Ensayos")
    builder.add_command_box("Diapositivas para [tema] / Presentación ejecutiva", "Arquitectura visual diapositiva por diapositiva con contenidos recomendados, métricas y notas del orador (speaker notes).", "Estructurador de Presentaciones")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 19: COPILOTO CURRICULAR UNAL PALMIRA (PENSUM ADMINISTRACIÓN DE EMPRESAS)
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("19. Copiloto Curricular UNAL Palmira: Pensum de Administración de Empresas")
    builder.add_paragraph(
        "Liseth integra la totalidad del plan de estudios oficial del programa de Administración de Empresas de la "
        "Universidad Nacional de Colombia (Sede Palmira), regido por el Acuerdo 19 de 2012 del Consejo de Facultad "
        "(Facultad de Ingeniería y Administración) y el Acuerdo 033 de 2007 del CSU. "
        "Contempla los 10 semestres, 166 créditos totales (35 Fundamentación, 97 Disciplinar, 34 Libre Elección), "
        "los 12 créditos obligatorios de suficiencia de inglés, cadenas de prerrequisitos, códigos SIA, y marcos normativos colombianos "
        "(CST, Estatuto Tributario DIAN, Ley 80/93, Ley 99/93, ISO 14001):",
        size=9.0
    )
    builder.add_command_box("Mi pensum / Malla curricular / Plan de estudios", "Muestra el resumen de distribución curricular (166 créditos), tipologías, porcentajes y rutas de profundización en Sede Palmira.", "Resumen Curricular UNAL")
    builder.add_command_box("Materias del semestre [1-10] / Matrícula [1-10]", "Despliega la lista completa de asignaturas sugeridas por semestre con sus códigos SIA, créditos, tipología y prerrequisitos.", "Mapeo Semestral de Asignaturas")
    builder.add_command_box("Prerrequisitos de [materia] / Qué necesito para ver [materia]", "Analiza la cadena de prerrequisitos académicos obligatorios y correquisitos (ej: Costos, Finanzas, Trabajo de Grado).", "Auditoría de Cadenas de Prerrequisitos")
    builder.add_command_box("Info de la materia [materia] / Ficha de [materia]", "Ficha académica integral: ejes temáticos, aplicación profesional en administración, teorías clave y fórmulas cuantitativas.", "Guía Académica y Fórmulas por Asignatura")
    builder.add_command_box("Auditoría de créditos para grado / Requisitos de grado", "Evalúa el avance académico hacia los hitos de grado: Consultoría (mínimo 68 cr disciplinares) y Trabajo de Grado/Pasantía (78 cr).", "Auditoría de Hitos de Grado")
    builder.add_command_box("Marco normativo de [laboral / tributario / contratación / ambiental]", "Resumen ejecutivo de leyes colombianas críticas: CST (prestaciones y nómina), DIAN (Renta, IVA, ICA), Ley 80 y Ley 99.", "Legislación Empresarial Colombiana")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 20: BÓVEDA CENTRAL DE AUTENTICADORES Y APIS (CENTRAL CREDENTIALS VAULT)
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("20. Bóveda Central de Autenticadores y APIs (Central Credentials Vault)")
    builder.add_paragraph(
        "Liseth cuenta con un centro de control y bóveda unificada para la gestión, prueba y respaldo de todas las llaves de acceso, "
        "tokens de autenticación y credenciales de servicios externos a través de 7 dominios estratégicos: "
        "(1) Cerebros IA (Gemini, Claude, Groq, OpenAI, Ollama Local y OpenRouter), "
        "(2) Voces Humanas Neuronales (Salomé, Dalia, Elvira, ElevenLabs, Picovoice Porcupine y Azure Speech), "
        "(3) Google Cloud OAuth 2.0 (Gmail, Google Calendar, Google Drive y Google Docs), "
        "(4) Mensajería Instantánea (Telegram Bot y Meta WhatsApp Cloud API), "
        "(5) Búsqueda Web y Servicios Académicos (SerpAPI, Google CSE, OpenAlex 100k req/día, Spotify, YouTube y OpenWeather), "
        "(6) Git y Despliegues en la Nube (GitHub Personal Access Token y Vercel CLI), y "
        "(7) Seguridad y Criptografía (PIN de acceso privado de Santiago, Clave AES-256, Secreto de Sesión y Límite Diario de Tokens). "
        "Opera con doble persistencia: sincroniza directamente con el archivo .env en disco cuando se ejecuta en el equipo local, "
        "y con almacenamiento local seguro cuando se accede a través del despliegue en GitHub Pages:",
        size=9.0
    )
    builder.add_command_box("Abre el menú de APIs / Bóveda de credenciales", "Despliega la interfaz interactiva de 7 pestañas para configurar, inspeccionar y editar cualquier clave del sistema.", "Apertura de la Bóveda Central")
    builder.add_command_box("Configurar autenticadores / Mis claves API", "Acceso directo a la bóveda por voz o texto con respuesta inmediata de Liseth y visualización de estados.", "Acceso por Voz a Credenciales")
    builder.add_command_box("Prueba de conexión en vivo (⚡ Probar)", "Verifica en tiempo real si su clave de Gemini, Claude, Groq, OpenAI, ElevenLabs, Telegram o GitHub responde (200 OK).", "Comprobación Activa de Servicios")
    builder.add_command_box("Exportar / Importar Backup de Credenciales", "Descarga una copia de seguridad segura en formato JSON (liseth-credentials-backup.json) o restaura sus claves al instante.", "Respaldo y Portabilidad")
    builder.add_command_box("Persistencia Dual (.env y LocalStorage)", "Garantiza operatividad 100% en Windows local (.env) y en la nube pública de GitHub Pages (LocalStorage).", "Doble Capa de Persistencia")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 21: ARQUITECTURA DE CEREBROS MÚLTIPLES Y MOTOR COGNITIVO NATIVO
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("21. Arquitectura de Cerebros Multi-Nivel y Motor Cognitivo Nativo")
    builder.add_paragraph(
        "Liseth opera con una arquitectura de failover y resiliencia cognitiva en 4 capas autónomas para garantizar que "
        "Señor Santiago nunca quede incomunicado ni sin asistencia: "
        "(1) Cerebro Primario en la Nube: Google Gemini 3.8 Flash y 3.5 Flash-Lite con auto-curación y descubrimiento dinámico de modelos en tiempo real; "
        "(2) Cerebros Auxiliares de Inferencia Rápida: Groq Cloud (LLaMA 3.3 70B a más de 500 tokens/segundo) y Anthropic Claude (razonamiento analítico profundo); "
        "(3) Centinela de Telegram Bidireccional: Mantiene la misma inteligencia, herramientas y cascada de cerebros disponible desde su móvil en cualquier lugar; y "
        "(4) Motor Cognitivo Nativo Integrado (EmbeddedCognitiveEngine): 100% offline, local y de respuesta inmediata en Windows que opera sin consumir saldo de API ni requerir conexión a internet:",
        size=9.0
    )
    builder.add_command_box("Cerebro Primario: Gemini 3.8 / 3.5 Flash", "Inferencia multimodal con auto-descubrimiento de modelos en caso de 404 y rotación de claves.", "Cerebro Primario en la Nube")
    builder.add_command_box("Inferencia Ultra-Rápida con Groq (LLaMA 3.3 70B)", "Velocidad extrema de respuesta inmediata (500+ tok/s) cuando se requiere respuesta instantánea.", "Cerebro Auxiliar Groq")
    builder.add_command_box("Centinela de Telegram Bidireccional", "Recibe y responde mensajes remotos de Santiago por Telegram con ejecución completa de acciones en el PC.", "Control Remoto Telegram")
    builder.add_command_box("Motor Cognitivo Nativo 100% Offline", "Núcleo de respaldo que resuelve fórmulas de Excel, VAN/TIR, citas APA 7 y hardware sin internet.", "Embedded Cognitive Engine")
    builder.add_command_box("Auto-Curación y Failover en <100ms", "Si un proveedor falla por cuota o red, Liseth conmuta de inmediato al siguiente cerebro sin error visible.", "Resiliencia Autónoma")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 22: EXPERIENCIA MÓVIL TOTAL Y PWA (ANDROID & IOS)
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("22. Experiencia Móvil de Vanguardia (Smartphone Web & PWA)")
    builder.add_paragraph(
        "Liseth cuenta con una interfaz web totalmente rediseñada y optimizada para ejecutarse con máxima fluidez "
        "en cualquier teléfono inteligente (iOS Safari y Android Chrome), tanto en su red local como a través de GitHub Pages: "
        "(1) Diseño 100% Responsivo: Se adapta dinámicamente a pantallas de 320px a 768px de ancho sin desbordamiento horizontal; "
        "(2) Compatibilidad PWA (Progressive Web App): Permite ser instalada en la pantalla de inicio del smartphone como una app nativa a pantalla completa; "
        "(3) Soporte de Áreas Seguras (Safe Areas): Compatible con notch, dynamic island y barras de navegación por gestos con `viewport-fit=cover`; "
        "(4) Prevención de Zoom Forzado: Fuentes calibradas a 16px en inputs para evitar que Safari amplíe bruscamente la pantalla al escribir; "
        "(5) Activación Táctil de Audio y Voz: Desbloqueo automático del sintetizador vocal y Web Audio Context al primer toque en el móvil; y "
        "(6) Teclado Virtual Dinámico: Detección visual de apertura de teclado en smartphone con ajuste automático de desplazamiento sin ocultar la barra de entrada:",
        size=9.0
    )
    builder.add_command_box("Modo PWA en Pantalla de Inicio", "Instalable desde Chrome/Safari ('Agregar a pantalla de inicio') con icono de alta resolución y aspecto nativo.", "PWA Standalone")
    builder.add_command_box("Cabecera y Modales Táctiles Ultra-Compactos", "Botones de acción circulares e interfaces de diálogo que se adaptan al 96% del ancho de pantalla.", "Diseño Adaptativo Táctil")
    builder.add_command_box("Desbloqueo Automático de Voz Móvil", "Garantiza que Liseth responda con voz dulce y fluida en su teléfono tras la primera interacción táctil.", "Voz Móvil Desbloqueada")
    builder.add_command_box("Teclado Virtual Inteligente", "Ajusta la vista y el chat automáticamente con window.visualViewport para que la barra de texto nunca quede tapada.", "Adaptación Teclado Móvil")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 23: INTERFAZ HOLOGRÁFICA CINEMÁTICA STARK HUD (MARK LXXXV)
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("23. Interfaz Holográfica Cinemática Stark HUD (Iron Man Mark LXXXV)")
    builder.add_paragraph(
        "Liseth incorpora el entorno visual cinemático más potente y avanzado, inspirado directamente en los sistemas "
        "holográficos de Tony Stark (Iron Man Mark LXXXV y Avengers Endgame): "
        "(1) Malla Cuántica y Haz de Escaneo Láser: Red hexagonal en el fondo con línea de barrido holográfico que recorre el sistema; "
        "(2) Alas de Telemetría Flotantes (Stark Wings): Paneles laterales de cristal holográfico con indicadores de carga neural en vivo, modelo activo (Gemini 3.8 / Groq 70B), radar y cronómetro digital de microsegundos; "
        "(3) Reactor Arc Cuántico Multi-Capa: Esfera central con 4 anillos giroscópicos giratorios independientes, retícula de apuntado cardinal y núcleo de plasma con filamentos de energía; "
        "(4) Radar Acústico y Partículas Cuánticas en Canvas 2D: Corona holográfica de 64 frecuencias radiales que vibran armónicamente con la voz, haz de radar continuo y 46 fotones cuánticos en órbita gravitacional; "
        "(5) Perspectiva Volumétrica Parallax 3D: Inclinación tridimensional de la interfaz en escritorios que sigue dinámicamente el movimiento del cursor; y "
        "(6) Sintetizador Procedural de Audio Web Audio API: Micro-sonidos electrónicos futuristas en botones, transmisión cuántica al enviar mensajes y apertura de módulos:",
        size=9.0
    )
    builder.add_command_box("Reactor Arc Cuántico & Modo Sobrecarga (Boost)", "Núcleo de plasma vibrante que entra en hiper-velocidad al tocarlo con fogueo dorado y armónicos.", "Holo-Reactor Central & Boost")
    builder.add_command_box("Malla 3D Wireframe Cuántica & Polvo Estelar", "Dodecaedro tridimensional vectorial que gira en el espacio y atrae estelas de chispas cuánticas al cursor.", "Geometría 3D & Gravedad de Partículas")
    builder.add_command_box("Alas Laterales de Telemetría Stark & Cinta Superior", "Cinta de diagnóstico en cabecera (MARK LXXXV) y paneles laterales con cronómetro digital de microsegundos.", "Stark HUD Wings & Ribbon")
    builder.add_command_box("Selector Rápido de Armaduras (Mark 85 / 50 / War Machine)", "Alterna al instante entre paletas de color cuánticas (Cian, Dorado Nanotech, Esmeralda y Plasma Violeta).", "Configuración de Armaduras")
    builder.add_command_box("Micro-Sonidos Procedurales Web Audio API & Control Táctil", "Efectos sonoros sutiles generados matemáticamente sin consumo de red y conmutador táctil de silencio.", "Sintetizador Sonoro HUD")
    builder.add_command_box("Anillo de 10 Bobinas de Inducción & Constelación", "Bobinas electromagnéticas en el reactor y red cuántica viva con haces láser entre fotones en tiempo real.", "Inductores Arc & Red Cuántica")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 24: ECOSISTEMA NFC Y PAGOS POR CONTACTO (CONTACTLESS & BEAM)
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("24. Ecosistema NFC y Pagos por Contacto (Contactless & Beam)")
    builder.add_paragraph(
        "Liseth incorpora un ecosistema completo de interacción por proximidad (Near Field Communication - NFC) y "
        "pagos por contacto de alta seguridad, adaptado para smartphones con hardware NFC (Android Chrome) y estaciones de escritorio: "
        "(1) Pagos y Cobros Tokenizados por Contacto: Soporte para estándares interoperables colombianos (Bre-B del Banco de la República), billeteras digitales (Nequi y Daviplata), tarjetas bancarias EMV y criptomonedas (USDT/BTC) con firma criptográfica SHA-256; "
        "(2) Lectura Universal de Etiquetas NDEF: Detección automática de UID de tag y decodificación de registros de texto, URLs web, credenciales y pagos; "
        "(3) Transmisión Digital de Tarjetas (Beam): Grabación y transferencia instantánea por contacto de su tarjeta de presentación ejecutiva vCard 3.0/4.0 de Santiago (UNAL Palmira, CEO, datos de contacto y redes); "
        "(4) Modo Dual Adaptativo y Simulador Holográfico: Cuando opera en PC o navegadores sin acceso directo al chip NFC, activa automáticamente el simulador holográfico táctil y generador dinámico de códigos QR Beam para escanear con la cámara del smartphone; "
        "(5) Libro Contable de Transacciones Auditado: Historial detallado de operaciones por proximidad con exportación en JSON y persistencia en SQLite; y "
        "(6) Retroalimentación Sensorial Stark: Sonidos procedurales de contacto electrónico (chimes), vibración háptica en teléfonos y pulso dorado del Reactor Arc:",
        size=9.0
    )
    builder.add_command_box("Terminal de Cobro por Contacto ($25k / $50k)", "Genera un token de cobro contactless (Bre-B, Nequi, Daviplata) listo para recibir el toque del pagador.", "Cobro Contactless Instantáneo")
    builder.add_command_box("Escanear Tag / Tarjeta NFC (Lectura NDEF)", "Lee credenciales, tarjetas inteligentes o etiquetas de proximidad mostrando UID y contenido.", "Escaneo NDEF Universal")
    builder.add_command_box("Transmitir Tarjeta de Presentación (vCard Beam)", "Transfiere los datos de contacto y perfil profesional de Santiago al tocar el móvil de un colega.", "Digital Business Card Beam")
    builder.add_command_box("Simulador Táctil NFC y QR Beam para PC", "Permite probar, verificar y compartir cobros y tarjetas en computadoras de escritorio sin chip NFC.", "Simulación y Respaldo QR")
    builder.add_command_box("Libro Contable Auditado de Operaciones NFC", "Supervisa el registro histórico de pagos, fechas, montos y firmas criptográficas con exportación.", "Ledger Criptográfico NFC")
    builder.add_command_box("Control por Voz de Cobros y Contactos", "Pídale a Liseth: 'Genera un cobro contactless de 30 mil pesos' o 'Transmite mi tarjeta de contacto'.", "Comandos de Voz NFC")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 25: FACTURACIÓN ELECTRÓNICA DIAN, DESBLOQUEO POR PROXIMIDAD Y DIVISAS
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("25. Facturación Electrónica DIAN, Desbloqueo NFC y Divisas")
    builder.add_paragraph(
        "Liseth amplía su ecosistema financiero y de proximidad con módulos avanzados de facturación legal, "
        "seguridad por hardware y conversión de divisas en tiempo real: "
        "(1) Facturación Electrónica Pro-Forma DIAN: Emisión instantánea de facturas comerciales con generación de hash criptográfico SHA-384 CUFE (Código Único de Facturación Electrónica), cálculo automatizado de IVA (19% o 5%), Retención en la Fuente (4% o 2.5%) y enlace de validación en el catálogo DIAN; "
        "(2) Vinculación Directa con Pagos Contactless: Cualquier cobro NFC por Bre-B, Nequi o tarjeta genera automáticamente su respectiva factura pro-forma imprimible y descargable; "
        "(3) Transmisión de Facturas por NFC: Grabación de facturas comerciales y comprobantes directamente en etiquetas NFC de clientes con un solo toque; "
        "(4) Desbloqueo por Proximidad (Stark Security Key): Autenticación biométrica y por tarjeta física en la pantalla de bloqueo sin necesidad de ingresar el PIN manualmente; y "
        "(5) Conversor Multidivisa y Criptoactivos: Conversión instantánea entre COP, USD, EUR, USDT, BTC y ETH para fijar montos exactos de cobro por proximidad en segundos:",
        size=9.0
    )
    builder.add_command_box("Emisión de Factura Pro-Forma con CUFE", "Genera el documento electrónico con desglose tributario legal y código QR de validación fiscal.", "Facturación Electrónica Pro-Forma")
    builder.add_command_box("Desbloqueo de Liseth con Llave Stark NFC", "Aproxime su carné universitario o tarjeta autorizada para desbloquear el sistema sin teclear su PIN.", "Stark Key Proximity Unlock")
    builder.add_command_box("Conversor Rápido de Divisas y Cripto (COP/USD/BTC)", "Calcule al instante equivalencias de $50 USD o 0.001 BTC y aplíquelas al cobro por contacto.", "Calculadora de Divisas & Cripto")
    builder.add_command_box("Impresión y Exportación de Facturas", "Abra e imprima el comprobante comercial pro-forma en formato ejecutivo limpio con un solo clic.", "Impresión de Comprobantes")
    builder.add_command_box("Comandos de Facturación y Conversión por Voz", "Pídale a Liseth: 'Emite una factura de 150 mil pesos para Constructora Bolívar' o 'Convierte 100 dólares a pesos'.", "Voz para Facturas y Divisas")

    # ─────────────────────────────────────────────────────────────────────────
    # SECCIÓN 26: GESTIÓN DE PATRIMONIO, BÓVEDA STARK, MINUTAS LEGALES Y FOCO
    # ─────────────────────────────────────────────────────────────────────────
    builder.add_section_header("26. Gestión de Patrimonio, Bóveda Stark, Minutas Legales y Foco")
    builder.add_paragraph(
        "Liseth completa su ecosistema ejecutivo de alta dirección con cuatro módulos estratégicos diseñados "
        "para la administración patrimonial, la ciberseguridad avanzada y la productividad personal de Señor Santiago: "
        "(1) Finanzas Personales y Flujo de Caja Mensual: Registro y supervisión de gastos e ingresos clasificados por categorías estratégicas (Alimentación, Transporte, Educación UNAL, Consultoría, etc.), cálculo automático de superávit neto, tasa de ahorro y alertas preventivas cuando una categoría supera el 80% o 100% de su límite presupuestal; "
        "(2) Bóveda Criptográfica Stark de Contraseñas: Generador de credenciales seguras con modos Complejo, Frase Diceware (palabras memorables) y PIN, con cálculo matemático de Entropía de Shannon (bits) y estimación de tiempo para ataque de fuerza bruta (desde segundos hasta siglos de invulnerabilidad); "
        "(3) Generador de Contratos Comerciales y Minutas Legales Colombianas: Redacción automatizada de contratos de prestación de servicios profesionales independientes, acuerdos de confidencialidad (NDA), pagarés a la orden ejecutivos y actas de liquidación a satisfacción conforme al Código de Comercio; y "
        "(4) Modo Foco Stark y Misión Control: Temporizador Pomodoro de 25 minutos con emisión de ondas binaurales alfa a 432 Hz para máxima concentración mental y optimización de memoria RAM con purga de ciclos:",
        size=9.0
    )
    builder.add_command_box("Balance de Finanzas Personales y Presupuesto", "Consulta ingresos, gastos, tasa de ahorro y alertas de consumo mensual por voz o en el modal HUD.", "Flujo de Caja y Presupuesto")
    builder.add_command_box("Generador de Contraseñas y Auditoría de Entropía", "Crea credenciales militares Stark y audita cualquier contraseña calculando su entropía de Shannon.", "Bóveda Criptográfica Stark")
    builder.add_command_box("Redacción de Contratos y NDAs Colombianos", "Genera minutas legales listas para imprimir o copiar: servicios profesionales, NDAs y pagarés.", "Ingeniería Legal Comercial")
    builder.add_command_box("Activación del Modo Foco y Campana Alfa 432 Hz", "Inicia bloques de 25 min de concentración profunda con audiofrecuencia binaural alfa y pulso visual.", "Stark Deep Work & Pomodoro")
    builder.add_command_box("Optimización de Memoria RAM del Sistema", "Libera memoria del host, ejecuta recolección de basura y compacta ciclos en un solo toque.", "Higiene y Purgado del Host")

    # ───
    # SECCIÓN 27: EVALUACIÓN DE PROYECTOS VAN/TIR, MATRIZ DE RIESGOS ISO 31000, RADAR MACRO Y PITCH DECKS
    # ───
    builder.add_section_header("27. Evaluacion de Proyectos, Matriz de Riesgos ISO 31000, Macroeconomia y Pitch Decks")
    builder.add_paragraph(
        "Liseth expande sus competencias ejecutivas para la alta direccion empresarial, alineadas especificamente con el perfil "
        "en Administracion de Empresas de Senor Santiago (UNAL Palmira), incorporando cuatro nuevas herramientas cuantitativas y estrategicas: "
        "(1) Evaluador Financiero de Proyectos de Inversion: Modelado completo de presupuesto de capital con Valor Actual Neto (VAN / NPV), "
        "Tasa Interna de Retorno (TIR / IRR mediante resolucion numerica por biseccion), Periodo de Recuperacion simple y descontado (Payback), "
        "Relacion Beneficio/Costo (B/C) y analisis de sensibilidad multi-escenario (Optimista +20%, Base, Pesimista -20%) con dictamen de viabilidad; "
        "(2) Matriz de Riesgos Corporativos y Mapa de Calor 5x5 (ISO 31000 / COSO ERM): Gobernanza integral de riesgos estrategicos, financieros, "
        "operacionales, legales y de ciberseguridad, con calculo automatico de riesgo inherente (P x I), definicion de controles mitigantes, "
        "evaluacion de riesgo residual y renderizado interactivo en cuadricula tactica de calor 5x5 en el HUD; "
        "(3) Radar Macroeconomico y Liquidador Laboral Colombia: Telemetria de indicadores oficiales (Dolar TRM, UVT 2026, SMLMV, Auxilio de Transporte, "
        "Tasa de Intervencion BanRep e IPC) y simulador patronal pro-forma con aportes a seguridad social, parafiscales (exoneracion Art. 114-1 E.T.) "
        "y provisiones de prestaciones sociales (Prima, Cesantias, Intereses, Vacaciones) con factor multiplicador real; y "
        "(4) Generador de Pitch Decks y Presentaciones Ejecutivas: Estructuracion de 10 diapositivas maestras para inversionistas o comites estrategicos "
        "siguiendo la metodologia Guy Kawasaki 10/20/30 y Sequoia Capital, con proyeccion en carrusel holografico e impresion en PDF:",
        size=9.0
    )
    builder.add_command_box("Evaluacion de Proyectos VAN / TIR", "Pidale a Liseth: 'Evalua un proyecto con inversion de 50 millones y flujos de 18, 22, 26 y 30 millones con tasa del 12%' o hazlo en el modal HUD.", "Presupuesto de Capital")
    builder.add_command_box("Matriz de Riesgos y Mapa de Calor 5x5", "Supervisa riesgos corporativos, consulta el mapa de calor ISO 31000 y agrega nuevos eventos con controles mitigantes.", "Gobernanza ISO 31000")
    builder.add_command_box("Radar Macro y Liquidador Laboral", "Consulta TRM, UVT o pide: 'Liquida una nomina con salario de 2.500.000 COP' para conocer el costo total empresa y factor prestacional.", "Economia y Laboral Colombia")
    builder.add_command_box("Generador de Pitch Decks (10 Slides)", "Disena presentaciones de inversion estructuradas para startups, consultoria o agroindustria con carrusel interactivo.", "Pitch Decks de Inversion")

    # ───
    # SECCIÓN 28: CADENA DE SUMINISTRO EOQ/ROP, NEGOCIACIÓN HARVARD, TRIBUTARIO DIAN Y OKRS
    # ───
    builder.add_section_header("28. Cadena de Suministro EOQ/ROP, Negociacion Harvard, Tributario DIAN y OKRs")
    builder.add_paragraph(
        "Liseth alcanza su maxima expresion operativa directiva para Senor Santiago con cuatro nuevos motores estrategicos: "
        "(1) Gestion de Cadena de Suministro e Inventarios: Optimizacion cuantitativa del Lote Economico de Pedido (EOQ / Modelo Wilson), "
        "calculo de Punto de Reorden (ROP) con Stock de Seguridad (SS) multi-nivel de servicio (Z = 90% a 99%) y clasificacion ABC por Ley de Pareto 80/20; "
        "(2) Simulador de Negociacion Estrategica (Modelo Harvard): Cuantificacion precisa de la Zona de Posible Acuerdo (ZOPA), excedente negociable, "
        "punto medio equitativo de Nash, identificacion de brechas de impasse y matriz de tacticas basadas en intereses objetivos frente a BATNA / MAAN; "
        "(3) Auditor Tributario DIAN y Regimen Simple (RST): Semaforo preventivo para obligacion de declarar Renta Persona Natural (topes UVT en patrimonio, "
        "ingresos, consumos y consignaciones), comparador financiero de carga impositiva RST vs Regimen Ordinario 35% con ahorro fiscal neto y calendario tributario 2026; y "
        "(4) Cuadro de Mando Integral (Balanced Scorecard) y OKRs Corporativos: Medicion sistematica del progreso en las cuatro perspectivas de Kaplan & Norton "
        "(Financiera, Clientes, Procesos Internos, Aprendizaje & Crecimiento), seguimiento dinamico de Resultados Clave (KRs) e Indice Global de Salud Corporativa:",
        size=9.0
    )
    builder.add_command_box("Optimizacion de Inventarios EOQ & ROP", "Pida a Liseth: 'Calcula el lote economico EOQ para demanda de 10000 unidades y costo de pedido de 50000' o calcule el punto de reorden en el HUD.", "Logistica & Cadena de Suministro")
    builder.add_command_box("Simulador de Negociacion ZOPA / Harvard", "Evalue un acuerdo comercial indicando precio maximo del comprador y minimo del vendedor para conocer la ZOPA y el punto de Nash.", "Negociacion Directiva")
    builder.add_command_box("Auditoria Tributaria DIAN & Regimen Simple", "Compare la carga fiscal del Regimen Simple frente al Ordinario y verifique si supera los topes de renta en UVT 2026.", "Estrategia Tributaria DIAN")
    builder.add_command_box("Cuadro de Mando Balanced Scorecard & OKRs", "Consulte el Indice Global de Salud Corporativa y el avance de los Resultados Clave en las 4 perspectivas directivas.", "OKRs & Balanced Scorecard")

    # ───
    # SECCIÓN 29: PAGO DE IMPUESTOS DIAN (FORM 490 & PSE), VALUACIÓN DCF, FLETES Y BIOCOGNICIÓN
    # ───
    builder.add_section_header("29. Pago de Impuestos DIAN (Form 490 & PSE), Valuacion DCF, Fletes y Biocognicion")
    builder.add_paragraph(
        "Liseth consolida una suite integral de pagos tributarios, finanzas corporativas avanzadas, logistica y alto rendimiento directivo: "
        "(1) Asistente y Pasarela de Pago de Impuestos DIAN (Formulario 490): Liquidacion oficial de tributos nacionales (Renta, Retencion en la Fuente, "
        "IVA, Anticipo RST, ICA), liquidacion sistematica de intereses moratorios dia por dia conforme a la tasa de usura oficial (Art. 635 E.T.), "
        "calculo de sanciones por extemporaneidad con tope minimo legal de 10 UVT (Art. 641 E.T.), generacion de intencion de pago PSE con codigo CUS bancario "
        "y archivo historico de paz y salvo tributario; "
        "(2) Valuacion Financiera de Empresas y Startups: Determinacion cientifica del valor corporativo mediante Flujo de Caja Libre Descontado (DCF), "
        "calculo de Valor Terminal Gordon-Shapiro, descomposicion de Enterprise Value (EV) y Equity Value (Patrimonio), multiplos de mercado EV/EBITDA "
        "y metodo Venture Capital (Pre-money, Post-money y porcentaje de dilucion para inversionistas); "
        "(3) Optimizador de Rutas y Fletes Logísticos en Colombia: Liquidacion de fletes de carga por carretera (Cali, Palmira, Yumbo, Buenaventura, "
        "Bogota, Medellin, Eje Cafetero), consumo de combustible ACPM/Gasolina, peajes INVIAS segun categoria vehicular, desgaste por km y huella de carbono CO2; y "
        "(4) Telemetria Biocognitiva y Habitos Ejecutivos del CEO: Monitor de recuperacion del descanso nocturno, ingesta de agua, bloques de trabajo profundo, "
        "nivel de vigor percibido, cronotipo (Alondra vs Buho), mapeo de horas pico de claridad mental y prescripcion neuro-ergonomica de alto rendimiento directivo:",
        size=9.0
    )
    builder.add_command_box("Liquidacion y Pago de Impuestos DIAN", "Pida a Liseth: 'Liquida el Formulario 490 de retencion en la fuente por 1.850.000 COP y genera el enlace PSE' para pagar de inmediato.", "Pago de Impuestos & PSE")
    builder.add_command_box("Valuacion de Empresas DCF & Multiplos", "Calcule el valor de su compania indicando flujos de caja libre, WACC y tasa de crecimiento, o por multiplo EV/EBITDA de su sector.", "Finanzas Corporativas & DCF")
    builder.add_command_box("Optimizacion de Fletes y Rutas Colombia", "Liquide el costo de transporte de carga entre Palmira y Buenaventura o Bogota con peajes INVIAS y consumo de combustible.", "Logistica & Ruteo Nacional")
    builder.add_command_box("Telemetria Biocognitiva del CEO", "Supervise su vigor diario, cronotipo y horas pico de enfoque para programar decisiones directivas en su momento de maxima claridad mental.", "Salud y Alto Rendimiento CEO")

    # ───
    # SECCIÓN 30: CENTRO DE ACCESIBILIDAD UNIVERSAL, CATÁLOGO DE 30 MÓDULOS HUD Y ATAJOS
    # ───
    builder.add_section_header("30. Centro de Accesibilidad Universal, Catalogo de 36 Modulos HUD y Atajos")
    builder.add_paragraph(
        "Liseth incorpora una arquitectura integral de ergonomia, diseno inclusivo WCAG 2.1 AA/AAA y acceso inmediato a sus 36 modulos tacticos: "
        "(1) Acceso Frontal y Busqueda en Vivo a los 36 Modulos HUD: El boton de modulos se posiciona como prioridad absoluta (#1) en la barra superior "
        "con distintivo neon resplandeciente, complementado con una pildora central '36 Modulos HUD' en el panel principal bajo la esfera y atajo Alt+H; "
        "la ventana de modulos integra un buscador reactivo en vivo que filtra instantaneamente por titulo o funcion ('impuestos', 'fletes', 'nfc', 'valuacion', 'pc'...) "
        "y pestanas tematicas que incluyen la categoria dedicada 'FINANZAS & ESTRATEGIA (8)'; "
        "(2) Navegacion Accesible por Teclado y Skip Links: Enlaces de omision (.skip-link) para saltar de inmediato al chat o a la cuadricula de modulos, "
        "junto a anillos de enfoque (:focus-visible) de alta visibilidad con contorno neon y desplazamiento de seguridad en cada control; "
        "(3) Modo de Alto Contraste Stark (WCAG AAA): Paleta de contraste absoluto con fondo negro (#000000) y acentos cian/oro con ratio superior a 7:1; "
        "(4) Escalabilidad Tipografica y Dislexia: Tamano ajustable a 100%, 115% y 130%, y tipografia de alta legibilidad sin remates con mayor interlineado; "
        "(5) Reduccion de Movimiento y Toques Ergonomicos: Suspension de animaciones complejas segun prefers-reduced-motion y areas tactiles minimas de 44x44px; y "
        "(6) Matriz Ejecutiva de Atajos Globales: Esc para cerrar modales, Alt+A para Accesibilidad, Alt+H para Modulos HUD, Alt+K para el chat, Alt+M para microfono y Alt+V para voz:",
        size=9.0
    )
    builder.add_command_box("Catalogo Completo 36 Modulos HUD (Alt+H)", "Haga clic en '30 MODULOS HUD' en el encabezado, presione la pildora central o Alt+H para desplegar y filtrar los 36 modulos.", "Centro de Control HUD Stark")
    builder.add_command_box("Buscador en Vivo de Modulos", "Escriba en la barra de busqueda dentro del modal ('impuestos', 'fletes', 'nfc'...) para filtrar en tiempo real con contador reactivo.", "Filtro Reactivo de Modulos")
    builder.add_command_box("Centro de Accesibilidad Stark (Alt+A)", "Haga clic en 'ACCESIBILIDAD' o presione Alt+A para personalizar tamano de fuente, alto contraste y animaciones.", "Accesibilidad Universal WCAG")
    builder.add_command_box("Cierre Instantaneo de Modales (Esc)", "Presione la tecla Escape en cualquier momento para cerrar cualquier modal, visor de documentos, pasarela o panel activo.", "Atajos Globales de Seguridad")

    # ───
    # SECCIÓN 31: ECOSISTEMA EJECUTIVO 360: CRECIMIENTO MKT, TALENTO HUMANO 9-BOX Y RADAR CAMBIARIO
    # ───
    builder.add_section_header("31. Crecimiento MKT (CAC/LTV), Talento 9-Box y Radar Cambiario (TRM BanRep)")
    builder.add_paragraph(
        "Liseth expande su suite directiva incorporando tres modulos de alto impacto en gestion empresarial, escalamiento y finanzas internacionales: "
        "(1) Motor de Crecimiento & Unit Economics 360 (MKT): Determinacion matematica del Costo de Adquisicion de Clientes (CAC), Lifetime Value (LTV), "
        "ratio LTV/CAC (benchmark ideal > 3.0x), periodo de recuperacion del CAC (Payback en meses), tasa de churn mensual y anualizada, auditoria de conversion "
        "en las 4 etapas del embudo comercial (Atraccion, Captura MQL, Calificacion SQL y Cierre Won) y atribucion de pauta publicitaria multicanal (ROAS); "
        "(2) Gestion Estrategica de Talento Humano & Matriz 9-Box: Clasificacion cientifica de colaboradores en los 9 cuadrantes de Desempeno vs Potencial "
        "(Estrellas, Futuros Lideres, Profesionales Clave, Especialistas y Dilemas), diseno de planes de sucesion y retencion, medicion de clima organizacional eNPS "
        "y diagnostico financiero del costo oculto de rotacion de personal (turnover) bajo el regimen laboral del Codigo Sustantivo del Trabajo de Colombia; y "
        "(3) Radar Cambiario de Divisas & Cobertura Forward (Hedging): Monitoreo en tiempo real de la TRM oficial de la Superintendencia Financiera / BanRep, "
        "Dolar Cripto USDT (P2P), Dolar Tarjeta de Credito con sobretasas bancarias, paridad Euro/COP y simulador de contratos de cobertura cambiaria Forward "
        "bajo la Paridad de Tasas de Interes (IRP) para blindar el margen de importaciones y exportaciones frente a la volatilidad del peso colombiano:",
        size=9.0
    )
    builder.add_command_box("Diagnostico Unit Economics & CAC/LTV", "Pida a Liseth: 'Calcula los unit economics con CAC de 120.000 COP, ARPU de 65.000 COP y churn del 3%' para auditar la viabilidad de escalamiento.", "Marketing 360 & SaaS")
    builder.add_command_box("Evaluacion de Colaboradores en Matriz 9-Box", "Pida a Liseth: 'Evalua a Juan Perez en la matriz 9-box con desempeno 2.8 y potencial 2.9' para obtener el plan de retencion y sucesion.", "Talento Humano & 9-Box")
    builder.add_command_box("Radar Cambiario TRM & Cobertura Forward", "Pida a Liseth: 'Muestrame el radar de divisas TRM y simula cobertura Forward de 25.000 USD a 90 dias' para proteger compras internacionales.", "Finanzas & Divisas BanRep")

    # ───
    # SECCIÓN 32: GOBIERNO CORPORATIVO ESG, TESORERÍA KTNO & FACTORING RADIAN (36 MÓDULOS)
    # ───
    builder.add_section_header("32. Gobierno Corporativo ESG, Tesoreria KTNO y Factoring RADIAN")
    builder.add_paragraph(
        "Liseth alcanza un nuevo hito de madurez operativa expandiendose a 36 modulos tacticos HUD con dos herramientas de nivel gerencial avanzado: "
        "(1) Gobierno Corporativo & Sostenibilidad ESG (IFRS S1/S2 & GRI): Diagnostico integral de los pilares Ambiental (E - huella de carbono Scope 1/2 y transicion energetica), "
        "Social (S - seguridad en el trabajo, bienestar y equidad de genero) y Gobernanza (G - codigo de etica, transparencia fiscal y comites de auditoria independientes), "
        "calculando la calificacion compuesta (AAA a CCC), nivel de riesgo y la hoja de ruta hacia la certificacion como Empresa B (B Corp) en Colombia; y "
        "(2) Tesoreria Corporativa, Capital de Trabajo (KTNO) y Factoring Electronico: Determinacion cuantitativa del Ciclo de Conversion de Efectivo (CCC = DSO + DIO - DPO) "
        "para identificar liquidez inmovilizada, evaluacion del Capital de Trabajo Neto Operativo (KTNO) y simulador financiero de descuento de facturas comerciales "
        "negociables a traves del sistema oficial RADIAN / DIAN con calculo exacto de Tasa Efectiva Anual (E.A.) y liberacion de liquidez en tiempo record:",
        size=9.0
    )
    builder.add_command_box("Auditoria ESG & Sostenibilidad (IFRS)", "Pida a Liseth: 'Evalua la sostenibilidad ESG de mi empresa con ambiental 82, social 85 y gobernanza 88' para obtener la calificacion compuesta.", "Sostenibilidad & Gobierno ESG")
    builder.add_command_box("Ciclo de Conversion de Efectivo (CCC)", "Pida a Liseth: 'Calcula el ciclo CCC con cobro de 45 dias, inventario de 30 dias y pago a proveedores de 50 dias' para diagnosticar la liquidez.", "Tesoreria & Capital de Trabajo")
    builder.add_command_box("Simulador de Factoring RADIAN / DIAN", "Pida a Liseth: 'Simula factoring para factura de 35.000.000 COP a 60 dias' para calcular el descuento y la tasa efectiva anual.", "Factoring & Liquidez Inmediata")


    # ───
    # SECCIÓN 33: TERMINAL BURSÁTIL CUANTITATIVO, TRADING DE PRECISIÓN Y RADAR DE ACCIONES CON DIVIDENDOS (38 MÓDULOS)
    # ───
    builder.add_section_header("33. Terminal Bursatil Cuantitativo, Trading de Precision y Radar de Dividendos")
    builder.add_paragraph(
        "Liseth alcanza la cúspide de inteligencia bursátil expandiéndose a 38 módulos tácticos HUD con dos herramientas de nivel institucional: "
        "(1) Terminal Bursátil Cuantitativo & Trading de Precisión (Margen de Error Minimizado): Algoritmo de convergencia multi-indicador en tiempo real que evalúa "
        "fuerza relativa (RSI 14 períodos), momentum de convergencia/divergencia (MACD Signal & Histograma) y estructura tendencial (Golden Cross EMA 50 / 200). "
        "Para eliminar la ruina estadística y minimizar el margen de error operacional, el motor calcula dinámicamente el Stop-Loss a 1.5 x ATR (Average True Range), "
        "un Take-Profit matemático con ratio asimétrico favorable 1 : 2.5 y el dimensionamiento exacto de la posición gobernado por la regla institucional estricta "
        "de arriesgar como máximo el 1.5% del capital total de la cuenta por operación. "
        "(2) Radar de Acciones con Dividendos & Portafolios de Presupuesto Ajustado: Rastreador bursátil especializado en empresas defensivas de alto rendimiento por dividendo "
        "(Dividend Yield) en la Bolsa de Valores de Colombia - BVC (Ecopetrol, Grupo Aval Pref., GEB, Mineros, Celsia, Bancolombia Pref., ISA) y Wall Street (Vale, Ford, AT&T, Pfizer, Realty Income 'O'). "
        "Permite armar portafolios diversificados incluso con presupuestos muy reducidos (desde $50.000 COP o $50 USD), calculando el flujo pasivo mensual/anual y proyectando "
        "el crecimiento exponencial mediante planes de reinversión automática de dividendos (DRIP a 1, 3 y 5 años) con interés compuesto:",
        size=9.0
    )
    builder.add_command_box("Trading Cuantitativo de Precision (BVC / Wall Street)", "Pida a Liseth: 'Analiza la accion de Ecopetrol a 1.960 pesos con RSI 44 y cruce alcista MACD con capital de 10 millones' para obtener la orden técnica con Stop-Loss ATR y tamaño de posición.", "Bolsa de Valores & Trading")
    builder.add_command_box("Radar de Dividendos para Presupuesto Reducido", "Pida a Liseth: 'Recomiendame que acciones comprar con presupuesto ajustado de 300.000 pesos que paguen buenos dividendos' para obtener la canasta óptima y flujo anual.", "Portafolio de Dividendos BVC")
    builder.add_command_box("Proyeccion Compuesta de Reinversion (DRIP)", "Pida a Liseth: 'Simula un plan de dividendos con 100 dolares en Wall Street a 5 anos con reinversion DRIP' para proyectar el interés compuesto.", "DRIP Compounding Wall Street")


    # ───
    # SECCIÓN 34: CONCILIACIÓN BANCARIA AUTOMATIZADA, AUDITORÍA GMF (4x1000) Y SIMULACIÓN MONTE CARLO (40 MÓDULOS)
    # ───
    builder.add_section_header("34. Conciliacion Bancaria Oficial, GMF (4x1000) y Simulacion Monte Carlo")
    builder.add_paragraph(
        "Liseth alcanza el hito historico de 40 modulos tacticos HUD integrando dos motores financieros de alta jerarquia corporativa y academica: "
        "(1) Conciliacion Bancaria Automatizada & Auditoria de GMF (4x1000): Motor de cuadre contable riguroso que contrasta saldos de extractos bancarios "
        "con libros auxiliares, determinando de forma automatica partidas conciliatorias (depositos en transito, cheques pendientes de cobro, notas debito por "
        "comisiones y notas credito por abonos directos) para generar el Acta Oficial de Conciliacion. Simultaneamente, audita el Gravamen a los Movimientos "
        "Financieros (GMF 4x1000) del periodo, certificando la exencion legal de hasta 350 UVT mensuales y calculando el 50% deducible en la Declaracion "
        "de Renta (Art. 115 Estatuto Tributario) junto con los asientos contables de ajuste sugeridos. "
        "(2) Simulacion Estocastica Monte Carlo & Stress Testing de Capital: Plataforma de simulacion probabilistica vectorizada de alto rendimiento que ejecuta "
        "entre 1.000 y 10.000 iteraciones aleatorias sobre proyectos de inversion y modelos de negocio. Computa la Probabilidad real de Rentabilidad P(VAN > 0), "
        "el VAN Esperado (media y mediana), la dispersion del riesgo y las metricas de cola institucional: Value at Risk (VaR 95% y VaR 99% de confianza), "
        "clasificando la resiliencia del capital entre Alta Resiliencia, Riesgo Moderado o Fragilidad Financiera con pautas de mitigacion cuantitativa:",
        size=9.0
    )
    builder.add_command_box("Conciliacion Bancaria & GMF (4x1000)", "Pida a Liseth: 'Concilia mi extracto de Bancolombia con saldo de 45 millones contra libros de 42.5 millones, depositos en transito de 5 millones y cheques pendientes de 7.2 millones' para cuadre y beneficio tributario.", "Tesoreria & Auditoria Bancaria")
    builder.add_command_box("Simulacion Monte Carlo de Inversiones (10K Trials)", "Pida a Liseth: 'Ejecuta simulacion Monte Carlo para proyecto de 60 millones con ingresos de 42 millones desv 5 millones y WACC del 11%' para calcular P(VAN > 0) y Value at Risk.", "Stress Testing Monte Carlo")

    # ───
    # SECCIÓN 35: ESTRATEGIA DE PRECIOS & ELASTICIDAD PED, Y SIMULADOR DE CRÉDITOS / AMORTIZACIÓN (42 MÓDULOS)
    # ───
    builder.add_section_header("35. Estrategia de Precios, Elasticidad PED y Simulador de Creditos (42 Modulos)")
    builder.add_paragraph(
        "Liseth alcanza la cifra cumbre de 42 modulos tacticos HUD integrando dos avanzadas herramientas de gestion gerencial y financiera cuantitativa: "
        "(1) Estrategia de Precios, Elasticidad Precio de la Demanda (PED) & Lerner Markup: Diagnostico microeconomico riguroso que determina el coeficiente de elasticidad arco "
        "Ed = [(Q2 - Q1) / ((Q1 + Q2)/2)] / [(P2 - P1) / ((P1 + P2)/2)], clasificando la demanda entre Inelastica (|Ed| < 1), Elastica (|Ed| > 1) o Unitaria (|Ed| = 1). "
        "Calcula la sensibilidad del ingreso total (Price Sensitivity), el precio teorico optimo mediante la Regla del Indice de Lerner P* = MC / (1 + 1/Ed) y simula "
        "la curva de impacto en ingresos y margen de contribucion para variaciones de precio desde -20% hasta +20%. "
        "(2) Simulador de Creditos, Amortizacion Francesa/Alemana y Alerta de Usura SuperFinanciera: Motor financiero corporativo que compara de manera simultanea "
        "el Sistema Frances (cuota mensual fija y abono creciente a capital) frente al Sistema Aleman (abono constante a capital y cuota mensual decreciente), "
        "mostrando el ahorro real en intereses totales. Realiza la conversion exacta de tasas mediante la formula de interes compuesto i_mv = (1 + EA)^(1/12) - 1, "
        "audita la tasa contra el limite legal de Usura de la SuperFinanciera (Art. 305 del Codigo Penal Colombiano, ~28.25% E.A.) y computa el beneficio de "
        "abonos extraordinarios directos a capital para reduccion de plazo o cuota mensual:",
        size=9.0
    )
    builder.add_command_box("Elasticidad de Precios & Lerner Markup", "Pida a Liseth: 'Calcula elasticidad con precio de 50.000 a 55.000 pesos, demanda de 1.000 a 920 unidades y costo marginal de 28.000' para optimizar ingresos y precio optimo.", "Pricing Strategy & Elasticidad PED")
    builder.add_command_box("Simulador de Creditos Frances vs Aleman", "Pida a Liseth: 'Simula un credito de 40 millones a 36 meses con tasa del 18.5% EA y abono extra de 5 millones en mes 6' para comparar cuotas y auditar tasa de usura.", "Finanzas Bancarias & Amortizacion")

    # Final summary note
    builder.add_paragraph(
        "\n*Nota de Mantenimiento:* Este manual se actualiza dinámicamente mediante el script `tools/generate_manual_pdf.py`. "
        "Cada vez que se añada una nueva capacidad, el PDF se recompilará reflejando las nuevas funciones para su comodidad.",
        font="F3", size=8.0, color=(0.4, 0.4, 0.4)
    )

    pdf_bytes = builder.compile()

    # Write to target path
    out_abs = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(out_abs) if os.path.dirname(out_abs) else ".", exist_ok=True)
    with open(out_abs, "wb") as f:
        f.write(pdf_bytes)

    logger_msg = f"[MANUAL] PDF generado exitosamente en: {out_abs} ({len(pdf_bytes):,} bytes)"
    print(logger_msg)
    return out_abs


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "Manual_Liseth.pdf"
    generate_manual_pdf(target)
