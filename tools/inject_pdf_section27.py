# -*- coding: utf-8 -*-
"""
Injects Section 27 into tools/generate_manual_pdf.py safely.
"""

SECTION_27_CODE = '''    # ───
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
'''

def main():
    path = "tools/generate_manual_pdf.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    target = "    # Final summary note"
    if target in content and "SECCIÓN 27:" not in content:
        content = content.replace(target, SECTION_27_CODE + "\n" + target)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("[SUCCESS] Sección 27 inyectada en tools/generate_manual_pdf.py")
    else:
        print("[INFO] Target no encontrado o Sección 27 ya existente")

if __name__ == "__main__":
    main()
