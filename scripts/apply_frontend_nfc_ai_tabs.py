# -*- coding: utf-8 -*-
"""
Helper script to inject NFC Core Hub and AI Performance tabs into index.html
and keep index.html, jarvis.html, and app/static/index.html 100% byte-identical.
"""
import sys
import shutil

def main():
    with open('index.html', 'r', encoding='utf-8') as f:
        text = f.read()

    # 1. Low power CSS rule
    css_target = '''    /* ========================================================
       TERMINAL NFC Y PAGOS POR CONTACTO (STARK CONTACTLESS)
       ======================================================== */'''
    css_replacement = '''    /* ========================================================
       MODO DE BAJO CONSUMO (LOW-POWER MODE) - CLIENTE & SERVIDOR
       ======================================================== */
    body.low-power-mode * {
      animation-duration: 0.001s !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.001s !important;
      backdrop-filter: none !important;
      -webkit-backdrop-filter: none !important;
      box-shadow: none !important;
      text-shadow: none !important;
    }

    /* ========================================================
       TERMINAL NFC Y PAGOS POR CONTACTO (STARK CONTACTLESS)
       ======================================================== */'''

    if css_target not in text:
        print('ERROR: css_target not found')
        sys.exit(1)
    text = text.replace(css_target, css_replacement, 1)

    # 2. Tab buttons in SaaS platform modal
    tab_target = '''        <button type="button" class="btn-secondary saas-tab-btn" id="saas-tab-btn-legal" onclick="switchSaasTab('legal')" style="padding: 6px 12px; font-size: 0.76rem; border-color: #38bdf8; color: #7dd3fc;">⚖️ Legal & Copyright</button>
        <button type="button" class="btn-secondary saas-tab-btn" id="saas-tab-btn-creator" onclick="switchSaasTab('creator')" style="padding: 6px 12px; font-size: 0.76rem; background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(168, 85, 247, 0.2)); border-color: #f59e0b; color: #ffd166;">👑 Superadmin CREATOR</button>'''

    tab_replacement = '''        <button type="button" class="btn-secondary saas-tab-btn" id="saas-tab-btn-legal" onclick="switchSaasTab('legal')" style="padding: 6px 12px; font-size: 0.76rem; border-color: #38bdf8; color: #7dd3fc;">⚖️ Legal & Copyright</button>
        <button type="button" class="btn-secondary saas-tab-btn" id="saas-tab-btn-creator" onclick="switchSaasTab('creator')" style="padding: 6px 12px; font-size: 0.76rem; background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(168, 85, 247, 0.2)); border-color: #f59e0b; color: #ffd166;">👑 Superadmin CREATOR</button>
        <button type="button" class="btn-secondary saas-tab-btn" id="saas-tab-btn-nfc" onclick="switchSaasTab('nfc')" style="padding: 6px 12px; font-size: 0.76rem; border-color: #00f0ff; color: #00f0ff;">📶 NFC Core Hub</button>
        <button type="button" class="btn-secondary saas-tab-btn" id="saas-tab-btn-ai-perf" onclick="switchSaasTab('ai-perf')" style="padding: 6px 12px; font-size: 0.76rem; border-color: #ec4899; color: #f472b6;">⚡ Optimización IA & RAM</button>'''

    if tab_target not in text:
        print('ERROR: tab_target not found')
        sys.exit(1)
    text = text.replace(tab_target, tab_replacement, 1)

    # 3. Tab panes in SaaS platform modal
    pane_target = '''      <!-- PESTAÑA 8: PANEL SUPERADMINISTRADOR CREATOR (EXCLUSIVO SEÑOR SANTIAGO) -->
      <div id="saas-pane-creator" class="saas-pane" style="display: none;">
        <div id="saas-creator-dashboard-box" style="font-size: 0.76rem; color: #e2e8f0; max-height: 460px; overflow-y: auto;"></div>
      </div>'''

    pane_replacement = '''      <!-- PESTAÑA 8: PANEL SUPERADMINISTRADOR CREATOR (EXCLUSIVO SEÑOR SANTIAGO) -->
      <div id="saas-pane-creator" class="saas-pane" style="display: none;">
        <div id="saas-creator-dashboard-box" style="font-size: 0.76rem; color: #e2e8f0; max-height: 460px; overflow-y: auto;"></div>
      </div>

      <!-- PESTAÑA 9: NFC CORE HUB (HARDWARE, LECTURA/ESCRITURA, VTAP, ENLACES DINÁMICOS Y TARJETA INTELIGENTE) -->
      <div id="saas-pane-nfc" class="saas-pane" style="display: none;">
        <div id="saas-nfc-dashboard-box" style="font-size: 0.76rem; color: #e2e8f0; max-height: 520px; overflow-y: auto;"></div>
      </div>

      <!-- PESTAÑA 10: OPTIMIZACIÓN EXTREMA DE RECURSOS, TOKENS Y TELEMETRÍA IA -->
      <div id="saas-pane-ai-perf" class="saas-pane" style="display: none;">
        <div id="saas-ai-perf-dashboard-box" style="font-size: 0.76rem; color: #e2e8f0; max-height: 520px; overflow-y: auto;"></div>
      </div>'''

    if pane_target not in text:
        print('ERROR: pane_target not found')
        sys.exit(1)
    text = text.replace(pane_target, pane_replacement, 1)

    # 4. switchSaasTab logic
    switch_target = '''      window.switchSaasTab = async function(tabName) {
        const panes = ["account", "workspace", "plans", "usage", "catalog", "referrals", "legal", "creator"];'''

    switch_replacement = '''      window.switchSaasTab = async function(tabName) {
        const panes = ["account", "workspace", "plans", "usage", "catalog", "referrals", "legal", "creator", "nfc", "ai-perf"];'''

    if switch_target not in text:
        print('ERROR: switch_target not found')
        sys.exit(1)
    text = text.replace(switch_target, switch_replacement, 1)

    switch_calls_target = '''        } else if (tabName === "creator") {
          await loadSaasCreatorDashboardUI();
        }'''

    switch_calls_replacement = '''        } else if (tabName === "creator") {
          await loadSaasCreatorDashboardUI();
        } else if (tabName === "nfc") {
          await loadCreatorNfcAdminUI();
        } else if (tabName === "ai-perf") {
          await loadCreatorAIPerformanceUI();
        }'''

    if switch_calls_target not in text:
        print('ERROR: switch_calls_target not found')
        sys.exit(1)
    text = text.replace(switch_calls_target, switch_calls_replacement, 1)

    # 5. Functions before closing script
    js_anchor = '''      window.handleFirebaseGoogleSignIn = async function() {'''
    if js_anchor not in text:
        print('ERROR: js_anchor not found')
        sys.exit(1)

    js_to_insert = '''      // =========================================================================
      // MODO DE BAJO CONSUMO (LOW-POWER MODE)
      // =========================================================================
      window.initClientLowPowerMode = function() {
        try {
          const enabled = localStorage.getItem("liseth_low_power_mode") === "true";
          if (enabled) {
            document.body.classList.add("low-power-mode");
          }
          const toggleEl = document.getElementById("low-power-mode-toggle");
          if (toggleEl) toggleEl.checked = enabled;
        } catch (_) {}
      };
      setTimeout(() => { window.initClientLowPowerMode(); }, 100);

      window.toggleClientLowPowerModeUI = async function(checkbox) {
        const enabled = checkbox ? checkbox.checked : !document.body.classList.contains("low-power-mode");
        if (enabled) {
          document.body.classList.add("low-power-mode");
          localStorage.setItem("liseth_low_power_mode", "true");
        } else {
          document.body.classList.remove("low-power-mode");
          localStorage.setItem("liseth_low_power_mode", "false");
        }
        showToast(enabled ? "⚡ Modo de Bajo Consumo ACTIVADO (Ahorro de CPU/Batería)" : "🚀 Modo de Rendimiento Máximo RESTAURADO");
        try {
          const clientId = localStorage.getItem("liseth_client_id") || "browser_" + Math.random().toString(36).substring(2, 9);
          localStorage.setItem("liseth_client_id", clientId);
          await fetch("/api/saas/system/low-power", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ client_id: clientId, enabled: enabled, trigger_gc: false })
          });
        } catch (_) {}
      };

      window.triggerGarbageCollectionUI = async function() {
        const btn = document.getElementById("btn-trigger-gc");
        const statusEl = document.getElementById("ai-perf-gc-status");
        if (btn) btn.disabled = true;
        if (statusEl) statusEl.textContent = "⏳ Ejecutando ciclo de Garbage Collection...";
        try {
          const res = await fetch("/api/saas/system/low-power", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ client_id: "admin_trigger", enabled: false, trigger_gc: true })
          });
          const data = await res.json();
          if (statusEl) statusEl.textContent = `✔ Memoria recolectada: ${data.objects_collected || 0} objetos purgados en ${data.duration_ms || 0} ms.`;
          showToast(`🧹 Garbage Collection completado (${data.objects_collected || 0} objetos liberados)`);
          setTimeout(window.loadCreatorAIPerformanceUI, 1000);
        } catch (e) {
          if (statusEl) statusEl.textContent = "Error ejecutando GC.";
        } finally {
          if (btn) btn.disabled = false;
        }
      };

      // =========================================================================
      // GESTIÓN DE TELEMETRÍA Y OPTIMIZACIÓN IA (CREATOR AI PERFORMANCE)
      // =========================================================================
      window.loadCreatorAIPerformanceUI = async function() {
        const box = document.getElementById("saas-ai-perf-dashboard-box");
        if (!box) return;
        box.innerHTML = `<div style="text-align:center;padding:24px;color:#94a3b8;">⏳ Cargando telemetría de recursos y métricas de optimización de tokens...</div>`;
        try {
          const [perfRes, resRes] = await Promise.all([
            fetch("/api/saas/admin/ai-performance", { headers: getSaasHeaders() }),
            fetch("/api/saas/admin/resource-metrics", { headers: getSaasHeaders() })
          ]);
          const perfData = perfRes.ok ? await perfRes.json() : { metrics: {} };
          const resData = resRes.ok ? await resRes.json() : {};
          const m = perfData.metrics || {};
          const mem = resData.memory || {};
          const cpu = resData.cpu || {};
          const proc = resData.process || {};
          const isLpm = (localStorage.getItem("liseth_low_power_mode") === "true");

          box.innerHTML = `
            <!-- PANEL DE CONTROL TELEMETRÍA Y HARDWARE -->
            <div style="background:rgba(15,23,42,0.9);border:1px solid rgba(236,72,153,0.4);border-radius:10px;padding:14px;margin-bottom:12px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:8px;">
                <div>
                  <div style="font-weight:900;color:#f472b6;font-size:0.86rem;">⚡ MONITOR DE RECURSOS DEL SISTEMA & RENDIMIENTO DEL SERVIDOR</div>
                  <div style="font-size:0.7rem;color:#94a3b8;">Telemetría en tiempo real de RAM, CPU, Hilos y Optimización de Ciclos GC</div>
                </div>
                <div style="display:flex;align-items:center;gap:10px;">
                  <label style="display:flex;align-items:center;gap:6px;font-size:0.72rem;color:#ffd166;cursor:pointer;background:rgba(0,0,0,0.3);padding:4px 8px;border-radius:6px;border:1px solid rgba(255,209,102,0.3);">
                    <input type="checkbox" id="low-power-mode-toggle" ${isLpm ? 'checked' : ''} onchange="toggleClientLowPowerModeUI(this)" />
                    <strong>Modo de Bajo Consumo</strong>
                  </label>
                  <button type="button" id="btn-trigger-gc" class="btn-secondary" style="padding:4px 10px;font-size:0.7rem;border-color:#38ef7d;color:#38ef7d;" onclick="triggerGarbageCollectionUI()">🧹 Liberar RAM (GC)</button>
                </div>
              </div>

              <!-- GAUGES & METRICS -->
              <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;text-align:center;">
                <div style="background:rgba(0,0,0,0.35);padding:10px;border-radius:6px;border:1px solid rgba(255,255,255,0.06);">
                  <div style="font-size:0.68rem;color:#94a3b8;">Memoria RAM (RSS)</div>
                  <div style="font-size:1.1rem;font-weight:900;color:#38bdf8;">${mem.rss_mb || 0} <span style="font-size:0.72rem;">MB</span></div>
                  <div style="font-size:0.65rem;color:#64748b;">${mem.percent || 0}% de memoria física</div>
                </div>
                <div style="background:rgba(0,0,0,0.35);padding:10px;border-radius:6px;border:1px solid rgba(255,255,255,0.06);">
                  <div style="font-size:0.68rem;color:#94a3b8;">Uso de CPU Host</div>
                  <div style="font-size:1.1rem;font-weight:900;color:#ffd166;">${cpu.percent || 0} <span style="font-size:0.72rem;">%</span></div>
                  <div style="font-size:0.65rem;color:#64748b;">${cpu.logical_cores || 4} núcleos lógicos</div>
                </div>
                <div style="background:rgba(0,0,0,0.35);padding:10px;border-radius:6px;border:1px solid rgba(255,255,255,0.06);">
                  <div style="font-size:0.68rem;color:#94a3b8;">Hilos de Ejecución</div>
                  <div style="font-size:1.1rem;font-weight:900;color:#a855f7;">${proc.thread_count || 1}</div>
                  <div style="font-size:0.65rem;color:#64748b;">Uptime: ${Math.round((proc.uptime_seconds || 0)/60)} min</div>
                </div>
                <div style="background:rgba(0,0,0,0.35);padding:10px;border-radius:6px;border:1px solid rgba(255,255,255,0.06);">
                  <div style="font-size:0.68rem;color:#94a3b8;">Ciclos GC Purgados</div>
                  <div style="font-size:1.1rem;font-weight:900;color:#38ef7d;">${proc.gc_counts ? proc.gc_counts[0] : 0}</div>
                  <div style="font-size:0.65rem;color:#64748b;">Generaciones 0/1/2</div>
                </div>
              </div>
              <div id="ai-perf-gc-status" style="font-size:0.7rem;color:#38ef7d;margin-top:8px;text-align:right;"></div>
            </div>

            <!-- OPTIMIZADOR DE TOKENS IA Y ENRUTAMIENTO INTELIGENTE -->
            <div style="background:rgba(15,23,42,0.9);border:1px solid rgba(0,240,255,0.35);border-radius:10px;padding:14px;">
              <div style="font-weight:900;color:#00f0ff;font-size:0.86rem;margin-bottom:8px;">🧠 OPTIMIZADOR DE TOKENS & ENRUTADOR INTELIGENTE DE MODELOS LLM</div>
              <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;text-align:center;margin-bottom:12px;">
                <div style="background:rgba(0,0,0,0.35);padding:8px;border-radius:6px;">
                  <div style="font-size:0.68rem;color:#94a3b8;">Tokens Originales</div>
                  <div style="font-size:1rem;font-weight:800;color:#94a3b8;">${(m.total_original_tokens || 0).toLocaleString()}</div>
                </div>
                <div style="background:rgba(0,0,0,0.35);padding:8px;border-radius:6px;">
                  <div style="font-size:0.68rem;color:#94a3b8;">Tokens Optimizados</div>
                  <div style="font-size:1rem;font-weight:800;color:#38ef7d;">${(m.total_optimized_tokens || 0).toLocaleString()}</div>
                </div>
                <div style="background:rgba(0,0,0,0.35);padding:8px;border-radius:6px;">
                  <div style="font-size:0.68rem;color:#94a3b8;">Tokens Ahorrados</div>
                  <div style="font-size:1rem;font-weight:800;color:#00f0ff;">${(m.total_tokens_saved || 0).toLocaleString()} <span style="font-size:0.7rem;">(${m.percent_tokens_saved || 0}%)</span></div>
                </div>
                <div style="background:rgba(0,0,0,0.35);padding:8px;border-radius:6px;">
                  <div style="font-size:0.68rem;color:#94a3b8;">Ahorro Económico Est.</div>
                  <div style="font-size:1rem;font-weight:800;color:#ffd166;">$${m.estimated_usd_saved || '0.0000'} USD</div>
                </div>
              </div>

              <!-- DESGLOSE DE MODELOS & CACHE -->
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                <div style="background:rgba(6,11,22,0.85);border:1px solid #334155;border-radius:8px;padding:10px;">
                  <div style="font-weight:700;color:#38bdf8;font-size:0.75rem;margin-bottom:6px;">🔀 Distribución por Modelo (Smart Routing)</div>
                  <div style="font-size:0.72rem;line-height:1.6;color:#cbd5e1;">
                    <div style="display:flex;justify-content:space-between;"><span>gemini-3.1-flash-lite (Rápido/Económico):</span><b style="color:#38ef7d;">${m.model_routing_breakdown?.['gemini-3.1-flash-lite'] || 0} req</b></div>
                    <div style="display:flex;justify-content:space-between;"><span>gemini-2.5-flash (Equilibrado):</span><b style="color:#00f0ff;">${m.model_routing_breakdown?.['gemini-2.5-flash'] || 0} req</b></div>
                    <div style="display:flex;justify-content:space-between;"><span>gemini-2.5-pro (Razonamiento Complejo):</span><b style="color:#ffd166;">${m.model_routing_breakdown?.['gemini-2.5-pro'] || 0} req</b></div>
                  </div>
                </div>
                <div style="background:rgba(6,11,22,0.85);border:1px solid #334155;border-radius:8px;padding:10px;">
                  <div style="font-weight:700;color:#a855f7;font-size:0.75rem;margin-bottom:6px;">⚡ Caché Aislado de Respuestas & Latencia</div>
                  <div style="font-size:0.72rem;line-height:1.6;color:#cbd5e1;">
                    <div style="display:flex;justify-content:space-between;"><span>Tasa de Aciertos de Caché (0 Tokens):</span><b style="color:#38ef7d;">${m.cache_hit_ratio_percent || 0}%</b></div>
                    <div style="display:flex;justify-content:space-between;"><span>Latencia Media de Respuesta:</span><b style="color:#00f0ff;">${m.average_latency_ms || 0} ms</b></div>
                    <div style="display:flex;justify-content:space-between;"><span>Total de Solicitudes Procesadas:</span><b style="color:#fff;">${m.total_requests || 0}</b></div>
                  </div>
                </div>
              </div>
            </div>
          `;
        } catch (e) {
          box.innerHTML = `<div style="color:#ef4444;padding:12px;">Error cargando métricas de IA.</div>`;
        }
      };

      // =========================================================================
      // GESTIÓN DE NFC CORE HUB (CREATOR NFC ADMIN)
      // =========================================================================
      window.loadCreatorNfcAdminUI = async function() {
        const box = document.getElementById("saas-nfc-dashboard-box");
        if (!box) return;
        box.innerHTML = `<div style="text-align:center;padding:24px;color:#94a3b8;">⏳ Detectando hardware NFC y cargando métricas del núcleo...</div>`;
        try {
          const [capRes, dashRes] = await Promise.all([
            fetch("/api/nfc/capabilities", { headers: getSaasHeaders() }),
            fetch("/api/nfc/admin/dashboard", { headers: getSaasHeaders() })
          ]);
          const cap = capRes.ok ? await capRes.json() : {};
          const dash = dashRes.ok ? await dashRes.json() : { registered_tags: [], dynamic_links: [] };

          const hasWebNFC = ("NDEFReader" in window) || cap.web_nfc_supported;
          const statusBadge = hasWebNFC
            ? `<span style="background:rgba(56,239,125,0.15);color:#38ef7d;border:1px solid #38ef7d;padding:3px 8px;border-radius:6px;font-weight:700;">🟢 Web NFC Nativo Activo</span>`
            : `<span style="background:rgba(255,209,102,0.15);color:#ffd166;border:1px solid #ffd166;padding:3px 8px;border-radius:6px;font-weight:700;">🟡 Fallback Dinámico (QR / Universal Link / Simulador)</span>`;

          box.innerHTML = `
            <!-- HARDWARE & COMPATIBILITY MATRIX -->
            <div style="background:rgba(15,23,42,0.9);border:1px solid rgba(0,240,255,0.4);border-radius:10px;padding:14px;margin-bottom:12px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:8px;">
                <div>
                  <div style="font-weight:900;color:#00f0ff;font-size:0.86rem;">📶 MATRIZ DE COMPATIBILIDAD NFC CORE UNIVERSAL</div>
                  <div style="font-size:0.7rem;color:#94a3b8;">Plataforma detectada: <b>${cap.os_platform || 'Universal'}</b> • Navegador: <b>${cap.browser || 'Web'}</b></div>
                </div>
                <div>${statusBadge}</div>
              </div>

              <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;font-size:0.72rem;">
                <div style="background:rgba(6,11,22,0.7);padding:8px;border-radius:6px;border:1px solid #334155;">
                  <div style="color:#94a3b8;font-size:0.68rem;">Protocolos Soportados</div>
                  <div style="font-weight:700;color:#38bdf8;">ISO 14443A/B, ISO 15693, FeliCa</div>
                </div>
                <div style="background:rgba(6,11,22,0.7);padding:8px;border-radius:6px;border:1px solid #334155;">
                  <div style="color:#94a3b8;font-size:0.68rem;">Etiquetas Compatibles</div>
                  <div style="font-weight:700;color:#38ef7d;">NTAG213 (144B), NTAG215 (504B), NTAG216 (888B)</div>
                </div>
                <div style="background:rgba(6,11,22,0.7);padding:8px;border-radius:6px;border:1px solid #334155;">
                  <div style="color:#94a3b8;font-size:0.68rem;">Operaciones Disponibles</div>
                  <div style="font-weight:700;color:#ffd166;">Lectura NDEF, Escritura, Dynamic Links, P2P Token</div>
                </div>
              </div>
            </div>

            <!-- VALIDADOR DE CAPACIDAD NDEF & SIMULADOR -->
            <div style="background:rgba(15,23,42,0.9);border:1px solid #334155;border-radius:10px;padding:14px;margin-bottom:12px;">
              <div style="font-weight:800;color:#ffd166;font-size:0.82rem;margin-bottom:6px;">📏 VALIDADOR DE CAPACIDAD NDEF ANTES DE GRABAR</div>
              <div style="display:grid;grid-template-columns:1fr 2fr auto;gap:8px;align-items:center;">
                <select id="nfc-val-tag-type" style="background:#090d16;border:1px solid #475569;color:#fff;padding:6px;border-radius:6px;font-size:0.72rem;">
                  <option value="NTAG213">NTAG213 (144 Bytes)</option>
                  <option value="NTAG215">NTAG215 (504 Bytes)</option>
                  <option value="NTAG216" selected>NTAG216 (888 Bytes)</option>
                  <option value="MIFARE_CLASSIC">MIFARE Classic (752 Bytes)</option>
                  <option value="MIFARE_DESFIRE">DESFire EV1/EV2 (4096 Bytes)</option>
                </select>
                <input type="text" id="nfc-val-payload" placeholder="Texto, URI o JSON para calcular bytes..." value="https://liseth.ai/register?ref=SANTIAGO-CREATOR" style="background:#090d16;border:1px solid #475569;color:#fff;padding:6px 8px;border-radius:6px;font-size:0.72rem;" />
                <button type="button" class="btn-primary" style="padding:6px 14px;font-size:0.72rem;" onclick="validateNfcWritePayloadUI()">Validar Capacidad</button>
              </div>
              <div id="nfc-val-feedback" style="margin-top:6px;font-size:0.72rem;color:#38ef7d;"></div>
            </div>

            <!-- TARJETA DE PRESENTACIÓN INTELIGENTE (SMART BUSINESS CARD) -->
            <div style="background:rgba(15,23,42,0.9);border:1px solid rgba(168,85,247,0.4);border-radius:10px;padding:14px;margin-bottom:12px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:6px;">
                <div>
                  <div style="font-weight:800;color:#c084fc;font-size:0.82rem;">📇 TARJETA DE PRESENTACIÓN INTELIGENTE & BEAM (vCard 3.0 / 4.0)</div>
                  <div style="font-size:0.7rem;color:#94a3b8;">Contacto oficial con redes sociales, WhatsApp y Llave Bre-B para pagos</div>
                </div>
                <div style="display:flex;gap:6px;">
                  <button type="button" class="btn-secondary" style="padding:4px 10px;font-size:0.7rem;border-color:#00f0ff;color:#00f0ff;" onclick="copySantiagoVCardUI()">📋 Copiar vCard</button>
                  <button type="button" class="btn-primary" style="padding:4px 12px;font-size:0.7rem;" onclick="writeSantiagoVCardNfcUI()">📲 Grabar en Tag NFC</button>
                </div>
              </div>
              <div style="background:rgba(6,11,22,0.85);border:1px solid #334155;border-radius:8px;padding:10px;font-size:0.72rem;color:#cbd5e1;display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">
                <div><b>Titular:</b> Santiago Huérfano López</div>
                <div><b>Email:</b> santigamerxdyt@gmail.com</div>
                <div><b>WhatsApp / Tel:</b> +57 312 237 6474</div>
                <div><b>Llave Bre-B:</b> <code style="color:#ffd166;">@NEQUISAN243100</code></div>
                <div><b>Rol:</b> Fundador & Arquitecto Principal</div>
                <div><b>Plataforma:</b> Liseth AI / JARVIS Ecosystem</div>
              </div>
            </div>

            <!-- ENLACES DINÁMICOS & P2P FILE EXCHANGE -->
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;">
              <!-- ENLACES DINÁMICOS -->
              <div style="background:rgba(15,23,42,0.9);border:1px solid #334155;border-radius:10px;padding:12px;">
                <div style="font-weight:800;color:#38bdf8;font-size:0.78rem;margin-bottom:6px;">🔗 Enlaces Dinámicos (Sin reescribir tag)</div>
                <input type="text" id="nfc-link-code" placeholder="Código corto (ej: promo-nov)" style="width:100%;background:#090d16;border:1px solid #475569;color:#fff;padding:5px;border-radius:4px;font-size:0.72rem;margin-bottom:6px;" />
                <input type="text" id="nfc-link-target" placeholder="URL Destino (ej: https://liseth.ai/...)" style="width:100%;background:#090d16;border:1px solid #475569;color:#fff;padding:5px;border-radius:4px;font-size:0.72rem;margin-bottom:6px;" />
                <button type="button" class="btn-primary" style="width:100%;padding:5px;font-size:0.72rem;" onclick="createNfcDynamicLinkUI()">Crear Enlace Dinámico</button>
                <div id="nfc-link-feedback" style="margin-top:6px;font-size:0.7rem;color:#38ef7d;"></div>
              </div>

              <!-- P2P FILE EXCHANGE -->
              <div style="background:rgba(15,23,42,0.9);border:1px solid #334155;border-radius:10px;padding:12px;">
                <div style="font-weight:800;color:#38ef7d;font-size:0.78rem;margin-bottom:6px;">📁 Transferencia P2P Efímera (Token 15 min)</div>
                <input type="text" id="nfc-file-name" placeholder="Nombre archivo (ej: informe-ejecutivo.pdf)" value="informe-ejecutivo.pdf" style="width:100%;background:#090d16;border:1px solid #475569;color:#fff;padding:5px;border-radius:4px;font-size:0.72rem;margin-bottom:6px;" />
                <button type="button" class="btn-secondary" style="width:100%;padding:5px;font-size:0.72rem;border-color:#38ef7d;color:#38ef7d;" onclick="createNfcFileTransferIntentUI()">Generar Token de Transferencia</button>
                <div id="nfc-file-feedback" style="margin-top:6px;font-size:0.7rem;color:#ffd166;"></div>
              </div>
            </div>

            <!-- REGISTRO DE ETIQUETAS & AUDITORÍA EN VIVO -->
            <div style="background:rgba(15,23,42,0.9);border:1px solid #334155;border-radius:10px;padding:12px;">
              <div style="font-weight:800;color:#00f0ff;font-size:0.78rem;margin-bottom:6px;">📋 ETIQUETAS REGISTRADAS & LIBRO DE AUDITORÍA</div>
              ${dash.registered_tags && dash.registered_tags.length
                ? `<div style="max-height:160px;overflow-y:auto;">
                    ${dash.registered_tags.map(t => `
                      <div style="display:flex;justify-content:space-between;padding:4px 6px;border-bottom:1px solid rgba(255,255,255,0.06);font-size:0.7rem;">
                        <div><code>${t.tag_uid}</code> • <b>${t.tag_type}</b> • ${t.label || 'Sin etiqueta'}</div>
                        <div><span style="color:${t.status === 'active' ? '#38ef7d' : '#ef4444'}">${t.status.toUpperCase()}</span> • Toques: <b>${t.tap_count}</b></div>
                      </div>
                    `).join('')}
                  </div>`
                : `<div style="color:#94a3b8;font-size:0.72rem;">No hay etiquetas físicas registradas aún. Al acercar una etiqueta se vinculará automáticamente.</div>`
              }
            </div>
          `;
        } catch (e) {
          box.innerHTML = `<div style="color:#ef4444;padding:12px;">Error cargando panel de control NFC.</div>`;
        }
      };

      window.validateNfcWritePayloadUI = async function() {
        const tagType = document.getElementById("nfc-val-tag-type")?.value || "NTAG216";
        const payload = (document.getElementById("nfc-val-payload")?.value || "").trim();
        const fb = document.getElementById("nfc-val-feedback");
        try {
          const res = await fetch("/api/nfc/validate-write", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ tag_type: tagType, payload: payload })
          });
          const data = await res.json();
          if (data.fits) {
            if (fb) fb.innerHTML = `✔ <b>Válido:</b> ${data.payload_bytes} Bytes requeridos de ${data.max_bytes} Bytes disponibles (${data.free_bytes} Bytes libres).`;
            fb.style.color = "#38ef7d";
          } else {
            if (fb) fb.innerHTML = `❌ <b>Excede Capacidad:</b> Se requieren ${data.payload_bytes} Bytes pero el tag ${tagType} solo soporta ${data.max_bytes} Bytes (${data.overflow_bytes} Bytes de exceso). Se recomienda usar un Enlace Dinámico corto.`;
            fb.style.color = "#ef4444";
          }
        } catch (e) {
          if (fb) fb.textContent = "Error validando capacidad.";
        }
      };

      window.copySantiagoVCardUI = async function() {
        const vcard = `BEGIN:VCARD\\nVERSION:3.0\\nFN:Santiago Huerfano Lopez\\nN:Huerfano Lopez;Santiago;;;\\nEMAIL:santigamerxdyt@gmail.com\\nTEL;TYPE=CELL:+573122376474\\nTITLE:Fundador & Arquitecto Principal\\nORG:Liseth AI\\nURL:https://liseth.ai\\nNOTE;CHARSET=UTF-8:Llave Bre-B: @NEQUISAN243100 | WhatsApp: +57 312 237 6474\\nEND:VCARD`;
        await window.copyPaymentValueUI(vcard, "vCard Digital Santiago");
      };

      window.writeSantiagoVCardNfcUI = async function() {
        if ("NDEFReader" in window) {
          try {
            const ndef = new window.NDEFReader();
            await ndef.write({
              records: [
                { recordType: "url", data: "https://liseth.ai/register?ref=SANTIAGO-CREATOR" },
                { recordType: "text", data: "Santiago Huerfano Lopez - Llave Bre-B: @NEQUISAN243100" }
              ]
            });
            showToast("📲 ¡Tarjeta vCard grabada exitosamente en el tag NFC!");
          } catch (e) {
            showToast("Aviso NFC: " + (e.message || "Acerca la tarjeta al sensor"));
          }
        } else {
          showToast("ℹ️ Tu navegador no soporta Web NFC directo. Se ha copiado el payload al portapapeles para grabadores externos.");
          await copySantiagoVCardUI();
        }
      };

      window.createNfcDynamicLinkUI = async function() {
        const short_code = (document.getElementById("nfc-link-code")?.value || "").trim();
        const target_url = (document.getElementById("nfc-link-target")?.value || "").trim();
        const fb = document.getElementById("nfc-link-feedback");
        if (!short_code || !target_url) {
          if (fb) fb.textContent = "Ingresa código corto y URL destino.";
          return;
        }
        try {
          const res = await fetch("/api/nfc/links", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ short_code, target_url, title: "Enlace Dinámico NFC" })
          });
          const data = await res.json();
          if (res.ok && data.ok) {
            if (fb) fb.innerHTML = `✔ Enlace creado: <code>${data.link.short_url}</code>`;
            showToast("🔗 Enlace Dinámico NFC configurado correctamente");
            setTimeout(window.loadCreatorNfcAdminUI, 800);
          } else {
            if (fb) fb.textContent = data.detail || "Error creando enlace.";
          }
        } catch (e) {
          if (fb) fb.textContent = "Error de red al crear enlace.";
        }
      };

      window.createNfcFileTransferIntentUI = async function() {
        const file_name = (document.getElementById("nfc-file-name")?.value || "documento.pdf").trim();
        const fb = document.getElementById("nfc-file-feedback");
        try {
          const res = await fetch("/api/nfc/files/intent", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ file_name, file_size_bytes: 1048576, owner_consent: true })
          });
          const data = await res.json();
          if (res.ok && data.ok) {
            if (fb) fb.innerHTML = `✔ Token P2P: <strong style="color:#00f0ff;font-size:0.84rem;">${data.transfer_token}</strong> (Expira en 15 min)<br><span style="font-size:0.65rem;">URI: ${data.download_url}</span>`;
            showToast(`📁 Token de intercambio P2P generado: ${data.transfer_token}`);
          }
        } catch (e) {
          if (fb) fb.textContent = "Error generando token P2P.";
        }
      };

'''

    text = text.replace(js_anchor, js_to_insert + js_anchor, 1)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(text)

    # Keep all 3 frontend files 100% byte-identical
    shutil.copyfile('index.html', 'jarvis.html')
    shutil.copyfile('index.html', 'app/static/index.html')

    print('SUCCESS: index.html, jarvis.html, and app/static/index.html synchronized perfectly!')

if __name__ == '__main__':
    main()
