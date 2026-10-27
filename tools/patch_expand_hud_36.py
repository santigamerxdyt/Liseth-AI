# -*- coding: utf-8 -*-
"""
Expands Liseth's HUD modules to 36 modules:
- Module 35: hud-card-esg (Gobierno Corporativo & Sostenibilidad ESG)
- Module 36: hud-card-treasury (Tesorería & Capital de Trabajo KTNO)
Integrates interactive modals (esg-modal, treasury-modal),
JS bindings, and updates count badges to 36.
"""

import os
import shutil

NEW_CARDS_36 = """
        <!-- 35. Gobierno Corporativo & Sostenibilidad ESG -->
        <div class="hud-card" data-category="intelligence finance" id="hud-card-esg">
          <div class="hud-card-top">
            <div class="hud-card-icon" style="color: #22c55e; border-color: rgba(34, 197, 94, 0.4); background: rgba(34, 197, 94, 0.12);">🌱</div>
            <span class="hud-card-status status-online">IFRS S1/S2</span>
          </div>
          <div class="hud-card-title">Gobierno Corporativo & ESG</div>
          <div class="hud-card-desc">Auditoría de pilares Ambiental, Social y Gobernanza (GRI), calificación compuesta (AAA) y descarbonización.</div>
          <div class="hud-card-action"><span>Evaluar ESG</span> <span>→</span></div>
        </div>

        <!-- 36. Tesorería & Capital de Trabajo (KTNO) -->
        <div class="hud-card" data-category="automation finance" id="hud-card-treasury">
          <div class="hud-card-top">
            <div class="hud-card-icon" style="color: #06b6d4; border-color: rgba(6, 182, 212, 0.4); background: rgba(6, 182, 212, 0.12);">💰</div>
            <span class="hud-card-status status-online">KTNO / RADIAN</span>
          </div>
          <div class="hud-card-title">Tesorería & Factoring</div>
          <div class="hud-card-desc">Ciclo de Conversión de Efectivo (CCC), optimización de KTNO y descuento de facturas electrónicas RADIAN.</div>
          <div class="hud-card-action"><span>Gestionar Tesorería</span> <span>→</span></div>
        </div>"""

