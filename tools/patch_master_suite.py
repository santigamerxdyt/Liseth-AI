# -*- coding: utf-8 -*-
"""
Patch script to inject the Master Executive Suite (Logistics EOQ, Harvard Negotiation, DIAN Tax, OKRs)
into jarvis.html, and synchronize to index.html and app/static/index.html.
"""
import os
import shutil

HUD_CARDS_INJECTION = """
        <!-- 21. Cadena de Suministro & Logística de Inventarios (EOQ & ROP) -->
        <div class="hud-card" data-category="automation" id="hud-card-logistics">
          <div class="hud-card-top">
            <div class="hud-card-icon" style="color: #38ef7d; border-color: rgba(56, 239, 125, 0.4); background: rgba(56, 239, 125, 0.12);">📦</div>
            <span class="hud-card-status status-online">EOQ & ROP</span>
          </div>
          <div class="hud-card-title">Logística & Cadena de Suministro</div>
          <div class="hud-card-desc">Modelo Wilson EOQ (Lote Económico de Pedido), Punto de Reorden (ROP), Stock de Seguridad y clasificación ABC de inventarios.</div>
          <div class="hud-card-action"><span>Optimizar Stock</span> <span>→</span></div>
        </div>

        <!-- 22. Simulador de Negociación Estratégica (Harvard BATNA & ZOPA) -->
        <div class="hud-card" data-category="intelligence" id="hud-card-negotiation">
          <div class="hud-card-top">
            <div class="hud-card-icon" style="color: #00d2ff; border-color: rgba(0, 210, 255, 0.4); background: rgba(0, 210, 255, 0.12);">🤝</div>
            <span class="hud-card-status status-online">ZOPA & BATNA</span>
          </div>
          <div class="hud-card-title">Negociación Estratégica Harvard</div>
          <div class="hud-card-desc">Análisis de Zona de Posible Acuerdo (ZOPA), precios de reserva, solución de Nash y tácticas de valor compartido.</div>
          <div class="hud-card-action"><span>Simular Acuerdo</span> <span>→</span></div>
        </div>

        <!-- 23. Auditor Tributario DIAN & Régimen Simple -->
        <div class="hud-card" data-category="system" id="hud-card-tax">
          <div class="hud-card-top">
            <div class="hud-card-icon" style="color: #ffd166; border-color: rgba(255, 209, 102, 0.4); background: rgba(255, 209, 102, 0.12);">🏛️</div>
            <span class="hud-card-status status-online">DIAN 2026</span>
          </div>
          <div class="hud-card-title">Auditor Tributario DIAN & RST</div>
          <div class="hud-card-desc">Semáforo de renta personas naturales, simulador comparativo Régimen Simple (RST) vs Ordinario y calendario fiscal por NIT.</div>
          <div class="hud-card-action"><span>Auditar Impuestos</span> <span>→</span></div>
        </div>

        <!-- 24. Cuadro de Mando Integral & OKRs Corporativos -->
        <div class="hud-card" data-category="connectors" id="hud-card-okrs">
          <div class="hud-card-top">
            <div class="hud-card-icon" style="color: #f43f5e; border-color: rgba(244, 63, 94, 0.4); background: rgba(244, 63, 94, 0.12);">📈</div>
            <span class="hud-card-status status-online">SCORECARD</span>
          </div>
          <div class="hud-card-title">Balanced Scorecard & OKRs</div>
          <div class="hud-card-desc">Cuadro de mando en 4 perspectivas (Financiera, Clientes, Procesos, Aprendizaje) con seguimiento de KRs y salud corporativa.</div>
          <div class="hud-card-action"><span>Ver Scorecard</span> <span>→</span></div>
        </div>
"""

