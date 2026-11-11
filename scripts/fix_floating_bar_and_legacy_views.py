import os
import re

CSS_FIX = """
    /* ====================================================================== */
    /* HUD JARVIS 3.8: SUPRESIÓN VISUAL DE ELEMENTOS LEGACY (BARRA FLOTANTE Y ESFERA 2D) */
    /* ====================================================================== */
    header,
    .header-top,
    .top-actions,
    .sphere-workspace,
    .executive-ticker-tape,
    .anticipatory-hud-card,
    .liseth-3d-avatar-container,
    .avatar-mode-switch,
    .stark-hud-wing {
      display: none !important;
      visibility: hidden !important;
      height: 0 !important;
      min-height: 0 !important;
      max-height: 0 !important;
      margin: 0 !important;
      padding: 0 !important;
      overflow: hidden !important;
      pointer-events: none !important;
      opacity: 0 !important;
    }

    .holographic-main-stage {
      flex: 1 1 auto !important;
      position: relative !important;
      display: flex !important;
      flex-direction: column !important;
      overflow-y: auto !important;
      overflow-x: hidden !important;
      width: 100% !important;
      min-height: 0 !important;
      padding: 4px 16px 12px !important;
      z-index: 10 !important;
      box-sizing: border-box !important;
    }

    .console-workspace,
    .console-workspace.hidden {
      position: relative !important;
      inset: auto !important;
      display: flex !important;
      flex-direction: column !important;
      flex: 1 1 auto !important;
      width: 100% !important;
      max-width: 960px !important;
      margin: 0 auto !important;
      opacity: 1 !important;
      pointer-events: auto !important;
      transform: none !important;
      min-height: 0 !important;
      z-index: 5 !important;
    }

    #chat-container {
      flex: 1 1 auto !important;
      width: 100% !important;
      max-width: 100% !important;
      overflow-y: visible !important;
      padding: 8px 0 24px !important;
      min-height: 120px !important;
      box-sizing: border-box !important;
    }

    .chat-wrapper {
      width: 100% !important;
      max-width: 100% !important;
      display: flex !important;
      flex-direction: column !important;
      gap: 14px !important;
    }
"""

JS_MODAL_HELPERS = """
      // Modular Navigation & Modal Openers HUD JARVIS 3.8
      window.openHudModulesModal = function() {
        const modal = document.getElementById("hud-interfaces-modal");
        if (modal) {
          modal.classList.add("active");
          modal.style.display = "flex";
          if (typeof playHudSound === "function") playHudSound("open");
        } else {
          const btn = document.getElementById("btn-hud-menu");
          if (btn) btn.click();
        }
      };

      window.openConvListModal = function() {
        const modal = document.getElementById("conversations-modal");
        if (modal) {
          modal.classList.add("active");
          modal.style.display = "flex";
          if (typeof renderConversationsList === "function") renderConversationsList();
          if (typeof updateStorageMeter === "function") updateStorageMeter();
          if (typeof playHudSound === "function") playHudSound("open");
        }
      };

      window.openMemoryViewerModal = function() {
        if (typeof openSaasModal === "function") {
          openSaasModal();
          if (typeof switchSaasTab === "function") switchSaasTab("memory");
          return;
        }
        const modal = document.getElementById("brain-modal");
        if (modal) {
          modal.classList.add("active");
          modal.style.display = "flex";
          if (typeof playHudSound === "function") playHudSound("open");
        }
      };
"""

def process_file(filepath):
    print(f"Processing {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Inject CSS_FIX right before </style> if not already present
    if "HUD JARVIS 3.8: SUPRESIÓN VISUAL DE ELEMENTOS LEGACY" not in content:
        style_close = content.find("</style>")
        if style_close != -1:
            content = content[:style_close] + CSS_FIX + "\n  " + content[style_close:]
            print("  -> Injected CSS_FIX")

    # 2. Add 48 Módulos chip in ai-core-orb-stage prompt chips
    old_chips = '<button type="button" class="orb-dock-toggle-btn" onclick="openAgentHubModal()" style="border-color:#a855f7;color:#c084fc;" title="Ver AI Agent Hub">\n            <span>🤖 Agentes IA</span>\n          </button>'
    new_chips = old_chips + '\n          <button type="button" class="orb-dock-toggle-btn" onclick="openHudModulesModal()" style="border-color:#00e5ff;color:#00e5ff;" title="Desplegar Centro de Control de 48 Módulos HUD">\n            <span>◈ 48 Módulos</span>\n          </button>'
    if 'onclick="openHudModulesModal()"' not in content[content.find("ai-core-orb-stage"):content.find("ai-core-orb-stage")+1200]:
        if old_chips in content:
            content = content.replace(old_chips, new_chips, 1)
            print("  -> Added 48 Módulos chip to ai-core-orb-stage")

    # 3. Ensure setViewMode keeps console visible and sphere hidden
    old_set_view = """      function setViewMode(mode) {
        currentViewMode = mode;
        localStorage.setItem("liseth_view_mode", mode);
        if (mode === "sphere") {
          sphereWorkspace?.classList.remove("hidden");
          consoleWorkspace?.classList.add("hidden");
          if (btnToggleView) {
            btnToggleView.classList.add("active");
            if (toggleViewIcon) toggleViewIcon.textContent = "📜";
            if (toggleViewText) toggleViewText.textContent = "Consola";
          }
        } else {
          sphereWorkspace?.classList.add("hidden");
          consoleWorkspace?.classList.remove("hidden");
          if (btnToggleView) {
            btnToggleView.classList.remove("active");
            btnToggleView.classList.remove("has-unread");
            if (toggleViewIcon) toggleViewIcon.textContent = "🔮";
            if (toggleViewText) toggleViewText.textContent = "Esfera";
          }
          scrollToBottom();
        }
      }"""

    new_set_view = """      function setViewMode(mode) {
        // En HUD JARVIS 3.8, la consola siempre está activa y el AI Core Orb 3D reemplaza la esfera 2D
        sphereWorkspace?.classList.add("hidden");
        consoleWorkspace?.classList.remove("hidden");
        currentViewMode = "console";
        localStorage.setItem("liseth_view_mode", "console");
        if (btnToggleView) {
          btnToggleView.classList.remove("active");
          btnToggleView.classList.remove("has-unread");
          if (toggleViewIcon) toggleViewIcon.textContent = "⚡";
          if (toggleViewText) toggleViewText.textContent = "HUD 3.8";
        }
        if (typeof scrollToBottom === "function") scrollToBottom();
      }"""

    if old_set_view in content:
        content = content.replace(old_set_view, new_set_view, 1)
        print("  -> Updated setViewMode function")

    # 4. Inject JS_MODAL_HELPERS if not present
    if "Modular Navigation & Modal Openers HUD JARVIS 3.8" not in content:
        target = "window.activateAgentPersona = function(agentKey) {"
        if target in content:
            content = content.replace(target, JS_MODAL_HELPERS + "\n      " + target, 1)
            print("  -> Injected JS_MODAL_HELPERS")

    # 5. Ensure initial view mode default is console
    content = content.replace('let currentViewMode = localStorage.getItem("liseth_view_mode") || "sphere";',
                              'let currentViewMode = "console"; localStorage.setItem("liseth_view_mode", "console");')

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  -> Successfully saved {filepath}")

for fp in ["index.html", "jarvis.html", "app/static/index.html"]:
    process_file(fp)
