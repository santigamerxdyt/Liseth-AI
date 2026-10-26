# -*- coding: utf-8 -*-
"""
Patch script to inject the Strategic & Executive Suite into jarvis.html,
and synchronize to index.html and app/static/index.html.
"""
import os
import shutil

HUD_CARDS_INJECTION = """
        <!-- 17. Evaluador de Proyectos de Inversión (VAN, TIR, Payback) -->
        <div class="hud-card" data-category="intelligence" id="hud-card-investment">
          <div class="hud-card-top">
            <div class="hud-card-icon" style="color: #00f0ff; border-color: rgba(0, 240, 255, 0.4); background: rgba(0, 240, 255, 0.12);">📊</div>
            <span class="hud-card-status status-online">FINANZAS UNAL</span>
          </div>
          <div class="hud-card-title">Evaluación de Proyectos (VAN & TIR)</div>
          <div class="hud-card-desc">Presupuesto de capital, VAN, TIR numérica, Payback simple/descontado, relación B/C y análisis de sensibilidad por escenarios.</div>
          <div class="hud-card-action"><span>Evaluar Proyecto</span> <span>→</span></div>
        </div>

        <!-- 18. Matriz de Riesgos Corporativos 5x5 (ISO 31000) -->
        <div class="hud-card" data-category="system" id="hud-card-risks">
          <div class="hud-card-top">
            <div class="hud-card-icon" style="color: #ff3366; border-color: rgba(255, 51, 102, 0.4); background: rgba(255, 51, 102, 0.12);">🛡️</div>
            <span class="hud-card-status status-online">HEATMAP 5x5</span>
          </div>
          <div class="hud-card-title">Matriz de Riesgos & Mapa de Calor</div>
          <div class="hud-card-desc">Gobernanza ISO 31000: riesgos estratégicos, financieros, operacionales y ciberseguridad con evaluación de controles y riesgo residual.</div>
          <div class="hud-card-action"><span>Ver Matriz 5x5</span> <span>→</span></div>
        </div>

        <!-- 19. Radar Macroeconómico & Nómina Colombia -->
        <div class="hud-card" data-category="automation" id="hud-card-macro">
          <div class="hud-card-top">
            <div class="hud-card-icon" style="color: #ffd166; border-color: rgba(255, 209, 102, 0.4); background: rgba(255, 209, 102, 0.12);">🇨🇴</div>
            <span class="hud-card-status status-online">COLOMBIA 2026</span>
          </div>
          <div class="hud-card-title">Radar Macro & Nómina Colombia</div>
          <div class="hud-card-desc">TRM, UVT, SMLMV, Tasa BanRep y liquidador laboral pro-forma con seguridad social, parafiscales (Art. 114-1 E.T.) y prestaciones.</div>
          <div class="hud-card-action"><span>Liquidar Nómina</span> <span>→</span></div>
        </div>

        <!-- 20. Generador de Pitch Decks & Presentaciones -->
        <div class="hud-card" data-category="connectors" id="hud-card-pitch">
          <div class="hud-card-top">
            <div class="hud-card-icon" style="color: #a855f7; border-color: rgba(168, 85, 247, 0.4); background: rgba(168, 85, 247, 0.12);">🎯</div>
            <span class="hud-card-status status-online">PITCH DECK</span>
          </div>
          <div class="hud-card-title">Pitch Decks & Presentaciones</div>
          <div class="hud-card-desc">Estructuración ejecutiva de 10 diapositivas maestras (Kawasaki / Sequoia) para capital semilla, inversionistas o comités directivos.</div>
          <div class="hud-card-action"><span>Generar Deck</span> <span>→</span></div>
        </div>
"""

