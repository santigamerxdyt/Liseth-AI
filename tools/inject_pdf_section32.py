# -*- coding: utf-8 -*-
"""
Injects Section 32 into tools/generate_manual_pdf.py and updates counts to 36 modules.
"""

SECTION_32_CODE = '''    # ───
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
'''

def main():
    path = "tools/generate_manual_pdf.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Update 34 to 36
    content = content.replace("Catalogo de 34 Modulos HUD", "Catalogo de 36 Modulos HUD")
    content = content.replace("sus 34 modulos tacticos", "sus 36 modulos tacticos")
    content = content.replace("34 Modulos HUD", "36 Modulos HUD")
    content = content.replace("filtrar los 34 modulos", "filtrar los 36 modulos")
    content = content.replace("los 34 modulos", "los 36 modulos")

    target = "    # Final summary note"
    if target in content and "SECCIÓN 32:" not in content:
        content = content.replace(target, SECTION_32_CODE + "\n" + target)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("[SUCCESS] Sección 32 inyectada en tools/generate_manual_pdf.py")
    else:
        print("[INFO] Target no encontrado o Sección 32 ya presente")

if __name__ == "__main__":
    main()
