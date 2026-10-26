# -*- coding: utf-8 -*-
"""
Patch script to inject the Tax Payment & Varied Executive Suite into jarvis.html,
and synchronize to index.html and app/static/index.html.
"""
import os
import shutil

HUD_CARDS_INJECTION = """
        <!-- 25. Asistente y Pasarela de Pago de Impuestos DIAN (Form 490 & PSE) -->
        <div class="hud-card" data-category="automation" id="hud-card-tax-pay">
          <div class="hud-card-top">
            <div class="hud-card-icon" style="color: #ffd166; border-color: rgba(255, 209, 102, 0.4); background: rgba(255, 209, 102, 0.12);">🧾</div>
            <span class="hud-card-status status-online">PAGO DIAN PSE</span>
          </div>
          <div class="hud-card-title">Pago de Impuestos DIAN (Form 490)</div>
          <div class="hud-card-desc">Liquidación oficial de recibos 490 (Renta, Retefuente, IVA), intereses moratorios día a día, sanciones y botón de pago PSE.</div>
          <div class="hud-card-action"><span>Pagar Impuesto</span> <span>→</span></div>
        </div>

        <!-- 26. Valuación Financiera de Empresas (DCF & Múltiplos) -->
        <div class="hud-card" data-category="intelligence" id="hud-card-valuation">
          <div class="hud-card-top">
            <div class="hud-card-icon" style="color: #00f0ff; border-color: rgba(0, 240, 255, 0.4); background: rgba(0, 240, 255, 0.12);">💎</div>
            <span class="hud-card-status status-online">VALUACIÓN DCF</span>
          </div>
          <div class="hud-card-title">Valuación de Empresas & Startups</div>
          <div class="hud-card-desc">Flujo de caja libre descontado (DCF), valor terminal Gordon-Shapiro, múltiplos EV/EBITDA y método Venture Capital.</div>
          <div class="hud-card-action"><span>Valorar Empresa</span> <span>→</span></div>
        </div>

        <!-- 27. Logística de Rutas & Fletes Colombia -->
        <div class="hud-card" data-category="connectors" id="hud-card-fleet">
          <div class="hud-card-top">
            <div class="hud-card-icon" style="color: #38ef7d; border-color: rgba(56, 239, 125, 0.4); background: rgba(56, 239, 125, 0.12);">🚛</div>
            <span class="hud-card-status status-online">FLETES CO</span>
          </div>
          <div class="hud-card-title">Rutas & Fletes Colombia</div>
          <div class="hud-card-desc">Liquidación de transporte de carga (Cali, Palmira, Yumbo, Buenaventura, Bogotá), peajes INVIAS, ACPM y huella de carbono.</div>
          <div class="hud-card-action"><span>Liquidar Flete</span> <span>→</span></div>
        </div>

        <!-- 28. Telemetría Biocognitiva & Hábitos Ejecutivos CEO -->
        <div class="hud-card" data-category="system" id="hud-card-biohabits">
          <div class="hud-card-top">
            <div class="hud-card-icon" style="color: #a855f7; border-color: rgba(168, 85, 247, 0.4); background: rgba(168, 85, 247, 0.12);">🧠</div>
            <span class="hud-card-status status-online">VIGOR CEO</span>
          </div>
          <div class="hud-card-title">Telemetría Biocognitiva & Hábitos</div>
          <div class="hud-card-desc">Índice biocognitivo del CEO, descanso nocturno, horas pico de claridad mental según cronotipo y prescripción neuro-ergonómica.</div>
          <div class="hud-card-action"><span>Ver Vigor</span> <span>→</span></div>
        </div>
"""