MODALS_INJECTION = """
  <!-- ======================================================== -->
  <!-- MODAL: EVALUACIÓN DE PROYECTOS DE INVERSIÓN (VAN & TIR)  -->
  <!-- ======================================================== -->
  <div class="modal-overlay" id="investment-modal">
    <div class="modal-card" style="max-width: 780px;">
      <div class="modal-header">
        <div class="modal-icon" style="color: #00f0ff; border-color: rgba(0, 240, 255, 0.4); background: rgba(0, 240, 255, 0.12);">📊</div>
        <div class="modal-title">
          <h2>Evaluador Financiero de Proyectos (VAN & TIR)</h2>
          <p>Presupuesto de capital, viabilidad económica y análisis de escenarios para alta dirección</p>
        </div>
        <button class="modal-close" onclick="closeInvestmentModal()">&times;</button>
      </div>

      <!-- Inputs del Proyecto -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
        <div>
          <label style="font-size: 0.78rem; color: #94a3b8; display: block; margin-bottom: 4px;">Nombre del Proyecto / Iniciativa:</label>
          <input type="text" id="inv-proj-name" value="Expansión de Consultoría & IA" style="width: 100%; background: #0f172a; border: 1px solid rgba(0, 240, 255, 0.3); color: #fff; padding: 8px; border-radius: 6px; font-size: 0.85rem;" />
        </div>
        <div>
          <label style="font-size: 0.78rem; color: #94a3b8; display: block; margin-bottom: 4px;">Inversión Inicial (COP):</label>
          <input type="number" id="inv-proj-initial" value="50000000" style="width: 100%; background: #0f172a; border: 1px solid rgba(0, 240, 255, 0.3); color: #fff; padding: 8px; border-radius: 6px; font-size: 0.85rem;" />
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 12px; margin-bottom: 14px;">
        <div>
          <label style="font-size: 0.78rem; color: #94a3b8; display: block; margin-bottom: 4px;">Flujos de Caja Anuales (Separados por coma):</label>
          <input type="text" id="inv-proj-flows" value="18000000, 22000000, 26000000, 30000000" placeholder="Año 1, Año 2, Año 3..." style="width: 100%; background: #0f172a; border: 1px solid rgba(0, 240, 255, 0.3); color: #fff; padding: 8px; border-radius: 6px; font-size: 0.85rem;" />
        </div>
        <div>
          <label style="font-size: 0.78rem; color: #94a3b8; display: block; margin-bottom: 4px;">Tasa Descuento (k %):</label>
          <input type="number" step="0.5" id="inv-proj-rate" value="12.0" style="width: 100%; background: #0f172a; border: 1px solid rgba(0, 240, 255, 0.3); color: #fff; padding: 8px; border-radius: 6px; font-size: 0.85rem;" />
        </div>
      </div>

      <div style="text-align: center; margin-bottom: 16px;">
        <button type="button" class="btn-primary" style="padding: 10px 24px; font-size: 0.88rem;" onclick="runInvestmentEvaluation()">
          ⚡ Evaluar Viabilidad Económica
        </button>
      </div>

      <!-- Tarjetas de Resultados Clave -->
      <div id="inv-results-container" style="display: none;">
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 14px;">
          <div style="background: rgba(0, 240, 255, 0.08); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 8px; padding: 10px; text-align: center;">
            <div style="font-size: 0.72rem; color: #94a3b8;">VALOR ACTUAL NETO (VAN)</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #00f0ff;" id="inv-res-npv">$0 COP</div>
          </div>
          <div style="background: rgba(56, 239, 125, 0.08); border: 1px solid rgba(56, 239, 125, 0.3); border-radius: 8px; padding: 10px; text-align: center;">
            <div style="font-size: 0.72rem; color: #94a3b8;">TIR (TASA RETORNO)</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #38ef7d;" id="inv-res-irr">0.0%</div>
          </div>
          <div style="background: rgba(255, 209, 102, 0.08); border: 1px solid rgba(255, 209, 102, 0.3); border-radius: 8px; padding: 10px; text-align: center;">
            <div style="font-size: 0.72rem; color: #94a3b8;">PAYBACK DESCONTADO</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #ffd166;" id="inv-res-dpb">0.0 años</div>
          </div>
          <div style="background: rgba(217, 70, 239, 0.08); border: 1px solid rgba(217, 70, 239, 0.3); border-radius: 8px; padding: 10px; text-align: center;">
            <div style="font-size: 0.72rem; color: #94a3b8;">RELACIÓN B / C</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #d946ef;" id="inv-res-bcr">0.0x</div>
          </div>
        </div>

        <div id="inv-verdict-banner" style="background: rgba(15, 23, 42, 0.8); border-left: 4px solid #00f0ff; border-radius: 6px; padding: 10px 14px; margin-bottom: 14px; font-size: 0.85rem; color: #e2e8f0;"></div>

        <!-- Escenarios Sensibilidad -->
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px; margin-bottom: 10px;">
          <div style="font-size: 0.76rem; font-weight: 600; color: #94a3b8; margin-bottom: 6px;">ANÁLISIS DE SENSIBILIDAD POR ESCENARIOS:</div>
          <table style="width: 100%; font-size: 0.78rem; text-align: left; border-collapse: collapse;">
            <thead>
              <tr style="border-bottom: 1px solid rgba(255,255,255,0.1); color: #64748b;">
                <th style="padding: 4px;">Escenario</th>
                <th style="padding: 4px;">Variación Flujos</th>
                <th style="padding: 4px;">VAN Proyectado</th>
                <th style="padding: 4px;">TIR</th>
              </tr>
            </thead>
            <tbody id="inv-scenarios-body"></tbody>
          </table>
        </div>
      </div>

      <div class="modal-actions" style="margin-top: 14px;">
        <button class="btn-secondary" onclick="closeInvestmentModal()">Cerrar</button>
      </div>
    </div>
  </div>


  <!-- ======================================================== -->
  <!-- MODAL: MATRIZ DE RIESGOS CORPORATIVOS 5x5 (ISO 31000)    -->
  <!-- ======================================================== -->
  <div class="modal-overlay" id="risks-modal">
    <div class="modal-card" style="max-width: 820px;">
      <div class="modal-header">
        <div class="modal-icon" style="color: #ff3366; border-color: rgba(255, 51, 102, 0.4); background: rgba(255, 51, 102, 0.12);">🛡️</div>
        <div class="modal-title">
          <h2>Matriz de Riesgos & Mapa de Calor 5x5</h2>
          <p>Supervisión continua ISO 31000: evaluación inherente vs residual y controles preventivos</p>
        </div>
        <button class="modal-close" onclick="closeRisksModal()">&times;</button>
      </div>

      <!-- Resumen Cuantitativo -->
      <div style="display: flex; gap: 8px; justify-content: space-around; margin-bottom: 14px; background: rgba(15, 23, 42, 0.6); padding: 10px; border-radius: 8px;">
        <span style="font-size: 0.8rem; color: #ff3366; font-weight: 600;">🔴 Críticos: <b id="risk-count-crit">0</b></span>
        <span style="font-size: 0.8rem; color: #ffd166; font-weight: 600;">🟡 Altos: <b id="risk-count-alt">0</b></span>
        <span style="font-size: 0.8rem; color: #00d2ff; font-weight: 600;">🔵 Moderados: <b id="risk-count-mod">0</b></span>
        <span style="font-size: 0.8rem; color: #38ef7d; font-weight: 600;">🟢 Bajos: <b id="risk-count-baj">0</b></span>
      </div>

      <!-- Mapa de Calor 5x5 Stark -->
      <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 12px; margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <span style="font-size: 0.76rem; font-weight: 700; color: #94a3b8;">MAPA DE CALOR (IMPACTO vs PROBABILIDAD)</span>
          <span style="font-size: 0.7rem; color: #64748b;">Eje Y = Impacto (5 a 1) | Eje X = Probabilidad (1 a 5)</span>
        </div>
        <div id="risk-heatmap-grid" style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; text-align: center;"></div>
      </div>

      <!-- Formulario para agregar riesgo -->
      <div style="background: rgba(15, 23, 42, 0.5); border: 1px dashed rgba(255,255,255,0.15); border-radius: 8px; padding: 12px; margin-bottom: 14px;">
        <div style="font-size: 0.78rem; font-weight: 600; color: #e2e8f0; margin-bottom: 8px;">+ Registrar Nuevo Evento de Riesgo:</div>
        <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 8px; margin-bottom: 8px;">
          <input type="text" id="new-risk-title" placeholder="Descripción del evento..." style="background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
          <select id="new-risk-cat" style="background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;">
            <option value="Estrategico">Estratégico</option>
            <option value="Financiero">Financiero</option>
            <option value="Operacional">Operacional</option>
            <option value="Legal">Legal</option>
            <option value="Ciberseguridad">Ciberseguridad</option>
          </select>
          <input type="number" min="1" max="5" id="new-risk-prob" value="3" placeholder="Prob (1-5)" style="background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
          <input type="number" min="1" max="5" id="new-risk-imp" value="3" placeholder="Imp (1-5)" style="background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
        </div>
        <div style="display: grid; grid-template-columns: 3fr 1fr; gap: 8px;">
          <input type="text" id="new-risk-ctrl" placeholder="Protocolo de control mitigante..." style="background: #0f172a; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 0.8rem;" />
          <button type="button" class="btn-primary" style="padding: 6px 12px; font-size: 0.8rem;" onclick="submitNewRisk()">Registrar</button>
        </div>
      </div>

      <!-- Tabla de Riesgos -->
      <div style="max-height: 180px; overflow-y: auto; background: rgba(15, 23, 42, 0.4); border-radius: 6px; padding: 6px;">
        <table style="width: 100%; font-size: 0.76rem; border-collapse: collapse; text-align: left;">
          <thead>
            <tr style="border-bottom: 1px solid #334155; color: #64748b;">
              <th style="padding: 4px;">ID</th>
              <th style="padding: 4px;">Título</th>
              <th style="padding: 4px;">Categoría</th>
              <th style="padding: 4px;">Inherente</th>
              <th style="padding: 4px;">Residual</th>
              <th style="padding: 4px; text-align: right;">Acción</th>
            </tr>
          </thead>
          <tbody id="risk-table-body"></tbody>
        </table>
      </div>

      <div class="modal-actions" style="margin-top: 14px;">
        <button class="btn-secondary" onclick="closeRisksModal()">Cerrar</button>
      </div>
    </div>
  </div>


  <!-- ======================================================== -->
  <!-- MODAL: RADAR MACROECONÓMICO & NÓMINA COLOMBIA            -->
  <!-- ======================================================== -->
  <div class="modal-overlay" id="macro-modal">
    <div class="modal-card" style="max-width: 780px;">
      <div class="modal-header">
        <div class="modal-icon" style="color: #ffd166; border-color: rgba(255, 209, 102, 0.4); background: rgba(255, 209, 102, 0.12);">🇨🇴</div>
        <div class="modal-title">
          <h2>Radar Macroeconómico & Nómina Colombia 2026</h2>
          <p>Indicadores oficiales y simulador de costos laborales patronales con Art. 114-1 E.T.</p>
        </div>
        <button class="modal-close" onclick="closeMacroModal()">&times;</button>
      </div>

      <!-- Radar de Indicadores -->
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 14px;">
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 209, 102, 0.3); border-radius: 8px; padding: 8px; text-align: center;">
          <div style="font-size: 0.7rem; color: #94a3b8;">DÓLAR TRM</div>
          <div style="font-size: 1rem; font-weight: 700; color: #ffd166;">$4,185.50 COP</div>
        </div>
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 8px; padding: 8px; text-align: center;">
          <div style="font-size: 0.7rem; color: #94a3b8;">UVT 2026</div>
          <div style="font-size: 1rem; font-weight: 700; color: #00f0ff;">$49,799 COP</div>
        </div>
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 239, 125, 0.3); border-radius: 8px; padding: 8px; text-align: center;">
          <div style="font-size: 0.7rem; color: #94a3b8;">SMLMV VIGENTE</div>
          <div style="font-size: 1rem; font-weight: 700; color: #38ef7d;">$1,423,500 COP</div>
        </div>
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(217, 70, 239, 0.3); border-radius: 8px; padding: 8px; text-align: center;">
          <div style="font-size: 0.7rem; color: #94a3b8;">TASA BANREP</div>
          <div style="font-size: 1rem; font-weight: 700; color: #d946ef;">9.25% E.A.</div>
        </div>
      </div>

      <!-- Calculadora Laboral Pro-Forma -->
      <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 14px; margin-bottom: 14px;">
        <div style="font-size: 0.8rem; font-weight: 700; color: #ffd166; margin-bottom: 10px;">⚡ LIQUIDADOR DE COSTO EMPRESA & SALARIO NETO</div>
        <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 10px; margin-bottom: 12px;">
          <div>
            <label style="font-size: 0.74rem; color: #94a3b8; display: block; margin-bottom: 2px;">Salario Base Mensual (COP):</label>
            <input type="number" id="macro-salary-input" value="2500000" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 8px; border-radius: 6px; font-size: 0.85rem;" />
          </div>
          <div>
            <label style="font-size: 0.74rem; color: #94a3b8; display: block; margin-bottom: 2px;">Riesgo ARL:</label>
            <select id="macro-arl-select" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 8px; border-radius: 6px; font-size: 0.85rem;">
              <option value="1">Nivel I (0.522% - Admin)</option>
              <option value="2">Nivel II (1.044% - Comercial)</option>
              <option value="3">Nivel III (2.436% - Agro)</option>
              <option value="4">Nivel IV (4.350% - Transporte)</option>
              <option value="5">Nivel V (6.960% - Alto riesgo)</option>
            </select>
          </div>
          <div style="display: flex; align-items: flex-end;">
            <button type="button" class="btn-primary" style="width: 100%; padding: 8px; font-size: 0.82rem;" onclick="calculatePayroll()">
              Liquidar Nómina
            </button>
          </div>
        </div>

        <div id="macro-payroll-results" style="display: none; background: rgba(0,0,0,0.3); border-radius: 6px; padding: 10px;">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; font-size: 0.78rem;">
            <div>
              <div style="font-weight: 700; color: #38ef7d; margin-bottom: 4px;">👤 EMPLEADO (NETO A RECIBIR)</div>
              <div>Base + Auxilio: <span id="pay-emp-devengado" style="float: right;">$0</span></div>
              <div>Deducciones (8% Salud+Pens): <span id="pay-emp-deduc" style="float: right; color: #ff3366;">-$0</span></div>
              <div style="border-top: 1px solid #334155; margin-top: 4px; padding-top: 4px; font-weight: 700;">Neto Pagado: <span id="pay-emp-net" style="float: right; color: #38ef7d;">$0</span></div>
            </div>
            <div>
              <div style="font-weight: 700; color: #ffd166; margin-bottom: 4px;">🏢 EMPLEADOR (CARGAS PATRONALES)</div>
              <div>Seguridad Social (Pensión, ARL): <span id="pay-pat-sec" style="float: right;">$0</span></div>
              <div>Parafiscales (Caja 4%): <span id="pay-pat-para" style="float: right;">$0</span></div>
              <div>Prestaciones (Prima, Cesantías): <span id="pay-pat-pres" style="float: right;">$0</span></div>
              <div style="border-top: 1px solid #334155; margin-top: 4px; padding-top: 4px; font-weight: 700; color: #00f0ff;">Costo Total Empresa: <span id="pay-pat-total" style="float: right;">$0</span></div>
            </div>
          </div>
          <div style="text-align: center; margin-top: 8px; font-size: 0.76rem; color: #94a3b8;" id="pay-factor-badge"></div>
        </div>
      </div>

      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeMacroModal()">Cerrar</button>
      </div>
    </div>
  </div>


  <!-- ======================================================== -->
  <!-- MODAL: GENERADOR DE PITCH DECKS & PRESENTACIONES (10 S) -->
  <!-- ======================================================== -->
  <div class="modal-overlay" id="pitch-modal">
    <div class="modal-card" style="max-width: 820px;">
      <div class="modal-header">
        <div class="modal-icon" style="color: #a855f7; border-color: rgba(168, 85, 247, 0.4); background: rgba(168, 85, 247, 0.12);">🎯</div>
        <div class="modal-title">
          <h2>Generador de Pitch Decks (Guy Kawasaki / Sequoia)</h2>
          <p>Estructuración interactiva de 10 diapositivas para levantar capital o convencer comités</p>
        </div>
        <button class="modal-close" onclick="closePitchModal()">&times;</button>
      </div>

      <!-- Configuración del Pitch -->
      <div style="display: grid; grid-template-columns: 2fr 1.5fr 1.5fr; gap: 10px; margin-bottom: 12px;">
        <div>
          <label style="font-size: 0.74rem; color: #94a3b8; display: block; margin-bottom: 2px;">Nombre de la Empresa / Proyecto:</label>
          <input type="text" id="pitch-name-input" value="Liseth AI & Stark Systems" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 7px; border-radius: 5px; font-size: 0.82rem;" />
        </div>
        <div>
          <label style="font-size: 0.74rem; color: #94a3b8; display: block; margin-bottom: 2px;">Sector / Enfoque:</label>
          <select id="pitch-industry-select" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 7px; border-radius: 5px; font-size: 0.82rem;">
            <option value="tech_saas">Tech & Software SaaS</option>
            <option value="consultoria">Consultoría & Finanzas UNAL</option>
            <option value="agroindustria">Agroindustria Valle del Cauca</option>
            <option value="ecommerce">E-commerce & Bre-B</option>
          </select>
        </div>
        <div>
          <label style="font-size: 0.74rem; color: #94a3b8; display: block; margin-bottom: 2px;">Capital Solicitado (COP):</label>
          <input type="number" id="pitch-ask-input" value="250000000" style="width: 100%; background: #0f172a; border: 1px solid #334155; color: #fff; padding: 7px; border-radius: 5px; font-size: 0.82rem;" />
        </div>
      </div>

      <div style="text-align: center; margin-bottom: 14px;">
        <button type="button" class="btn-primary" style="padding: 8px 22px; font-size: 0.85rem;" onclick="generatePitchDeck()">
          ⚡ Proyectar Diapositivas Holográficas (10 Slides)
        </button>
      </div>

      <!-- Carrusel Interactivo de Diapositivas -->
      <div id="pitch-carousel-container" style="display: none;">
        <div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.9)); border: 1px solid rgba(168, 85, 247, 0.35); box-shadow: 0 0 20px rgba(168, 85, 247, 0.15); border-radius: 10px; padding: 18px; min-height: 230px; margin-bottom: 12px; position: relative;">
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; margin-bottom: 10px;">
            <span style="font-size: 0.75rem; color: #a855f7; font-weight: 700; text-transform: uppercase;" id="pitch-slide-badge">DIAPOSITIVA 1 DE 10</span>
            <span style="font-size: 0.7rem; color: #64748b;" id="pitch-deck-tagline"></span>
          </div>

          <h3 id="pitch-slide-title" style="margin: 0 0 4px 0; color: #fff; font-size: 1.15rem;"></h3>
          <p id="pitch-slide-sub" style="margin: 0 0 12px 0; font-size: 0.82rem; color: #94a3b8; font-style: italic;"></p>

          <ul id="pitch-slide-bullets" style="margin: 0 0 14px 18px; padding: 0; font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;"></ul>

          <div id="pitch-slide-takeaway" style="background: rgba(168, 85, 247, 0.1); border-left: 3px solid #a855f7; border-radius: 4px; padding: 6px 12px; font-size: 0.78rem; color: #e2e8f0;"></div>
        </div>

        <!-- Controles del Carrusel -->
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <button type="button" class="btn-secondary" style="padding: 6px 16px; font-size: 0.8rem;" onclick="prevPitchSlide()">◀ Anterior</button>
          <span style="font-size: 0.78rem; color: #94a3b8;" id="pitch-counter-text">1 / 10</span>
          <button type="button" class="btn-secondary" style="padding: 6px 16px; font-size: 0.8rem;" onclick="nextPitchSlide()">Siguiente ▶</button>
          <button type="button" class="btn-primary" style="padding: 6px 14px; font-size: 0.8rem; background: #a855f7;" onclick="printPitchDeck()">🖨️ Imprimir / Guardar PDF</button>
        </div>
      </div>

      <div class="modal-actions" style="margin-top: 14px;">
        <button class="btn-secondary" onclick="closePitchModal()">Cerrar</button>
      </div>
    </div>
  </div>
"""

