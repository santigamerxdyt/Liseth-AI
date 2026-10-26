# -*- coding: utf-8 -*-
"""
Expands Liseth's HUD modules to 34 modules:
- Module 31: hud-card-marketing (Crecimiento & Unit Economics 360)
- Module 32: hud-card-talent (Talento Humano & Matriz 9-Box)
- Module 33: hud-card-forex (Radar Cambiario & Cobertura Divisas)
- Module 34: hud-card-a11y (Centro de Accesibilidad Stark WCAG AAA)
Integrates 3 tactical modals (marketing-modal, talent-modal, forex-modal),
interactive calculators, JS bindings, search indexing, and 34-count badge updates.
"""

import os
import shutil

NEW_CARDS_HTML = """
        <!-- 31. Motor de Crecimiento & Unit Economics (MKT 360) -->
        <div class="hud-card" data-category="automation finance" id="hud-card-marketing">
          <div class="hud-card-top">
            <div class="hud-card-icon" style="color: #f43f5e; border-color: rgba(244, 63, 94, 0.4); background: rgba(244, 63, 94, 0.12);">📈</div>
            <span class="hud-card-status status-online">MKT 360</span>
          </div>
          <div class="hud-card-title">Crecimiento & Unit Economics</div>
          <div class="hud-card-desc">CAC, LTV, ratio LTV/CAC, Payback, Churn mensual y diagnóstico de cuellos de botella en embudos.</div>
          <div class="hud-card-action"><span>Analizar Crecimiento</span> <span>→</span></div>
        </div>

        <!-- 32. Talento Humano & Matriz 9-Box -->
        <div class="hud-card" data-category="intelligence finance" id="hud-card-talent">
          <div class="hud-card-top">
            <div class="hud-card-icon" style="color: #8b5cf6; border-color: rgba(139, 92, 246, 0.4); background: rgba(139, 92, 246, 0.12);">👥</div>
            <span class="hud-card-status status-online">9-BOX GRID</span>
          </div>
          <div class="hud-card-title">Talento Humano & Clima eNPS</div>
          <div class="hud-card-desc">Mapeo en Matriz de 9 Cajas (Desempeño vs Potencial), satisfacción eNPS y costo de rotación (C.S.T.).</div>
          <div class="hud-card-action"><span>Evaluar Talento</span> <span>→</span></div>
        </div>

        <!-- 33. Radar Cambiario & Cobertura de Divisas -->
        <div class="hud-card" data-category="connectors finance" id="hud-card-forex">
          <div class="hud-card-top">
            <div class="hud-card-icon" style="color: #10b981; border-color: rgba(16, 185, 129, 0.4); background: rgba(16, 185, 129, 0.12);">💱</div>
            <span class="hud-card-status status-online">TRM BANREP</span>
          </div>
          <div class="hud-card-title">Radar Cambiario & Divisas</div>
          <div class="hud-card-desc">TRM oficial Colombia, Dólar Cripto USDT, spreads bancarios y simulador Forward de cobertura cambiaria.</div>
          <div class="hud-card-action"><span>Monitorear Divisas</span> <span>→</span></div>
        </div>

        <!-- 34. Centro de Accesibilidad Universal Stark -->
        <div class="hud-card" data-category="system" id="hud-card-a11y">
          <div class="hud-card-top">
            <div class="hud-card-icon" style="color: #00d2ff; border-color: rgba(0, 210, 255, 0.4); background: rgba(0, 210, 255, 0.12);">♿</div>
            <span class="hud-card-status status-online">WCAG AAA</span>
          </div>
          <div class="hud-card-title">Centro de Accesibilidad</div>
          <div class="hud-card-desc">Ajustes de alto contraste Stark, escala de texto (100%-130%), reducción de movimiento y atajos de teclado.</div>
          <div class="hud-card-action"><span>Abrir Accesibilidad</span> <span>→</span></div>
        </div>"""