MODALS_INJECTION = """
  <!-- ======================================================== -->
  <!-- MODAL: LOGÍSTICA DE INVENTARIOS & MODELO EOQ / ROP       -->
  <!-- ======================================================== -->
  <div class="modal-overlay" id="logistics-modal">
    <div class="modal-card" style="max-width: 780px;">
      <div class="modal-header">
        <div class="modal-icon" style="color: #38ef7d; border-color: rgba(56, 239, 125, 0.4); background: rgba(56, 239, 125, 0.12);">📦</div>
        <div class="modal-title">
          <h2>Logística de Inventarios & Modelo EOQ / ROP</h2>
          <p>Optimización del lote de pedido (Wilson), punto de reorden y stock de seguridad</p>
        </div>
        <button class="modal-close" onclick="closeLogisticsModal()">&times;</button>
      </div>

      <!-- Formulario EOQ -->
      <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(56, 239, 125, 0.25); border-radius: 8px; padding: 12px; margin-bottom: 12px;">
        <div style="font-size: 0.8rem; font-weight: 700; color: #38ef7d; margin-bottom: 8px;">📊 CÁLCULO DE LOTE ECONÓMICO DE PEDIDO (EOQ)</div>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 10px;">
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Demanda Anual (D):</label>
            <input type="number" id="eoq-demand" value="10000" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.82rem;" />
          </div>
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Costo por Pedir (S):</label>
            <input type="number" id="eoq-order-cost" value="50000" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.82rem;" />
          </div>
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Costo Mantener (H):</label>
            <input type="number" id="eoq-holding-cost" value="2500" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.82rem;" />
          </div>
          <div style="display: flex; align-items: flex-end;">
            <button type="button" class="btn-primary" style="width: 100%; padding: 7px; font-size: 0.8rem;" onclick="calculateEoq()">Calcular EOQ</button>
          </div>
        </div>

        <div id="eoq-results-panel" style="display: none; background: rgba(0,0,0,0.3); border-radius: 6px; padding: 10px;">
          <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; text-align: center;">
            <div>
              <div style="font-size: 0.7rem; color: #94a3b8;">LOTE ÓPTIMO (Q*)</div>
              <div style="font-size: 1.1rem; font-weight: 700; color: #38ef7d;" id="eoq-res-q">0 un</div>
            </div>
            <div>
              <div style="font-size: 0.7rem; color: #94a3b8;">PEDIDOS AL AÑO (N)</div>
              <div style="font-size: 1.1rem; font-weight: 700; color: #00d2ff;" id="eoq-res-n">0</div>
            </div>
            <div>
              <div style="font-size: 0.7rem; color: #94a3b8;">COSTO GESTIÓN TOTAL</div>
              <div style="font-size: 1.1rem; font-weight: 700; color: #ffd166;" id="eoq-res-cost">$0 COP</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Formulario ROP -->
      <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(0, 210, 255, 0.25); border-radius: 8px; padding: 12px; margin-bottom: 12px;">
        <div style="font-size: 0.8rem; font-weight: 700; color: #00d2ff; margin-bottom: 8px;">🚨 PUNTO DE REORDEN (ROP) & STOCK DE SEGURIDAD</div>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 10px;">
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Demanda Diaria (d):</label>
            <input type="number" id="rop-daily" value="30" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.82rem;" />
          </div>
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Lead Time (L días):</label>
            <input type="number" id="rop-lead" value="5" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.82rem;" />
          </div>
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Desv. Diaria (sigma):</label>
            <input type="number" id="rop-sigma" value="5" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.82rem;" />
          </div>
          <div style="display: flex; align-items: flex-end;">
            <button type="button" class="btn-primary" style="width: 100%; padding: 7px; font-size: 0.8rem; background: #00d2ff; border-color: #00d2ff;" onclick="calculateRop()">Calcular ROP</button>
          </div>
        </div>

        <div id="rop-results-panel" style="display: none; background: rgba(0,0,0,0.3); border-radius: 6px; padding: 10px; text-align: center;">
          <span style="font-size: 0.85rem; color: #e2e8f0;">Stock de Seguridad: <b id="rop-res-ss" style="color: #ffd166;">0 un</b> | Punto de Reorden: <b id="rop-res-rop" style="color: #00d2ff;">0 un</b></span>
          <div style="font-size: 0.74rem; color: #94a3b8; margin-top: 4px;">Disparar orden tan pronto el inventario llegue a este nivel.</div>
        </div>
      </div>

      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeLogisticsModal()">Cerrar</button>
      </div>
    </div>
  </div>


  <!-- ======================================================== -->
  <!-- MODAL: NEGOCIACIÓN ESTRATÉGICA (MODELO HARVARD: ZOPA)    -->
  <!-- ======================================================== -->
  <div class="modal-overlay" id="negotiation-modal">
    <div class="modal-card" style="max-width: 780px;">
      <div class="modal-header">
        <div class="modal-icon" style="color: #00d2ff; border-color: rgba(0, 210, 255, 0.4); background: rgba(0, 210, 255, 0.12);">🤝</div>
        <div class="modal-title">
          <h2>Simulador de Negociación Estratégica (Harvard)</h2>
          <p>Análisis de Zona de Posible Acuerdo (ZOPA), precios de reserva y BATNA/MAAN</p>
        </div>
        <button class="modal-close" onclick="closeNegotiationModal()">&times;</button>
      </div>

      <!-- Inputs Comprador vs Vendedor -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px;">
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(0, 210, 255, 0.3); border-radius: 8px; padding: 12px;">
          <div style="font-size: 0.8rem; font-weight: 700; color: #00d2ff; margin-bottom: 8px;">👤 COMPRADOR (CLIENTE)</div>
          <div style="margin-bottom: 6px;">
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Precio Máximo de Reserva (COP):</label>
            <input type="number" id="neg-buyer-res" value="50000000" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.82rem;" />
          </div>
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">BATNA / Alternativa Externa:</label>
            <input type="text" id="neg-buyer-batna" value="Cotizar con proveedores de Cali o Bogotá" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.78rem;" />
          </div>
        </div>

        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 239, 125, 0.3); border-radius: 8px; padding: 12px;">
          <div style="font-size: 0.8rem; font-weight: 700; color: #38ef7d; margin-bottom: 8px;">🏢 VENDEDOR (STARK / SANTIAGO)</div>
          <div style="margin-bottom: 6px;">
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Precio Mínimo de Reserva (COP):</label>
            <input type="number" id="neg-seller-res" value="42000000" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.82rem;" />
          </div>
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">BATNA / Alternativa Externa:</label>
            <input type="text" id="neg-seller-batna" value="Dedicar tiempo a contratos de mayor margen" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.78rem;" />
          </div>
        </div>
      </div>

      <div style="text-align: center; margin-bottom: 14px;">
        <button type="button" class="btn-primary" style="padding: 8px 24px; font-size: 0.85rem;" onclick="runNegotiationEval()">
          ⚡ Evaluar Rango ZOPA & Solución de Nash
        </button>
      </div>

      <!-- Resultados ZOPA -->
      <div id="neg-results-container" style="display: none; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 14px; margin-bottom: 12px;">
        <div style="text-align: center; margin-bottom: 10px;">
          <span id="neg-badge-status" style="font-size: 0.85rem; font-weight: 700; padding: 4px 12px; border-radius: 20px;"></span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.82rem; margin-bottom: 10px;">
          <div>Tamaño ZOPA (Excedente): <b id="neg-res-size" style="color: #00d2ff;">$0 COP</b></div>
          <div>Punto Medio Equitativo (Nash): <b id="neg-res-nash" style="color: #38ef7d;">$0 COP</b></div>
        </div>
        <div id="neg-res-verdict" style="font-size: 0.8rem; color: #cbd5e1; line-height: 1.4; border-top: 1px solid #334155; padding-top: 8px;"></div>
      </div>

      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeNegotiationModal()">Cerrar</button>
      </div>
    </div>
  </div>


  <!-- ======================================================== -->
  <!-- MODAL: AUDITOR TRIBUTARIO DIAN & RÉGIMEN SIMPLE          -->
  <!-- ======================================================== -->
  <div class="modal-overlay" id="tax-modal">
    <div class="modal-card" style="max-width: 800px;">
      <div class="modal-header">
        <div class="modal-icon" style="color: #ffd166; border-color: rgba(255, 209, 102, 0.4); background: rgba(255, 209, 102, 0.12);">🏛️</div>
        <div class="modal-title">
          <h2>Auditor Tributario DIAN & Régimen Simple 2026</h2>
          <p>Semáforo de renta, comparativa RST vs Ordinario y calendario fiscal por NIT</p>
        </div>
        <button class="modal-close" onclick="closeTaxModal()">&times;</button>
      </div>

      <!-- Comparador RST vs Ordinario -->
      <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 209, 102, 0.25); border-radius: 8px; padding: 12px; margin-bottom: 12px;">
        <div style="font-size: 0.8rem; font-weight: 700; color: #ffd166; margin-bottom: 8px;">⚖️ COMPARADOR: RÉGIMEN SIMPLE (RST) VS ORDINARIO</div>
        <div style="display: grid; grid-template-columns: 2fr 1.5fr 1.5fr; gap: 8px; margin-bottom: 10px;">
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Ingresos Brutos Anuales (COP):</label>
            <input type="number" id="tax-income-input" value="150000000" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.82rem;" />
          </div>
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Costos y Deducciones (COP):</label>
            <input type="number" id="tax-expenses-input" value="50000000" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.82rem;" />
          </div>
          <div style="display: flex; align-items: flex-end;">
            <button type="button" class="btn-primary" style="width: 100%; padding: 7px; font-size: 0.8rem;" onclick="compareRstVsOrdinario()">Comparar Regímenes</button>
          </div>
        </div>

        <div id="tax-rst-results" style="display: none; background: rgba(0,0,0,0.3); border-radius: 6px; padding: 10px;">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 0.78rem;">
            <div style="border-right: 1px solid #334155; padding-right: 8px;">
              <div style="color: #ff3366; font-weight: 700;">🏢 RÉGIMEN ORDINARIO</div>
              <div>Impuesto Renta 35%: <span id="tax-ord-renta" style="float: right;">$0</span></div>
              <div>ICA Municipal Estimado: <span id="tax-ord-ica" style="float: right;">$0</span></div>
              <div style="border-top: 1px solid #334155; margin-top: 4px; padding-top: 4px; font-weight: 700;">Total: <span id="tax-ord-total" style="float: right; color: #ff3366;">$0</span></div>
            </div>
            <div>
              <div style="color: #38ef7d; font-weight: 700;">🚀 RÉGIMEN SIMPLE (RST)</div>
              <div>Tarifa Consolidada: <span id="tax-rst-rate" style="float: right;">5.9%</span></div>
              <div>Total Consolidado (Renta+ICA): <span id="tax-rst-total" style="float: right; color: #38ef7d;">$0</span></div>
              <div style="border-top: 1px solid #334155; margin-top: 4px; padding-top: 4px; font-weight: 700; color: #00d2ff;">Ahorro Fiscal: <span id="tax-rst-savings" style="float: right;">$0</span></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Verificador Renta Persona Natural -->
      <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(0, 210, 255, 0.25); border-radius: 8px; padding: 12px;">
        <div style="font-size: 0.8rem; font-weight: 700; color: #00d2ff; margin-bottom: 8px;">📋 VERIFICADOR DE OBLIGACIÓN RENTA (TOPES 1.400 / 4.500 UVT)</div>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 8px;">
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Patrimonio Bruto (COP):</label>
            <input type="number" id="tax-pat-input" value="180000000" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
          </div>
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Ingresos Brutos (COP):</label>
            <input type="number" id="tax-ing-input" value="55000000" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
          </div>
          <div style="display: flex; align-items: flex-end;">
            <button type="button" class="btn-primary" style="width: 100%; padding: 6px; font-size: 0.78rem; background: #00d2ff; border-color: #00d2ff;" onclick="checkRentaObligation()">Verificar Obligación</button>
          </div>
        </div>
        <div id="tax-renta-verdict" style="font-size: 0.78rem; color: #e2e8f0; padding: 6px 10px; border-radius: 4px; background: rgba(0,0,0,0.3); display: none;"></div>
      </div>

      <div class="modal-actions" style="margin-top: 14px;">
        <button class="btn-secondary" onclick="closeTaxModal()">Cerrar</button>
      </div>
    </div>
  </div>


  <!-- ======================================================== -->
  <!-- MODAL: BALANCED SCORECARD & OKRS CORPORATIVOS            -->
  <!-- ======================================================== -->
  <div class="modal-overlay" id="okrs-modal">
    <div class="modal-card" style="max-width: 820px;">
      <div class="modal-header">
        <div class="modal-icon" style="color: #f43f5e; border-color: rgba(244, 63, 94, 0.4); background: rgba(244, 63, 94, 0.12);">📈</div>
        <div class="modal-title">
          <h2>Balanced Scorecard (BSC) & OKRs Corporativos</h2>
          <p>Cuadro de mando en 4 perspectivas: Financiera, Clientes, Procesos y Aprendizaje</p>
        </div>
        <button class="modal-close" onclick="closeOkrsModal()">&times;</button>
      </div>

      <!-- Banner de Salud Corporativa -->
      <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(244, 63, 94, 0.3); border-radius: 8px; padding: 12px 18px; margin-bottom: 14px;">
        <div>
          <span style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase;">ÍNDICE DE SALUD CORPORATIVA GLOBAL</span>
          <div style="font-size: 1.4rem; font-weight: 700; color: #38ef7d;" id="okr-global-score">0.0%</div>
        </div>
        <div>
          <span id="okr-global-badge" style="font-size: 0.8rem; font-weight: 700; padding: 6px 16px; border-radius: 20px; background: rgba(56, 239, 125, 0.15); color: #38ef7d; border: 1px solid #38ef7d;">ESTADO ÓPTIMO</span>
        </div>
      </div>

      <!-- Grid de 4 Perspectivas -->
      <div id="okrs-perspectives-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;"></div>

      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeOkrsModal()">Cerrar</button>
      </div>
    </div>
  </div>
"""