JS_ENGINE_INJECTION = """
      // ========================================================
      // MOTOR TÁCTICO: EVALUACIÓN DE PROYECTOS, RIESGOS, MACRO & PITCH
      // ========================================================
      window.openInvestmentModal = function() {
        const m = document.getElementById("investment-modal");
        if (m) m.classList.add("active");
        playHudSound("open");
      };

      window.closeInvestmentModal = function() {
        const m = document.getElementById("investment-modal");
        if (m) m.classList.remove("active");
        playHudSound("close");
      };

      window.runInvestmentEvaluation = async function() {
        playHudSound("click");
        const name = document.getElementById("inv-proj-name")?.value || "Proyecto";
        const inv = parseFloat(document.getElementById("inv-proj-initial")?.value || "0");
        const rawFlows = document.getElementById("inv-proj-flows")?.value || "";
        const rate = (parseFloat(document.getElementById("inv-proj-rate")?.value || "12")) / 100.0;

        const flows = rawFlows.split(",").map(x => parseFloat(x.trim())).filter(x => !isNaN(x));
        if (inv <= 0 || flows.length === 0) {
          showToast("Indique una inversión válida y al menos un flujo de caja");
          return;
        }

        try {
          const res = await fetch("/api/suite/projects/eval", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              name: name,
              initial_investment: inv,
              cash_flows: flows,
              discount_rate: rate,
              currency: "COP"
            })
          });
          if (res.ok) {
            const data = await res.json();
            const ev = data.evaluation;
            document.getElementById("inv-results-container").style.display = "block";
            document.getElementById("inv-res-npv").textContent = "$" + Math.round(ev.npv).toLocaleString("es-CO") + " COP";
            document.getElementById("inv-res-irr").textContent = (ev.irr_pct !== null ? ev.irr_pct : "N/A") + "%";
            document.getElementById("inv-res-dpb").textContent = (ev.discounted_payback_years !== null ? ev.discounted_payback_years : "> horizon") + " años";
            document.getElementById("inv-res-bcr").textContent = ev.benefit_cost_ratio + "x";
            document.getElementById("inv-verdict-banner").innerHTML = "<b>Dictamen:</b> " + ev.verdict;

            const scBody = document.getElementById("inv-scenarios-body");
            if (scBody) {
              scBody.innerHTML = `
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05); color: #ff6b81;">
                  <td style="padding: 4px;">🔴 Pesimista</td>
                  <td style="padding: 4px;">-20%</td>
                  <td style="padding: 4px;">$${Math.round(ev.scenarios.pessimistic_minus_20.npv).toLocaleString('es-CO')}</td>
                  <td style="padding: 4px;">${ev.scenarios.pessimistic_minus_20.irr_pct}%</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05); color: #00d2ff;">
                  <td style="padding: 4px;">🔵 Base</td>
                  <td style="padding: 4px;">0%</td>
                  <td style="padding: 4px;">$${Math.round(ev.scenarios.base.npv).toLocaleString('es-CO')}</td>
                  <td style="padding: 4px;">${ev.scenarios.base.irr_pct}%</td>
                </tr>
                <tr style="color: #38ef7d;">
                  <td style="padding: 4px;">🟢 Optimista</td>
                  <td style="padding: 4px;">+20%</td>
                  <td style="padding: 4px;">$${Math.round(ev.scenarios.optimistic_plus_20.npv).toLocaleString('es-CO')}</td>
                  <td style="padding: 4px;">${ev.scenarios.optimistic_plus_20.irr_pct}%</td>
                </tr>
              `;
            }
            showToast("Evaluación calculada con éxito");
          }
        } catch (e) {
          console.error(e);
          showToast("Error al evaluar el proyecto");
        }
      };

      // ─── RIESGOS & HEATMAP ───
      window.openRisksModal = function() {
        const m = document.getElementById("risks-modal");
        if (m) m.classList.add("active");
        playHudSound("open");
        window.loadRisksHeatmap();
      };

      window.closeRisksModal = function() {
        const m = document.getElementById("risks-modal");
        if (m) m.classList.remove("active");
        playHudSound("close");
      };

      window.loadRisksHeatmap = async function() {
        try {
          const res = await fetch("/api/suite/risks/heatmap");
          if (res.ok) {
            const data = await res.json();
            document.getElementById("risk-count-crit").textContent = data.inherent_counts.CRITICO || 0;
            document.getElementById("risk-count-alt").textContent = data.inherent_counts.ALTO || 0;
            document.getElementById("risk-count-mod").textContent = data.inherent_counts.MODERADO || 0;
            document.getElementById("risk-count-baj").textContent = data.inherent_counts.BAJO || 0;

            const grid = document.getElementById("risk-heatmap-grid");
            if (grid) {
              grid.innerHTML = "";
              // Render 5 down to 1 for impact, 1 to 5 for prob
              for (let imp = 5; imp >= 1; imp--) {
                for (let prob = 1; prob <= 5; prob++) {
                  const key = imp + "_" + prob;
                  const cell = data.cells[key];
                  const score = cell.score;
                  let color = "#38ef7d";
                  let bg = "rgba(56, 239, 125, 0.15)";
                  if (score >= 16) { color = "#ff3366"; bg = "rgba(255, 51, 102, 0.25)"; }
                  else if (score >= 10) { color = "#ffd166"; bg = "rgba(255, 209, 102, 0.25)"; }
                  else if (score >= 5) { color = "#00d2ff"; bg = "rgba(0, 210, 255, 0.2)"; }

                  const count = cell.risks.length;
                  const el = document.createElement("div");
                  el.style.cssText = `background: ${bg}; border: 1px solid ${color}; border-radius: 4px; padding: 6px 2px; font-size: 0.68rem; color: ${color}; min-height: 38px; display: flex; flex-direction: column; justify-content: center; align-items: center;`;
                  el.innerHTML = `<b>${imp}x${prob}</b><span>${count > 0 ? "⚠️ (" + count + ")" : "•"}</span>`;
                  el.title = `Impacto ${imp}, Probabilidad ${prob}: ${count} riesgos`;
                  grid.appendChild(el);
                }
              }
            }

            const tb = document.getElementById("risk-table-body");
            if (tb) {
              tb.innerHTML = data.risks.map(r => `
                <tr style="border-bottom: 1px solid #1e293b;">
                  <td style="padding: 4px; color: #64748b;">${r.id}</td>
                  <td style="padding: 4px; color: #fff;">${r.title}</td>
                  <td style="padding: 4px; color: #94a3b8;">${r.category}</td>
                  <td style="padding: 4px; font-weight: 700; color: ${r.inherent_level === 'CRITICO' ? '#ff3366' : r.inherent_level === 'ALTO' ? '#ffd166' : '#00d2ff'};">${r.inherent_risk}</td>
                  <td style="padding: 4px; font-weight: 700; color: #38ef7d;">${r.residual_risk} (${r.residual_level})</td>
                  <td style="padding: 4px; text-align: right;"><button onclick="deleteRiskItem('${r.id}')" style="background:none; border:none; color:#ff3366; cursor:pointer;">✕</button></td>
                </tr>
              `).join("");
            }
          }
        } catch (e) {
          console.error(e);
        }
      };

      window.submitNewRisk = async function() {
        const title = document.getElementById("new-risk-title")?.value || "";
        const cat = document.getElementById("new-risk-cat")?.value || "Estrategico";
        const prob = parseInt(document.getElementById("new-risk-prob")?.value || "3");
        const imp = parseInt(document.getElementById("new-risk-imp")?.value || "3");
        const ctrl = document.getElementById("new-risk-ctrl")?.value || "Controles estándar";

        if (!title.trim()) {
          showToast("Escriba el título del riesgo");
          return;
        }

        try {
          const res = await fetch("/api/suite/risks/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              title: title,
              category: cat,
              probability: prob,
              impact: imp,
              control: ctrl,
              residual_probability: Math.max(1, prob - 1),
              residual_impact: Math.max(1, imp - 1),
              owner: "Santiago / CEO"
            })
          });
          if (res.ok) {
            showToast("Riesgo incorporado a la matriz");
            document.getElementById("new-risk-title").value = "";
            window.loadRisksHeatmap();
          }
        } catch (e) {
          console.error(e);
        }
      };

      window.deleteRiskItem = async function(id) {
        try {
          const res = await fetch(`/api/suite/risks/${id}`, { method: "DELETE" });
          if (res.ok) {
            showToast("Riesgo eliminado");
            window.loadRisksHeatmap();
          }
        } catch (e) {
          console.error(e);
        }
      };

      // ─── RADAR MACRO & NÓMINA ───
      window.openMacroModal = function() {
        const m = document.getElementById("macro-modal");
        if (m) m.classList.add("active");
        playHudSound("open");
      };

      window.closeMacroModal = function() {
        const m = document.getElementById("macro-modal");
        if (m) m.classList.remove("active");
        playHudSound("close");
      };

      window.calculatePayroll = async function() {
        playHudSound("click");
        const sal = parseFloat(document.getElementById("macro-salary-input")?.value || "0");
        const arl = parseInt(document.getElementById("macro-arl-select")?.value || "1");

        if (sal <= 0) {
          showToast("Indique un salario base válido");
          return;
        }

        try {
          const res = await fetch("/api/suite/macro/payroll", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              base_salary: sal,
              risk_level: arl
            })
          });
          if (res.ok) {
            const data = await res.json();
            const p = data.payroll;
            document.getElementById("macro-payroll-results").style.display = "block";
            document.getElementById("pay-emp-devengado").textContent = "$" + Math.round(p.base_salary + p.transport_allowance).toLocaleString("es-CO");
            document.getElementById("pay-emp-deduc").textContent = "-$" + Math.round(p.employee.total_deductions).toLocaleString("es-CO");
            document.getElementById("pay-emp-net").textContent = "$" + Math.round(p.employee.net_pay).toLocaleString("es-CO");

            document.getElementById("pay-pat-sec").textContent = "$" + Math.round(p.employer_social_security.subtotal).toLocaleString("es-CO");
            document.getElementById("pay-pat-para").textContent = "$" + Math.round(p.parafiscales.subtotal).toLocaleString("es-CO");
            document.getElementById("pay-pat-pres").textContent = "$" + Math.round(p.statutory_benefits_provisions.subtotal).toLocaleString("es-CO");
            document.getElementById("pay-pat-total").textContent = "$" + Math.round(p.total_company_cost).toLocaleString("es-CO");
            document.getElementById("pay-factor-badge").innerHTML = `Factor Prestacional Real: <b>${p.cost_multiplier}x</b> (Por cada $1.000 de salario, la empresa eroga $${Math.round(p.cost_multiplier * 1000).toLocaleString("es-CO")})`;
            showToast("Nómina calculada con éxito");
          }
        } catch (e) {
          console.error(e);
        }
      };

      // ─── PITCH DECK 10 SLIDES ───
      let currentDeckSlides = [];
      let currentSlideIdx = 0;

      window.openPitchModal = function() {
        const m = document.getElementById("pitch-modal");
        if (m) m.classList.add("active");
        playHudSound("open");
      };

      window.closePitchModal = function() {
        const m = document.getElementById("pitch-modal");
        if (m) m.classList.remove("active");
        playHudSound("close");
      };

      window.generatePitchDeck = async function() {
        playHudSound("click");
        const name = document.getElementById("pitch-name-input")?.value || "Stark Ventures";
        const ind = document.getElementById("pitch-industry-select")?.value || "tech_saas";
        const ask = parseFloat(document.getElementById("pitch-ask-input")?.value || "250000000");

        try {
          const res = await fetch("/api/suite/pitch/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              business_name: name,
              industry: ind,
              funding_ask: ask,
              currency: "COP",
              founder: "Santiago Huerfano Lopez",
              city: "Palmira / Cali, Colombia"
            })
          });
          if (res.ok) {
            const data = await res.json();
            currentDeckSlides = data.deck.slides;
            currentSlideIdx = 0;
            document.getElementById("pitch-carousel-container").style.display = "block";
            document.getElementById("pitch-deck-tagline").textContent = data.deck.tagline;
            renderCurrentSlide();
            showToast("Pitch Deck generado con éxito (10 Slides)");
          }
        } catch (e) {
          console.error(e);
        }
      };

      function renderCurrentSlide() {
        if (!currentDeckSlides || currentDeckSlides.length === 0) return;
        const s = currentDeckSlides[currentSlideIdx];
        document.getElementById("pitch-slide-badge").textContent = `DIAPOSITIVA ${s.slide_number} DE ${currentDeckSlides.length}`;
        document.getElementById("pitch-counter-text").textContent = `${s.slide_number} / ${currentDeckSlides.length}`;
        document.getElementById("pitch-slide-title").textContent = s.title;
        document.getElementById("pitch-slide-sub").textContent = s.subtitle;
        document.getElementById("pitch-slide-takeaway").innerHTML = "💡 <b>Conclusión Clave:</b> " + s.key_takeaway;

        const ul = document.getElementById("pitch-slide-bullets");
        if (ul) {
          ul.innerHTML = s.bullets.map(b => `<li style="margin-bottom: 4px;">${b}</li>`).join("");
        }
      }

      window.prevPitchSlide = function() {
        if (currentSlideIdx > 0) {
          currentSlideIdx--;
          renderCurrentSlide();
          playHudSound("click");
        }
      };

      window.nextPitchSlide = function() {
        if (currentSlideIdx < currentDeckSlides.length - 1) {
          currentSlideIdx++;
          renderCurrentSlide();
          playHudSound("click");
        }
      };

      window.printPitchDeck = function() {
        if (!currentDeckSlides || currentDeckSlides.length === 0) return;
        const printWindow = window.open("", "_blank");
        if (!printWindow) return;
        const slidesHtml = currentDeckSlides.map(s => `
          <div style="page-break-after: always; padding: 40px; font-family: sans-serif; min-height: 90vh; display: flex; flex-direction: column; justify-content: space-between; border: 1px solid #cbd5e1; margin-bottom: 20px;">
            <div>
              <div style="font-size: 14px; color: #64748b; text-transform: uppercase;">Diapositiva ${s.slide_number} de 10</div>
              <h1 style="font-size: 28px; margin: 10px 0; color: #0f172a;">${s.title}</h1>
              <h3 style="font-size: 16px; color: #475569; font-style: italic; margin-bottom: 24px;">${s.subtitle}</h3>
              <ul style="font-size: 16px; line-height: 1.8; color: #1e293b;">
                ${s.bullets.map(b => `<li>${b}</li>`).join("")}
              </ul>
            </div>
            <div style="background: #f1f5f9; padding: 12px 18px; border-left: 4px solid #0284c7; font-size: 14px; color: #0f172a;">
              <strong>Conclusión:</strong> ${s.key_takeaway}
            </div>
          </div>
        `).join("");

        printWindow.document.write(`
          <!DOCTYPE html>
          <html>
          <head><title>Pitch Deck Ejecutivo</title></head>
          <body onload="window.print();">${slidesHtml}</body>
          </html>
        `);
        printWindow.document.close();
      };
"""

