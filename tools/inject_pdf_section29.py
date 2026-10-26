# -*- coding: utf-8 -*-
"""
Injects Section 29 into tools/generate_manual_pdf.py safely.
"""

SECTION_29_CODE = '''    # ───
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
'''

def main():
    path = "tools/generate_manual_pdf.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    target = "    # Final summary note"
    if target in content and "SECCIÓN 29:" not in content:
        content = content.replace(target, SECTION_29_CODE + "\n" + target)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("[SUCCESS] Sección 29 inyectada en tools/generate_manual_pdf.py")
    else:
        print("[INFO] Target no encontrado o Sección 29 ya existente")

if __name__ == "__main__":
    main()