MODALS_INJECTION = """
  <!-- ======================================================== -->
  <!-- MODAL: ASISTENTE & PASARELA DE PAGO IMPUESTOS DIAN (490) -->
  <!-- ======================================================== -->
  <div class="modal-overlay" id="tax-pay-modal">
    <div class="modal-card" style="max-width: 820px;">
      <div class="modal-header">
        <div class="modal-icon" style="color: #ffd166; border-color: rgba(255, 209, 102, 0.4); background: rgba(255, 209, 102, 0.12);">🧾</div>
        <div class="modal-title">
          <h2>Asistente de Liquidación & Pago de Impuestos DIAN</h2>
          <p>Generación oficial de Formulario 490, intereses moratorios día a día y pasarela PSE</p>
        </div>
        <button class="modal-close" onclick="closeTaxPayModal()">&times;</button>
      </div>

      <!-- Formulario de Liquidación 490 -->
      <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 209, 102, 0.3); border-radius: 8px; padding: 12px; margin-bottom: 12px;">
        <div style="font-size: 0.8rem; font-weight: 700; color: #ffd166; margin-bottom: 8px;">🏛️ DATOS DE LA OBLIGACIÓN FISCAL (FORMULARIO 490)</div>
        <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 8px; margin-bottom: 8px;">
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Concepto Tributario:</label>
            <select id="f490-concept" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;">
              <option value="retefuente">[02] Retención en la Fuente Mensual (Form 350)</option>
              <option value="iva">[03] Impuesto sobre las Ventas IVA (Form 300)</option>
              <option value="renta_pn">[01] Renta Personas Naturales (Form 210)</option>
              <option value="renta_pj">[01] Renta Personas Jurídicas (Form 110)</option>
              <option value="rst_anticipo">[49] Anticipo Bimestral Régimen Simple (Form 2593)</option>
              <option value="ica_municipal">[05] Impuesto Industria y Comercio (ICA)</option>
            </select>
          </div>
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Año Gravable:</label>
            <input type="number" id="f490-year" value="2026" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
          </div>
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Período (Mes/Bim):</label>
            <input type="text" id="f490-period" value="01" placeholder="Ej: 01" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
          </div>
        </div>

        <div style="display: grid; grid-template-columns: 1.5fr 1.5fr 1fr 1fr; gap: 8px; margin-bottom: 10px;">
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">NIT o Cédula:</label>
            <input type="text" id="f490-nit" value="901.884.221-3" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
          </div>
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Monto del Impuesto Base (COP):</label>
            <input type="number" id="f490-amount" value="1850000" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
          </div>
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Vencimiento Oficial:</label>
            <input type="date" id="f490-due-date" value="2026-02-15" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.78rem;" />
          </div>
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Fecha de Pago:</label>
            <input type="date" id="f490-pay-date" value="2026-02-15" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.78rem;" />
          </div>
        </div>

        <div style="text-align: center;">
          <button type="button" class="btn-primary" style="padding: 8px 24px; font-size: 0.85rem;" onclick="settleTaxForm()">
            ⚡ Liquidar Formulario 490 Oficial
          </button>
        </div>
      </div>

      <!-- Panel de Liquidación Oficial -->
      <div id="f490-settlement-results" style="display: none; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 14px; margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 6px; margin-bottom: 8px;">
          <span style="font-size: 0.78rem; font-weight: 700; color: #ffd166;" id="f490-res-id">F490-2026-XXXXXX</span>
          <span style="font-size: 0.72rem; color: #94a3b8;" id="f490-res-concept"></span>
        </div>

        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 10px; font-size: 0.78rem;">
          <div>Base Impuesto: <b id="f490-res-base" style="color: #fff; display: block;">$0</b></div>
          <div>Sanción Extemporaneidad: <b id="f490-res-penalty" style="color: #ff3366; display: block;">$0</b></div>
          <div>Intereses Mora (Usura): <b id="f490-res-interest" style="color: #ff3366; display: block;">$0</b></div>
          <div>TOTAL A PAGAR: <b id="f490-res-total" style="color: #00f0ff; font-size: 1.1rem; display: block;">$0 COP</b></div>
        </div>

        <!-- Pasarela PSE Directa -->
        <div style="background: rgba(0,0,0,0.3); border-radius: 6px; padding: 10px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
          <div style="font-size: 0.78rem; color: #cbd5e1;">
            Pagar en línea vía <b>PSE / Transferencia Interoperable Bre-B</b>:
          </div>
          <div style="display: flex; gap: 8px; align-items: center;">
            <select id="f490-pse-bank" style="background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;">
              <option value="Bancolombia">Bancolombia</option>
              <option value="Davivienda">Davivienda</option>
              <option value="Nequi">Nequi</option>
              <option value="Banco de Bogota">Banco de Bogotá</option>
              <option value="Portal MUISCA DIAN">Portal MUISCA DIAN</option>
            </select>
            <button type="button" class="btn-primary" style="padding: 6px 16px; font-size: 0.82rem; background: #38ef7d; border-color: #38ef7d; color: #0f172a; font-weight: 700;" onclick="initiatePsePayment()">
              💳 Pagar con PSE
            </button>
          </div>
        </div>
      </div>

      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeTaxPayModal()">Cerrar</button>
      </div>
    </div>
  </div>


  <!-- ======================================================== -->
  <!-- MODAL: VALUACIÓN FINANCIERA DE EMPRESAS (DCF)            -->
  <!-- ======================================================== -->
  <div class="modal-overlay" id="valuation-modal">
    <div class="modal-card" style="max-width: 800px;">
      <div class="modal-header">
        <div class="modal-icon" style="color: #00f0ff; border-color: rgba(0, 240, 255, 0.4); background: rgba(0, 240, 255, 0.12);">💎</div>
        <div class="modal-title">
          <h2>Valuación Financiera de Empresas & Startups</h2>
          <p>Flujo de caja libre descontado (DCF), múltiplos de mercado y método Venture Capital</p>
        </div>
        <button class="modal-close" onclick="closeValuationModal()">&times;</button>
      </div>

      <!-- Formulario DCF -->
      <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(0, 240, 255, 0.25); border-radius: 8px; padding: 12px; margin-bottom: 12px;">
        <div style="font-size: 0.8rem; font-weight: 700; color: #00f0ff; margin-bottom: 8px;">📊 VALUACIÓN POR FLUJO DE CAJA LIBRE DESCONTADO (DCF)</div>
        <div style="margin-bottom: 8px;">
          <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Flujos de Caja Libres Proyectados (Años 1 al 5, separados por coma):</label>
          <input type="text" id="dcf-flows-input" value="50000000, 70000000, 95000000, 120000000, 150000000" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.82rem;" />
        </div>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 10px;">
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">WACC (%):</label>
            <input type="number" step="0.5" id="dcf-wacc-input" value="12.0" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
          </div>
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Crecimiento g (%):</label>
            <input type="number" step="0.5" id="dcf-g-input" value="3.0" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
          </div>
          <div>
            <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Caja Neta (COP):</label>
            <input type="number" id="dcf-cash-input" value="30000000" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
          </div>
          <div style="display: flex; align-items: flex-end;">
            <button type="button" class="btn-primary" style="width: 100%; padding: 7px; font-size: 0.8rem;" onclick="runDcfValuation()">Calcular Valor</button>
          </div>
        </div>

        <div id="dcf-results-panel" style="display: none; background: rgba(0,0,0,0.3); border-radius: 6px; padding: 10px;">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: center;">
            <div style="background: rgba(0, 240, 255, 0.08); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 6px; padding: 8px;">
              <div style="font-size: 0.7rem; color: #94a3b8;">VALOR DE LA EMPRESA (EV)</div>
              <div style="font-size: 1.15rem; font-weight: 700; color: #00f0ff;" id="dcf-res-ev">$0 COP</div>
            </div>
            <div style="background: rgba(56, 239, 125, 0.08); border: 1px solid rgba(56, 239, 125, 0.3); border-radius: 6px; padding: 8px;">
              <div style="font-size: 0.7rem; color: #94a3b8;">VALOR PATRIMONIAL (EQUITY)</div>
              <div style="font-size: 1.15rem; font-weight: 700; color: #38ef7d;" id="dcf-res-equity">$0 COP</div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeValuationModal()">Cerrar</button>
      </div>
    </div>
  </div>


  <!-- ======================================================== -->
  <!-- MODAL: LOGÍSTICA DE RUTAS & FLETES COLOMBIA              -->
  <!-- ======================================================== -->
  <div class="modal-overlay" id="fleet-modal">
    <div class="modal-card" style="max-width: 780px;">
      <div class="modal-header">
        <div class="modal-icon" style="color: #38ef7d; border-color: rgba(56, 239, 125, 0.4); background: rgba(56, 239, 125, 0.12);">🚛</div>
        <div class="modal-title">
          <h2>Rutas & Fletes Logísticos en Colombia</h2>
          <p>Liquidación de costos de despacho, peajes INVIAS, ACPM y emisiones CO2</p>
        </div>
        <button class="modal-close" onclick="closeFleetModal()">&times;</button>
      </div>

      <!-- Selector de Rutas y Vehículo -->
      <div style="display: grid; grid-template-columns: 2fr 2fr 1fr; gap: 8px; margin-bottom: 12px;">
        <div>
          <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Ruta Comercial:</label>
          <select id="fleet-route-select" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;">
            <option value="palmira_cali">Palmira ➔ Cali (28 km - 1 peaje)</option>
            <option value="palmira_yumbo">Palmira ➔ Yumbo Industrial (36 km - 1 peaje)</option>
            <option value="palmira_buenaventura">Palmira ➔ Buenaventura Puerto (145 km - 3 peajes)</option>
            <option value="palmira_pereira">Palmira ➔ Pereira Eje Cafetero (195 km - 3 peajes)</option>
            <option value="palmira_bogota">Palmira ➔ Bogotá D.C. La Línea (480 km - 8 peajes)</option>
            <option value="palmira_medellin">Palmira ➔ Medellín (430 km - 6 peajes)</option>
          </select>
        </div>
        <div>
          <label style="font-size: 0.72rem; color: #94a3b8; display: block;">Tipo de Vehículo de Carga:</label>
          <select id="fleet-veh-select" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;">
            <option value="van_urbana">Furgón Urbano / Van (1.5 Ton)</option>
            <option value="turbo_4_ton">Camión Turbo (4.5 Ton)</option>
            <option value="sencillo_8_ton">Camión Sencillo (8.5 Ton)</option>
            <option value="tractomula_32_ton">Tractocamión / Mula (32 Ton)</option>
          </select>
        </div>
        <div style="display: flex; align-items: flex-end;">
          <button type="button" class="btn-primary" style="width: 100%; padding: 7px; font-size: 0.8rem;" onclick="calculateFleetFreight()">Liquidar Flete</button>
        </div>
      </div>

      <div id="fleet-results-panel" style="display: none; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 12px; margin-bottom: 12px;">
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; font-size: 0.78rem; margin-bottom: 8px;">
          <div>Combustible: <span id="fleet-res-fuel" style="float: right; color: #fff;">$0</span></div>
          <div>Peajes INVIAS: <span id="fleet-res-tolls" style="float: right; color: #fff;">$0</span></div>
          <div>Desgaste / Viáticos: <span id="fleet-res-wear" style="float: right; color: #fff;">$0</span></div>
          <div>TOTAL FLETE: <span id="fleet-res-total" style="float: right; color: #38ef7d; font-weight: 700;">$0 COP</span></div>
        </div>
        <div style="text-align: center; font-size: 0.74rem; color: #94a3b8; border-top: 1px solid #334155; padding-top: 6px;" id="fleet-res-co2"></div>
      </div>

      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeFleetModal()">Cerrar</button>
      </div>
    </div>
  </div>


  <!-- ======================================================== -->
  <!-- MODAL: TELEMETRÍA BIOCOGNITIVA & HÁBITOS EJECUTIVOS CEO   -->
  <!-- ======================================================== -->
  <div class="modal-overlay" id="biohabits-modal">
    <div class="modal-card" style="max-width: 780px;">
      <div class="modal-header">
        <div class="modal-icon" style="color: #a855f7; border-color: rgba(168, 85, 247, 0.4); background: rgba(168, 85, 247, 0.12);">🧠</div>
        <div class="modal-title">
          <h2>Telemetría Biocognitiva & Salud Ejecutiva</h2>
          <p>Monitoreo de energía mental, descanso, cronotipo y ventanas de máxima productividad</p>
        </div>
        <button class="modal-close" onclick="closeBiohabitsModal()">&times;</button>
      </div>

      <!-- Inputs de Hábitos -->
      <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin-bottom: 12px;">
        <div>
          <label style="font-size: 0.7rem; color: #94a3b8; display: block;">Sueño (Horas):</label>
          <input type="number" step="0.5" id="bio-sleep-input" value="7.5" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
        </div>
        <div>
          <label style="font-size: 0.7rem; color: #94a3b8; display: block;">Agua (Vasos):</label>
          <input type="number" id="bio-water-input" value="8" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
        </div>
        <div>
          <label style="font-size: 0.7rem; color: #94a3b8; display: block;">Trabajo Foco (h):</label>
          <input type="number" step="0.5" id="bio-focus-input" value="4.0" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
        </div>
        <div>
          <label style="font-size: 0.7rem; color: #94a3b8; display: block;">Vigor (1-10):</label>
          <input type="number" min="1" max="10" id="bio-energy-input" value="8" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
        </div>
        <div style="display: flex; align-items: flex-end;">
          <button type="button" class="btn-primary" style="width: 100%; padding: 7px; font-size: 0.78rem;" onclick="submitBiohabits()">Evaluar Vigor</button>
        </div>
      </div>

      <div id="bio-results-panel" style="display: none; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 12px; margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <span style="font-size: 0.78rem; font-weight: 700; color: #a855f7;">ÍNDICE BIOCOGNITIVO: <b id="bio-res-score" style="color: #38ef7d;">0.0%</b></span>
          <span id="bio-res-status" style="font-size: 0.72rem; padding: 2px 8px; border-radius: 12px; background: rgba(56, 239, 125, 0.2); color: #38ef7d;"></span>
        </div>
        <div style="font-size: 0.8rem; color: #e2e8f0; margin-bottom: 6px;" id="bio-res-banner"></div>
        <div style="font-size: 0.74rem; color: #94a3b8;" id="bio-res-peak"></div>
      </div>

      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeBiohabitsModal()">Cerrar</button>
      </div>
    </div>
  </div>
"""