CARD_LISTENERS_INJECTION = """
        // Conexiones de apertura para los 4 módulos de la Suite Estratégica
        const cardInv = document.getElementById("hud-card-investment");
        if (cardInv) cardInv.addEventListener("click", () => {
          document.getElementById("hud-interfaces-modal")?.classList.remove("active");
          window.openInvestmentModal();
        });
        const cardRsk = document.getElementById("hud-card-risks");
        if (cardRsk) cardRsk.addEventListener("click", () => {
          document.getElementById("hud-interfaces-modal")?.classList.remove("active");
          window.openRisksModal();
        });
        const cardMac = document.getElementById("hud-card-macro");
        if (cardMac) cardMac.addEventListener("click", () => {
          document.getElementById("hud-interfaces-modal")?.classList.remove("active");
          window.openMacroModal();
        });
        const cardPit = document.getElementById("hud-card-pitch");
        if (cardPit) cardPit.addEventListener("click", () => {
          document.getElementById("hud-interfaces-modal")?.classList.remove("active");
          window.openPitchModal();
        });
"""

def main():
    target_path = "jarvis.html"
    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update filter tab count
    if 'TODOS (15)' in content:
        content = content.replace('TODOS (15)', 'TODOS (22)')
        print("[PATCH] Actualizado tab contador a TODOS (22)")
    elif 'TODOS (18)' in content:
        content = content.replace('TODOS (18)', 'TODOS (22)')
        print("[PATCH] Actualizado tab contador a TODOS (22)")

    # 2. Inject HUD Cards
    target_card_end = '<!-- 12. Control y Ejecución en Windows PC -->'
    if 'id="hud-card-investment"' not in content:
        if target_card_end in content:
            content = content.replace(target_card_end, HUD_CARDS_INJECTION.strip() + "\n\n        " + target_card_end)
            print("[PATCH] Inyectadas 4 HUD cards estratégicas")
        else:
            print("[WARN] No se encontró target_card_end")
    else:
        print("[SKIP] HUD cards ya presentes")

    # 3. Inject Modals
    if 'id="investment-modal"' not in content:
        target_modal_end = '<div class="liseth-toast" id="liseth-toast"></div>'
        if target_modal_end in content:
            content = content.replace(target_modal_end, MODALS_INJECTION.strip() + "\n\n  " + target_modal_end)
            print("[PATCH] Inyectados 4 modales estratégicos")
        else:
            print("[WARN] No se encontró target_modal_end")
    else:
        print("[SKIP] Modales ya presentes")

    # 4. Inject JS Engine
    if 'window.openInvestmentModal' not in content:
        target_js_end = 'window.lisethViewer = {'
        if target_js_end in content:
            content = content.replace(target_js_end, JS_ENGINE_INJECTION.strip() + "\n\n        " + target_js_end)
            print("[PATCH] Inyectado motor JS de evaluación, riesgos, macro y pitch")
        else:
            print("[WARN] No se encontró target_js_end")
    else:
        print("[SKIP] Motor JS ya presente")

    # 5. Inject Card Listeners
    if 'hud-card-investment' not in content or 'cardInv.addEventListener' not in content:
        target_card_listener = 'window.openFocusModal();\n        });'
        if target_card_listener in content:
            content = content.replace(target_card_listener, target_card_listener + "\n" + CARD_LISTENERS_INJECTION.strip())
            print("[PATCH] Inyectados listeners para apertura de modales")
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
