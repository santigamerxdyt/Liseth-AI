# -*- coding: utf-8 -*-
"""
Patch script to inject Universal Accessibility (WCAG 2.1 AA/AAA) and
Iron Man Mark 85 Visual Enhancements into jarvis.html,
and synchronize to index.html and app/static/index.html.
"""
import os
import shutil

CSS_A11Y_INJECTION = """
    /* ======================================================== */
    /* ACCESIBILIDAD UNIVERSAL & ALTO RENDIMIENTO VISUAL (A11Y) */
    /* ======================================================== */
    
    /* Skip Links para Navegación Rápida por Teclado */
    .skip-link {
      position: absolute;
      top: -70px;
      left: 16px;
      background: var(--accent-blue);
      color: #04070d;
      font-weight: 700;
      padding: 12px 20px;
      border-radius: 8px;
      z-index: 99999;
      text-decoration: none;
      transition: top 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
      font-size: 0.88rem;
      box-shadow: 0 0 20px rgba(0, 210, 255, 0.8);
    }
    .skip-link:focus, .skip-link:focus-visible {
      top: 16px;
      outline: 3px solid #ffffff;
      outline-offset: 3px;
    }

    /* Anillo de Enfoque de Alta Visibilidad Accesible (:focus-visible) */
    :focus-visible {
      outline: 2px solid var(--accent-blue) !important;
      outline-offset: 3px !important;
      box-shadow: 0 0 16px rgba(0, 210, 255, 0.75) !important;
    }

    /* Soporte de Reducción de Movimiento (Vestibular A11y) */
    @media (prefers-reduced-motion: reduce) {
      *, ::before, ::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
      }
      .sphere-wrap, .hud-deck-pulse, .ambient-grid, .hud-scanline {
        animation: none !important;
      }
    }

    /* Modo Reducción de Movimiento Forzado por Usuario */
    body.a11y-reduced-motion *, body.a11y-reduced-motion ::before, body.a11y-reduced-motion ::after {
      animation: none !important;
      transition: none !important;
    }

    /* Modo de Alto Contraste Stark (WCAG AAA - Ratio > 7:1) */
    body.a11y-high-contrast {
      --bg-primary: #000000 !important;
      --bg-secondary: #050505 !important;
      --bg-card: #0a0a0a !important;
      --border-card: #00f0ff !important;
      --border-user: #ffd700 !important;
      --text-main: #ffffff !important;
      --text-muted: #e2e8f0 !important;
      --accent-blue: #00f0ff !important;
      --accent-glow: rgba(0, 240, 255, 0.9) !important;
    }
    body.a11y-high-contrast .hud-card {
      border: 2px solid #00f0ff !important;
      background: #000000 !important;
    }
    body.a11y-high-contrast .hud-card-desc,
    body.a11y-high-contrast .chat-bubble,
    body.a11y-high-contrast p {
      color: #ffffff !important;
    }
    body.a11y-high-contrast .modal-card {
      border: 2px solid #00f0ff !important;
      background: #000000 !important;
    }

    /* Escalas Tipográficas Accesibles */
    body.a11y-font-lg {
      font-size: 115% !important;
    }
    body.a11y-font-xl {
      font-size: 130% !important;
    }
    body.a11y-dyslexia {
      font-family: Arial, Helvetica, -apple-system, sans-serif !important;
      letter-spacing: 0.06em !important;
      word-spacing: 0.12em !important;
      line-height: 1.8 !important;
    }

    /* Áreas Táctiles Mínimas Accesibles (44x44px min para móviles y pantallas táctiles) */
    .icon-btn, .hud-deck-btn, .modal-close, button {
      min-height: 44px;
      min-width: 44px;
    }

    /* Efectos Visuales Holográficos Mark 85: Esquinas Tácticas & Scanline */
    .hud-card {
      position: relative;
      transition: all 0.28s cubic-bezier(0.2, 0.8, 0.2, 1);
    }
    .hud-card::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      background: linear-gradient(180deg, rgba(0, 210, 255, 0.04) 0%, transparent 100%);
      border-radius: inherit;
    }
    .hud-card:hover {
      transform: translateY(-3px) scale(1.015);
      border-color: var(--accent-blue);
      box-shadow: 0 0 24px rgba(0, 210, 255, 0.35), inset 0 0 14px rgba(0, 210, 255, 0.15);
    }
"""

