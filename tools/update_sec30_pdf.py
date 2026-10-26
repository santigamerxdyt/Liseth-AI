# -*- coding: utf-8 -*-
"""
Updates Section 30 in tools/generate_manual_pdf.py with HUD Module Catalog & Live Search.
"""

NEW_SECTION_30 = '''    # ───
    # SECCIÓN 30: CENTRO DE ACCESIBILIDAD UNIVERSAL, CATÁLOGO DE 30 MÓDULOS HUD Y ATAJOS
    # ───
    builder.add_section_header("30. Centro de Accesibilidad Universal, Catalogo de 30 Modulos HUD y Atajos")
    builder.add_paragraph(
        "Liseth incorpora una arquitectura integral de ergonomia, diseno inclusivo WCAG 2.1 AA/AAA y acceso inmediato a sus 30 modulos tacticos: "
        "(1) Acceso Frontal y Busqueda en Vivo a los 30 Modulos HUD: El boton de modulos se posiciona como prioridad absoluta (#1) en la barra superior "
        "con distintivo neon resplandeciente, complementado con una pildora central '30 Modulos HUD' en el panel principal bajo la esfera y atajo Alt+H; "
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
    builder.add_command_box("Catalogo Completo 30 Modulos HUD (Alt+H)", "Haga clic en '30 MODULOS HUD' en el encabezado, presione la pildora central o Alt+H para desplegar y filtrar los 30 modulos.", "Centro de Control HUD Stark")
    builder.add_command_box("Buscador en Vivo de Modulos", "Escriba en la barra de busqueda dentro del modal ('impuestos', 'fletes', 'nfc'...) para filtrar en tiempo real con contador reactivo.", "Filtro Reactivo de Modulos")
    builder.add_command_box("Centro de Accesibilidad Stark (Alt+A)", "Haga clic en 'ACCESIBILIDAD' o presione Alt+A para personalizar tamano de fuente, alto contraste y animaciones.", "Accesibilidad Universal WCAG")
    builder.add_command_box("Cierre Instantaneo de Modales (Esc)", "Presione la tecla Escape en cualquier momento para cerrar cualquier modal, visor de documentos, pasarela o panel activo.", "Atajos Globales de Seguridad")
'''

def main():
    path = "tools/generate_manual_pdf.py"
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    idx_start = text.find("# SECCIÓN 30:")
    if idx_start == -1:
        print("[ERROR] SECCIÓN 30 no encontrada")
        return

    # Back up to the comment line start
    comment_start = text.rfind("# ───", 0, idx_start)
    idx_end = text.find("    # Final summary note", idx_start)

    if comment_start != -1 and idx_end != -1:
        updated_text = text[:comment_start] + NEW_SECTION_30.strip() + "\n\n" + text[idx_end:]
        with open(path, "w", encoding="utf-8") as f:
            f.write(updated_text)
        print("[SUCCESS] Sección 30 actualizada en tools/generate_manual_pdf.py")
    else:
        print("[ERROR] Delimitadores no encontrados")

if __name__ == "__main__":
    main()