NEW_MODALS_HTML = """
  <!-- ======================================================== -->
  <!-- MODAL: MOTOR DE CRECIMIENTO & UNIT ECONOMICS (MKT 360)   -->
  <!-- ======================================================== -->
  <div class="modal-overlay" id="marketing-modal">
    <div class="modal-card" style="max-width: 800px;">
      <div class="modal-header">
        <div class="modal-icon" style="color: #f43f5e; border-color: rgba(244, 63, 94, 0.4); background: rgba(244, 63, 94, 0.12);">📈</div>
        <div class="modal-title">
          <h2>Motor de Crecimiento & Unit Economics (MKT 360)</h2>
          <p>Métricas SaaS, CAC, LTV, Payback, Churn y Diagnóstico de Embudos</p>
        </div>
        <button class="modal-close" onclick="closeMarketingModal()">&times;</button>
      </div>

      <!-- Formulario de Entrada Unit Economics -->
      <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px; margin-bottom: 14px;">
        <div>
          <label style="font-size: 0.7rem; color: #94a3b8; display: block;">CAC ($ COP):</label>
          <input type="number" id="mkt-cac-input" value="120000" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
        </div>
        <div>
          <label style="font-size: 0.7rem; color: #94a3b8; display: block;">ARPU Mensual ($):</label>
          <input type="number" id="mkt-arpu-input" value="65000" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
        </div>
        <div>
          <label style="font-size: 0.7rem; color: #94a3b8; display: block;">Churn Mensual (%):</label>
          <input type="number" step="0.1" id="mkt-churn-input" value="3.0" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
        </div>
        <div>
          <label style="font-size: 0.7rem; color: #94a3b8; display: block;">Margen Bruto (%):</label>
          <input type="number" id="mkt-margin-input" value="80" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
        </div>
      </div>

      <div style="display: flex; gap: 10px; margin-bottom: 12px;">
        <button type="button" class="btn-primary" style="flex: 1; padding: 8px; font-size: 0.8rem;" onclick="submitMarketingUnitEconomics()">Calcular Unit Economics</button>
        <button type="button" class="btn-secondary" style="padding: 8px 14px; font-size: 0.8rem;" onclick="runQuickFunnelAudit()">Auditar Embudo 50k</button>
      </div>

      <div id="mkt-results-panel" style="display: none; background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(244, 63, 94, 0.3); border-radius: 8px; padding: 14px; margin-bottom: 12px;">
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 8px; margin-bottom: 10px; text-align: center;">
          <div style="background: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px;">
            <div style="font-size: 0.68rem; color: #94a3b8;">RATIO LTV/CAC</div>
            <div id="mkt-res-ratio" style="font-size: 1.15rem; font-weight: 700; color: #38ef7d;">0.0x</div>
          </div>
          <div style="background: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px;">
            <div style="font-size: 0.68rem; color: #94a3b8;">PAYBACK (MESES)</div>
            <div id="mkt-res-payback" style="font-size: 1.15rem; font-weight: 700; color: #00d2ff;">0.0 m</div>
          </div>
          <div style="background: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px;">
            <div style="font-size: 0.68rem; color: #94a3b8;">LTV ESTIMADO</div>
            <div id="mkt-res-ltv" style="font-size: 1.05rem; font-weight: 700; color: #ffd166;">$0 COP</div>
          </div>
          <div style="background: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px;">
            <div style="font-size: 0.68rem; color: #94a3b8;">CHURN ANUAL</div>
            <div id="mkt-res-annualchurn" style="font-size: 1.05rem; font-weight: 700; color: #f43f5e;">0.0%</div>
          </div>
        </div>
        <div id="mkt-res-diagnostic" style="font-size: 0.8rem; color: #e2e8f0; line-height: 1.4;"></div>
      </div>

      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeMarketingModal()">Cerrar</button>
      </div>
    </div>
  </div>

  <!-- ======================================================== -->
  <!-- MODAL: GESTIÓN DE TALENTO & MATRIZ 9-BOX (C.S.T.)        -->
  <!-- ======================================================== -->
  <div class="modal-overlay" id="talent-modal">
    <div class="modal-card" style="max-width: 820px;">
      <div class="modal-header">
        <div class="modal-icon" style="color: #8b5cf6; border-color: rgba(139, 92, 246, 0.4); background: rgba(139, 92, 246, 0.12);">👥</div>
        <div class="modal-title">
          <h2>Gestión Estratégica de Talento & Matriz 9-Box</h2>
          <p>Evaluación de Desempeño vs Potencial, Clima eNPS y Costo de Rotación Laboral</p>
        </div>
        <button class="modal-close" onclick="closeTalentModal()">&times;</button>
      </div>

      <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 8px; margin-bottom: 12px;">
        <div>
          <label style="font-size: 0.7rem; color: #94a3b8; display: block;">Nombre Colaborador:</label>
          <input type="text" id="talent-name-input" value="Santiago Martínez" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
        </div>
        <div>
          <label style="font-size: 0.7rem; color: #94a3b8; display: block;">Cargo / Rol:</label>
          <input type="text" id="talent-role-input" value="Gerente Operaciones" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
        </div>
        <div>
          <label style="font-size: 0.7rem; color: #94a3b8; display: block;">Desempeño (1-3):</label>
          <input type="number" step="0.1" min="1.0" max="3.0" id="talent-perf-input" value="2.9" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
        </div>
        <div>
          <label style="font-size: 0.7rem; color: #94a3b8; display: block;">Potencial (1-3):</label>
          <input type="number" step="0.1" min="1.0" max="3.0" id="talent-pot-input" value="3.0" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
        </div>
      </div>

      <div style="display: flex; gap: 10px; margin-bottom: 12px;">
        <button type="button" class="btn-primary" style="flex: 1; padding: 8px; font-size: 0.8rem;" onclick="submitTalentEvaluation()">Clasificar en 9-Box Grid</button>
        <button type="button" class="btn-secondary" style="padding: 8px 14px; font-size: 0.8rem;" onclick="quickCalculateENPS()">Calcular eNPS Clima</button>
      </div>

      <div id="talent-results-panel" style="display: none; background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 8px; padding: 14px; margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <span style="font-size: 0.82rem; font-weight: 700; color: #8b5cf6;">CUADRANTE: <b id="talent-res-quadrant" style="color: #38ef7d;"></b></span>
          <span id="talent-res-risk" style="font-size: 0.72rem; padding: 2px 8px; border-radius: 12px; background: rgba(139, 92, 246, 0.2); color: #c4b5fd;"></span>
        </div>
        <div id="talent-res-action" style="font-size: 0.8rem; color: #e2e8f0; line-height: 1.45;"></div>
      </div>

      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeTalentModal()">Cerrar</button>
      </div>
    </div>
  </div>

  <!-- ======================================================== -->
  <!-- MODAL: RADAR CAMBIARIO & COBERTURA FORWARD (DIVISAS)     -->
  <!-- ======================================================== -->
  <div class="modal-overlay" id="forex-modal">
    <div class="modal-card" style="max-width: 820px;">
      <div class="modal-header">
        <div class="modal-icon" style="color: #10b981; border-color: rgba(16, 185, 129, 0.4); background: rgba(16, 185, 129, 0.12);">💱</div>
        <div class="modal-title">
          <h2>Radar Cambiario & Cobertura Forward de Divisas</h2>
          <p>Cotizaciones Oficiales BanRep, Dólar Cripto USDT, Spreads Bancarios y Hedging</p>
        </div>
        <button class="modal-close" onclick="closeForexModal()">&times;</button>
      </div>

      <!-- Ticker de Tasas Actuales -->
      <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 8px; margin-bottom: 14px; text-align: center;">
        <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(0, 210, 255, 0.3); padding: 8px; border-radius: 6px;">
          <div style="font-size: 0.68rem; color: #94a3b8;">TRM OFICIAL BANREP</div>
          <div style="font-size: 1.05rem; font-weight: 700; color: #00d2ff;">$4,185.00</div>
        </div>
        <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(16, 185, 129, 0.3); padding: 8px; border-radius: 6px;">
          <div style="font-size: 0.68rem; color: #94a3b8;">DÓLAR CRIPTO (USDT)</div>
          <div style="font-size: 1.05rem; font-weight: 700; color: #38ef7d;">$4,176.60</div>
        </div>
        <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(244, 63, 94, 0.3); padding: 8px; border-radius: 6px;">
          <div style="font-size: 0.68rem; color: #94a3b8;">DÓLAR TARJETA (+2.6%)</div>
          <div style="font-size: 1.05rem; font-weight: 700; color: #f43f5e;">$4,293.80</div>
        </div>
        <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255, 209, 102, 0.3); padding: 8px; border-radius: 6px;">
          <div style="font-size: 0.68rem; color: #94a3b8;">EURO OFICIAL (EUR)</div>
          <div style="font-size: 1.05rem; font-weight: 700; color: #ffd166;">$4,540.70</div>
        </div>
      </div>

      <!-- Simulador de Cobertura Forward -->
      <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 12px; margin-bottom: 12px;">
        <div style="font-size: 0.78rem; font-weight: 700; color: #10b981; margin-bottom: 8px;">🛡️ SIMULADOR DE COBERTURA FORWARD (PARIDAD IRP)</div>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 10px;">
          <div>
            <label style="font-size: 0.7rem; color: #94a3b8; display: block;">Monto USD a Cubrir:</label>
            <input type="number" id="forex-usd-input" value="25000" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
          </div>
          <div>
            <label style="font-size: 0.7rem; color: #94a3b8; display: block;">Plazo (Días):</label>
            <input type="number" id="forex-days-input" value="90" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
          </div>
          <div style="display: flex; align-items: flex-end;">
            <button type="button" class="btn-primary" style="width: 100%; padding: 7px; font-size: 0.78rem;" onclick="submitForexForward()">Simular Forward</button>
          </div>
        </div>

        <div id="forex-results-panel" style="display: none; background: rgba(0,0,0,0.3); border-radius: 6px; padding: 10px;">
          <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 6px;">
            <span style="color: #94a3b8;">Tasa Forward Teórica:</span>
            <strong id="forex-res-forward" style="color: #10b981;"></strong>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 6px;">
            <span style="color: #94a3b8;">Prima de Devaluación:</span>
            <strong id="forex-res-premium" style="color: #ffd166;"></strong>
          </div>
          <div id="forex-res-tip" style="font-size: 0.74rem; color: #cbd5e1; margin-top: 6px; line-height: 1.4;"></div>
        </div>
      </div>

      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeForexModal()">Cerrar</button>
      </div>
    </div>
  </div>"""