SKIP_LINKS_INJECTION = """
  <!-- Saltos de Teclado Accesibles (WCAG 2.1) -->
  <a href="#user-input" class="skip-link">Saltar al campo de entrada de chat (Alt+K)</a>
  <a href="#btn-hud-menu" class="skip-link">Saltar al Centro de Módulos HUD (Alt+H)</a>
"""

HEADER_BUTTON_INJECTION = """
        <!-- BOTÓN ACCESIBILIDAD UNIVERSAL STARK (A11Y) -->
        <button class="hud-deck-btn" id="btn-a11y-panel" title="Centro de Accesibilidad Universal (Escala de texto, Alto contraste, Lector y Atajos) - Alt+A">
          <span class="hud-deck-icon">♿</span>
          <span>ACCESIBILIDAD</span>
          <span class="hud-deck-badge" id="a11y-badge">A11Y</span>
        </button>
"""

MODAL_A11Y_INJECTION = """
  <!-- ======================================================== -->
  <!-- MODAL: CENTRO DE ACCESIBILIDAD UNIVERSAL STARK (A11Y)    -->
  <!-- ======================================================== -->
  <div class="modal-overlay" id="a11y-modal" role="dialog" aria-modal="true" aria-labelledby="a11y-title">
    <div class="modal-card" style="max-width: 680px;">
      <div class="modal-header">
        <div class="modal-icon" style="color: #00d2ff; border-color: rgba(0, 210, 255, 0.4); background: rgba(0, 210, 255, 0.12);">♿</div>
        <div class="modal-title">
          <h2 id="a11y-title">Centro de Accesibilidad Universal & Ergonomía</h2>
          <p>Conformidad WCAG 2.1 AA/AAA: escala tipográfica, contraste, reducción de movimiento y atajos</p>
        </div>
        <button class="modal-close" onclick="closeA11yModal()" aria-label="Cerrar panel de accesibilidad">&times;</button>
      </div>

      <!-- Controles de Accesibilidad -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
        
        <!-- Escala de Fuente -->
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(0, 210, 255, 0.3); border-radius: 8px; padding: 12px;">
          <div style="font-size: 0.8rem; font-weight: 700; color: #00d2ff; margin-bottom: 6px;">🔠 TAMAÑO DE TEXTO / ESCALA</div>
          <p style="font-size: 0.72rem; color: #94a3b8; margin-bottom: 8px;">Ajusta el tamaño tipográfico en toda la interfaz:</p>
          <div style="display: flex; gap: 6px;">
            <button type="button" class="btn-secondary" style="flex: 1; padding: 6px 8px; font-size: 0.75rem;" onclick="setA11yFontSize('normal')">100%</button>
            <button type="button" class="btn-secondary" style="flex: 1; padding: 6px 8px; font-size: 0.75rem;" onclick="setA11yFontSize('lg')">115%</button>
            <button type="button" class="btn-secondary" style="flex: 1; padding: 6px 8px; font-size: 0.75rem;" onclick="setA11yFontSize('xl')">130%</button>
          </div>
        </div>

        <!-- Modo Alto Contraste -->
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 209, 102, 0.3); border-radius: 8px; padding: 12px;">
          <div style="font-size: 0.8rem; font-weight: 700; color: #ffd166; margin-bottom: 6px;">👁️ ALTO CONTRASTE (WCAG AAA)</div>
          <p style="font-size: 0.72rem; color: #94a3b8; margin-bottom: 8px;">Fondo negro absoluto y colores de máxima visibilidad:</p>
          <button type="button" class="btn-primary" id="btn-toggle-high-contrast" style="width: 100%; padding: 6px 10px; font-size: 0.78rem;" onclick="toggleHighContrast()">
            Alternar Alto Contraste
          </button>
        </div>

        <!-- Reducción de Movimiento -->
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 239, 125, 0.3); border-radius: 8px; padding: 12px;">
          <div style="font-size: 0.8rem; font-weight: 700; color: #38ef7d; margin-bottom: 6px;">🚫 REDUCCIÓN DE MOVIMIENTO</div>
          <p style="font-size: 0.72rem; color: #94a3b8; margin-bottom: 8px;">Desactiva giros, pulsaciones y animaciones rápidas:</p>
          <button type="button" class="btn-secondary" id="btn-toggle-motion" style="width: 100%; padding: 6px 10px; font-size: 0.78rem;" onclick="toggleReducedMotion()">
            Alternar Animaciones
          </button>
        </div>

        <!-- Fuente para Dislexia -->
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(217, 70, 239, 0.3); border-radius: 8px; padding: 12px;">
          <div style="font-size: 0.8rem; font-weight: 700; color: #d946ef; margin-bottom: 6px;">📖 ALTA LEGIBILIDAD (DISLEXIA)</div>
          <p style="font-size: 0.72rem; color: #94a3b8; margin-bottom: 8px;">Tipografía sin remates con mayor interletreado:</p>
          <button type="button" class="btn-secondary" id="btn-toggle-dyslexia" style="width: 100%; padding: 6px 10px; font-size: 0.78rem;" onclick="toggleDyslexiaFont()">
            Alternar Fuente Clara
          </button>
        </div>

      </div>

      <!-- Guía de Atajos de Teclado Stark -->
      <div style="background: rgba(15, 23, 42, 0.8); border: 1px dashed rgba(255,255,255,0.2); border-radius: 8px; padding: 12px; margin-bottom: 12px;">
        <div style="font-size: 0.8rem; font-weight: 700; color: #e2e8f0; margin-bottom: 8px;">⌨️ ATAJOS DE TECLADO EJECUTIVOS (NAVEGACIÓN RÁPIDA)</div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.76rem; color: #cbd5e1;">
          <div><kbd style="background: #1e293b; padding: 2px 6px; border-radius: 4px; border: 1px solid #475569; color: #00d2ff;">Esc</kbd> : Cerrar cualquier modal o menú activo</div>
          <div><kbd style="background: #1e293b; padding: 2px 6px; border-radius: 4px; border: 1px solid #475569; color: #00d2ff;">Alt + K</kbd> : Enfocar el campo de entrada de chat</div>
          <div><kbd style="background: #1e293b; padding: 2px 6px; border-radius: 4px; border: 1px solid #475569; color: #00d2ff;">Alt + H</kbd> : Abrir Centro de Módulos HUD (30)</div>
          <div><kbd style="background: #1e293b; padding: 2px 6px; border-radius: 4px; border: 1px solid #475569; color: #00d2ff;">Alt + A</kbd> : Abrir este Panel de Accesibilidad</div>
          <div><kbd style="background: #1e293b; padding: 2px 6px; border-radius: 4px; border: 1px solid #475569; color: #00d2ff;">Alt + M</kbd> : Activar / Detener micrófono de voz</div>
          <div><kbd style="background: #1e293b; padding: 2px 6px; border-radius: 4px; border: 1px solid #475569; color: #00d2ff;">Alt + V</kbd> : Conmutar voz de Liseth (habla)</div>
        </div>
      </div>

      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeA11yModal()">Cerrar</button>
      </div>
    </div>
  </div>
"""

