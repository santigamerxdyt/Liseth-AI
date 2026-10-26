# -*- coding: utf-8 -*-
"""
Injects Section 31 and updates Section 30 to 34 modules in tools/generate_manual_pdf.py.
"""

SECTION_31_CODE = '''    # ───
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
'''

def main():
    path = "tools/generate_manual_pdf.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Update 30 modules references in Section 30 to 34 modules
    content = content.replace("Catalogo de 30 Modulos HUD", "Catalogo de 34 Modulos HUD")
    content = content.replace("sus 30 modulos tacticos", "sus 34 modulos tacticos")
    content = content.replace("30 Modulos HUD", "34 Modulos HUD")
    content = content.replace("filtrar los 30 modulos", "filtrar los 34 modulos")
    content = content.replace("los 30 modulos", "los 34 modulos")

    target = "    # Final summary note"
    if target in content and "SECCIÓN 31:" not in content:
        content = content.replace(target, SECTION_31_CODE + "\n" + target)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("[SUCCESS] Sección 31 inyectada con éxito en tools/generate_manual_pdf.py")
    else:
        print("[INFO] Target no encontrado o Sección 31 ya presente")

if __name__ == "__main__":
    main()