NEW_JS_ENGINE = """
      // ========================================================
      // CONTROLADORES INTERACTIVOS: MARKETING, TALENTO Y FOREX
      // ========================================================
      window.openMarketingModal = function() {
        const m = document.getElementById("marketing-modal");
        if (m) m.classList.add("active");
        playHudSound("open");
      };
      window.closeMarketingModal = function() {
        const m = document.getElementById("marketing-modal");
        if (m) m.classList.remove("active");
        playHudSound("close");
      };

      window.submitMarketingUnitEconomics = function() {
        const cac = parseFloat(document.getElementById("mkt-cac-input")?.value || 120000);
        const arpu = parseFloat(document.getElementById("mkt-arpu-input")?.value || 65000);
        const churn = parseFloat(document.getElementById("mkt-churn-input")?.value || 3.0);
        const margin = parseFloat(document.getElementById("mkt-margin-input")?.value || 80.0);

        const marginDec = margin / 100.0;
        const churnDec = Math.max(0.001, churn / 100.0);
        const monthlyProfit = arpu * marginDec;
        const ltv = monthlyProfit / churnDec;
        const ratio = ltv / Math.max(1, cac);
        const payback = cac / Math.max(1, monthlyProfit);
        const annualChurn = (1.0 - Math.pow(1.0 - churnDec, 12)) * 100.0;

        document.getElementById("mkt-res-ratio").textContent = ratio.toFixed(2) + "x";
        document.getElementById("mkt-res-ratio").style.color = ratio >= 3.0 ? "#38ef7d" : (ratio >= 1.5 ? "#ffd166" : "#f43f5e");
        document.getElementById("mkt-res-payback").textContent = payback.toFixed(1) + " m";
        document.getElementById("mkt-res-ltv").textContent = "$" + Math.round(ltv).toLocaleString() + " COP";
        document.getElementById("mkt-res-annualchurn").textContent = annualChurn.toFixed(1) + "%";

        let diag = "";
        if (ratio >= 3.0) {
          diag = "✅ <b>Benchmark SaaS Saludable:</b> Por cada peso invertido en adquisición, el cliente genera " + ratio.toFixed(1) + "x de margen. Modelo listo para escalar pauta publicitaria.";
        } else {
          diag = "⚠️ <b>Optimización Requerida:</b> Ratio LTV/CAC inferior a 3.0x. Se recomienda reducir CAC en canales de pauta o elevar la retención mensual.";
        }
        document.getElementById("mkt-res-diagnostic").innerHTML = diag;
        document.getElementById("mkt-results-panel").style.display = "block";
        playHudSound("click");
      };

      window.runQuickFunnelAudit = function() {
        const p = document.getElementById("mkt-results-panel");
        p.style.display = "block";
        document.getElementById("mkt-res-ratio").textContent = "3.25x";
        document.getElementById("mkt-res-payback").textContent = "2.3 m";
        document.getElementById("mkt-res-ltv").textContent = "$1,733,333 COP";
        document.getElementById("mkt-res-annualchurn").textContent = "30.6%";
        document.getElementById("mkt-res-diagnostic").innerHTML = "🎯 <b>Auditoría Embudo:</b> CTR: 2.5% | Clic a MQL: 8.0% | MQL a SQL: 25.0% | Win Rate Cierre: 30.0%. Flujo equilibrado y eficiente.";
        playHudSound("click");
      };

      window.openTalentModal = function() {
        const m = document.getElementById("talent-modal");
        if (m) m.classList.add("active");
        playHudSound("open");
      };
      window.closeTalentModal = function() {
        const m = document.getElementById("talent-modal");
        if (m) m.classList.remove("active");
        playHudSound("close");
      };

      window.submitTalentEvaluation = function() {
        const name = document.getElementById("talent-name-input")?.value || "Colaborador";
        const perf = parseFloat(document.getElementById("talent-perf-input")?.value || 2.5);
        const pot = parseFloat(document.getElementById("talent-pot-input")?.value || 2.5);

        let quad = "Colaborador Pilar (Core Player)";
        let risk = "Riesgo Moderado";
        let action = "Feedback trimestral y metas cuantitativas claras.";

        if (perf >= 2.5 && pot >= 2.5) {
          quad = "Estrella de Alto Valor (Star)";
          risk = "Alto Riesgo de Headhunting Externo";
          action = "Plan de sucesión ejecutiva, retención por equity/bonos y proyectos de máxima visibilidad para Santiago.";
        } else if (perf < 1.7 && pot >= 2.5) {
          quad = "Enigma / Diamante en Bruto";
          risk = "Desajuste de Rol";
          action = "Evaluar cambio de área y mentoría técnica directa antes de tomar decisiones drásticas.";
        } else if (perf >= 2.5 && pot < 1.7) {
          quad = "Especialista Confiable (Workhorse)";
          risk = "Resistencia a Roles Gerenciales";
          action = "Mantener en rol técnico como referente sénior sin forzar a gestión de personal.";
        }

        document.getElementById("talent-res-quadrant").textContent = quad;
        document.getElementById("talent-res-risk").textContent = risk;
        document.getElementById("talent-res-action").innerHTML = "<b>Plan Recomendado para " + name + ":</b> " + action;
        document.getElementById("talent-results-panel").style.display = "block";
        playHudSound("click");
      };

      window.quickCalculateENPS = function() {
        const p = document.getElementById("talent-results-panel");
        p.style.display = "block";
        document.getElementById("talent-res-quadrant").textContent = "eNPS: +50.0 Puntos (Excelente)";
        document.getElementById("talent-res-risk").textContent = "60% Promotores // 10% Detractores";
        document.getElementById("talent-res-action").innerHTML = "🌟 <b>Cultura de Alta Fidelidad:</b> Los colaboradores recomiendan activamente la empresa. Rotación estimada inferior al 8% anual.";
        playHudSound("click");
      };

      window.openForexModal = function() {
        const m = document.getElementById("forex-modal");
        if (m) m.classList.add("active");
        playHudSound("open");
      };
      window.closeForexModal = function() {
        const m = document.getElementById("forex-modal");
        if (m) m.classList.remove("active");
        playHudSound("close");
      };

      window.submitForexForward = function() {
        const usd = parseFloat(document.getElementById("forex-usd-input")?.value || 25000);
        const days = parseInt(document.getElementById("forex-days-input")?.value || 90);
        const spot = 4185.0;
        const rCop = (0.0975 * days) / 360.0;
        const rUsd = (0.0450 * days) / 360.0;
        const forward = spot * ((1.0 + rCop) / (1.0 + rUsd));
        const premium = forward - spot;
        const premiumPct = (premium / spot) * 100.0;

        document.getElementById("forex-res-forward").textContent = "$" + forward.toFixed(2) + " COP";
        document.getElementById("forex-res-premium").textContent = "+$" + premium.toFixed(2) + " COP (+" + premiumPct.toFixed(2) + "%)";
        document.getElementById("forex-res-tip").innerHTML = "💡 <b>Estrategia:</b> Cobertura Forward para $" + usd.toLocaleString() + " USD asegura un desembolso fijo de $" + Math.round(usd * forward).toLocaleString() + " COP frente a la volatilidad de la TRM.";
        document.getElementById("forex-results-panel").style.display = "block";
        playHudSound("click");
      };
"""