JS_A11Y_ENGINE = """
      // ========================================================
      // MOTOR DE ACCESIBILIDAD UNIVERSAL (A11Y) & TECLADO STARK
      // ========================================================
      window.openA11yModal = function() {
        const m = document.getElementById("a11y-modal");
        if (m) m.classList.add("active");
        playHudSound("open");
      };

      window.closeA11yModal = function() {
        const m = document.getElementById("a11y-modal");
        if (m) m.classList.remove("active");
        playHudSound("close");
      };

      window.setA11yFontSize = function(size) {
        document.body.classList.remove("a11y-font-lg", "a11y-font-xl");
        if (size === "lg") document.body.classList.add("a11y-font-lg");
        if (size === "xl") document.body.classList.add("a11y-font-xl");
        localStorage.setItem("liseth_a11y_fontsize", size);
        showToast("Tamaño de texto actualizado");
        playHudSound("click");
      };

      window.toggleHighContrast = function() {
        document.body.classList.toggle("a11y-high-contrast");
        const active = document.body.classList.contains("a11y-high-contrast");
        localStorage.setItem("liseth_a11y_contrast", active ? "1" : "0");
        showToast(active ? "Modo Alto Contraste Activado" : "Alto Contraste Desactivado");
        playHudSound("click");
      };

      window.toggleReducedMotion = function() {
        document.body.classList.toggle("a11y-reduced-motion");
        const active = document.body.classList.contains("a11y-reduced-motion");
        localStorage.setItem("liseth_a11y_motion", active ? "1" : "0");
        showToast(active ? "Reducción de Movimiento Activada" : "Movimiento Normal");
        playHudSound("click");
      };

      window.toggleDyslexiaFont = function() {
        document.body.classList.toggle("a11y-dyslexia");
        const active = document.body.classList.contains("a11y-dyslexia");
        localStorage.setItem("liseth_a11y_dyslexia", active ? "1" : "0");
        showToast(active ? "Fuente de Alta Legibilidad Activada" : "Fuente Estándar");
        playHudSound("click");
      };

      // Cargar preferencias A11y persistidas
      function loadPersistedA11y() {
        const fs = localStorage.getItem("liseth_a11y_fontsize");
        if (fs === "lg") document.body.classList.add("a11y-font-lg");
        if (fs === "xl") document.body.classList.add("a11y-font-xl");

        if (localStorage.getItem("liseth_a11y_contrast") === "1") {
          document.body.classList.add("a11y-high-contrast");
        }
        if (localStorage.getItem("liseth_a11y_motion") === "1") {
          document.body.classList.add("a11y-reduced-motion");
        }
        if (localStorage.getItem("liseth_a11y_dyslexia") === "1") {
          document.body.classList.add("a11y-dyslexia");
        }
      }

      // Controlador Global de Atajos de Teclado Accesibles
      window.addEventListener("keydown", function(e) {
        // 1. Escape cierra cualquier modal activo
        if (e.key === "Escape") {
          const activeModals = document.querySelectorAll(".modal-overlay.active");
          if (activeModals && activeModals.length > 0) {
            activeModals.forEach(m => m.classList.remove("active"));
            playHudSound("close");
            e.preventDefault();
            return;
          }
        }

        // 2. Alt + A: Abrir panel de accesibilidad
        if (e.altKey && (e.key === "a" || e.key === "A")) {
          e.preventDefault();
          const m = document.getElementById("a11y-modal");
          if (m && m.classList.contains("active")) {
            closeA11yModal();
          } else {
            openA11yModal();
          }
          return;
        }

        // 3. Alt + H: Abrir Centro de Módulos HUD
        if (e.altKey && (e.key === "h" || e.key === "H")) {
          e.preventDefault();
          const hudMenu = document.getElementById("btn-hud-menu");
          if (hudMenu) hudMenu.click();
          return;
        }

        // 4. Alt + K: Enfocar campo de chat
        if (e.altKey && (e.key === "k" || e.key === "K")) {
          e.preventDefault();
          const input = document.getElementById("user-input");
          if (input) input.focus();
          return;
        }

        // 5. Alt + M: Alternar micrófono
        if (e.altKey && (e.key === "m" || e.key === "M")) {
          e.preventDefault();
          const mic = document.getElementById("mic-btn");
          if (mic) mic.click();
          return;
        }

        // 6. Alt + V: Alternar voz de Liseth
        if (e.altKey && (e.key === "v" || e.key === "V")) {
          e.preventDefault();
          const vToggle = document.getElementById("btn-voice-toggle");
          if (vToggle) vToggle.click();
          return;
        }
      });
"""