JS_ENGINE_INJECTION = """
      // ========================================================
      // MOTOR TÁCTICO: PAGO IMPUESTOS DIAN, VALUACIÓN, FLETES Y BIOHABITS
      // ========================================================
      let lastForm490Settlement = null;

      window.openTaxPayModal = function() {
        const m = document.getElementById("tax-pay-modal");
        if (m) m.classList.add("active");
        playHudSound("open");
      };

      window.closeTaxPayModal = function() {
        const m = document.getElementById("tax-pay-modal");
        if (m) m.classList.remove("active");
        playHudSound("close");
      };

      window.settleTaxForm = async function() {
        playHudSound("click");
        const concept = document.getElementById("f490-concept")?.value || "retefuente";
        const year = parseInt(document.getElementById("f490-year")?.value || "2026");
        const period = document.getElementById("f490-period")?.value || "01";
        const nit = document.getElementById("f490-nit")?.value || "901.884.221-3";
        const amount = parseFloat(document.getElementById("f490-amount")?.value || "0");
        const dueDate = document.getElementById("f490-due-date")?.value;
        const payDate = document.getElementById("f490-pay-date")?.value;

        if (amount <= 0) {
          showToast("Indique un monto de impuesto válido");
          return;
        }

        try {
          const res = await fetch("/api/suite/tax-payment/settle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              concept: concept,
              year: year,
              period: period,
              nit: nit,
              amount: amount,
              due_date: dueDate ? dueDate + "T00:00:00Z" : null,
              payment_date: payDate ? payDate + "T00:00:00Z" : null
            })
          });
          if (res.ok) {
            const data = await res.json();
            const s = data.settlement;
            lastForm490Settlement = s;
            document.getElementById("f490-settlement-results").style.display = "block";
            document.getElementById("f490-res-id").textContent = s.receipt_id;
            document.getElementById("f490-res-concept").textContent = `[${s.concept_code}] ${s.concept_name}`;
            document.getElementById("f490-res-base").textContent = "$" + Math.round(s.base_tax_amount).toLocaleString("es-CO");
            document.getElementById("f490-res-penalty").textContent = "$" + Math.round(s.extemporaneity_penalty).toLocaleString("es-CO");
            document.getElementById("f490-res-interest").textContent = "$" + Math.round(s.moratory_interest).toLocaleString("es-CO");
            document.getElementById("f490-res-total").textContent = "$" + Math.round(s.total_payable).toLocaleString("es-CO") + " COP";
            showToast("Formulario 490 liquidado exitosamente");
          }
        } catch (e) {
          console.error(e);
        }
      };

      window.initiatePsePayment = async function() {
        if (!lastForm490Settlement) {
          showToast("Liquide primero el Formulario 490");
          return;
        }
        playHudSound("click");
        const bank = document.getElementById("f490-pse-bank")?.value || "Bancolombia";

        try {
          const res = await fetch("/api/suite/tax-payment/pse", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              receipt_id: lastForm490Settlement.receipt_id,
              bank_name: bank
            })
          });
          if (res.ok) {
            const data = await res.json();
            const intent = data.intent;
            showToast(`Pago PSE generado con éxito (CUS: ${intent.cus_code})`);
            window.open(intent.payment_url, "_blank");
          }
        } catch (e) {
          console.error(e);
        }
      };

      // ─── VALUACIÓN DCF ───
      window.openValuationModal = function() {
        const m = document.getElementById("valuation-modal");
        if (m) m.classList.add("active");
        playHudSound("open");
      };

      window.closeValuationModal = function() {
        const m = document.getElementById("valuation-modal");
        if (m) m.classList.remove("active");
        playHudSound("close");
      };

      window.runDcfValuation = async function() {
        playHudSound("click");
        const rawFlows = document.getElementById("dcf-flows-input")?.value || "";
        const wacc = (parseFloat(document.getElementById("dcf-wacc-input")?.value || "12")) / 100.0;
        const g = (parseFloat(document.getElementById("dcf-g-input")?.value || "3")) / 100.0;
        const cash = parseFloat(document.getElementById("dcf-cash-input")?.value || "0");

        const flows = rawFlows.split(",").map(x => parseFloat(x.trim())).filter(x => !isNaN(x));
        if (flows.length === 0) {
          showToast("Indique los flujos de caja proyectados");
          return;
        }

        try {
          const res = await fetch("/api/suite/valuation/dcf", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ cash_flows: flows, wacc: wacc, terminal_growth_g: g, cash: cash })
          });
          if (res.ok) {
            const data = await res.json();
            const v = data.valuation;
            document.getElementById("dcf-results-panel").style.display = "block";
            document.getElementById("dcf-res-ev").textContent = "$" + Math.round(v.enterprise_value_ev).toLocaleString("es-CO") + " COP";
            document.getElementById("dcf-res-equity").textContent = "$" + Math.round(v.equity_value).toLocaleString("es-CO") + " COP";
            showToast("Valuación calculada exitosamente");
          }
        } catch (e) {
          console.error(e);
        }
      };

      // ─── FLETES LOGÍSTICOS ───
      window.openFleetModal = function() {
        const m = document.getElementById("fleet-modal");
        if (m) m.classList.add("active");
        playHudSound("open");
      };

      window.closeFleetModal = function() {
        const m = document.getElementById("fleet-modal");
        if (m) m.classList.remove("active");
        playHudSound("close");
      };

      window.calculateFleetFreight = async function() {
        playHudSound("click");
        const route = document.getElementById("fleet-route-select")?.value || "palmira_cali";
        const veh = document.getElementById("fleet-veh-select")?.value || "turbo_4_ton";

        try {
          const res = await fetch("/api/suite/fleet/freight", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ route: route, vehicle: veh })
          });
          if (res.ok) {
            const data = await res.json();
            const f = data.freight;
            document.getElementById("fleet-results-panel").style.display = "block";
            document.getElementById("fleet-res-fuel").textContent = "$" + Math.round(f.fuel_cost_cop).toLocaleString("es-CO");
            document.getElementById("fleet-res-tolls").textContent = "$" + Math.round(f.tolls_cost_cop).toLocaleString("es-CO");
            document.getElementById("fleet-res-wear").textContent = "$" + Math.round(f.wear_and_maintenance_cop + f.driver_stipend_cop).toLocaleString("es-CO");
            document.getElementById("fleet-res-total").textContent = "$" + Math.round(f.total_freight_cost_cop).toLocaleString("es-CO") + " COP";
            document.getElementById("fleet-res-co2").innerHTML = `Distancia: <b>${f.distance_km} km</b> | Consumo: <b>${f.gallons_consumed} gal</b> | Huella CO₂: <b>${f.co2_emissions_kg} kg</b>`;
            showToast("Flete liquidado exitosamente");
          }
        } catch (e) {
          console.error(e);
        }
      };

      // ─── TELEMETRÍA BIOCOGNITIVA ───
      window.openBiohabitsModal = function() {
        const m = document.getElementById("biohabits-modal");
        if (m) m.classList.add("active");
        playHudSound("open");
      };

      window.closeBiohabitsModal = function() {
        const m = document.getElementById("biohabits-modal");
        if (m) m.classList.remove("active");
        playHudSound("close");
      };

      window.submitBiohabits = async function() {
        playHudSound("click");
        const sleep = parseFloat(document.getElementById("bio-sleep-input")?.value || "7.5");
        const water = parseInt(document.getElementById("bio-water-input")?.value || "8");
        const focus = parseFloat(document.getElementById("bio-focus-input")?.value || "4.0");
        const energy = parseInt(document.getElementById("bio-energy-input")?.value || "8");

        try {
          const res = await fetch("/api/suite/biohabits/eval", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              sleep_hours: sleep,
              water_glasses: water,
              deep_work_hours: focus,
              energy_rating: energy,
              chronotype: "matutino_alondra"
            })
          });
          if (res.ok) {
            const data = await res.json();
            const b = data.biocognitive;
            document.getElementById("bio-results-panel").style.display = "block";
            document.getElementById("bio-res-score").textContent = b.biocognitive_index_pct + "%";
            document.getElementById("bio-res-status").textContent = b.status;
            document.getElementById("bio-res-banner").textContent = b.banner;
            document.getElementById("bio-res-peak").innerHTML = `Horas Pico de Claridad: <b>${b.peak_window}</b>`;
            showToast("Vigor biocognitivo evaluado");
          }
        } catch (e) {
          console.error(e);
        }
      };
"""