def main():
    target_path = "jarvis.html"
    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update Header Button text & count to 34
    content = content.replace("30 MÓDULOS HUD", "34 MÓDULOS HUD")
    content = content.replace("◈ 30 Módulos HUD", "◈ 34 Módulos HUD")
    content = content.replace("30 Módulos HUD", "34 Módulos HUD")
    content = content.replace("TODOS (30)", "TODOS (34)")
    content = content.replace("FINANZAS & ESTRATEGIA (8)", "FINANZAS & ESTRATEGIA (11)")
    content = content.replace("30 / 30 MÓDULOS", "34 / 34 MÓDULOS")
    content = content.replace("${visibleCount} / 30 MÓDULOS", "${visibleCount} / 34 MÓDULOS")
    content = content.replace("Alt+H) - 30 Módulos", "Alt+H) - 34 Módulos")
    content = content.replace(">30</span>", ">34</span>")

    # 2. Inject 4 new cards into #hud-modules-grid right after hud-card-system-pc
    card_pc_end = """          <div class="hud-card-action"><span>Ver PC</span> <span>→</span></div>
        </div>"""

    if card_pc_end in content and 'id="hud-card-marketing"' not in content:
        content = content.replace(card_pc_end, card_pc_end + "\n" + NEW_CARDS_HTML.strip())
        print("[PATCH 1] Inyectadas 4 nuevas tarjetas HUD (marketing, talent, forex, a11y)")
    else:
        print("[INFO 1] Tarjetas ya presentes o spot no encontrado")

    # 3. Inject 3 new modals right before <!-- ======================================================== -->\n  <!-- MODAL: CENTRO DE ACCESIBILIDAD
    target_a11y_modal = '<!-- ======================================================== -->\n  <!-- MODAL: CENTRO DE ACCESIBILIDAD UNIVERSAL STARK (A11Y)'
    if target_a11y_modal in content and 'id="marketing-modal"' not in content:
        content = content.replace(target_a11y_modal, NEW_MODALS_HTML.strip() + "\n\n  " + target_a11y_modal)
        print("[PATCH 2] Inyectados 3 nuevos modales (marketing-modal, talent-modal, forex-modal)")
    else:
        print("[INFO 2] Modales ya presentes o spot no encontrado")

    # 4. Inject JS engine & card bindings
    target_biohabits_bind = 'if (cardBio) cardBio.addEventListener("click", () => {\n          document.getElementById("hud-interfaces-modal")?.classList.remove("active");\n          window.openBiohabitsModal();\n        });'

    card_bindings = """
        const cardMkt = document.getElementById("hud-card-marketing");
        if (cardMkt) cardMkt.addEventListener("click", () => {
          document.getElementById("hud-interfaces-modal")?.classList.remove("active");
          window.openMarketingModal();
        });

        const cardTalent = document.getElementById("hud-card-talent");
        if (cardTalent) cardTalent.addEventListener("click", () => {
          document.getElementById("hud-interfaces-modal")?.classList.remove("active");
          window.openTalentModal();
        });

        const cardForex = document.getElementById("hud-card-forex");
        if (cardForex) cardForex.addEventListener("click", () => {
          document.getElementById("hud-interfaces-modal")?.classList.remove("active");
          window.openForexModal();
        });

        const cardA11y = document.getElementById("hud-card-a11y");
        if (cardA11y) cardA11y.addEventListener("click", () => {
          document.getElementById("hud-interfaces-modal")?.classList.remove("active");
          window.openA11yModal();
        });
"""

    if target_biohabits_bind in content and 'cardMkt' not in content:
        content = content.replace(target_biohabits_bind, target_biohabits_bind + "\n" + card_bindings.strip())
        print("[PATCH 3] Inyectados enlaces de apertura de tarjetas HUD en JS")

    target_js_spot = 'window.lisethViewer = {'
    if target_js_spot in content and 'window.openMarketingModal' not in content:
        content = content.replace(target_js_spot, NEW_JS_ENGINE.strip() + "\n\n        " + target_js_spot)
        print("[PATCH 4] Inyectados controladores JS de los nuevos modales")

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[SUCCESS] {target_path} guardado ({len(content)} caracteres)")

    # Sincronizar
    for dest in ["index.html", os.path.join("app", "static", "index.html")]:
        shutil.copyfile(target_path, dest)
        print(f"[SYNC] Sincronizado a {dest}")

if __name__ == "__main__":
    main()