NEW_MODALS_36 = """
  <!-- ======================================================== -->
  <!-- MODAL: GOBIERNO CORPORATIVO & SOSTENIBILIDAD ESG        -->
  <!-- ======================================================== -->
  <div class="modal-overlay" id="esg-modal">
    <div class="modal-card" style="max-width: 820px;">
      <div class="modal-header">
        <div class="modal-icon" style="color: #22c55e; border-color: rgba(34, 197, 94, 0.4); background: rgba(34, 197, 94, 0.12);">🌱</div>
        <div class="modal-title">
          <h2>Gobierno Corporativo & Sostenibilidad ESG</h2>
          <p>Evaluación Integral Ambiental (E), Social (S) y Gobernanza (G) bajo Estándares IFRS y GRI</p>
        </div>
        <button class="modal-close" onclick="closeEsgModal()">&times;</button>
      </div>

      <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 8px; margin-bottom: 12px;">
        <div>
          <label style="font-size: 0.7rem; color: #94a3b8; display: block;">Empresa / Organización:</label>
          <input type="text" id="esg-company-input" value="Empresa de Santiago" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
        </div>
        <div>
          <label style="font-size: 0.7rem; color: #94a3b8; display: block;">Pilar E (0-100):</label>
          <input type="number" id="esg-env-input" value="82" min="0" max="100" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
        </div>
        <div>
          <label style="font-size: 0.7rem; color: #94a3b8; display: block;">Pilar S (0-100):</label>
          <input type="number" id="esg-soc-input" value="85" min="0" max="100" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
        </div>
        <div>
          <label style="font-size: 0.7rem; color: #94a3b8; display: block;">Pilar G (0-100):</label>
          <input type="number" id="esg-gov-input" value="88" min="0" max="100" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
        </div>
      </div>

      <div style="margin-bottom: 12px;">
        <button type="button" class="btn-primary" style="width: 100%; padding: 8px; font-size: 0.8rem;" onclick="submitEsgEvaluation()">Calcular Calificación ESG Compuesta</button>
      </div>

      <div id="esg-results-panel" style="display: none; background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(34, 197, 94, 0.35); border-radius: 8px; padding: 14px; margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <span style="font-size: 0.85rem; font-weight: 700; color: #22c55e;">PUNTAJE ESG: <b id="esg-res-score" style="color: #38ef7d;">0.0 / 100</b></span>
          <span id="esg-res-rating" style="font-size: 0.75rem; padding: 3px 10px; border-radius: 12px; background: rgba(34, 197, 94, 0.2); color: #86efac; font-weight: 700;"></span>
        </div>
        <div id="esg-res-roadmap" style="font-size: 0.78rem; color: #e2e8f0; line-height: 1.45;"></div>
      </div>

      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeEsgModal()">Cerrar</button>
      </div>
    </div>
  </div>

  <!-- ======================================================== -->
  <!-- MODAL: TESORERÍA, CAPITAL DE TRABAJO (KTNO) & FACTORING  -->
  <!-- ======================================================== -->
  <div class="modal-overlay" id="treasury-modal">
    <div class="modal-card" style="max-width: 840px;">
      <div class="modal-header">
        <div class="modal-icon" style="color: #06b6d4; border-color: rgba(6, 182, 212, 0.4); background: rgba(6, 182, 212, 0.12);">💰</div>
        <div class="modal-title">
          <h2>Tesorería Corporativa & Factoring Electrónico</h2>
          <p>Ciclo de Conversión de Efectivo (CCC), KTNO y Descuento de Facturas DIAN / RADIAN</p>
        </div>
        <button class="modal-close" onclick="closeTreasuryModal()">&times;</button>
      </div>

      <!-- Sección CCC -->
      <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(0, 210, 255, 0.2); border-radius: 8px; padding: 12px; margin-bottom: 12px;">
        <div style="font-size: 0.78rem; font-weight: 700; color: #06b6d4; margin-bottom: 8px;">🔄 CICLO DE CONVERSIÓN DE EFECTIVO (CCC)</div>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 8px; margin-bottom: 8px;">
          <div>
            <label style="font-size: 0.7rem; color: #94a3b8; display: block;">DSO Cobro (Días):</label>
            <input type="number" id="tr-dso-input" value="45" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 5px; border-radius: 4px; font-size: 0.8rem;" />
          </div>
          <div>
            <label style="font-size: 0.7rem; color: #94a3b8; display: block;">DIO Inventario (Días):</label>
            <input type="number" id="tr-dio-input" value="30" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 5px; border-radius: 4px; font-size: 0.8rem;" />
          </div>
          <div>
            <label style="font-size: 0.7rem; color: #94a3b8; display: block;">DPO Pago Prov. (Días):</label>
            <input type="number" id="tr-dpo-input" value="50" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 5px; border-radius: 4px; font-size: 0.8rem;" />
          </div>
          <div style="display: flex; align-items: flex-end;">
            <button type="button" class="btn-primary" style="width: 100%; padding: 6px; font-size: 0.76rem;" onclick="submitTreasuryCCC()">Calcular CCC</button>
          </div>
        </div>
        <div id="tr-ccc-res" style="display: none; font-size: 0.8rem; color: #e2e8f0; background: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px;"></div>
      </div>

      <!-- Sección Factoring RADIAN -->
      <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 209, 102, 0.2); border-radius: 8px; padding: 12px; margin-bottom: 12px;">
        <div style="font-size: 0.78rem; font-weight: 700; color: #ffd166; margin-bottom: 8px;">📑 SIMULADOR DE FACTORING ELECTRÓNICO (RADIAN)</div>
        <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 8px; margin-bottom: 8px;">
          <div>
            <label style="font-size: 0.7rem; color: #94a3b8; display: block;">Valor Factura ($ COP):</label>
            <input type="number" id="tr-fact-val-input" value="35000000" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 5px; border-radius: 4px; font-size: 0.8rem;" />
          </div>
          <div>
            <label style="font-size: 0.7rem; color: #94a3b8; display: block;">Vencimiento (Días):</label>
            <input type="number" id="tr-fact-days-input" value="60" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 5px; border-radius: 4px; font-size: 0.8rem;" />
          </div>
          <div style="display: flex; align-items: flex-end;">
            <button type="button" class="btn-secondary" style="width: 100%; padding: 6px; font-size: 0.76rem;" onclick="submitTreasuryFactoring()">Simular RADIAN</button>
          </div>
        </div>
        <div id="tr-fact-res" style="display: none; font-size: 0.8rem; color: #e2e8f0; background: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px;"></div>
      </div>

      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeTreasuryModal()">Cerrar</button>
      </div>
    </div>
  </div>"""