def main():
    target_path = "jarvis.html"
    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Inject CSS
    target_css_end = '.ambient-grid {'
    if ':focus-visible' not in content:
        if target_css_end in content:
            content = content.replace(target_css_end, CSS_A11Y_INJECTION.strip() + "\n\n    " + target_css_end)
            print("[PATCH] Inyectado CSS de Accesibilidad y Estilo Mark 85")
        else:
            print("[WARN] target_css_end no encontrado")
    else:
        print("[SKIP] CSS de accesibilidad ya presente")

    # 2. Inject Skip Links right after <body>
    if '<a href="#user-input" class="skip-link">' not in content:
        target_body = '<body'
        idx = content.find(target_body)
        if idx != -1:
            body_close_bracket = content.find('>', idx)
            if body_close_bracket != -1:
                content = content[:body_close_bracket+1] + "\n" + SKIP_LINKS_INJECTION.strip() + "\n" + content[body_close_bracket+1:]
                print("[PATCH] Inyectados Skip Links accesibles tras <body>")
        else:
            print("[WARN] <body> no encontrado")
    else:
        print("[SKIP] Skip links ya presentes")

    # 3. Inject A11y Header Button
    if 'id="btn-a11y-panel"' not in content:
        target_header_btn = '<!-- BOTÓN CONMUTAR SONIDO HUD -->'
        if target_header_btn in content:
            content = content.replace(target_header_btn, HEADER_BUTTON_INJECTION.strip() + "\n\n        " + target_header_btn)
            print("[PATCH] Inyectado botón de accesibilidad en top-actions del header")
        else:
            print("[WARN] target_header_btn no encontrado")
    else:
        print("[SKIP] Botón de header ya presente")

    # 4. Inject Modal
    if 'id="a11y-modal"' not in content:
        target_modal_toast = '<div class="liseth-toast" id="liseth-toast"></div>'
        if target_modal_toast in content:
            content = content.replace(target_modal_toast, MODAL_A11Y_INJECTION.strip() + "\n\n  " + target_modal_toast)
            print("[PATCH] Inyectado modal de accesibilidad universal")
        else:
            print("[WARN] target_modal_toast no encontrado")
    else:
        print("[SKIP] Modal ya presente")

    # 5. Inject JS Engine
    if 'window.openA11yModal' not in content:
        target_js = 'window.lisethViewer = {'
        if target_js in content:
            content = content.replace(target_js, JS_A11Y_ENGINE.strip() + "\n\n        " + target_js)
            print("[PATCH] Inyectado motor JS de accesibilidad y atajos de teclado")
        else:
            print("[WARN] target_js no encontrado")
    else:
        print("[SKIP] Motor JS ya presente")

    # 6. Add listener for header button and init loadPersistedA11y
    if 'btnA11y.addEventListener' not in content:
        target_listener_spot = 'const cardBio = document.getElementById("hud-card-biohabits");'
        if target_listener_spot in content:
            hook = """
        const btnA11y = document.getElementById("btn-a11y-panel");
        if (btnA11y) btnA11y.addEventListener("click", () => window.openA11yModal());
        loadPersistedA11y();
"""
            content = content.replace(target_listener_spot, hook.strip() + "\n        " + target_listener_spot)
            print("[PATCH] Inyectado event listener para btn-a11y-panel")

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[PATCH] {target_path} guardado con éxito ({len(content)} caracteres)")

    # Sincronizar a index.html y app/static/index.html
    for dest in ["index.html", os.path.join("app", "static", "index.html")]:
        shutil.copyfile(target_path, dest)
        print(f"[SYNC] Sincronizado a {dest}")

if __name__ == "__main__":
    main()