JS_ENGINE_INJECTION = """
      // ========================================================
      // MOTOR TÁCTICO: LOGÍSTICA, NEGOCIACIÓN HARVARD, DIAN Y OKRS
      // ========================================================
      window.openLogisticsModal = function() {
        const m = document.getElementById("logistics-modal");
        if (m) m.classList.add("active");
        playHudSound("open");
      };

      window.closeLogisticsModal = function() {
        const m = document.getElementById("logistics-modal");
        if (m) m.classList.remove("active");
        playHudSound("close");
      };

      window.calculateEoq = async function() {
        playHudSound("click");
        const d = parseFloat(document.getElementById("eoq-demand")?.value || "10000");
        const s = parseFloat(document.getElementById("eoq-order-cost")?.value || "50000");
        const h = parseFloat(document.getElementById("eoq-holding-cost")?.value || "2500");

        try {
          const res = await fetch("/api/suite/logistics/eoq", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ annual_demand: d, order_cost: s, holding_cost: h })
          });
          if (res.ok) {
            const data = await res.json();
            const e = data.eoq;
            document.getElementById("eoq-results-panel").style.display = "block";
            document.getElementById("eoq-res-q").textContent = e.optimal_order_quantity_eoq + " un";
            document.getElementById("eoq-res-n").textContent = e.orders_per_year + " pedidos/año";
            document.getElementById("eoq-res-cost").textContent = "$" + Math.round(e.total_inventory_cost).toLocaleString("es-CO") + " COP";
            showToast("Lote óptimo calculado con éxito");
          }
        } catch (e) {
          console.error(e);
        }
      };

      window.calculateRop = async function() {
        playHudSound("click");
        const d = parseFloat(document.getElementById("rop-daily")?.value || "30");
        const l = parseFloat(document.getElementById("rop-lead")?.value || "5");
        const sig = parseFloat(document.getElementById("rop-sigma")?.value || "5");

        try {
          const res = await fetch("/api/suite/logistics/rop", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ daily_demand: d, lead_time_days: l, std_dev_daily_demand: sig })
          });
          if (res.ok) {
            const data = await res.json();
            const r = data.rop;
            document.getElementById("rop-results-panel").style.display = "block";
            document.getElementById("rop-res-ss").textContent = r.safety_stock_units + " un";
            document.getElementById("rop-res-rop").textContent = r.reorder_point_rop_units + " un";
            showToast("Punto de reorden (ROP) calculado");
          }
        } catch (e) {
          console.error(e);
        }
      };

      // ─── NEGOCIACIÓN HARVARD ───
      window.openNegotiationModal = function() {
        const m = document.getElementById("negotiation-modal");
        if (m) m.classList.add("active");
        playHudSound("open");
      };

      window.closeNegotiationModal = function() {
        const m = document.getElementById("negotiation-modal");
        if (m) m.classList.remove("active");
        playHudSound("close");
      };

      window.runNegotiationEval = async function() {
        playHudSound("click");
        const bRes = parseFloat(document.getElementById("neg-buyer-res")?.value || "50000000");
        const sRes = parseFloat(document.getElementById("neg-seller-res")?.value || "42000000");
        const bBatna = document.getElementById("neg-buyer-batna")?.value;
        const sBatna = document.getElementById("neg-seller-batna")?.value;

        try {
          const res = await fetch("/api/suite/negotiation/eval", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              buyer_reservation_price: bRes,
              seller_reservation_price: sRes,
              buyer_batna: bBatna,
              seller_batna: sBatna
            })
          });
          if (res.ok) {
            const data = await res.json();
            const n = data.negotiation;
            document.getElementById("neg-results-container").style.display = "block";
            const badge = document.getElementById("neg-badge-status");
            if (n.has_zopa) {
              badge.textContent = "🟢 ZOPA POSITIVA: ACUERDO VIABLE";
              badge.style.background = "rgba(56, 239, 125, 0.15)";
              badge.style.color = "#38ef7d";
              badge.style.border = "1px solid #38ef7d";
              document.getElementById("neg-res-size").textContent = "$" + Math.round(n.zopa_size).toLocaleString("es-CO") + " COP";
              document.getElementById("neg-res-nash").textContent = "$" + Math.round(n.fair_midpoint_price).toLocaleString("es-CO") + " COP";
            } else {
              badge.textContent = "🔴 IMPASSE: BRECHA DE NEGOCIACIÓN";
              badge.style.background = "rgba(255, 51, 102, 0.15)";
              badge.style.color = "#ff3366";
              badge.style.border = "1px solid #ff3366";
              document.getElementById("neg-res-size").textContent = "Brecha: $" + Math.round(n.gap).toLocaleString("es-CO") + " COP";
              document.getElementById("neg-res-nash").textContent = "N/A (Sin acuerdo)";
            }
            document.getElementById("neg-res-verdict").innerHTML = "💡 " + n.verdict;
            showToast("Simulación de negociación completada");
          }
        } catch (e) {
          console.error(e);
        }
      };

      // ─── AUDITORÍA DIAN ───
      window.openTaxModal = function() {
        const m = document.getElementById("tax-modal");
        if (m) m.classList.add("active");
        playHudSound("open");
      };

      window.closeTaxModal = function() {
        const m = document.getElementById("tax-modal");
        if (m) m.classList.remove("active");
        playHudSound("close");
      };

      window.compareRstVsOrdinario = async function() {
        playHudSound("click");
        const inc = parseFloat(document.getElementById("tax-income-input")?.value || "150000000");
        const exp = parseFloat(document.getElementById("tax-expenses-input")?.value || "50000000");

        try {
          const res = await fetch("/api/suite/tax/rst-compare", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ gross_annual_income: inc, deductible_expenses: exp })
          });
          if (res.ok) {
            const data = await res.json();
            const s = data.simulation;
            document.getElementById("tax-rst-results").style.display = "block";
            document.getElementById("tax-ord-renta").textContent = "$" + Math.round(s.ordinario.income_tax_35pct).toLocaleString("es-CO");
            document.getElementById("tax-ord-ica").textContent = "$" + Math.round(s.ordinario.ica_municipal_est).toLocaleString("es-CO");
            document.getElementById("tax-ord-total").textContent = "$" + Math.round(s.ordinario.total_liability).toLocaleString("es-CO");

            document.getElementById("tax-rst-rate").textContent = s.regimen_simple.consolidated_rate_pct + "%";
            document.getElementById("tax-rst-total").textContent = "$" + Math.round(s.regimen_simple.total_liability).toLocaleString("es-CO");
            document.getElementById("tax-rst-savings").textContent = "$" + Math.round(s.estimated_savings_cop).toLocaleString("es-CO") + " COP";
            showToast("Comparativa de regímenes completada");
          }
        } catch (e) {
          console.error(e);
        }
      };

      window.checkRentaObligation = async function() {
        playHudSound("click");
        const pat = parseFloat(document.getElementById("tax-pat-input")?.value || "0");
        const ing = parseFloat(document.getElementById("tax-ing-input")?.value || "0");

        try {
          const res = await fetch("/api/suite/tax/renta-check", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ patrimonio_bruto: pat, ingresos_brutos: ing })
          });
          if (res.ok) {
            const data = await res.json();
            const a = data.audit;
            const el = document.getElementById("tax-renta-verdict");
            el.style.display = "block";
            if (a.is_obligated) {
              el.style.color = "#ff3366";
              el.innerHTML = "⚠️ <b>OBLIGADO A DECLARAR RENTA:</b> " + a.reasons.join(" | ");
            } else {
              el.style.color = "#38ef7d";
              el.innerHTML = "🟢 <b>NO OBLIGADO:</b> Sus valores están por debajo de los topes legales de 1.400 y 4.500 UVT.";
            }
          }
        } catch (e) {
          console.error(e);
        }
      };

      // ─── BALANCED SCORECARD & OKRS ───
      window.openOkrsModal = function() {
        const m = document.getElementById("okrs-modal");
        if (m) m.classList.add("active");
        playHudSound("open");
        window.loadOkrsDashboard();
      };

      window.closeOkrsModal = function() {
        const m = document.getElementById("okrs-modal");
        if (m) m.classList.remove("active");
        playHudSound("close");
      };

      window.loadOkrsDashboard = async function() {
        try {
          const res = await fetch("/api/suite/okrs/dashboard");
          if (res.ok) {
            const data = await res.json();
            document.getElementById("okr-global-score").textContent = data.global_corporate_health_pct + "%";
            const grid = document.getElementById("okrs-perspectives-grid");
            if (!grid) return;
            grid.innerHTML = "";

            for (const [pName, pInfo] of Object.entries(data.perspectives)) {
              const card = document.createElement("div");
              card.style.cssText = "background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 12px;";
              card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                  <span style="font-size: 0.82rem; font-weight: 700; color: #fff;">${pName}</span>
                  <span style="font-size: 0.78rem; font-weight: 700; color: ${pInfo.status === 'VERDE' ? '#38ef7d' : '#ffd166'};">${pInfo.average_pct}%</span>
                </div>
                <div style="background: #1e293b; height: 6px; border-radius: 3px; overflow: hidden; margin-bottom: 10px;">
                  <div style="background: ${pInfo.status === 'VERDE' ? '#38ef7d' : '#ffd166'}; height: 100%; width: ${pInfo.average_pct}%;"></div>
                </div>
                <div style="font-size: 0.74rem; color: #cbd5e1;">
                  ${pInfo.objectives.map(o => `
                    <div style="margin-bottom: 6px;">
                      <div>• <b>${o.objective}</b> (${o.progress_pct}%)</div>
                      <div style="color: #64748b; font-size: 0.7rem; margin-left: 8px;">${o.key_results.map(k => `${k.title} [${k.progress_pct}%]`).join("<br>")}</div>
                    </div>
                  `).join("")}
                </div>
              `;
              grid.appendChild(card);
            }
          }
        } catch (e) {
          console.error(e);
        }
      };
"""