NEW_JS_ENGINE_36 = """
      // ========================================================
      // CONTROLADORES INTERACTIVOS: ESG & TESORERÍA / FACTORING
      // ========================================================
      window.openEsgModal = function() {
        const m = document.getElementById("esg-modal");
        if (m) m.classList.add("active");
        playHudSound("open");
      };
      window.closeEsgModal = function() {
        const m = document.getElementById("esg-modal");
        if (m) m.classList.remove("active");
        playHudSound("close");
      };

      window.submitEsgEvaluation = function() {
        const comp = document.getElementById("esg-company-input")?.value || "Empresa de Santiago";
        const e = parseFloat(document.getElementById("esg-env-input")?.value || 80);
        const s = parseFloat(document.getElementById("esg-soc-input")?.value || 85);
        const g = parseFloat(document.getElementById("esg-gov-input")?.value || 88);

        const composite = (e * 0.35) + (s * 0.35) + (g * 0.30);
        let rating = "AAA (Líder Sostenible)";
        let badgeColor = "#38ef7d";
        if (composite < 50) { rating = "CCC (Riesgo Crítico)"; badgeColor = "#f43f5e"; }
        else if (composite < 65) { rating = "BBB (En Transición)"; badgeColor = "#ffd166"; }
        else if (composite < 80) { rating = "AA (Sólido)"; badgeColor = "#00d2ff"; }

        document.getElementById("esg-res-score").textContent = composite.toFixed(1) + " / 100";
        document.getElementById("esg-res-rating").textContent = rating;
        document.getElementById("esg-res-rating").style.color = badgeColor;
        document.getElementById("esg-res-roadmap").innerHTML = "🌱 <b>Hoja de Ruta para " + comp + ":</b> Gobernanza fortalecida con reporte anual IFRS S1/S2, huella de carbono auditada y plan de impacto comunitario en el Valle del Cauca.";
        document.getElementById("esg-results-panel").style.display = "block";
        playHudSound("click");
      };

      window.openTreasuryModal = function() {
        const m = document.getElementById("treasury-modal");
        if (m) m.classList.add("active");
        playHudSound("open");
      };
      window.closeTreasuryModal = function() {
        const m = document.getElementById("treasury-modal");
        if (m) m.classList.remove("active");
        playHudSound("close");
      };

      window.submitTreasuryCCC = function() {
        const dso = parseFloat(document.getElementById("tr-dso-input")?.value || 45);
        const dio = parseFloat(document.getElementById("tr-dio-input")?.value || 30);
        const dpo = parseFloat(document.getElementById("tr-dpo-input")?.value || 50);

        const ccc = (dso + dio) - dpo;
        const box = document.getElementById("tr-ccc-res");
        box.style.display = "block";
        box.innerHTML = "<b>Ciclo CCC: " + ccc.toFixed(1) + " Días</b> (Cobro: " + dso + "d + Inventario: " + dio + "d - Pago: " + dpo + "d). " +
          (ccc <= 30 ? "⚡ <b>Alta Eficiencia:</b> Financiación óptima vía proveedores." : "⚠️ <b>Atención:</b> Capital de trabajo inmovilizado.");
        playHudSound("click");
      };

      window.submitTreasuryFactoring = function() {
        const val = parseFloat(document.getElementById("tr-fact-val-input")?.value || 35000000);
        const days = parseInt(document.getElementById("tr-fact-days-input")?.value || 60);

        const months = days / 30.0;
        const discountCost = val * (0.0145 * months);
        const platformFee = val * 0.0030;
        const netCash = val - (discountCost + platformFee);
        const ea = ((Math.pow(1 + (discountCost + platformFee)/netCash, 365.0/days)) - 1.0) * 100.0;

        const box = document.getElementById("tr-fact-res");
        box.style.display = "block";
        box.innerHTML = "💵 <b>Liquidez Inmediata Liberada:</b> $" + Math.round(netCash).toLocaleString() + " COP hoy.<br>" +
          "• Descuento: $" + Math.round(discountCost).toLocaleString() + " COP | Comisión RADIAN: $" + Math.round(platformFee).toLocaleString() + " COP | <b>Tasa: " + ea.toFixed(1) + "% E.A.</b>";
        playHudSound("click");
      };
"""