CARD_LISTENERS_INJECTION = """
        // Conexiones de apertura para los 4 módulos de la Suite Variada
        const cardTaxPay = document.getElementById("hud-card-tax-pay");
        if (cardTaxPay) cardTaxPay.addEventListener("click", () => {
          document.getElementById("hud-interfaces-modal")?.classList.remove("active");
          window.openTaxPayModal();
        });
        const cardVal = document.getElementById("hud-card-valuation");
        if (cardVal) cardVal.addEventListener("click", () => {
          document.getElementById("hud-interfaces-modal")?.classList.remove("active");
          window.openValuationModal();
        });
        const cardFleet = document.getElementById("hud-card-fleet");
        if (cardFleet) cardFleet.addEventListener("click", () => {
          document.getElementById("hud-interfaces-modal")?.classList.remove("active");
          window.openFleetModal();
        });
        const cardBio = document.getElementById("hud-card-biohabits");
        if (cardBio) cardBio.addEventListener("click", () => {
          document.getElementById("hud-interfaces-modal")?.classList.remove("active");
          window.openBiohabitsModal();
        });
"""

def main():
    target_path = "jarvis.html"
    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update filter tab count to TODOS (30)
    if 'TODOS (26)' in content:
        content = content.replace('TODOS (26)', 'TODOS (30)')
        print("[PATCH] Actualizado tab contador a TODOS (30)")
    elif 'TODOS (22)' in content:
        content = content.replace('TODOS (22)', 'TODOS (30)')
        print("[PATCH] Actualizado tab contador a TODOS (30)")

    # 2. Inject HUD Cards
    target_card_end = '<!-- 12. Control y Ejecución en Windows PC -->'
    if 'id="hud-card-tax-pay"' not in content:
        if target_card_end in content:
            content = content.replace(target_card_end, HUD_CARDS_INJECTION.strip() + "\n\n        " + target_card_end)
            print("[PATCH] Inyectadas 4 HUD cards variadas")
        else:
            print("[WARN] No se encontró target_card_end")
    else:
        print("[SKIP] HUD cards ya presentes")

    # 3. Inject Modals
    if 'id="tax-pay-modal"' not in content:
        target_modal_end = '<div class="liseth-toast" id="liseth-toast"></div>'
        if target_modal_end in content:
            content = content.replace(target_modal_end, MODALS_INJECTION.strip() + "\n\n  " + target_modal_end)
            print("[PATCH] Inyectados 4 modales variados")
        else:
            print("[WARN] No se encontró target_modal_end")
    else:
        print("[SKIP] Modales ya presentes")

    # 4. Inject JS Engine
    if 'window.openTaxPayModal' not in content:
        target_js_end = 'window.lisethViewer = {'
        if target_js_end in content:
            content = content.replace(target_js_end, JS_ENGINE_INJECTION.strip() + "\n\n        " + target_js_end)
            print("[PATCH] Inyectado motor JS de pago de impuestos, valuación, fletes y biohabits")
        else:
            print("[WARN] No se encontró target_js_end")
    else:
        print("[SKIP] Motor JS ya presente")

    # 5. Inject Card Listeners
    if 'hud-card-tax-pay' not in content or 'cardTaxPay.addEventListener' not in content:
        target_card_listener = 'window.openOkrsModal();\n        });'
        if target_card_listener in content:
            content = content.replace(target_card_listener, target_card_listener + "\n" + CARD_LISTENERS_INJECTION.strip())
            print("[PATCH] Inyectados listeners para apertura de modales variados")
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
