"""
Universidad Nacional de Colombia (Sede Palmira) - Pensum & Academic Companion Service.
Plan de Estudios del Programa Curricular de Administración de Empresas.
Facultad de Ingeniería y Administración (FIA).
Acuerdo 19 de 2012 del Consejo de Facultad & Acuerdo 033 de 2007 del CSU.

Proporciona soporte integral para las 10 matrículas / semestres, 166 créditos totales:
- Componente de Fundamentación (35 créditos)
- Componente Disciplinar / Profesional (97 créditos)
- Componente de Libre Elección (34 créditos - 20%)
- Requisitos de grado: 12 créditos de inglés y Trabajo de Grado (80% disciplinar)
- Rutas curriculares: Finanzas, Producción, Mercados, Organizaciones, Economía, Talento Humano y Sistemas
- Base de conocimiento disciplinar por asignatura: fórmulas, teorías, marcos normativos colombianos y metodologías.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger("jarvis.unal_pensum")


# Catálogo completo estructurado de asignaturas del pensum oficial
UNAL_ASIGNATURAS: Dict[str, Dict[str, Any]] = {
    # ─── MATRÍCULA 1 ───
    "1000001": {
        "codigo": "1000001",
        "nombre": "Matemática Básica",
        "creditos": 4,
        "tipologia": "Nivelación",
        "semestre": 1,
        "agrupacion": "Nivelación / Cuantitativa",
        "prerrequisitos": [],
        "temas_clave": ["Álgebra básica", "Ecuaciones e inecuaciones", "Funciones lineales y cuadráticas", "Exponenciales y logaritmos", "Trigonometría"],
        "aplicacion_administracion": "Bases matemáticas para optimización de funciones de costo, ingreso y utilidad empresarial."
    },
    "1000002": {
        "codigo": "1000002",
        "nombre": "Lecto-Escritura",
        "creditos": 4,
        "tipologia": "Nivelación",
        "semestre": 1,
        "agrupacion": "Nivelación / Sociohumanística",
        "prerrequisitos": [],
        "temas_clave": ["Comprensión lectora", "Cohesión y coherencia textual", "Argumentación", "Ensayos académicos", "Normas APA"],
        "aplicacion_administracion": "Habilidad directiva para redacción de informes gerenciales, propuestas comerciales y artículos de investigación."
    },
    "5000877": {
        "codigo": "5000877",
        "nombre": "Sociología del Trabajo",
        "creditos": 3,
        "tipologia": "Fundamentación",
        "semestre": 1,
        "agrupacion": "Sociohumanística",
        "prerrequisitos": [],
        "temas_clave": ["Evolución histórica del trabajo", "División del trabajo", "Relaciones laborales contemporáneas", "Trabajo y nuevas tecnologías", "Alienación y motivación"],
        "aplicacion_administracion": "Comprensión del contexto social de la fuerza laboral y las dinámicas de poder en las organizaciones."
    },
    "5000859": {
        "codigo": "5000859",
        "nombre": "Fundamentos de la Administración y Organizaciones",
        "creditos": 4,
        "tipologia": "Fundamentación",
        "semestre": 1,
        "agrupacion": "Económico Organizacional",
        "prerrequisitos": [],
        "temas_clave": ["Escuelas administrativas (Taylor, Fayol, Mayo, Weber)", "Proceso administrativo (PODC)", "Enfoque sistémico y contingencial", "Responsabilidad social empresarial"],
        "aplicacion_administracion": "Columna vertebral teórica de la gestión: planear, organizar, dirigir y controlar organizaciones de cualquier sector."
    },
    "5000851": {
        "codigo": "5000851",
        "nombre": "Contabilidad",
        "creditos": 3,
        "tipologia": "Fundamentación",
        "semestre": 1,
        "agrupacion": "Económico Organizacional",
        "prerrequisitos": [],
        "temas_clave": ["Partida doble", "Ecuación patrimonial (Activo = Pasivo + Patrimonio)", "PUC y NIIF", "Balance General", "Estado de Resultados"],
        "aplicacion_administracion": "Lenguaje de los negocios: registro sistemático de transacciones y evaluación del desempeño patrimonial."
    },

    # ─── MATRÍCULA 2 ───
    "1000004": {
        "codigo": "1000004",
        "nombre": "Cálculo Diferencial",
        "creditos": 4,
        "tipologia": "Fundamentación",
        "semestre": 2,
        "agrupacion": "Cuantitativa",
        "prerrequisitos": ["1000001"],
        "temas_clave": ["Límites y continuidad", "Derivadas y reglas de derivación", "Optimización (máximos y mínimos)", "Costo marginal e ingreso marginal", "Elasticidad matemática"],
        "aplicacion_administracion": "Maximización de beneficios económicos y minimización de costos de producción mediante derivadas de primer y segundo orden."
    },
    "5000868": {
        "codigo": "5000868",
        "nombre": "Matemática Financiera",
        "creditos": 3,
        "tipologia": "Fundamentación",
        "semestre": 2,
        "agrupacion": "Cuantitativa",
        "prerrequisitos": [],
        "temas_clave": ["Valor del dinero en el tiempo", "Interés simple y compuesto", "Tasas nominales y efectivas", "Anualidades (vencidas, anticipadas, diferidas)", "Sistemas de amortización", "Gradientes aritméticos y geométricos"],
        "aplicacion_administracion": "Cálculo de cuotas de créditos, equivalencia de tasas para evaluación de fuentes de fondeo y costo financiero."
    },
    "5000857": {
        "codigo": "5000857",
        "nombre": "Epistemología de la Investigación en Administración y Organizaciones",
        "creditos": 3,
        "tipologia": "Fundamentación",
        "semestre": 2,
        "agrupacion": "Sociohumanística",
        "prerrequisitos": [],
        "temas_clave": ["Paradigmas científicos (Positivismo, Hermenéutica, Teoría Crítica)", "Construcción del conocimiento administrativo", "Método científico", "Diseño metodológico"],
        "aplicacion_administracion": "Rigor metodológico indispensable para la elaboración del proyecto de grado y diagnósticos de consultoría."
    },
    "5000849": {
        "codigo": "5000849",
        "nombre": "Categorías Económicas",
        "creditos": 3,
        "tipologia": "Fundamentación",
        "semestre": 2,
        "agrupacion": "Económico Organizacional",
        "prerrequisitos": [],
        "temas_clave": ["Mercancía y valor", "Teoría del valor-trabajo vs. utilidad marginal", "Plusvalía y acumulación de capital", "Dinero y circulación", "Modos de producción"],
        "aplicacion_administracion": "Comprensión estructural del sistema económico global y la relación capital-trabajo."
    },
    "5000852": {
        "codigo": "5000852",
        "nombre": "Costos",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 2,
        "agrupacion": "Finanzas",
        "prerrequisitos": ["5000851"],
        "temas_clave": ["Elementos del costo (MPD, MOD, CIF)", "Costeo por órdenes de producción", "Costeo por procesos", "Costeo Basado en Actividades (ABC)", "Punto de equilibrio y margen de contribución"],
        "aplicacion_administracion": "Fijación estratégica de precios de venta, control de pérdidas en planta y análisis costo-volumen-utilidad (CVU)."
    },
    "1000044": {
        "codigo": "1000044",
        "nombre": "Inglés I",
        "creditos": 3,
        "tipologia": "Idioma Extranjero",
        "semestre": 2,
        "agrupacion": "Idioma Extranjero",
        "prerrequisitos": [],
        "temas_clave": ["Gramática básica A1/A2", "Vocabulario general y laboral", "Lectura de textos simples en inglés"],
        "aplicacion_administracion": "Apertura a literatura académica internacional y negocios globales."
    },

    # ─── MATRÍCULA 3 ───
    "5000873": {
        "codigo": "5000873",
        "nombre": "Planeación y Control",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 3,
        "agrupacion": "Teoría de la Organización y Administración Estratégica",
        "prerrequisitos": ["5000859"],
        "temas_clave": ["Planeación estratégica, táctica y operativa", "Misión, visión y valores", "Indicadores de gestión (KPIs)", "Tablero de comando (Balanced Scorecard)", "Sistemas de control"],
        "aplicacion_administracion": "Direccionamiento estratégico organizacional y establecimiento de mecanismos de control y mejora continua."
    },
    "5000875": {
        "codigo": "5000875",
        "nombre": "Presupuestos",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 3,
        "agrupacion": "Finanzas",
        "prerrequisitos": ["5000852"],
        "temas_clave": ["Presupuesto maestro", "Presupuesto de ventas y cobranzas", "Presupuesto de producción y compras", "Presupuesto de caja (Cash Flow)", "Estados financieros presupuestados"],
        "aplicacion_administracion": "Planificación cuantitativa de recursos y prevención de iliquidez operativa."
    },
    "5000871": {
        "codigo": "5000871",
        "nombre": "Microeconomía",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 3,
        "agrupacion": "Economía",
        "prerrequisitos": ["1000004", "5000849"],
        "temas_clave": ["Teoría del consumidor (curvas de indiferencia)", "Teoría del productor e isocuantas", "Estructuras de mercado (competencia perfecta, monopolio, oligopolio)", "Elasticidad precio e ingreso"],
        "aplicacion_administracion": "Toma de decisiones de precios, producción y estrategia competitiva frente a competidores directos."
    },
    "5000866": {
        "codigo": "5000866",
        "nombre": "Legislación Empresarial y Laboral",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 3,
        "agrupacion": "Talento Humano",
        "prerrequisitos": [],
        "temas_clave": ["Código Sustantivo del Trabajo (CST)", "Tipos de contratos laborales en Colombia", "Salarios, recargos y horas extras", "Prestaciones sociales (cesantías, primas, vacaciones)", "Liquidación de nómina", "Derecho comercial y sociedades (SAS)"],
        "aplicacion_administracion": "Blindaje legal de la empresa, cumplimiento normativo laboral y gestión de contratos de trabajo sin contingencias jurídicas."
    },
    "1000013": {
        "codigo": "1000013",
        "nombre": "Probabilidad y Estadística",
        "creditos": 3,
        "tipologia": "Fundamentación",
        "semestre": 3,
        "agrupacion": "Cuantitativa",
        "prerrequisitos": ["1000004"],
        "temas_clave": ["Estadística descriptiva", "Probabilidad clásica y Bayes", "Distribuciones discretas (Binomial, Poisson)", "Distribuciones continuas (Normal, t-Student)", "Muestreo e intervalos de confianza"],
        "aplicacion_administracion": "Tratamiento de la incertidumbre, estimación de demanda y sustento cuantitativo para investigación de mercados."
    },
    "1000045": {
        "codigo": "1000045",
        "nombre": "Inglés II",
        "creditos": 3,
        "tipologia": "Idioma Extranjero",
        "semestre": 3,
        "agrupacion": "Idioma Extranjero",
        "prerrequisitos": ["1000044"],
        "temas_clave": ["Tiempos verbales compuestos", "Redacción de correos en inglés", "Expresión oral profesional"],
        "aplicacion_administracion": "Comunicación con contrapartes internacionales y comprensión de manuales corporativos."
    },

    # ─── MATRÍCULA 4 ───
    "5000865": {
        "codigo": "5000865",
        "nombre": "Legislación Ambiental",
        "creditos": 2,
        "tipologia": "Fundamentación",
        "semestre": 4,
        "agrupacion": "Sociohumanística",
        "prerrequisitos": [],
        "temas_clave": ["Constitución Política de 1991 (Derecho ambiental)", "Ley 99 de 1993", "Licenciamiento ambiental", "Gestión de residuos y emisiones", "Sanciones ambientales y normatividad ISO 14001"],
        "aplicacion_administracion": "Alineación de operaciones empresariales con desarrollo sostenible y normatividad de corporaciones autónomas (CVC, etc.)."
    },
    "5000998": {
        "codigo": "5000998",
        "nombre": "Legislación Tributaria",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 4,
        "agrupacion": "Administración Pública y Derecho",
        "prerrequisitos": [],
        "temas_clave": ["Estatuto Tributario Nacional", "Impuesto sobre la Renta y Complementarios", "Impuesto al Valor Agregado (IVA)", "Retención en la Fuente", "Impuestos territoriales (ICA, Predial)", "Planeación tributaria"],
        "aplicacion_administracion": "Optimización fiscal lícita, cálculo de cargas impositivas y cumplimiento de obligaciones ante la DIAN."
    },
    "5000867": {
        "codigo": "5000867",
        "nombre": "Macroeconomía",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 4,
        "agrupacion": "Economía",
        "prerrequisitos": ["5000871"],
        "temas_clave": ["Cuentas nacionales y PIB", "Modelo IS-LM", "Inflación y política monetaria (Banco de la República)", "Desempleo y Curva de Phillips", "Balanza de pagos y tipo de cambio"],
        "aplicacion_administracion": "Anticipación de ciclos económicos, tasas de interés e impacto de la devaluación sobre compras y ventas de la firma."
    },
    "5000846": {
        "codigo": "5000846",
        "nombre": "Administración Financiera I",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 4,
        "agrupacion": "Finanzas",
        "prerrequisitos": ["5000868"],
        "temas_clave": ["Análisis horizontal y vertical de estados financieros", "Razones financieras (Liquidez, Actividad, Endeudamiento, Rentabilidad)", "Capital de Trabajo Neto Operativo (KTNO)", "EBITDA y Flujo de Caja Operativo"],
        "aplicacion_administracion": "Diagnóstico de la salud financiera de la empresa y gestión del ciclo de conversión del efectivo."
    },
    "5000854": {
        "codigo": "5000854",
        "nombre": "Diseño y Dirección Organizacional",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 4,
        "agrupacion": "Teoría de la Organización y Administración Estratégica",
        "prerrequisitos": ["5000873"],
        "temas_clave": ["Estructuras organizacionales (funcional, divisional, matricial)", "Diseño de puestos y manuales de funciones", "Centralización vs. descentralización", "Liderazgo directivo", "Cultura y clima organizacional"],
        "aplicacion_administracion": "Configuración de organigramas eficientes que respondan a la estrategia corporativa."
    },
    "1000046": {
        "codigo": "1000046",
        "nombre": "Inglés III",
        "creditos": 3,
        "tipologia": "Idioma Extranjero",
        "semestre": 4,
        "agrupacion": "Idioma Extranjero",
        "prerrequisitos": ["1000045"],
        "temas_clave": ["Inglés intermedio B1", "Presentaciones ejecutivas en inglés", "Negociación formal"],
        "aplicacion_administracion": "Participación en rondas de negocios y formulación de pitches en entornos multilenguaje."
    },

    # ─── MATRÍCULA 5 ───
    "5000869": {
        "codigo": "5000869",
        "nombre": "Mercados",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 5,
        "agrupacion": "Mercados",
        "prerrequisitos": [],
        "temas_clave": ["Investigación de mercados", "Segmentación, Targeting y Posicionamiento (STP)", "Marketing Mix (4 Ps: Producto, Precio, Plaza, Promoción)", "Comportamiento del consumidor", "Marketing digital"],
        "aplicacion_administracion": "Creación y captura de valor comercial mediante el conocimiento profundo de las necesidades del cliente."
    },
    "5000879": {
        "codigo": "5000879",
        "nombre": "Teoría Organizacional I",
        "creditos": 4,
        "tipologia": "Disciplinar",
        "semestre": 5,
        "agrupacion": "Teoría de la Organización y Administración Estratégica",
        "prerrequisitos": ["5000871", "5000854"],
        "temas_clave": ["Teoría institucional", "Ecología poblacional de las organizaciones", "Costos de transacción", "Teoría de la agencia", "Poder y conflicto organizacional"],
        "aplicacion_administracion": "Análisis profundo de la supervivencia y evolución de las firmas en mercados complejos."
    },
    "5000863": {
        "codigo": "5000863",
        "nombre": "Historia Económica, Social y Política de Colombia",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 5,
        "agrupacion": "Economía",
        "prerrequisitos": [],
        "temas_clave": ["Economía cafetera y primera industrialización", "Modelo ISI (Sustitución de Importaciones)", "Apertura económica de los 90s", "Conflicto armado y desarrollo rural", "Estructura productiva actual"],
        "aplicacion_administracion": "Comprensión del contexto histórico y territorial donde operan las empresas en Colombia."
    },
    "5000847": {
        "codigo": "5000847",
        "nombre": "Administración Financiera II",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 5,
        "agrupacion": "Finanzas",
        "prerrequisitos": ["5000846"],
        "temas_clave": ["Costo de Capital y WACC", "Estructura óptima de capital (Modigliani-Miller)", "Política de dividendos", "Apalancamiento operativo y financiero (GAO, GAF, GAT)", "Valor Económico Agregado (EVA)"],
        "aplicacion_administracion": "Maximización del valor intrínseco de la empresa mediante decisiones óptimas de financiamiento e inversión de largo plazo."
    },
    "5000864": {
        "codigo": "5000864",
        "nombre": "Investigación de Operaciones",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 5,
        "agrupacion": "Producción",
        "prerrequisitos": ["1000004"],
        "temas_clave": ["Programación lineal y Método Simplex", "Problemas de Transporte y Asignación", "Análisis de sensibilidad y dualidad", "Teoría de Colas y líneas de espera", "Redes y PERT/CPM para gestión de proyectos"],
        "aplicacion_administracion": "Modelado cuantitativo de toma de decisiones para maximizar ganancias y minimizar tiempos/costos en operaciones."
    },
    "1000047": {
        "codigo": "1000047",
        "nombre": "Inglés IV",
        "creditos": 3,
        "tipologia": "Idioma Extranjero",
        "semestre": 5,
        "agrupacion": "Idioma Extranjero",
        "prerrequisitos": ["1000046"],
        "temas_clave": ["Nivel B2", "Lectura crítica de papers científicos en inglés", "Negociación y contratos internacionales"],
        "aplicacion_administracion": "Requisito de grado UNAL y competencia para maestrías o movilidad internacional."
    },

    # ─── MATRÍCULA 6 ───
    "5000845": {
        "codigo": "5000845",
        "nombre": "Administración de Personal",
        "creditos": 4,
        "tipologia": "Disciplinar",
        "semestre": 6,
        "agrupacion": "Talento Humano",
        "prerrequisitos": [],
        "temas_clave": ["Reclutamiento y selección de personal", "Inducción y capacitación", "Evaluación del desempeño", "Compensación salarial e incentivos", "Seguridad y Salud en el Trabajo (SG-SST)"],
        "aplicacion_administracion": "Gestión operativa del ciclo de vida del colaborador en la empresa."
    },
    "5000861": {
        "codigo": "5000861",
        "nombre": "Gestión de la Producción y Calidad",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 6,
        "agrupacion": "Producción",
        "prerrequisitos": ["5000864"],
        "temas_clave": ["Planificación y control de la producción", "Plan Agregado y MRP (Planificación de Requerimientos de Materiales)", "Control Estadístico de Procesos (SPC)", "Gestión de la Calidad Total (TQM) e ISO 9001", "Filosofía Lean Manufacturing y Just in Time (JIT)"],
        "aplicacion_administracion": "Garantía de estándares de excelencia operativa, reducción de mermas y optimización de cadenas de suministro."
    },
    "5000880": {
        "codigo": "5000880",
        "nombre": "Teoría Organizacional II",
        "creditos": 4,
        "tipologia": "Disciplinar",
        "semestre": 6,
        "agrupacion": "Teoría de la Organización y Administración Estratégica",
        "prerrequisitos": ["5000879"],
        "temas_clave": ["Cambio organizacional y aprendizaje", "Teoría del caos y complejidad en organizaciones", "Gobernanza corporativa", "Redes interorganizacionales", "Perspectivas críticas de la administración"],
        "aplicacion_administracion": "Transformación ágil de la cultura empresarial frente a entornos de alta volatilidad (VUCA/BANI)."
    },
    "5000848": {
        "codigo": "5000848",
        "nombre": "Antropología (Optativa)",
        "creditos": 3,
        "tipologia": "Fundamentación",
        "semestre": 6,
        "agrupacion": "Sociohumanística",
        "prerrequisitos": [],
        "temas_clave": ["Antropología cultural", "Ritos, símbolos e identidades", "Etnografía aplicada al consumo"],
        "aplicacion_administracion": "Comprensión antropológica del comportamiento del consumidor y culturas de trabajo."
    },
    "5000878": {
        "codigo": "5000878",
        "nombre": "Sicología Organizacional (Optativa)",
        "creditos": 3,
        "tipologia": "Fundamentación",
        "semestre": 6,
        "agrupacion": "Sociohumanística",
        "prerrequisitos": [],
        "temas_clave": ["Conducta individual y grupal", "Motivación y liderazgo", "Manejo del estrés laboral y burnout", "Dinámicas de equipo"],
        "aplicacion_administracion": "Fomento del bienestar laboral y liderazgo transformacional en equipos de alto rendimiento."
    },
    "5000858": {
        "codigo": "5000858",
        "nombre": "Estadística Aplicada (Optativa)",
        "creditos": 4,
        "tipologia": "Fundamentación",
        "semestre": 6,
        "agrupacion": "Cuantitativa",
        "prerrequisitos": ["1000013"],
        "temas_clave": ["Pruebas de hipótesis paramétricas y no paramétricas", "ANOVA (Análisis de Varianza)", "Regresión múltiple", "Series de tiempo"],
        "aplicacion_administracion": "Validación empírica y pruebas estadísticas para estudios de mercado y finanzas."
    },
    "5000855": {
        "codigo": "5000855",
        "nombre": "Econometría (Optativa)",
        "creditos": 4,
        "tipologia": "Fundamentación",
        "semestre": 6,
        "agrupacion": "Cuantitativa",
        "prerrequisitos": ["1000013"],
        "temas_clave": ["Modelo lineal clásico", "Heterocedasticidad, multicolinealidad y autocorrelación", "Modelos de variables instrumentales"],
        "aplicacion_administracion": "Modelado econométrico para proyecciones de demanda e impacto macroeconómico en la empresa."
    },

    # ─── MATRÍCULA 7 ───
    "5000993": {
        "codigo": "5000993",
        "nombre": "Administración Pública",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 7,
        "agrupacion": "Administración Pública y Derecho",
        "prerrequisitos": ["5000867"],
        "temas_clave": ["Estructura del Estado Colombiano", "Ley 489 de 1998", "Descentralización y ordenamiento territorial", "Políticas públicas (ciclo de diseño, implementación y evaluación)", "Nueva Gestión Pública (NPM)"],
        "aplicacion_administracion": "Articulación entre sector privado y entidades estatales, licitaciones públicas y asociaciones público-privadas (APP)."
    },
    "5000870": {
        "codigo": "5000870",
        "nombre": "Métodos de Investigación en Marketing",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 7,
        "agrupacion": "Mercados",
        "prerrequisitos": ["5000869", "1000013"],
        "temas_clave": ["Diseño de instrumentos (encuestas, focus groups)", "Muestreo probabilístico", "Análisis multivariado de datos de mercado", "Netnografía y analítica web", "Pruebas de concepto y producto"],
        "aplicacion_administracion": "Validación científica de ideas de negocio y reducción del riesgo en lanzamientos comerciales."
    },
    "5000771": {
        "codigo": "5000771",
        "nombre": "Formulación y Evaluación de Proyectos",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 7,
        "agrupacion": "Finanzas",
        "prerrequisitos": ["5000847"],
        "correquisitos": ["5000870"],
        "temas_clave": ["Ciclo de vida del proyecto", "Estudio de mercado y tamaño de planta", "Estudio técnico y localización", "Estudio legal y ambiental", "Estudio financiero (Flujo de fondos, VAN, TIR, Razón B/C, Período de Recuperación)"],
        "aplicacion_administracion": "Estructuración de planes de negocio bancables y evaluación de viabilidad de nuevas inversiones."
    },
    "5000856": {
        "codigo": "5000856",
        "nombre": "Enfoques y Modelos Administrativos",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 7,
        "agrupacion": "Teoría de la Organización y Administración Estratégica",
        "prerrequisitos": ["5000854"],
        "temas_clave": ["Reingeniería de procesos", "Benchmarking", "Outsourcing y cadenas de valor", "Metodologías ágiles (Scrum, Kanban)", "Gestión del conocimiento e innovación"],
        "aplicacion_administracion": "Modernización de modelos de gestión para elevar la competitividad de las empresas."
    },
    "5000860": {
        "codigo": "5000860",
        "nombre": "Gestión Ambiental (Optativa)",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 7,
        "agrupacion": "Teoría de la Organización y Administración Estratégica",
        "prerrequisitos": [],
        "temas_clave": ["Economía circular", "Huella de carbono e hídrica", "Responsabilidad ambiental empresarial (ESG)", "Producción más limpia"],
        "aplicacion_administracion": "Desarrollo de ventajas competitivas a través de la sostenibilidad ambiental corporativa."
    },
    "5000876": {
        "codigo": "5000876",
        "nombre": "Sistemas de Información Administrativos (Optativa)",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 7,
        "agrupacion": "Teoría de la Organización y Administración Estratégica",
        "prerrequisitos": [],
        "temas_clave": ["Sistemas ERP (SAP, Oracle)", "CRM y SCM", "Bases de datos relacionales y SQL", "Business Intelligence (BI) y analítica de datos"],
        "aplicacion_administracion": "Integración tecnológica para la toma de decisiones basada en datos."
    },

    # ─── MATRÍCULA 8 ───
    "5000853": {
        "codigo": "5000853",
        "nombre": "Empresariado y Creación de Empresas",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 8,
        "agrupacion": "Teoría de la Organización y Administración Estratégica",
        "prerrequisitos": [],
        "temas_clave": ["Espíritu emprendedor", "Metodología Lean Startup y Customer Development", "Validación de MVP (Producto Mínimo Viable)", "Modelo de Negocio Canvas", "Financiamiento de startups (Venture Capital, Ángeles Inversionistas, Fondo Emprender)"],
        "aplicacion_administracion": "Creación y escalamiento de nuevas empresas sostenibles y de base tecnológica."
    },
    "5000997": {
        "codigo": "5000997",
        "nombre": "Gestión Pública",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 8,
        "agrupacion": "Administración Pública y Derecho",
        "prerrequisitos": ["5000993"],
        "temas_clave": ["Presupuesto General de la Nación (PGN)", "Contratación estatal (Ley 80 de 1993 y SECOP)", "Modelo Integrado de Planeación y Gestión (MIPG)", "Control fiscal y disciplinario (Contraloría, Procuraduría)", "Gestión por resultados"],
        "aplicacion_administracion": "Liderazgo de entidades públicas y participación en licitaciones del Estado."
    },
    "5000862": {
        "codigo": "5000862",
        "nombre": "Gestión Estratégica del Talento Humano",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 8,
        "agrupacion": "Talento Humano",
        "prerrequisitos": ["5000845"],
        "temas_clave": ["Modelo de gestión por competencias", "Planes de carrera y sucesión", "Compromiso laboral (Engagement)", "Liderazgo transformacional y coaching", "Gestión del cambio y negociación colectiva"],
        "aplicacion_administracion": "Alineación del capital humano con la visión de largo plazo de la compañía."
    },
    "5000996": {
        "codigo": "5000996",
        "nombre": "Economía Colombiana (Optativa)",
        "creditos": 4,
        "tipologia": "Disciplinar",
        "semestre": 8,
        "agrupacion": "Economía",
        "prerrequisitos": ["5000867"],
        "temas_clave": ["Estructura económica sectorial en Colombia", "Déficit fiscal y deuda pública", "Mercado laboral y desempleo estructural", "Sector externo y tratados de libre comercio (TLC)"],
        "aplicacion_administracion": "Lectura crítica del entorno económico nacional para inversiones y expansión corporativa."
    },
    "5000872": {
        "codigo": "5000872",
        "nombre": "Modelos de Desarrollo Económico (Optativa)",
        "creditos": 4,
        "tipologia": "Disciplinar",
        "semestre": 8,
        "agrupacion": "Economía",
        "prerrequisitos": ["5000867"],
        "temas_clave": ["Teorías de crecimiento endógeno", "Desarrollo humano (PNUD)", "Institucionalismo y economía política", "Desarrollo regional y competitividad"],
        "aplicacion_administracion": "Formulación de políticas de desarrollo productivo y clústeres empresariales."
    },

    # ─── MATRÍCULA 9 ───
    "5000850": {
        "codigo": "5000850",
        "nombre": "Consultoría y Asesoría",
        "creditos": 3,
        "tipologia": "Disciplinar",
        "semestre": 9,
        "agrupacion": "Teoría de la Organización y Administración Estratégica",
        "prerrequisitos": ["70% créditos disciplinar"],  # Requisito especial reglamentado
        "temas_clave": ["Metodología de consultoría gerencial", "Diagnóstico organizacional integral", "Herramientas de intervención y solución de problemas", "Elaboración de informes de consultoría", "Consultorio Empresarial UNAL"],
        "aplicacion_administracion": "Práctica profesional directa asesorando pymes y empresas de la región del Valle del Cauca."
    },
    "5000874": {
        "codigo": "5000874",
        "nombre": "Práctica Empresarial",
        "creditos": 6,
        "tipologia": "Disciplinar",
        "semestre": 9,
        "agrupacion": "Práctica y Trabajo de Grado",
        "prerrequisitos": ["80% créditos disciplinar"],  # Requisito: 78 créditos del componente disciplinar
        "temas_clave": ["Inserción laboral profesional", "Desarrollo de proyectos de mejora en empresas", "Aplicación interdisciplinar de saberes", "Ética y responsabilidad profesional"],
        "aplicacion_administracion": "Experiencia laboral profesional supervisada que conecta al estudiante con el sector productivo."
    },

    # ─── MATRÍCULA 10 ───
    "5000943": {
        "codigo": "5000943",
        "nombre": "Trabajo de Grado",
        "creditos": 6,
        "tipologia": "Disciplinar",
        "semestre": 10,
        "agrupacion": "Práctica y Trabajo de Grado",
        "prerrequisitos": ["80% créditos disciplinar"],  # 78 créditos aprobados del componente disciplinar
        "temas_clave": ["Modalidades de grado: 1. Trabajos investigativos (Tesis/Monografía), 2. Prácticas de extensión (Pasantía), 3. Asignaturas de posgrado (Maestría en Administración)"],
        "aplicacion_administracion": "Demostración final de rigor científico y capacidad resolutiva para la obtención del título de Administrador de Empresas de la Universidad Nacional."
    }
}


class UNALPensumService:
    """
    Academic companion service specialized in Universidad Nacional de Colombia (Sede Palmira).
    """

    def get_curriculum_overview(self) -> Dict[str, Any]:
        """Returns the high-level metrics of the UNAL Administration degree."""
        return {
            "universidad": "Universidad Nacional de Colombia",
            "sede": "Sede Palmira",
            "facultad": "Facultad de Ingeniería y Administración (FIA)",
            "programa": "Administración de Empresas",
            "acuerdo_vigente": "Acuerdo 19 de 2012 del Consejo de Facultad (FIA)",
            "creditos_totales": 166,
            "distribucion_creditos": {
                "fundamentacion": {"total": 35, "obligatorios": 28, "optativos": 7},
                "disciplinar": {"total": 97, "obligatorios": 90, "optativos": 7},
                "libre_eleccion": {"total": 34, "porcentaje": "20%"}
            },
            "requisitos_adicionales": {
                "ingles": "12 créditos aprobados o acreditados por examen de suficiencia (Inglés I a IV)",
                "trabajo_de_grado": "Haber aprobado mínimo el 80% del componente disciplinar (78 créditos)",
                "consultoria_asesoria": "Haber aprobado mínimo el 70% del componente disciplinar (68 créditos)",
                "modalidades_grado": ["Trabajos investigativos (Monografía)", "Prácticas de extensión (Pasantía)", "Asignaturas de posgrado (Maestría)"]
            },
            "rutas_profundizacion_palmira": [
                "Comercial / Marketing",
                "Producción / Calidad / Operaciones",
                "Finanzas y Evaluación de Proyectos",
                "Teoría de la Organización y Estrategia",
                "Economía y Entorno",
                "Gestión del Talento Humano",
                "Sistemas de Información y Analítica de Datos"
            ]
        }

    def get_semester_subjects(self, semester_num: int) -> List[Dict[str, Any]]:
        """Returns the list of subjects corresponding to a given semester (1 to 10)."""
        sem = int(semester_num)
        results = []
        for code, sub in UNAL_ASIGNATURAS.items():
            if sub["semestre"] == sem:
                results.append(sub)
        return results

    @staticmethod
    def _normalize(text: str) -> str:
        import unicodedata
        t = unicodedata.normalize('NFKD', text or "")
        return "".join(c for c in t if not unicodedata.combining(c)).lower().strip()

    def get_subject_detail(self, query: str) -> Optional[Dict[str, Any]]:
        """Finds subject by exact code or fuzzy normalized name match."""
        raw_q = (query or "").strip().lower()
        if raw_q in UNAL_ASIGNATURAS:
            return UNAL_ASIGNATURAS[raw_q]

        norm_q = self._normalize(query)
        # 1. Exact normalized name match or containment
        for code, sub in UNAL_ASIGNATURAS.items():
            norm_name = self._normalize(sub["nombre"])
            if norm_q == norm_name or norm_q in norm_name or norm_name in norm_q:
                return sub

        # 2. Token overlap match (e.g. "administracion financiera" matches "Administración Financiera I")
        q_tokens = set(norm_q.split())
        best_match = None
        best_score = 0
        for code, sub in UNAL_ASIGNATURAS.items():
            norm_name = self._normalize(sub["nombre"])
            name_tokens = set(norm_name.split())
            intersection = q_tokens.intersection(name_tokens)
            if len(intersection) > best_score and len(intersection) >= max(1, len(q_tokens) - 1):
                best_score = len(intersection)
                best_match = sub

        return best_match

    def check_prerequisites(self, subject_query: str) -> str:
        """Verifies and reports the prerequisites for any subject in the curriculum."""
        sub = self.get_subject_detail(subject_query)
        if not sub:
            return f"No se encontró la asignatura '{subject_query}' en el pensum de Administración de Empresas de la UNAL Sede Palmira."

        prereqs = sub.get("prerrequisitos", [])
        correqs = sub.get("correquisitos", [])

        prereq_names = []
        for p in prereqs:
            if p in UNAL_ASIGNATURAS:
                prereq_names.append(f"`{UNAL_ASIGNATURAS[p]['nombre']}` (Cód. {p})")
            else:
                prereq_names.append(f"`{p}`")

        correq_names = []
        for c in correqs:
            if c in UNAL_ASIGNATURAS:
                correq_names.append(f"`{UNAL_ASIGNATURAS[c]['nombre']}` (Cód. {c})")
            else:
                correq_names.append(f"`{c}`")

        lines = [
            f"### 📋 Requisitos Académicos: *{sub['nombre']}* (Cód. {sub['codigo']})",
            f"- **Semestre Sugerido**: Matrícula {sub['semestre']} | **Créditos**: {sub['creditos']}",
            f"- **Tipología**: {sub['tipologia']} | **Agrupación**: {sub['agrupacion']}",
            f"- **Prerrequisitos Obligatorios**: {', '.join(prereq_names) if prereq_names else '🟢 Ninguno (No tiene prerrequisito)'}",
            f"- **Correquisitos**: {', '.join(correq_names) if correq_names else '🟢 Ninguno'}",
            f"- **Aporte al Perfil Profesional**: {sub.get('aplicacion_administracion', 'Formación integral del Administrador.')}",
        ]

        if "80% créditos disciplinar" in prereqs:
            lines.append("\n> **⚠️ Requisito Especial de Egreso:** Para matricular Trabajo de Grado o Práctica Empresarial debe contar con **al menos 78 créditos aprobados** en el componente disciplinar (80%).")

        if "70% créditos disciplinar" in prereqs:
            lines.append("\n> **📌 Requisito Especial:** Para matricular Consultoría y Asesoría debe contar con **al menos 68 créditos aprobados** en el componente disciplinar (70%).")

        return "\n".join(lines)

    def generate_subject_academic_briefing(self, subject_query: str) -> str:
        """
        Produces a rich, executive academic cheat sheet for any subject in the UNAL curriculum,
        covering core theories, formulas, Colombian legal frameworks, and practical applications.
        """
        sub = self.get_subject_detail(subject_query)
        if not sub:
            return f"No se encontró la asignatura '{subject_query}' en el pensum oficial de la UNAL Sede Palmira."

        lines = [
            f"### 🎓 Guía Académica Integral: *{sub['nombre']}* (Cód. {sub['codigo']})",
            f"**Programa**: Administración de Empresas — Universidad Nacional de Colombia (Sede Palmira)",
            f"**Ubicación Curricular**: Semestre {sub['semestre']} | **Créditos**: {sub['creditos']} ({sub['tipologia']})\n",
            f"#### 1. Agrupación Disciplinar",
            f"Pertenece a la agrupación de **{sub['agrupacion']}**.\n",
            f"#### 2. Ejes Temáticos Fundamentales",
        ]
        for t in sub.get("temas_clave", []):
            lines.append(f"- **{t}**")

        lines.extend([
            "",
            f"#### 3. Aplicación Gerencial y Profesional",
            f"{sub.get('aplicacion_administracion')}\n",
            f"#### 4. Soporte y Asistencia de Liseth para esta Materia",
            f"Durante el cursado de **{sub['nombre']}**, puedo asistirle inmediatamente en:",
            f"- Resolución y explicación paso a paso de ejercicios prácticos, cálculos cuantitativos y modelos.",
            f"- Redacción de ensayos, monografías y reportes de lectura bajo Normas APA 7ª Edición.",
            f"- Búsqueda de artículos científicos indexados en bases de datos abiertas (OpenAlex/arXiv) pertinentes para los talleres.",
            f"- Generación de hojas de cálculo de soporte en Excel con fórmulas auditadas.\n",
            f"> **💡 Consejo para Santiago:** Avíseme cuando tenga un taller, parcial o caso de estudio de *{sub['nombre']}* para estructurarlo con el estándar de excelencia exigido por la Universidad Nacional."
        ])

        return "\n".join(lines)

    def calculate_graduation_checklist(self, approved_disciplinary_credits: int = 0) -> str:
        """Computes graduation milestone criteria according to UNAL Palmira regulations."""
        disc = int(approved_disciplinary_credits)
        req_consultoria = 68  # 70% of 97
        req_grado = 78        # 80% of 97

        can_consultoria = disc >= req_consultoria
        can_grado = disc >= req_grado

        lines = [
            "### 🎯 Checklist de Avance Curricular — UNAL Sede Palmira",
            f"**Estudiante**: Señor Santiago | **Programa**: Administración de Empresas (Acuerdo 19 de 2012 FIA)\n",
            "#### 1. Componentes del Plan de Estudios (166 Créditos Exigidos)",
            "- **Componente de Fundamentación**: 35 créditos (28 obligatorios + 7 optativos)",
            "- **Componente Disciplinar / Profesional**: 97 créditos (90 obligatorios + 7 optativos)",
            "- **Componente de Libre Elección**: 34 créditos (20% del total)\n",
            f"#### 2. Hitos Críticos para Créditos Disciplinares Registrados (`{disc} / 97 cr`)",
            f"- **Consultoría y Asesoría (70% = 68 cr disciplinares)**: {'✅ Habilitado para matricular' if can_consultoria else f'⏳ Faltan {req_consultoria - disc} créditos disciplinares'}",
            f"- **Práctica Empresarial (80% = 78 cr disciplinares)**: {'✅ Habilitado para matricular' if can_grado else f'⏳ Faltan {req_grado - disc} créditos disciplinares'}",
            f"- **Trabajo de Grado (80% = 78 cr disciplinares)**: {'✅ Habilitado para matricular' if can_grado else f'⏳ Faltan {req_grado - disc} créditos disciplinares'}\n",
            "#### 3. Requisito de Lengua Extranjera",
            "- **Inglés**: 12 créditos aprobados en los niveles I, II, III y IV (o suficiencia certificada ante la DRE / Dirección Académica).\n",
            "#### 4. Modalidades de Trabajo de Grado Disponibles (Art. 5)",
            "1. **Trabajo Investigativo:** Tesis o monografía sobre un problema empírico o teórico de la administración.",
            "2. **Práctica de Extensión (Pasantía):** Convenio empresarial reglamentado (No acumulable simultáneamente con Práctica Empresarial).",
            "3. **Asignaturas de Posgrado:** Cursar y aprobar materias de la Maestría en Administración de la Facultad de Ingeniería y Administración."
        ]
        return "\n".join(lines)

    def get_pensum_overview(self) -> Dict[str, Any]:
        """Returns the high-level metrics of the UNAL Administration degree (flat + nested)."""
        base = self.get_curriculum_overview()
        base.update({
            "total_creditos": 166,
            "fundamentacion_creditos": 35,
            "disciplinar_creditos": 97,
            "libre_eleccion_creditos": 34,
            "duracion_semestres": 10,
        })
        return base

    def get_subject_details(self, query: str) -> Optional[Dict[str, Any]]:
        """Alias for get_subject_detail."""
        return self.get_subject_detail(query)

    def get_prerequisites_chain(self, query: str) -> Dict[str, Any]:
        """Returns structured dictionary of subject and its prerequisites."""
        sub = self.get_subject_detail(query)
        if not sub:
            return {"error": f"Asignatura '{query}' no encontrada"}

        direct = []
        for p in sub.get("prerrequisitos", []):
            if p in UNAL_ASIGNATURAS:
                direct.append(UNAL_ASIGNATURAS[p])
            else:
                direct.append({"codigo": p, "nombre": p, "creditos": 0})

        return {
            "materia": sub,
            "prerrequisitos_directos": direct,
            "correquisitos": sub.get("correquisitos", [])
        }

    def audit_graduation_checklist(self, credits_approved: int = 0) -> Dict[str, Any]:
        """Computes graduation milestone criteria dictionary and formatted report."""
        cr = int(credits_approved or 0)
        disc_cr = min(cr, 97) if cr <= 97 else int(cr * (97 / 166))

        pct = round((cr / 166.0) * 100.0, 1) if cr <= 166 else 100.0
        can_consultoria = disc_cr >= 68 or cr >= 115
        can_grado = disc_cr >= 78 or cr >= 132

        report_str = self.calculate_graduation_checklist(disc_cr)
        return {
            "creditos_ingresados": cr,
            "porcentaje_avance": pct,
            "consultoria_habilitada": can_consultoria,
            "trabajo_grado_habilitado": can_grado,
            "reporte_formateado": report_str
        }

    def get_normative_framework(self, query: str = "") -> str:
        """Returns Colombian legal/normative summary applicable to Business Administration."""
        q = self._normalize(query or "")
        if any(w in q for w in ["contratacion", "publica", "ley 80", "estatal", "licitacion", "secop"]):
            return (
                "### 📜 Marco Normativo de Contratación Pública en Colombia\n\n"
                "- **Norma Principal:** Estatuto General de Contratación de la Administración Pública (Ley 80 de 1993, Ley 1150 de 2007 y Decreto 1082 de 2015).\n"
                "- **Modalidades de Selección:**\n"
                "  1. Licitación Pública (regla general).\n"
                "  2. Selección Abreviada (menor cuantía, bienes y servicios de características uniformes).\n"
                "  3. Concurso de Méritos (consultoría e interventoría).\n"
                "  4. Contratación Directa (urgencia manifiesta, contratos interadministrativos, prestación de servicios profesionales).\n"
                "  5. Mínima Cuantía (hasta el 10% de la menor cuantía de la entidad).\n"
                "- **Plataforma SECOP II:** Sistema Electrónico de Contratación Pública para trazabilidad y transparencia obligatoria."
            )
        elif any(w in q for w in ["laboral", "trabajo", "cst", "nomina", "contrato"]):
            return (
                "### ⚖️ Marco Normativo Laboral Colombiano (Administración de Empresas - UNAL Palmira)\n\n"
                "- **Norma Principal:** Código Sustantivo del Trabajo (CST) y Ley 50 de 1990.\n"
                "- **Elementos Esenciales del Contrato (Art. 23 CST):** Prestación personal del servicio, continua subordinación o dependencia, y retribución (salario).\n"
                "- **Jornada Laboral (Ley 2101 de 2021):** Reducción gradual hacia 42 horas semanales sin disminución salarial.\n"
                "- **Prestaciones Sociales Legales:**\n"
                "  - Prima de servicios: 1 mes de salario por año (pagadera en junio y diciembre).\n"
                "  - Cesantías: 1 mes de salario por año consignado al fondo antes del 15 de febrero.\n"
                "  - Intereses sobre cesantías: 12% anual pagadero al trabajador en enero.\n"
                "  - Vacaciones: 15 días hábiles remunerados por año laborado (Art. 186 CST).\n"
                "- **Seguridad Social Integral (Ley 100 de 1993):** Salud (8.5% empleador, 4% empleado), Pensión (12% empleador, 4% empleado), ARL (según nivel de riesgo I a V) y Aportes Parafiscales (SENA, ICBF, Caja de Compensación: 9% total)."
            )
        elif any(w in q for w in ["tributario", "dian", "impuesto", "renta", "iva", "ica"]):
            return (
                "### 🏛️ Marco Normativo Tributario Colombiano (DIAN)\n\n"
                "- **Norma Principal:** Estatuto Tributario Nacional (Decreto 624 de 1989 y reformas tributarias).\n"
                "- **Impuesto sobre la Renta de Personas Jurídicas:** Tarifa general vigente (35%). Obligación de liquidar sobre renta líquida gravable o renta presuntiva.\n"
                "- **Impuesto al Valor Agregado (IVA):** Impuesto indirecto de orden nacional. Tarifa general del 19%, con tarifas diferenciales y bienes exentos/excluidos.\n"
                "- **Retención en la Fuente:** Mecanismo de recaudo anticipado del impuesto sobre la renta, IVA e ICA.\n"
                "- **Impuesto de Industria y Comercio (ICA):** Impuesto municipal sobre actividades industriales, comerciales o de servicios (Palmira / Cali)."
            )
        elif any(w in q for w in ["ambiental", "sostenibilidad", "ley 99", "cvc"]):
            return (
                "### 🌱 Marco Normativo Ambiental Colombiano (Ley 99 de 1993)\n\n"
                "- **Sistema Nacional Ambiental (SINA):** Marco regulatorio coordinado por el Ministerio de Ambiente y Desarrollo Sostenible.\n"
                "- **Autoridad Regional (Valle del Cauca):** CVC (Corporación Autónoma Regional del Valle del Cauca).\n"
                "- **Obligaciones Empresariales:** Licenciamiento ambiental, permisos de vertimientos, concesiones de aguas y plan de manejo integral de residuos sólidos (PGIRS)."
            )
        else:
            return (
                "### 📚 Marcos Normativos Colombianos Clave para Administración de Empresas (UNAL Palmira)\n\n"
                "1. **Código Sustantivo del Trabajo (CST):** Relaciones laborales, contratación, salarios y prestaciones sociales.\n"
                "2. **Estatuto Tributario (DIAN):** Impuesto sobre la renta, IVA, retención en la fuente e ICA.\n"
                "3. **Ley 80 de 1993 y Ley 1150 de 2007:** Contratación pública estatal y plataformas SECOP.\n"
                "4. **Ley 99 de 1993:** Normatividad ambiental y desarrollo sostenible.\n"
                "5. **Código de Comercio (Decreto 410 de 1971):** Sociedades comerciales (SAS - Ley 1258 de 2008) y títulos valores."
            )


# Global Singleton
unal_pensum_service = UNALPensumService()