def main():
    target_path = "jarvis.html"
    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update Header Button text & count to 36
    content = content.replace("34 MÓDULOS HUD", "36 MÓDULOS HUD")
    content = content.replace("◈ 34 Módulos HUD", "◈ 36 Módulos HUD")
    content = content.replace("34 Módulos HUD", "36 Módulos HUD")
    content = content.replace("TODOS (34)", "TODOS (36)")
    content = content.replace("FINANZAS & ESTRATEGIA (11)", "FINANZAS & ESTRATEGIA (13)")
    content = content.replace("34 / 34 MÓDULOS", "36 / 36 MÓDULOS")
    content = content.replace("${visibleCount} / 34 MÓDULOS", "${visibleCount} / 36 MÓDULOS")
    content = content.replace("Alt+H) - 34 Módulos", "Alt+H) - 36 Módulos")
    content = content.replace(">34</span>", ">36</span>")

    # 2. Inject 2 new cards into #hud-modules-grid right after hud-card-a11y
    card_a11y_end = """          <div class="hud-card-action"><span>Abrir Accesibilidad</span> <span>→</span></div>
        </div>"""

    if card_a11y_end in content and 'id="hud-card-esg"' not in content:
        content = content.replace(card_a11y_end, card_a11y_end + "\n" + NEW_CARDS_36.strip())
        print("[PATCH 1] Inyectadas 2 nuevas tarjetas HUD (esg, treasury)")
    else:
        print("[INFO 1] Tarjetas ya presentes o spot no encontrado")

    # 3. Inject 2 new modals right before <!-- ======================================================== -->\n  <!-- MODAL: CENTRO DE ACCESIBILIDAD
    target_a11y_modal = '<!-- ======================================================== -->\n  <!-- MODAL: CENTRO DE ACCESIBILIDAD UNIVERSAL STARK (A11Y)'
    if target_a11y_modal in content and 'id="esg-modal"' not in content:
        content = content.replace(target_a11y_modal, NEW_MODALS_36.strip() + "\n\n  " + target_a11y_modal)
        print("[PATCH 2] Inyectados 2 nuevos modales (esg-modal, treasury-modal)")
    else:
        print("[INFO 2] Modales ya presentes o spot no encontrado")

    # 4. Inject JS engine & card bindings
    target_a11y_bind = 'if (cardA11y) cardA11y.addEventListener("click", () => {\n          document.getElementById("hud-interfaces-modal")?.classList.remove("active");\n          window.openA11yModal();\n        });'

    card_bindings_36 = """
        const cardEsg = document.getElementById("hud-card-esg");
        if (cardEsg) cardEsg.addEventListener("click", () => {
          document.getElementById("hud-interfaces-modal")?.classList.remove("active");
          window.openEsgModal();
        });

        const cardTreasury = document.getElementById("hud-card-treasury");
        if (cardTreasury) cardTreasury.addEventListener("click", () => {
          document.getElementById("hud-interfaces-modal")?.classList.remove("active");
          window.openTreasuryModal();
        });
"""

    if target_a11y_bind in content and 'cardEsg' not in content:
        content = content.replace(target_a11y_bind, target_a11y_bind + "\n" + card_bindings_36.strip())
        print("[PATCH 3] Inyectados enlaces de apertura de tarjetas ESG y Treasury en JS")

    target_js_spot = 'window.openMarketingModal = function() {'
    if target_js_spot in content and 'window.openEsgModal' not in content:
        content = content.replace(target_js_spot, NEW_JS_ENGINE_36.strip() + "\n\n      " + target_js_spot)
        print("[PATCH 4] Inyectados controladores JS para ESG y Tesorería")

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[SUCCESS] {target_path} guardado ({len(content)} caracteres)")

    # Sincronizar
    for dest in ["index.html", os.path.join("app", "static", "index.html")]:
        shutil.copyfile(target_path, dest)
        print(f"[SYNC] Sincronizado a {dest}")

if __name__ == "__main__":
    main()
