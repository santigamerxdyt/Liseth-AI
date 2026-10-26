# -*- coding: utf-8 -*-
"""
Injects Section 28 into tools/generate_manual_pdf.py safely.
"""

SECTION_28_CODE = '''    # ───
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
'''

def main():
    path = "tools/generate_manual_pdf.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    target = "    # Final summary note"
    if target in content and "SECCIÓN 28:" not in content:
        content = content.replace(target, SECTION_28_CODE + "\n" + target)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("[SUCCESS] Sección 28 inyectada en tools/generate_manual_pdf.py")
    else:
        print("[INFO] Target no encontrado o Sección 28 ya existente")

if __name__ == "__main__":
    main()