CARD_LISTENERS_INJECTION = """
        // Conexiones de apertura para los 4 módulos de la Suite Master
        const cardLog = document.getElementById("hud-card-logistics");
        if (cardLog) cardLog.addEventListener("click", () => {
          document.getElementById("hud-interfaces-modal")?.classList.remove("active");
          window.openLogisticsModal();
        });
        const cardNeg = document.getElementById("hud-card-negotiation");
        if (cardNeg) cardNeg.addEventListener("click", () => {
          document.getElementById("hud-interfaces-modal")?.classList.remove("active");
          window.openNegotiationModal();
        });
        const cardTax = document.getElementById("hud-card-tax");
        if (cardTax) cardTax.addEventListener("click", () => {
          document.getElementById("hud-interfaces-modal")?.classList.remove("active");
          window.openTaxModal();
        });
        const cardOkr = document.getElementById("hud-card-okrs");
        if (cardOkr) cardOkr.addEventListener("click", () => {
          document.getElementById("hud-interfaces-modal")?.classList.remove("active");
          window.openOkrsModal();
        });
"""

def main():
    target_path = "jarvis.html"
    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update filter tab count to TODOS (26)
    if 'TODOS (22)' in content:
        content = content.replace('TODOS (22)', 'TODOS (26)')
        print("[PATCH] Actualizado tab contador a TODOS (26)")
    elif 'TODOS (15)' in content:
        content = content.replace('TODOS (15)', 'TODOS (26)')
        print("[PATCH] Actualizado tab contador a TODOS (26)")

    # 2. Inject HUD Cards
    target_card_end = '<!-- 12. Control y Ejecución en Windows PC -->'
    if 'id="hud-card-logistics"' not in content:
        if target_card_end in content:
            content = content.replace(target_card_end, HUD_CARDS_INJECTION.strip() + "\n\n        " + target_card_end)
            print("[PATCH] Inyectadas 4 HUD cards master")
        else:
            print("[WARN] No se encontró target_card_end")
    else:
        print("[SKIP] HUD cards ya presentes")

    # 3. Inject Modals
    if 'id="logistics-modal"' not in content:
        target_modal_end = '<div class="liseth-toast" id="liseth-toast"></div>'
        if target_modal_end in content:
            content = content.replace(target_modal_end, MODALS_INJECTION.strip() + "\n\n  " + target_modal_end)
            print("[PATCH] Inyectados 4 modales master")
        else:
            print("[WARN] No se encontró target_modal_end")
    else:
        print("[SKIP] Modales ya presentes")

    # 4. Inject JS Engine
    if 'window.openLogisticsModal' not in content:
        target_js_end = 'window.lisethViewer = {'
        if target_js_end in content:
            content = content.replace(target_js_end, JS_ENGINE_INJECTION.strip() + "\n\n        " + target_js_end)
            print("[PATCH] Inyectado motor JS de logística, negociación, impuestos y okrs")
        else:
            print("[WARN] No se encontró target_js_end")
    else:
        print("[SKIP] Motor JS ya presente")

    # 5. Inject Card Listeners
    if 'hud-card-logistics' not in content or 'cardLog.addEventListener' not in content:
        target_card_listener = 'window.openPitchModal();\n        });'
        if target_card_listener in content:
            content = content.replace(target_card_listener, target_card_listener + "\n" + CARD_LISTENERS_INJECTION.strip())
            print("[PATCH] Inyectados listeners para apertura de modales master")
        else:
            print("[WARN] No se encontró target_card_listener")
    else:
        print("[SKIP] Card listeners ya presentes")

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[PATCH] {target_path} guardado con éxito ({len(content)} caracteres)")

    # Sincronizar a index.html y app/static/index.html
    for dest in ["index.html", os.path.join("app", "static", "index.html")]:
        shutil.copyfile(target_path, dest)
        print(f"[SYNC] Sincronizado a {dest}")

if __name__ == "__main__":
    main()
