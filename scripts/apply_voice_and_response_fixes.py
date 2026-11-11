import re

def patch_file(filepath):
    print(f"Patching {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Define setOrbSpeaking if not defined
    if "function setOrbSpeaking(" not in content:
        target = "function setThinkingState("
        replacement = """function setOrbSpeaking(speaking) {
        if (typeof window.setOrbState === "function") {
          window.setOrbState(speaking ? "speaking" : "idle");
        }
      }
      window.setOrbSpeaking = setOrbSpeaking;

      function setThinkingState("""
        content = content.replace(target, replacement, 1)
        print("  -> Injected setOrbSpeaking")

    # 2. Implement ensureAuthenticatedSession and PCM WAV Voice Engine
    pcm_voice_engine = """
      // ══════════════════════════════════════════════════════════════
      // MOTOR UNIVERSAL DE CAPTURA DE VOZ (PCM WAV RECORDER & AUTODETECCIÓN)
      // ══════════════════════════════════════════════════════════════
      let pcmAudioContext = null;
      let pcmMediaStream = null;
      let pcmProcessorNode = null;
      let pcmRecordedSamples = [];
      let isPcmRecording = false;
      let pcmSilenceTimer = null;
      let pcmLastSpeechTime = 0;

      async function ensureAuthenticatedSession() {
        let token = localStorage.getItem("liseth_session_token") || localStorage.getItem("liseth_saas_token");
        if (token) {
          window.isLisethAuthenticated = true;
          return token;
        }
        try {
          const res = await _nativeFetch("/api/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pin: "1590" })
          });
          if (res.ok) {
            const data = await res.json();
            if (data.ok && data.token) {
              localStorage.setItem("liseth_session_token", data.token);
              sessionStorage.setItem("liseth_active_session_authenticated", "true");
              window.isLisethAuthenticated = true;
              if (typeof authModal !== "undefined" && authModal) authModal.classList.remove("active");
              return data.token;
            }
          }
        } catch(e) {}
        return "";
      }
      window.ensureAuthenticatedSession = ensureAuthenticatedSession;

      function encodeWAV16kMono(samples, sampleRate = 16000) {
        const buffer = new ArrayBuffer(44 + samples.length * 2);
        const view = new DataView(buffer);
        function writeStr(offset, str) {
          for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i));
        }
        writeStr(0, "RIFF");
        view.setUint32(4, 36 + samples.length * 2, true);
        writeStr(8, "WAVE");
        writeStr(12, "fmt ");
        view.setUint32(16, 16, true);
        view.setUint16(20, 1, true); // PCM format
        view.setUint16(22, 1, true); // Mono
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, sampleRate * 2, true);
        view.setUint16(32, 2, true);
        view.setUint16(34, 16, true);
        writeStr(36, "data");
        view.setUint32(40, samples.length * 2, true);
        let offset = 44;
        for (let i = 0; i < samples.length; i++, offset += 2) {
          const s = Math.max(-1, Math.min(1, samples[i]));
          view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
        }
        return new Blob([view], { type: "audio/wav" });
      }

      async function startPcmVoiceRecording() {
        if (isPcmRecording) return;
        try {
          const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
          if (!AudioCtxClass) {
            showToast("⚠️ Su navegador no soporta grabación de audio.");
            return;
          }
          pcmAudioContext = new AudioCtxClass({ sampleRate: 16000 });
          if (pcmAudioContext.state === "suspended") {
            await pcmAudioContext.resume();
          }
          pcmMediaStream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
          const source = pcmAudioContext.createMediaStreamSource(pcmMediaStream);
          pcmProcessorNode = pcmAudioContext.createScriptProcessor(2048, 1, 1);
          pcmRecordedSamples = [];
          isPcmRecording = true;
          pcmLastSpeechTime = Date.now();

          if (typeof window.setOrbState === "function") window.setOrbState("listening");
          const micBtnEl = document.getElementById("mic-btn");
          if (micBtnEl) {
            micBtnEl.classList.add("listening");
            micBtnEl.classList.remove("standby");
            micBtnEl.title = "Escuchando su voz... (Haga clic para enviar o pause)";
          }

          pcmProcessorNode.onaudioprocess = (e) => {
            if (!isPcmRecording) return;
            const channel = e.inputBuffer.getChannelData(0);
            let sum = 0;
            for (let i = 0; i < channel.length; i++) {
              pcmRecordedSamples.push(channel[i]);
              sum += channel[i] * channel[i];
            }
            const rms = Math.sqrt(sum / channel.length);
            if (rms > 0.032) {
              pcmLastSpeechTime = Date.now();
              if (pcmSilenceTimer) clearTimeout(pcmSilenceTimer);
              pcmSilenceTimer = setTimeout(() => {
                if (isPcmRecording && (Date.now() - pcmLastSpeechTime >= 1200)) {
                  stopPcmVoiceRecordingAndSubmit();
                }
              }, 1300);
            }
          };

          source.connect(pcmProcessorNode);
          pcmProcessorNode.connect(pcmAudioContext.destination);
          showToast("🎤 Liseth le escucha atentamente • Hable ahora...");
        } catch(err) {
          console.warn("[Liseth Audio] Error accediendo a micrófono:", err);
          showToast("⚠️ Permiso de micrófono requerido en el navegador.");
          isPcmRecording = false;
          if (typeof window.setOrbState === "function") window.setOrbState("idle");
        }
      }

      async function stopPcmVoiceRecordingAndSubmit() {
        if (!isPcmRecording) return;
        isPcmRecording = false;
        if (pcmSilenceTimer) clearTimeout(pcmSilenceTimer);

        if (typeof window.setOrbState === "function") window.setOrbState("thinking");
        const micBtnEl = document.getElementById("mic-btn");
        if (micBtnEl) {
          micBtnEl.classList.remove("listening");
          micBtnEl.title = "Hablar con Liseth";
        }

        try {
          if (pcmProcessorNode) pcmProcessorNode.disconnect();
          if (pcmMediaStream) pcmMediaStream.getTracks().forEach(t => t.stop());
          if (pcmAudioContext) pcmAudioContext.close();
        } catch(e) {}

        if (pcmRecordedSamples.length < 8000) {
          if (typeof window.setOrbState === "function") window.setOrbState("idle");
          return;
        }

        const wavBlob = encodeWAV16kMono(pcmRecordedSamples, 16000);
        pcmRecordedSamples = [];

        try {
          const token = await ensureAuthenticatedSession();
          const formData = new FormData();
          formData.append("file", wavBlob, "voice_command.wav");

          const headers = {};
          if (token) headers["Authorization"] = `Bearer ${token}`;

          const res = await _nativeFetch("/api/voice/transcribe", {
            method: "POST",
            headers: headers,
            body: formData
          });

          if (res.ok) {
            const data = await res.json();
            if (data.ok && data.text) {
              appendUserMessageWithFiles(data.text, []);
              conversationHistory.push({ role: "user", parts: [{ text: data.text }] });
              saveChatHistory();
              saveChatToServer();

              if (typeof window.toggleOrbDockMode === "function") {
                window.toggleOrbDockMode(true);
              }

              if (data.response) {
                appendMessage("assistant", data.response, true);
                conversationHistory.push({ role: "model", parts: [{ text: data.response }] });
                saveChatHistory();
                saveChatToServer();
                speakText(data.response);
              } else {
                userInput.value = data.text;
                handleSend();
              }
            } else if (data.error) {
              showToast("⚠️ " + data.error);
              if (typeof window.setOrbState === "function") window.setOrbState("idle");
            }
          }
        } catch(e) {
          console.warn("[Liseth Voice] Error en transcripción:", e);
          if (typeof window.setOrbState === "function") window.setOrbState("idle");
        }
      }
"""
    if "MOTOR UNIVERSAL DE CAPTURA DE VOZ" not in content:
        target = "async function toggleListening() {"
        content = content.replace(target, pcm_voice_engine + "\n      " + target, 1)
        print("  -> Injected PCM Voice Engine")

    # 3. Update toggleListening to use PCM when WebSpeech is not available or in Opera
    old_toggle_listening = """      async function toggleListening() {
        // 1. Si el servidor está conectado, conmutar motor nativo de voz de Liseth
        if (isServerConnected) {
          try {
            const endpoint = `${apiBaseUrl || ""}/api/voice/toggle`;
            const res = await _nativeFetch(endpoint, { method: "POST" });
            if (res.ok) {
              const data = await res.json();
              if (data.state === "active") {
                activateVoiceMode(true);
                showToast("🟢 Comunicación por voz activa • Liseth le escucha atentamente.");
              } else if (data.state === "standby") {
                enterStandbyMode();
                showToast("🟣 Modo Reposo: Liseth sigue escuchando en segundo plano (diga 'Liseth').");
              } else {
                voiceAssistantState = "off";
                stopListeningVisuals();
                showToast("🔇 Micrófono pausado.");
              }
              return;
            }
          } catch(e) {
            console.warn("Fallo conectando al motor nativo de voz, recurriendo a Web Speech API:", e);
          }
        }

        // 2. Fallback de navegador (Web Speech API)
        if (!recognition) {
          showToast("⚠️ El reconocimiento de voz en navegador requiere Google Chrome o Microsoft Edge.");
          return;
        }

        if (voiceAssistantState === "active") {
          enterStandbyMode();
          showToast("🟣 Modo Reposo: Liseth sigue escuchando en segundo plano (diga 'Liseth').");
        } else if (voiceAssistantState === "standby") {
          activateVoiceMode(true);
          showToast("🟢 Liseth atenta • Hable ahora, Santiago.");
        } else {
          continuousListeningEnabled = true;
          stopSpeaking();
          activateVoiceMode(true);
          showToast("🟢 Comunicación por voz activa • Liseth le escucha atentamente.");
        }
      }"""

    new_toggle_listening = """      async function toggleListening() {
        if (isPcmRecording) {
          stopPcmVoiceRecordingAndSubmit();
          return;
        }

        // Detectar si el navegador soporta Google Web Speech de forma fiable
        const isChromiumClean = !navigator.userAgent.includes("OPR/") && !navigator.userAgent.includes("Opera") && !navigator.userAgent.includes("Firefox");
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (SpeechRec && isChromiumClean && recognition) {
          if (voiceAssistantState === "active") {
            enterStandbyMode();
            showToast("🟣 Modo Reposo: Liseth sigue escuchando en segundo plano (diga 'Liseth').");
          } else if (voiceAssistantState === "standby") {
            activateVoiceMode(true);
            showToast("🟢 Liseth atenta • Hable ahora, Santiago.");
          } else {
            continuousListeningEnabled = true;
            stopSpeaking();
            activateVoiceMode(true);
            showToast("🟢 Comunicación por voz activa • Liseth le escucha atentamente.");
          }
          return;
        }

        // Failsafe universal de alta fidelidad: Motor de audio PCM WAV directo a Liseth
        startPcmVoiceRecording();
      }"""

    if old_toggle_listening in content:
        content = content.replace(old_toggle_listening, new_toggle_listening, 1)
        print("  -> Updated toggleListening function")

    # 4. In recognition.onerror, fallback to PCM recorder
    old_onerror = """            if (event.error === "not-allowed" || event.error === "service-not-allowed") {
              showToast("⚠️ Permiso de micrófono requerido. Haga clic en el icono del micrófono y permita el acceso en el navegador.");
              stopListeningVisuals();
            }"""
    new_onerror = """            if (event.error === "not-allowed" || event.error === "service-not-allowed" || event.error === "network") {
              console.warn("WebSpeech no disponible en este navegador, activando motor PCM de respaldo:", event.error);
              startPcmVoiceRecording();
            }"""
    if old_onerror in content:
        content = content.replace(old_onerror, new_onerror, 1)
        print("  -> Updated recognition.onerror with PCM fallback")

    # 5. In handleSend, ensure authenticated session and auto-dock
    old_handle_send_check = """        // Verificación Estricta de Acceso SaaS + Firebase: Prohibido usar Liseth sin iniciar sesión o crear cuenta
        if (!window.isLisethAuthenticated || (!localStorage.getItem("liseth_session_token") && !localStorage.getItem("liseth_saas_token"))) {
          showAuthModal();
          showToast("🔒 Debes crear una cuenta o iniciar sesión para usar Liseth.");
          return;
        }"""
    new_handle_send_check = """        // Auto-asegurar sesión del Creador o usuario autenticado
        const currentTok = await ensureAuthenticatedSession();
        if (!window.isLisethAuthenticated && (!currentTok && !localStorage.getItem("liseth_session_token") && !localStorage.getItem("liseth_saas_token"))) {
          showAuthModal();
          showToast("🔒 Inicie sesión o ingrese su PIN para interactuar con Liseth.");
          return;
        }
        window.isLisethAuthenticated = true;"""
    if old_handle_send_check in content:
        content = content.replace(old_handle_send_check, new_handle_send_check, 1)
        print("  -> Updated handleSend authentication check")

    # 6. Auto-dock orb on message append
    old_append_user = "appendUserMessageWithFiles(text, attached);"
    new_append_user = """appendUserMessageWithFiles(text, attached);
        if (typeof window.toggleOrbDockMode === "function") {
          window.toggleOrbDockMode(true);
        }"""
    if old_append_user in content and "window.toggleOrbDockMode(true)" not in content[content.find(old_append_user):content.find(old_append_user)+100]:
        content = content.replace(old_append_user, new_append_user, 1)
        print("  -> Injected auto-dock on user message")

    # 7. Pass auth headers in callGeminiAPI
    old_call_gemini_fetch = """            const serverRes = await fetch("/api/brain/chat", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              credentials: "include",
              signal: controller.signal,
              body: JSON.stringify({
                systemInstruction: buildEffectiveSystemInstruction(),
                contents: history,
                apiKey: apiKey || ""
              })
            });"""

    new_call_gemini_fetch = """            const token = await ensureAuthenticatedSession();
            const headers = { "Content-Type": "application/json" };
            if (token) headers["Authorization"] = `Bearer ${token}`;
            const saasTok = localStorage.getItem("liseth_saas_token");
            if (saasTok) headers["X-SaaS-Token"] = saasTok;

            const serverRes = await fetch("/api/brain/chat", {
              method: "POST",
              headers: headers,
              credentials: "include",
              signal: controller.signal,
              body: JSON.stringify({
                systemInstruction: buildEffectiveSystemInstruction(),
                contents: history,
                apiKey: apiKey || ""
              })
            });"""

    if old_call_gemini_fetch in content:
        content = content.replace(old_call_gemini_fetch, new_call_gemini_fetch, 1)
        print("  -> Injected auth headers in callGeminiAPI")

    # 8. Update toggleOrbDockMode to accept boolean force argument
    old_toggle_dock = """      window.toggleOrbDockMode = function() {
        const stage = document.getElementById("ai-core-orb-stage");
        const icon = document.getElementById("orb-dock-icon");
        const lbl = document.getElementById("orb-dock-label");
        if (!stage) return;
        stage.classList.toggle("compact");
        const isCompact = stage.classList.contains("compact");
        aiCoreOrb.dockMode = isCompact ? "compact" : "hero";
        if (icon) icon.textContent = isCompact ? "▲" : "↕";
        if (lbl) lbl.textContent = isCompact ? "Expandir Núcleo" : "Acoplar Núcleo";
        setTimeout(onAICoreOrbResize, 200);
      };"""

    new_toggle_dock = """      window.toggleOrbDockMode = function(force) {
        const stage = document.getElementById("ai-core-orb-stage");
        const icon = document.getElementById("orb-dock-icon");
        const lbl = document.getElementById("orb-dock-label");
        if (!stage) return;
        if (typeof force === "boolean") {
          if (force) stage.classList.add("compact");
          else stage.classList.remove("compact");
        } else {
          stage.classList.toggle("compact");
        }
        const isCompact = stage.classList.contains("compact");
        if (window.aiCoreOrb) window.aiCoreOrb.dockMode = isCompact ? "compact" : "hero";
        if (icon) icon.textContent = isCompact ? "▲" : "↕";
        if (lbl) lbl.textContent = isCompact ? "Expandir Núcleo" : "Acoplar Núcleo";
        if (typeof onAICoreOrbResize === "function") setTimeout(onAICoreOrbResize, 200);
      };"""

    if old_toggle_dock in content:
        content = content.replace(old_toggle_dock, new_toggle_dock, 1)
        print("  -> Updated toggleOrbDockMode function with force argument")

    # 9. Update checkServerConnection to call ensureAuthenticatedSession
    old_server_connected = """            if (connectedResult.authRequired) {
              serverStatusText.textContent = `🔒 Requiere PIN (:${portNum})`;
              showAuthModal();
            } else {
              serverStatusText.textContent = `🟢 En línea (:${portNum})`;"""
    new_server_connected = """            if (connectedResult.authRequired) {
              serverStatusText.textContent = `🔒 Requiere PIN (:${portNum})`;
              ensureAuthenticatedSession();
            } else {
              serverStatusText.textContent = `🟢 En línea (:${portNum})`;
              ensureAuthenticatedSession();"""
    if old_server_connected in content:
        content = content.replace(old_server_connected, new_server_connected, 1)
        print("  -> Updated checkServerConnection with ensureAuthenticatedSession")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  -> Successfully saved {filepath}")

for fp in ["index.html", "jarvis.html", "app/static/index.html"]:
    patch_file(fp)
