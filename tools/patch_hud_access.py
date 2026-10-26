# -*- coding: utf-8 -*-
"""
Script to fix the display and full access to all 30 HUD modules for Señor Santiago:
1. Re-orders .top-actions so btn-hud-menu is at the very FRONT (Position #1) with high-visibility styling and badge.
2. Expands .header-top max-width to 1480px and makes .top-actions smoothly scrollable (overflow-x: auto) so all buttons can be reached.
3. Adds a dedicated central quick chip in .quick-chips: "◈ 30 Módulos HUD" for instant 1-click access.
4. Adds an instant live search bar in hud-interfaces-modal to filter all 30 modules by title, keyword, or category in real-time.
5. Adds a "FINANZAS & ESTRATEGIA (8)" category filter tab in hud-interfaces-modal and assigns multi-category tags to financial cards.
6. Ensures all 30 cards reset to display: flex whenever the modal is opened.
7. Exposes window.openHudModal() and binds keyboard Alt+H, header button, and central chip.
8. Synchronizes jarvis.html -> index.html -> app/static/index.html.
"""

import os
import shutil
import re

def apply_patch():
    target_path = "jarvis.html"
    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()

    # -------------------------------------------------------------
    # 1. Update CSS: .header-top & .top-actions & .hud-deck-window
    # -------------------------------------------------------------
    old_header_top_css = """.header-top {
      width: 100%;
      max-width: 900px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: absolute;
      top: 12px;
      left: 50%;
      transform: translateX(-50%);
      padding: 0 20px;
      pointer-events: none;
    }"""

    new_header_top_css = """.header-top {
      width: calc(100% - 32px);
      max-width: 1480px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: absolute;
      top: 10px;
      left: 50%;
      transform: translateX(-50%);
      padding: 0 16px;
      pointer-events: none;
      gap: 12px;
    }"""

    if old_header_top_css in content:
        content = content.replace(old_header_top_css, new_header_top_css)
        print("[PATCH 1] CSS .header-top actualizado a max-width 1480px")
    else:
        print("[WARN 1] old_header_top_css no encontrado directamente, buscando regex")
        content = re.sub(
            r'\.header-top\s*\{[^}]*max-width:\s*900px;[^}]*\}',
            new_header_top_css,
            content
        )

    old_top_actions_css = """.top-actions {
      pointer-events: auto;
      display: flex;
      gap: 8px;
    }"""

    new_top_actions_css = """.top-actions {
      pointer-events: auto;
      display: flex;
      align-items: center;
      gap: 8px;
      max-width: calc(100% - 190px);
      overflow-x: auto;
      overflow-y: hidden;
      scrollbar-width: none;
      -ms-overflow-style: none;
      padding: 4px 6px;
      border-radius: 20px;
    }
    .top-actions::-webkit-scrollbar {
      display: none;
    }"""

    if old_top_actions_css in content:
        content = content.replace(old_top_actions_css, new_top_actions_css)
        print("[PATCH 2] CSS .top-actions actualizado con soporte horizontal responsive")
    else:
        print("[WARN 2] old_top_actions_css no encontrado")

    # Increase max-width of .hud-deck-window from 980px to 1120px
    content = content.replace("max-width: 980px;", "max-width: 1120px;")

    # -------------------------------------------------------------
    # 2. Re-order buttons in .top-actions so btn-hud-menu is at the FRONT
    # -------------------------------------------------------------
    # First, let's remove the old btn-hud-menu in position #7
    old_btn_hud_menu = """        <!-- BOTÓN CENTRAL HUD FUTURISTA DE INTERFACES -->
        <button class="hud-deck-btn" id="btn-hud-menu" title="Desplegar Centro de Control de Interfaces e Inteligencia (HUD)">
          <span class="hud-deck-icon">◈</span>
          <span>MÓDULOS</span>
          <span class="hud-deck-badge">HUD</span>
        </button>"""

    new_front_btn_hud_menu = """        <!-- BOTÓN CENTRAL HUD FUTURISTA DE INTERFACES (ACCESO DIRECTO PRIORITARIO #1) -->
        <button class="hud-deck-btn hud-deck-btn-primary" id="btn-hud-menu" title="Desplegar Centro de Control de Interfaces e Inteligencia (Alt+H) - 30 Módulos" style="border: 2px solid #00f0ff; background: rgba(0, 240, 255, 0.22); box-shadow: 0 0 18px rgba(0, 240, 255, 0.55); font-weight: 700; flex-shrink: 0;">
          <span class="hud-deck-icon" style="color: #00f0ff; font-size: 1.05rem;">◈</span>
          <span style="color: #ffffff; letter-spacing: 0.04em;">30 MÓDULOS HUD</span>
          <span class="hud-deck-badge" style="background: linear-gradient(135deg, #00f0ff, #0077ff); color: #04070d; font-weight: 900;">30</span>
        </button>"""

    if old_btn_hud_menu in content:
        # Remove old position
        content = content.replace(old_btn_hud_menu, "")
        # Insert at the beginning of .top-actions
        target_top_actions_start = '<div class="top-actions">'
        content = content.replace(target_top_actions_start, target_top_actions_start + "\n" + new_front_btn_hud_menu)
        print("[PATCH 3] btn-hud-menu movido al frente (Posición #1) de .top-actions")
    else:
        print("[WARN 3] old_btn_hud_menu no encontrado")

    # -------------------------------------------------------------
    # 3. Add Quick Chip "30 Módulos HUD" in .quick-chips
    # -------------------------------------------------------------
    old_quick_chip_spot = """      <!-- Píldoras de Acciones Rápidas -->
      <div class="quick-chips" style="margin-top: 18px;">
        <button class="chip-btn" data-prompt="Santiago requiere tus ideas de optimización: ¿Cómo puedo automatizar y ahorrar tiempo hoy en mi día a día?">"""

    new_quick_chip_spot = """      <!-- Píldoras de Acciones Rápidas -->
      <div class="quick-chips" style="margin-top: 18px;">
        <button class="chip-btn" id="btn-quick-hud-modules" style="border: 1.5px solid #00f0ff; background: rgba(0, 240, 255, 0.18); box-shadow: 0 0 16px rgba(0, 240, 255, 0.4); font-weight: 700; color: #ffffff;" title="Abrir catálogo completo de los 30 módulos tácticos de Liseth">
          <span style="color: #00f0ff; font-size: 1rem;">◈</span> 30 Módulos HUD
        </button>
        <button class="chip-btn" data-prompt="Santiago requiere tus ideas de optimización: ¿Cómo puedo automatizar y ahorrar tiempo hoy en mi día a día?">"""

    if old_quick_chip_spot in content and 'id="btn-quick-hud-modules"' not in content:
        content = content.replace(old_quick_chip_spot, new_quick_chip_spot)
        print("[PATCH 4] Píldora central '30 Módulos HUD' inyectada en .quick-chips")
    else:
        print("[INFO 4] Píldora central ya presente o spot no encontrado")

    # -------------------------------------------------------------
    # 4. Add Live Search Bar & Category Tabs in hud-interfaces-modal
    # -------------------------------------------------------------
    old_tabs_section = """      <!-- Pestañas de filtrado de categorías -->
      <div class="hud-filter-tabs">
        <button class="hud-tab active" data-filter="all">TODOS (30)</button>
        <button class="hud-tab" data-filter="intelligence">INTELIGENCIA</button>
        <button class="hud-tab" data-filter="connectors">CONECTORES</button>
        <button class="hud-tab" data-filter="automation">AUTOMATIZACIÓN</button>
        <button class="hud-tab" data-filter="system">SISTEMA & MEMORIA</button>
      </div>"""

    new_search_and_tabs = """      <!-- Barra de Búsqueda Rápida y Contador de Módulos Activos -->
      <div class="hud-search-filter-container" style="display: flex; gap: 12px; align-items: center; margin-bottom: 14px; width: 100%;">
        <div style="position: relative; flex: 1;">
          <span style="position: absolute; left: 14px; top: 50%; transform: translateY(-50%); font-size: 1rem; color: #00d2ff; pointer-events: none;">🔍</span>
          <input type="text" id="hud-modules-search" placeholder="Buscar módulo por nombre o función (ej: Impuestos, Fletes, Valuación, NFC, Google, PC, Finanzas...)" style="width: 100%; padding: 11px 40px 11px 42px; background: rgba(10, 18, 36, 0.85); border: 1.5px solid rgba(0, 210, 255, 0.45); border-radius: 12px; color: #ffffff; font-size: 0.9rem; outline: none; transition: all 0.25s;" onfocus="this.style.borderColor='#00f0ff'; this.style.boxShadow='0 0 18px rgba(0,240,255,0.4)';" onblur="this.style.borderColor='rgba(0, 210, 255, 0.45)'; this.style.boxShadow='none';">
          <button type="button" id="hud-search-clear" style="display: none; position: absolute; right: 12px; top: 50%; transform: translateY(-50%); background: none; border: none; color: #94a3b8; font-size: 1.1rem; cursor: pointer;" title="Limpiar búsqueda">&times;</button>
        </div>
        <div class="hud-count-pill" id="hud-visible-count-pill" style="background: rgba(0, 210, 255, 0.12); border: 1px solid rgba(0, 210, 255, 0.45); padding: 9px 16px; border-radius: 10px; color: #00d2ff; font-family: var(--font-mono); font-size: 0.82rem; font-weight: 700; white-space: nowrap; box-shadow: 0 0 10px rgba(0,210,255,0.2);">
          30 / 30 MÓDULOS
        </div>
      </div>

      <!-- Pestañas de filtrado de categorías -->
      <div class="hud-filter-tabs">
        <button class="hud-tab active" data-filter="all">TODOS (30)</button>
        <button class="hud-tab" data-filter="finance">FINANZAS & ESTRATEGIA (8)</button>
        <button class="hud-tab" data-filter="intelligence">INTELIGENCIA</button>
        <button class="hud-tab" data-filter="connectors">CONECTORES</button>
        <button class="hud-tab" data-filter="automation">AUTOMATIZACIÓN</button>
        <button class="hud-tab" data-filter="system">SISTEMA & MEMORIA</button>
      </div>"""

    if old_tabs_section in content and 'id="hud-modules-search"' not in content:
        content = content.replace(old_tabs_section, new_search_and_tabs)
        print("[PATCH 5] Barra de búsqueda en vivo y pestaña FINANZAS inyectadas en hud-interfaces-modal")
    else:
        print("[INFO 5] Pestañas o buscador ya presentes")

    # -------------------------------------------------------------
    # 5. Add 'finance' category to financial cards
    # -------------------------------------------------------------
    fin_replacements = [
        ('data-category="automation" id="hud-card-finances"', 'data-category="automation finance" id="hud-card-finances"'),
        ('data-category="automation" id="hud-card-tax-pay"', 'data-category="automation finance" id="hud-card-tax-pay"'),
        ('data-category="intelligence" id="hud-card-valuation"', 'data-category="intelligence finance" id="hud-card-valuation"'),
        ('data-category="intelligence" id="hud-card-investment"', 'data-category="intelligence finance" id="hud-card-investment"'),
        ('data-category="system" id="hud-card-tax"', 'data-category="system finance" id="hud-card-tax"'),
        ('data-category="automation" id="hud-card-macro"', 'data-category="automation finance" id="hud-card-macro"'),
        ('data-category="automation" id="hud-card-logistics"', 'data-category="automation finance" id="hud-card-logistics"'),
        ('data-category="connectors" id="hud-card-contracts"', 'data-category="connectors finance" id="hud-card-contracts"')
    ]
    for old_tag, new_tag in fin_replacements:
        if old_tag in content:
            content = content.replace(old_tag, new_tag)

    print("[PATCH 6] Categorías 'finance' añadidas a los 8 módulos financieros y estratégicos")

    # -------------------------------------------------------------
    # 6. Update JS logic for opening HUD modal, search filtering, and tabs
    # -------------------------------------------------------------
    old_js_listener = """          if (btnHudMenu && hudModal) {
            btnHudMenu.addEventListener("click", () => {
              playHudSound("open");
              hudModal.classList.add("active");
              updateHudTelemetry();
            });
          }"""

    new_js_hud_engine = """          // Función maestra global para abrir el Centro de Módulos HUD
          window.openHudModal = function() {
            if (!hudModal) return;
            playHudSound("open");
            hudModal.classList.add("active");
            updateHudTelemetry();

            // Resetear búsqueda y restaurar todos los módulos
            const searchInput = document.getElementById("hud-modules-search");
            if (searchInput) {
              searchInput.value = "";
              filterHudModules("");
            }
            // Activar pestaña 'TODOS'
            const allTab = document.querySelector('.hud-filter-tabs .hud-tab[data-filter="all"]');
            if (allTab) {
              document.querySelectorAll(".hud-filter-tabs .hud-tab").forEach(t => t.classList.remove("active"));
              allTab.classList.add("active");
            }
            // Asegurar despliegue de todas las tarjetas
            document.querySelectorAll(".hud-modules-grid .hud-card").forEach(card => {
              card.style.display = "flex";
            });
          };

          if (btnHudMenu) {
            btnHudMenu.addEventListener("click", () => window.openHudModal());
          }

          const btnQuickHud = document.getElementById("btn-quick-hud-modules");
          if (btnQuickHud) {
            btnQuickHud.addEventListener("click", () => window.openHudModal());
          }

          // Motor de filtrado por búsqueda en tiempo real
          function filterHudModules(query) {
            const cleanQ = (query || "").trim().toLowerCase();
            const hudCards = document.querySelectorAll(".hud-modules-grid .hud-card");
            const countPill = document.getElementById("hud-visible-count-pill");
            const clearBtn = document.getElementById("hud-search-clear");
            if (clearBtn) clearBtn.style.display = cleanQ ? "block" : "none";

            let visibleCount = 0;
            hudCards.forEach(card => {
              const title = (card.querySelector(".hud-card-title")?.textContent || "").toLowerCase();
              const desc = (card.querySelector(".hud-card-desc")?.textContent || "").toLowerCase();
              const cat = (card.getAttribute("data-category") || "").toLowerCase();

              const matches = !cleanQ || title.includes(cleanQ) || desc.includes(cleanQ) || cat.includes(cleanQ);
              if (matches) {
                card.style.display = "flex";
                visibleCount++;
              } else {
                card.style.display = "none";
              }
            });

            if (countPill) {
              countPill.textContent = `${visibleCount} / 30 MÓDULOS`;
              countPill.style.color = visibleCount > 0 ? "#00d2ff" : "#ef4444";
              countPill.style.borderColor = visibleCount > 0 ? "rgba(0, 210, 255, 0.45)" : "rgba(239, 68, 68, 0.5)";
            }
          }

          const searchInputEl = document.getElementById("hud-modules-search");
          if (searchInputEl) {
            searchInputEl.addEventListener("input", (e) => filterHudModules(e.target.value));
          }
          const clearSearchBtn = document.getElementById("hud-search-clear");
          if (clearSearchBtn) {
            clearSearchBtn.addEventListener("click", () => {
              if (searchInputEl) {
                searchInputEl.value = "";
                filterHudModules("");
                searchInputEl.focus();
              }
            });
          }"""

    if old_js_listener in content:
        content = content.replace(old_js_listener, new_js_hud_engine)
        print("[PATCH 7] Motor JS de apertura HUD, búsqueda en vivo y reset inyectado con éxito")
    else:
        print("[WARN 7] old_js_listener no encontrado")

    # Update category tab filter listener to support multi-category tags (e.g. "automation finance")
    old_tabs_js = """              hudCards.forEach(card => {
                const cat = card.getAttribute("data-category");
                if (filter === "all" || cat === filter) {
                  card.style.display = "flex";
                  card.style.animation = "none";
                  void card.offsetWidth;
                  card.style.animation = "hudCardDeploy 0.35s cubic-bezier(0.16, 1, 0.3, 1) backwards";
                } else {
                  card.style.display = "none";
                }
              });"""

    new_tabs_js = """              hudCards.forEach(card => {
                const cat = (card.getAttribute("data-category") || "").split(" ");
                if (filter === "all" || cat.includes(filter)) {
                  card.style.display = "flex";
                  card.style.animation = "none";
                  void card.offsetWidth;
                  card.style.animation = "hudCardDeploy 0.35s cubic-bezier(0.16, 1, 0.3, 1) backwards";
                } else {
                  card.style.display = "none";
                }
              });
              // Actualizar píldora de conteo
              const visibleNow = document.querySelectorAll(".hud-modules-grid .hud-card:not([style*='display: none'])").length;
              const pill = document.getElementById("hud-visible-count-pill");
              if (pill) pill.textContent = `${visibleNow} / 30 MÓDULOS`;"""

    if old_tabs_js in content:
        content = content.replace(old_tabs_js, new_tabs_js)
        print("[PATCH 8] Lógica de filtrado por pestañas actualizada con soporte multi-categoría")
    else:
        print("[WARN 8] old_tabs_js no encontrado")

    # -------------------------------------------------------------
    # 7. Write to jarvis.html and sync
    # -------------------------------------------------------------
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[PATCH SUCCESS] {target_path} guardado con éxito ({len(content)} caracteres)")

    for dest in ["index.html", os.path.join("app", "static", "index.html")]:
        shutil.copyfile(target_path, dest)
        print(f"[SYNC] Sincronizado a {dest}")

if __name__ == "__main__":
    apply_patch()
