# -*- coding: utf-8 -*-
"""
Injects Section 30 into tools/generate_manual_pdf.py safely.
"""

SECTION_30_CODE = '''    # ───
    # SECCIÓN 30: CENTRO DE ACCESIBILIDAD UNIVERSAL (A11Y), DISEÑO VISUAL MARK 85 Y ATAJOS DE TECLADO
    # ───
    builder.add_section_header("30. Centro de Accesibilidad Universal (A11Y), Diseno Visual Mark 85 y Atajos")
    builder.add_paragraph(
        "Liseth incorpora una arquitectura integral de ergonomia y diseno inclusivo bajo los estandares internacionales WCAG 2.1 nivel AA y AAA, "
        "combinando la estetica futurista Stark Iron Man Mark 85 con maxima accesibilidad visual, motriz y cognitiva: "
        "(1) Navegacion Accesible por Teclado y Skip Links: Incorporacion de enlaces de omision (.skip-link) para saltar de inmediato al campo de texto del chat "
        "o a la cuadricula de modulos HUD sin necesidad de tabulacion exhaustiva; anillos de enfoque de alta visibilidad (:focus-visible) con contorno neon y "
        "desplazamiento de seguridad en todos los elementos interactivos; "
        "(2) Modo de Alto Contraste Stark (WCAG AAA): Activacion de paleta de maximo contraste con fondo negro absoluto (#000000), texto blanco puro y "
        "bordes de acento cian (#00f0ff) y oro (#ffd700), garantizando una relacion de contraste superior a 7:1 para personas con baja vision o condiciones de alta luminosidad; "
        "(3) Escalabilidad Tipografica y Soporte de Dislexia: Selector de tamano de fuente dinamico (100%, 115% y 130%), complementado con un modo de "
        "fuente de alta legibilidad sin remates con mayor interletreado e interlineado para usuarios con dislexia o fatiga visual ejecutiva; "
        "(4) Modo de Reduccion de Movimiento y Ergonomia Tactil: Respeto automatico de la preferencia de sistema prefers-reduced-motion y switch manual para "
        "desactivar rotaciones, pulsaciones 3D y destellos estroboscopicos (prevencion de trastornos vestibulares); dimension minima de toques tactiles de 44x44px "
        "en todos los botones e iconos de la interfaz movil; y "
        "(5) Matriz Ejecutiva de Atajos de Teclado Stark: Operacion ultra rapida sin raton mediante combinaciones globales (Esc para cerrar modales, Alt+A para el "
        "Centro de Accesibilidad, Alt+H para el Centro de Modulos HUD, Alt+K para enfocar el chat, Alt+M para el microfono y Alt+V para la voz de Liseth), "
        "con persistencia automatica en localStorage del navegador:",
        size=9.0
    )
    builder.add_command_box("Centro de Accesibilidad Stark (Alt+A)", "Haga clic en el boton 'ACCESIBILIDAD' del encabezado o presione Alt+A para personalizar tamano de fuente, alto contraste y animaciones.", "Accesibilidad Universal WCAG")
    builder.add_command_box("Modo Alto Contraste (WCAG AAA)", "Active el modo de alto contraste para un fondo negro profundo y acentos cian/oro de maxima visibilidad y cero reflejo.", "Modo Stark Visibilidad Extrema")
    builder.add_command_box("Navegacion sin Raton y Skip Links", "Navegue usando Tab y presione Enter en los Skip Links para saltar directamente al chat (Alt+K) o a los modulos HUD (Alt+H).", "Ergonomia y Teclado Ejecutivo")
    builder.add_command_box("Cierre Instantaneo de Modales (Esc)", "Presione la tecla Escape en cualquier momento para cerrar cualquier modal, visor de documentos, pasarela o panel activo.", "Atajos Globales de Seguridad")
'''

def main():
    path = "tools/generate_manual_pdf.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    target = "    # Final summary note"
    if target in content and "SECCIÓN 30:" not in content:
        content = content.replace(target, SECTION_30_CODE + "\n" + target)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("[SUCCESS] Sección 30 inyectada en tools/generate_manual_pdf.py")
    else:
        print("[INFO] Target no encontrado o Sección 30 ya existente")

if __name__ == "__main__":
    main()
