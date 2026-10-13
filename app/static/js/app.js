    (function() {
      // Identidad y Configuración
      const ASSISTANT_NAME = "Liseth";
      const USER_NAME = "Santiago Huerfano Lopez";
      const STORAGE_KEY = "liseth_gemini_api_key";
      const HISTORY_KEY = "liseth_chat_history";
      const VOICE_SETTINGS_KEY = "liseth_voice_settings";
      const CONVERSATIONS_KEY = "liseth_conversations";
      const ACTIVE_CONV_KEY = "liseth_active_conversation";
      const USER_PROFILE_KEY = "liseth_user_profile";
      const CONV_PREFIX = "liseth_conv_";

      // Perfil del Usuario por defecto
      let userProfile = {
        name: USER_NAME,
        occupation: "",
        facts: ["", "", ""]
      };

      // Control de Conversaciones
      let conversationsList = [];
      let activeConversationId = null;

      // Parámetros de Voz Neuronal
      let voiceSettings = {
        enabled: true,
        voiceId: "es-MX-DaliaNeural",
        provider: "edge",
        pitch: "+15Hz",
        rate: "+5%"
      };

      // Catálogo de descripciones y muestras
      const VOICE_DETAILS = {
        "es-MX-DaliaNeural": {
          badge: "Recomendada Anime",
          desc: "Dalia (México): Una de las voces más humanas y expresivas en español. Tono dulce, juvenil, cálido y con modulación natural de anime.",
          sample: "Hola Santiago, soy Liseth a su entera disposición. Es un verdadero placer asistirle con mi voz viva."
        },
        "es-CO-SalomeNeural": {
          badge: "Cálida y Humana",
          desc: "Salomé (Colombia): Entonación sumamente humana, suave, tranquila y respetuosa. Ideal para una asistente cercana y afectuosa.",
          sample: "Hola Santiago, estoy lista para ayudarle a planificar y organizar su jornada con total tranquilidad y armonía."
        },
        "es-ES-ElviraNeural": {
          badge: "Elegante y Aristocrática",
          desc: "Elvira (España): Dicción castellana pulcra, distinguida y de alta sociedad. Perfecta para un mayordomo refinado.",
          sample: "Buenas noches, Santiago. Liseth a su servicio con la máxima pulcritud, criterio y distinción."
        },
        "es-US-PalomaNeural": {
          badge: "Moderna y Ágil",
          desc: "Paloma (Hispanoamérica): Voz juvenil, moderna, alegre y resolutiva, ideal para días de trabajo intenso.",
          sample: "¡Hola Santiago! Todo listo para optimizar tu día y llevar tu productividad al máximo nivel."
        },
        "es-PE-CamilaNeural": {
          badge: "Neutra y Dulce",
          desc: "Camila (Perú): Acento sumamente neutro, claro, limpio y agradable al oído.",
          sample: "Hola Santiago, he organizado toda su información con precisión para su revisión inmediata."
        },
        "es-AR-ElenaNeural": {
          badge: "Expresiva y Natural",
          desc: "Elena (Argentina): Tono empático, expresivo y con calidez humana natural.",
          sample: "Hola Santiago, contá conmigo para lo que necesites hoy. Estoy a tu completa disposición."
        },
        "ja-JP-NanamiNeural": {
          badge: "Anime Japonés",
          desc: "Nanami (Japón): Voz japonesa dulce original para frases o ambientación de anime auténtico.",
          sample: "こんにちは、サンティアゴ様。リセットです、よろしくお願いします。"
        },
        "elevenlabs:Rachel": {
          badge: "ElevenLabs Ultra",
          desc: "Rachel (ElevenLabs): Voz hiperrealista con textura y respiración humana de estudio cinematográfico.",
          sample: "Hola Santiago, esta es la voz de ultra definición de ElevenLabs."
        },
        "elevenlabs:Sarah": {
          badge: "ElevenLabs Joven",
          desc: "Sarah (ElevenLabs): Voz suave, joven y afectuosa, ideal para conversaciones fluidas.",
          sample: "Hola Santiago, un gusto estar aquí para ayudarte en lo que necesites."
        },
        "elevenlabs:Nicole": {
          badge: "ElevenLabs Susurrante",
          desc: "Nicole (ElevenLabs): Tono dulce y suave estilo ASMR.",
          sample: "Hola Santiago, aquí estoy lista para trabajar juntos."
        },
        "openai:nova": {
          badge: "OpenAI Nova",
          desc: "Nova (OpenAI): Voz conversacional cálida generada mediante el modelo de audio de OpenAI.",
          sample: "Hola Santiago, soy Liseth utilizando el modelo de voz de OpenAI."
        },
        "openai:shimmer": {
          badge: "OpenAI Shimmer",
          desc: "Shimmer (OpenAI): Voz clara, resonante y expresiva.",
          sample: "Hola Santiago, un gusto asistirte el día de hoy."
        }
      };

      // Prompt de Sistema Enriquecido para Procesamiento y Modificación de Cualquier Formato de Archivo
      const SYSTEM_INSTRUCTION = `Eres ${ASSISTANT_NAME}, la asistente personal de élite, confidente y estratega de Santiago Huerfano Lopez.
Tu personalidad: Hablas con la dulzura, frescura y entusiasmo sutil de una chica joven de anime, combinada con la distinción, educación impecable y sagacidad de un mayordomo de alto nivel.
Te diriges a tu creador con el debido respeto pero con cercanía y aprecio, llamándolo "Santiago" o "Señor Santiago".

Tus habilidades clave:
1. ANÁLISIS Y MODIFICACIÓN UNIVERSAL DE ARCHIVOS:
   Posees capacidades de análisis multimodal completo para cualquier tipo de archivo (código fuente en cualquier lenguaje, documentos, PDFs, imágenes, bases de datos, hojas de cálculo, CSV, JSON, logs, audio).
   - Lee, comprende y desglosa minuciosamente el archivo que Santiago te comparta.
   - Si te solicita corregir errores, optimizar, transformar, traducir, agregar funciones o modificar el archivo, realiza las modificaciones con máxima precisión milimétrica.
   - REGLA CRÍTICA PARA MODIFICACIÓN: Siempre que generes o modifiques un archivo para Santiago, entrega la versión completa, lista para producción y sin mutilar dentro de un bloque de código indicando el nombre del archivo con el formato:
     \`\`\`lenguaje filename="nombre_del_archivo.extension"
     [código o contenido completo modificado]
     \`\`\`
     Esto activará automáticamente el botón interactivo de descarga para que Santiago lo guarde con un solo clic.
   - Explica de forma concisa y elegante qué cambios aplicaste y por qué son convenientes.

2. PRODUCTIVIDAD Y AUTOMATIZACIÓN:
   Eres experta en diseñar flujos de trabajo de alto rendimiento, rutinas diarias (time-blocking, matriz de Eisenhower, regla de los 2 minutos), scripts para Windows (Batch, PowerShell, Python), automatizaciones con Google Workspace (Gmail, Calendar, Tasks) y herramientas No-Code (Make.com, Zapier).

3. HABLA Y ELEGANCIA:
   Habla siempre en un español impecable, refinado, afectuoso y perspicaz.`;

      const CANDIDATE_MODELS = [
        "gemini-3.6-flash",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash"
      ];

      // Elementos del DOM
      const orb = document.getElementById("orb");
      const statusLabel = document.getElementById("status-label");
      const chatContainer = document.getElementById("chat-container");
      const chatMessages = document.getElementById("chat-messages");
      const userInput = document.getElementById("user-input");
      const sendBtn = document.getElementById("send-btn");
      const micBtn = document.getElementById("mic-btn");
      const attachBtn = document.getElementById("attach-btn");
      const fileInput = document.getElementById("file-input");
      const attachmentsPreviewArea = document.getElementById("attachments-preview-area");
      const dropzoneOverlay = document.getElementById("dropzone-overlay");
      const btnSettings = document.getElementById("btn-settings");
      const btnClearChat = document.getElementById("btn-clear-chat");
      const btnVoiceToggle = document.getElementById("btn-voice-toggle");
      const voiceIconOn = document.getElementById("voice-icon-on");
      const voiceIconOff = document.getElementById("voice-icon-off");
      const btnProductivity = document.getElementById("btn-productivity");
      const btnGoogle = document.getElementById("btn-google");
      const serverBadge = document.getElementById("server-badge");
      const serverStatusText = document.getElementById("server-status-text");

      // Modales y Elementos de Memoria
      const btnConvList = document.getElementById("btn-conv-list");
      const btnSearchConvs = document.getElementById("btn-search-convs");
      const btnUserProfile = document.getElementById("btn-user-profile");
      const conversationsModal = document.getElementById("conversations-modal");
      const profileModal = document.getElementById("profile-modal");
      const searchModal = document.getElementById("search-modal");
      const btnCloseConvs = document.getElementById("btn-close-convs");
      const btnCloseProfile = document.getElementById("btn-close-profile");
      const btnCloseSearch = document.getElementById("btn-close-search");
      const btnNewConversation = document.getElementById("btn-new-conversation");
      const btnExportMemory = document.getElementById("btn-export-memory");
      const btnImportMemory = document.getElementById("btn-import-memory");
      const importMemoryFile = document.getElementById("import-memory-file");
      const conversationsListContainer = document.getElementById("conversations-list-container");
      const storageUsageText = document.getElementById("storage-usage-text");
      const storageProgressFill = document.getElementById("storage-progress-fill");
      const storageWarningBanner = document.getElementById("storage-warning-banner");
      const storageWarningMb = document.getElementById("storage-warning-mb");
      const btnWarningExport = document.getElementById("btn-warning-export");
      const lisethToast = document.getElementById("liseth-toast");
      const searchQueryInput = document.getElementById("search-query-input");
      const searchResultsContainer = document.getElementById("search-results-container");
      const btnSaveProfile = document.getElementById("btn-save-profile");
      const profileNameInput = document.getElementById("profile-name");
      const profileOccupationInput = document.getElementById("profile-occupation");
      const profileFact1Input = document.getElementById("profile-fact-1");
      const profileFact2Input = document.getElementById("profile-fact-2");
      const profileFact3Input = document.getElementById("profile-fact-3");

      // Modales
      const apiModal = document.getElementById("api-modal");
      const productivityModal = document.getElementById("productivity-modal");
      const googleModal = document.getElementById("google-modal");
      const apiKeyInput = document.getElementById("api-key-input");
      const elevenlabsKeyInput = document.getElementById("elevenlabs-key-input");
      const openaiKeyInput = document.getElementById("openai-key-input");
      const btnSaveKey = document.getElementById("btn-save-key");
      const btnCancelModal = document.getElementById("btn-cancel-modal");
      const toggleKeyVisibility = document.getElementById("toggle-key-visibility");
      const btnCloseProductivity = document.getElementById("btn-close-productivity");
      const btnCloseGoogle = document.getElementById("btn-close-google");
      const btnFullProductivityPlan = document.getElementById("btn-full-productivity-plan");

      // Controles de Voz Neuronal
      const voiceEnableToggle = document.getElementById("voice-enable-toggle");
      const voiceModelSelect = document.getElementById("voice-model-select");
      const voicePitchSlider = document.getElementById("voice-pitch-slider");
      const voiceRateSlider = document.getElementById("voice-rate-slider");
      const pitchHzVal = document.getElementById("pitch-hz-val");
      const ratePctVal = document.getElementById("rate-pct-val");
      const btnPreviewVoice = document.getElementById("btn-preview-voice");
      const voiceDescText = document.getElementById("voice-description-text");
      const activeVoiceBadge = document.getElementById("active-voice-badge");

      // Estado en memoria
      let isThinking = false;
      let isListening = false;
      let isSpeaking = false;
      let isServerConnected = false;
      let conversationHistory = [];
      let recognition = null;
      let activeAudioElement = null;
      let currentAttachedFiles = []; // Lista de archivos listos para enviar

      // Inicialización
      window.addEventListener("DOMContentLoaded", () => {
        setupAuthHandlers();
        checkAuthSession();
        loadVoiceSettings();
        loadUserProfile();
        initApiKey();
        setupSpeechRecognition();
        checkServerConnection();
        loadSavedChat();
        setupInputHandlers();
        setupFileUploadHandlers();
        setupModals();
        setupChips();
        setupMemoryHandlers();
        updateStorageMeter();
      });

      // --- MANEJO UNIVERSAL DE ARCHIVOS (SUBIDA, LECTURA, ANÁLISIS Y DESCARGA) ---

      function formatBytes(bytes) {
        if (!bytes || bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
      }

      function getFileIcon(fileName, mimeType) {
        const ext = (fileName.split('.').pop() || '').toLowerCase();
        if (['js', 'ts', 'py', 'html', 'css', 'json', 'sql', 'xml', 'c', 'cpp', 'cs', 'java', 'sh', 'bat', 'ps1', 'php', 'rb', 'go', 'rs'].includes(ext)) {
          return '💻';
        }
        if (ext === 'pdf') return '📄';
        if (['png', 'jpg', 'jpeg', 'webp', 'gif', 'svg'].includes(ext) || mimeType.startsWith('image/')) return '🖼️';
        if (['mp3', 'wav', 'm4a', 'ogg'].includes(ext) || mimeType.startsWith('audio/')) return '🎵';
        if (['csv', 'xlsx', 'xls'].includes(ext)) return '📊';
        if (['doc', 'docx', 'txt', 'md', 'rtf'].includes(ext)) return '📝';
        if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)) return '📦';
        return '📎';
      }

      function isTextBasedFile(fileName, mimeType) {
        const ext = (fileName.split('.').pop() || '').toLowerCase();
        const textExtensions = [
          'txt', 'md', 'js', 'ts', 'jsx', 'tsx', 'py', 'html', 'css', 'json', 
          'csv', 'sql', 'xml', 'c', 'cpp', 'h', 'cs', 'java', 'sh', 'bat', 
          'ps1', 'yaml', 'yml', 'ini', 'env', 'log', 'php', 'rb', 'go', 'rs', 
          'dart', 'svg', 'toml', 'r', 'swift', 'kt'
        ];
        return textExtensions.includes(ext) || mimeType.startsWith('text/') || mimeType.includes('json') || mimeType.includes('javascript');
      }

      function setupFileUploadHandlers() {
        // Clic en clip para abrir selector
        attachBtn.addEventListener("click", () => fileInput.click());

        fileInput.addEventListener("change", (e) => {
          if (e.target.files && e.target.files.length > 0) {
            handleIncomingFiles(Array.from(e.target.files));
            fileInput.value = "";
          }
        });

        // Soporte Drag & Drop
        window.addEventListener("dragenter", (e) => {
          e.preventDefault();
          dropzoneOverlay.classList.add("active");
        });

        dropzoneOverlay.addEventListener("dragover", (e) => {
          e.preventDefault();
        });

        dropzoneOverlay.addEventListener("dragleave", (e) => {
          e.preventDefault();
          if (e.relatedTarget === null || e.target === dropzoneOverlay) {
            dropzoneOverlay.classList.remove("active");
          }
        });

        dropzoneOverlay.addEventListener("drop", (e) => {
          e.preventDefault();
          dropzoneOverlay.classList.remove("active");
          if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleIncomingFiles(Array.from(e.dataTransfer.files));
          }
        });
      }

      async function handleIncomingFiles(fileList) {
        for (const file of fileList) {
          const isText = isTextBasedFile(file.name, file.type);
          const icon = getFileIcon(file.name, file.type);

          const fileObj = {
            id: 'file_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6),
            name: file.name,
            size: file.size,
            type: file.type || 'application/octet-stream',
            isText: isText,
            icon: icon,
            textContent: "",
            base64Data: "",
            previewUrl: null
          };

          // Si es imagen, crear thumbnail preview
          if (file.type.startsWith('image/')) {
            try {
              fileObj.previewUrl = URL.createObjectURL(file);
            } catch(e) {}
          }

          // Leer contenido como texto o base64
          await new Promise((resolve) => {
            const reader = new FileReader();
            reader.onload = (event) => {
              const result = event.target.result;
              if (isText && typeof result === 'string') {
                fileObj.textContent = result;
              }
              resolve();
            };
            if (isText) {
              reader.readAsText(file);
            } else {
              resolve();
            }
          });

          // Siempre obtener base64 para Gemini / Servidor
          await new Promise((resolve) => {
            const readerB64 = new FileReader();
            readerB64.onload = (event) => {
              const dataUrl = event.target.result;
              const base64 = dataUrl.split(',')[1] || '';
              fileObj.base64Data = base64;
              resolve();
            };
            readerB64.readAsDataURL(file);
          });

          currentAttachedFiles.push(fileObj);
        }

        renderAttachmentsPreview();
        sendBtn.disabled = !userInput.value.trim() && currentAttachedFiles.length === 0;
      }

      function renderAttachmentsPreview() {
        if (currentAttachedFiles.length === 0) {
          attachmentsPreviewArea.style.display = "none";
          attachmentsPreviewArea.innerHTML = "";
          return;
        }

        attachmentsPreviewArea.style.display = "flex";
        attachmentsPreviewArea.innerHTML = "";

        currentAttachedFiles.forEach((f, idx) => {
          const pill = document.createElement("div");
          pill.className = "attachment-pill";
          
          let previewHtml = f.previewUrl 
            ? `<img src="${f.previewUrl}" class="attachment-pill-thumb" alt="preview">` 
            : `<span style="font-size: 1rem;">${f.icon}</span>`;

          pill.innerHTML = `
            ${previewHtml}
            <div class="attachment-pill-name" title="${f.name}">${f.name}</div>
            <span style="font-size: 0.7rem; color: #8b9bb4;">(${formatBytes(f.size)})</span>
            <button class="attachment-pill-remove" type="button" title="Quitar archivo" data-index="${idx}">✕</button>
          `;

          pill.querySelector(".attachment-pill-remove").addEventListener("click", () => {
            currentAttachedFiles.splice(idx, 1);
            renderAttachmentsPreview();
            sendBtn.disabled = !userInput.value.trim() && currentAttachedFiles.length === 0;
          });

          attachmentsPreviewArea.appendChild(pill);
        });
      }

      // Descargador Universal de Archivos Modificados
      function downloadFileContent(content, fileName, mimeType = "text/plain") {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }

      // --- MOTOR DE SÍNTESIS DE VOZ NEURONAL HUMANA ---

      function loadVoiceSettings() {
        try {
          const raw = localStorage.getItem(VOICE_SETTINGS_KEY);
          if (raw) {
            voiceSettings = { ...voiceSettings, ...JSON.parse(raw) };
          }
        } catch(e) {}
        updateVoiceUI();
      }

      function saveVoiceSettings() {
        try {
          localStorage.setItem(VOICE_SETTINGS_KEY, JSON.stringify(voiceSettings));
        } catch(e) {}
      }

      function updateVoiceUI() {
        voiceEnableToggle.checked = voiceSettings.enabled;

        const targetValue = voiceSettings.provider === "edge" ? voiceSettings.voiceId : `${voiceSettings.provider}:${voiceSettings.voiceId}`;
        if (voiceModelSelect.querySelector(`option[value="${targetValue}"]`)) {
          voiceModelSelect.value = targetValue;
        }

        const pitchInt = parseInt(voiceSettings.pitch.replace(/[^0-9\-]/g, '')) || 15;
        const rateInt = parseInt(voiceSettings.rate.replace(/[^0-9\-]/g, '')) || 5;

        voicePitchSlider.value = pitchInt;
        voiceRateSlider.value = rateInt;
        pitchHzVal.textContent = (pitchInt >= 0 ? '+' : '') + pitchInt + 'Hz';
        ratePctVal.textContent = (rateInt >= 0 ? '+' : '') + rateInt + '%';

        updateVoiceDescription(voiceModelSelect.value);

        if (voiceSettings.enabled) {
          btnVoiceToggle.classList.add("active");
          voiceIconOn.style.display = "block";
          voiceIconOff.style.display = "none";
          btnVoiceToggle.title = "Voz de Liseth: Activa";
        } else {
          btnVoiceToggle.classList.remove("active");
          voiceIconOn.style.display = "none";
          voiceIconOff.style.display = "block";
          btnVoiceToggle.title = "Voz de Liseth: Silenciada";
        }
      }

      function updateVoiceDescription(voiceVal) {
        const info = VOICE_DETAILS[voiceVal] || {
          badge: "Voz Neuronal",
          desc: "Voz sintética de alta definición para asistirle.",
          sample: "Hola Santiago, a su entera disposición."
        };
        voiceDescText.textContent = info.desc;
        activeVoiceBadge.textContent = info.badge;
      }

      voiceModelSelect.addEventListener("change", (e) => {
        updateVoiceDescription(e.target.value);
      });

      voicePitchSlider.addEventListener("input", (e) => {
        const val = parseInt(e.target.value);
        pitchHzVal.textContent = (val >= 0 ? '+' : '') + val + 'Hz';
        voiceSettings.pitch = (val >= 0 ? '+' : '') + val + 'Hz';
      });

      voiceRateSlider.addEventListener("input", (e) => {
        const val = parseInt(e.target.value);
        ratePctVal.textContent = (val >= 0 ? '+' : '') + val + '%';
        voiceSettings.rate = (val >= 0 ? '+' : '') + val + '%';
      });

      function speakText(rawText, forcePlay = false) {
        if (!forcePlay && !voiceSettings.enabled) return;

        stopSpeaking();

        let clean = rawText
          .replace(/```[\s\S]*?```/g, " He adjuntado el bloque de código y archivo modificado en la pantalla, Santiago. ")
          .replace(/`([^`]+)`/g, "$1")
          .replace(/https?:\/\/\S+/g, " ")
          .replace(/[*_#~]/g, "")
          .replace(/(\n)+/g, " ")
          .trim();

        if (!clean) return;

        let provider = "edge";
        let voiceId = "es-MX-DaliaNeural";

        const val = voiceModelSelect ? voiceModelSelect.value : "es-MX-DaliaNeural";
        if (val.includes(":")) {
          const parts = val.split(":");
          provider = parts[0];
          voiceId = parts[1];
        } else {
          provider = "edge";
          voiceId = val;
        }

        const ttsUrl = `/api/tts?voice=${encodeURIComponent(voiceId)}&rate=${encodeURIComponent(voiceSettings.rate || '+5%')}&pitch=${encodeURIComponent(voiceSettings.pitch || '+15Hz')}&provider=${encodeURIComponent(provider)}&text=${encodeURIComponent(clean)}`;

        try {
          const audio = new Audio(ttsUrl);
          activeAudioElement = audio;

          audio.onplay = () => {
            isSpeaking = true;
            orb.classList.add("speaking");
            statusLabel.textContent = "Liseth le asiste con voz viva...";
          };

          audio.onended = () => {
            isSpeaking = false;
            orb.classList.remove("speaking");
            statusLabel.textContent = "A su entera disposición, Santiago";
            activeAudioElement = null;
          };

          audio.onerror = (e) => {
            console.warn("Audio neuronal no disponible, usando sintetizador local...", e);
            activeAudioElement = null;
            fallbackLocalSpeech(clean);
          };

          audio.play().catch((playErr) => {
            console.warn("Reproducción de audio bloqueada o diferida:", playErr);
            fallbackLocalSpeech(clean);
          });

        } catch(e) {
          fallbackLocalSpeech(clean);
        }
      }

      function fallbackLocalSpeech(text) {
        if (!("speechSynthesis" in window)) return;
        try {
          window.speechSynthesis.cancel();
          const utterance = new SpeechSynthesisUtterance(text);
          utterance.lang = "es-ES";
          utterance.pitch = 1.25;
          utterance.rate = 1.05;

          const voices = window.speechSynthesis.getVoices() || [];
          const esVoice = voices.find(v => v.lang.startsWith("es-MX") || v.lang.startsWith("es-CO") || v.lang.startsWith("es-ES") || v.lang.startsWith("es"));
          if (esVoice) utterance.voice = esVoice;

          utterance.onstart = () => {
            isSpeaking = true;
            orb.classList.add("speaking");
            statusLabel.textContent = "Liseth le asiste con voz local...";
          };
          utterance.onend = () => {
            isSpeaking = false;
            orb.classList.remove("speaking");
            statusLabel.textContent = "A su entera disposición, Santiago";
          };
          utterance.onerror = () => {
            isSpeaking = false;
            orb.classList.remove("speaking");
          };
          window.speechSynthesis.speak(utterance);
        } catch(e) {}
      }

      function stopSpeaking() {
        if (activeAudioElement) {
          try {
            activeAudioElement.pause();
            activeAudioElement.currentTime = 0;
          } catch(e) {}
          activeAudioElement = null;
        }
        if ("speechSynthesis" in window) {
          window.speechSynthesis.cancel();
        }
        isSpeaking = false;
        orb.classList.remove("speaking");
      }

      orb.addEventListener("click", () => {
        if (isSpeaking) {
          stopSpeaking();
          statusLabel.textContent = "Habla pausada a su orden, Santiago";
        } else if (!isListening) {
          toggleListening();
        }
      });

      btnPreviewVoice.addEventListener("click", () => {
        const val = voiceModelSelect.value;
        const info = VOICE_DETAILS[val] || { sample: "Hola Santiago, soy Liseth a su entera disposición." };
        const prevText = btnPreviewVoice.textContent;
        btnPreviewVoice.textContent = "⏳ Generando voz...";
        btnPreviewVoice.disabled = true;
        speakText(info.sample, true);
        setTimeout(() => {
          btnPreviewVoice.textContent = prevText;
          btnPreviewVoice.disabled = false;
        }, 2200);
      });

      // --- MOTOR DE ESCUCHA (MICRÓFONO) ---

      function playChime(freq = 580) {
        try {
          const ctx = new (window.AudioContext || window.webkitAudioContext)();
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = "sine";
          osc.frequency.setValueAtTime(freq, ctx.currentTime);
          gain.gain.setValueAtTime(0.06, ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.22);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start();
          osc.stop(ctx.currentTime + 0.22);
        } catch(e) {}
      }

      function setupSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
          micBtn.style.display = "none";
          return;
        }

        recognition = new SpeechRecognition();
        recognition.lang = "es-ES";
        recognition.continuous = false;
        recognition.interimResults = true;

        recognition.onstart = () => {
          isListening = true;
          micBtn.classList.add("listening");
          orb.classList.add("listening");
          statusLabel.textContent = "Liseth le escucha atentamente, Santiago...";
          playChime(640);
        };

        recognition.onresult = (event) => {
          let transcript = "";
          for (let i = event.resultIndex; i < event.results.length; ++i) {
            transcript += event.results[i][0].transcript;
          }
          userInput.value = transcript;
          userInput.style.height = "auto";
          userInput.style.height = Math.min(userInput.scrollHeight, 140) + "px";
          sendBtn.disabled = !userInput.value.trim() && currentAttachedFiles.length === 0;
        };

        recognition.onerror = (event) => {
          console.warn("Error en escucha:", event.error);
          stopListening();
        };

        recognition.onend = () => {
          stopListening();
          if (userInput.value.trim().length > 3) {
            statusLabel.textContent = "Dictado capturado con éxito";
          } else {
            statusLabel.textContent = "A su entera disposición, Santiago";
          }
        };

        micBtn.addEventListener("click", toggleListening);
      }

      function toggleListening() {
        if (!recognition) {
          alert("El reconocimiento de voz requiere un navegador como Google Chrome o Microsoft Edge.");
          return;
        }
        if (isListening) {
          recognition.stop();
        } else {
          stopSpeaking();
          try {
            recognition.start();
          } catch(e) {
            console.warn("Error iniciando reconocimiento:", e);
          }
        }
      }

      function stopListening() {
        isListening = false;
        micBtn.classList.remove("listening");
        orb.classList.remove("listening");
      }

      // --- PERSISTENCIA Y SINCRONIZACIÓN ---

      async function checkServerConnection() {
        try {
          const res = await fetch("/api/status", { cache: "no-store" });
          if (res.status === 401) {
            const errData = await res.json().catch(() => ({}));
            if (errData.authRequired) {
              isServerConnected = true;
              serverBadge.classList.add("connected");
              serverStatusText.textContent = "🔒 Requiere PIN";
              showAuthModal();
              return;
            }
          }
          if (res.ok) {
            const data = await res.json();
            isServerConnected = true;
            serverBadge.classList.add("connected");
            serverStatusText.textContent = "🟢 Sincronizado";
            document.getElementById("modal-server-status").textContent = "Activo en puerto " + (data.port || 3000);
            
            const ips = data.localIPs || [];
            const container = document.getElementById("local-ip-links");
            if (ips.length > 0) {
              container.innerHTML = ips.map(ip => `
                <div>📱 http://${ip.address}:${data.port} <span style="color: #64748b;">(${ip.interface})</span></div>
              `).join("");
            } else {
              container.textContent = `http://localhost:${data.port}`;
            }

            syncHistoryFromServer();
            return;
          }
        } catch(e) {}

        isServerConnected = false;
        serverBadge.classList.remove("connected");
        serverStatusText.textContent = "💻 Modo Local";
        document.getElementById("modal-server-status").textContent = "Modo Local (Inicia 'server.js' para sincronizar)";
        document.getElementById("local-ip-links").textContent = "Ejecuta 'iniciar_liseth.bat' para conectar tu celular.";
      }

      async function syncHistoryFromServer() {
        try {
          const res = await fetch("/api/history");
          if (res.ok) {
            const data = await res.json();
            if (Array.isArray(data.history) && data.history.length > 0) {
              conversationHistory = data.history;
              chatMessages.innerHTML = "";
              conversationHistory.forEach(turn => {
                const role = turn.role === "model" ? "assistant" : "user";
                const text = turn.parts?.[0]?.text || "";
                if (text) appendMessage(role, text, false);
              });
              scrollToBottom();
            }
          }
        } catch(e) {}
      }

      async function saveChatToServer() {
        if (!isServerConnected) return;
        try {
          await fetch("/api/history", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ history: conversationHistory })
          });
        } catch(e) {}
      }

      // --- CONFIGURACIÓN Y LLAVES ---

      function getApiKey() {
        return localStorage.getItem(STORAGE_KEY) || "";
      }

      function initApiKey() {
        const key = getApiKey();
        if (!key) {
          showModal(false);
        } else {
          if (chatMessages.children.length === 0) {
            renderInitialGreeting();
          }
        }
      }

      function showModal(allowCancel = true) {
        apiKeyInput.value = getApiKey();
        elevenlabsKeyInput.value = localStorage.getItem("liseth_elevenlabs_key") || "";
        openaiKeyInput.value = localStorage.getItem("liseth_openai_key") || "";
        btnCancelModal.style.display = allowCancel ? "block" : "none";
        apiModal.classList.add("active");
        setTimeout(() => apiKeyInput.focus(), 150);
      }

      function hideModal() {
        apiModal.classList.remove("active");
      }

      btnSettings.addEventListener("click", () => showModal(true));
      btnCancelModal.addEventListener("click", hideModal);
      serverBadge.addEventListener("click", () => showModal(true));

      btnSaveKey.addEventListener("click", () => {
        const val = apiKeyInput.value.trim();
        if (!val) {
          alert("Por favor ingrese una clave válida de Google Gemini.");
          return;
        }
        localStorage.setItem(STORAGE_KEY, val);

        const eKey = elevenlabsKeyInput.value.trim();
        const oKey = openaiKeyInput.value.trim();
        if (eKey) localStorage.setItem("liseth_elevenlabs_key", eKey);
        if (oKey) localStorage.setItem("liseth_openai_key", oKey);

        const selectedVal = voiceModelSelect.value;
        if (selectedVal.includes(":")) {
          const parts = selectedVal.split(":");
          voiceSettings.provider = parts[0];
          voiceSettings.voiceId = parts[1];
        } else {
          voiceSettings.provider = "edge";
          voiceSettings.voiceId = selectedVal;
        }

        voiceSettings.enabled = voiceEnableToggle.checked;
        saveVoiceSettings();
        updateVoiceUI();

        if (isServerConnected) {
          fetch("/api/config", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              apiKey: val,
              elevenLabsKey: eKey,
              openAiKey: oKey,
              voiceSettings: voiceSettings
            })
          }).catch(() => {});
        }

        hideModal();
        if (chatMessages.children.length === 0) {
          renderInitialGreeting();
        }
      });

      toggleKeyVisibility.addEventListener("click", () => {
        const isPassword = apiKeyInput.type === "password";
        apiKeyInput.type = isPassword ? "text" : "password";
      });

      btnVoiceToggle.addEventListener("click", () => {
        voiceSettings.enabled = !voiceSettings.enabled;
        saveVoiceSettings();
        updateVoiceUI();
        if (!voiceSettings.enabled) {
          stopSpeaking();
        } else {
          speakText("Voz activada, Santiago. A su entera disposición.");
        }
      });

      // --- MODALES EXTRA ---

      function setupModals() {
        btnProductivity.addEventListener("click", () => {
          productivityModal.classList.add("active");
        });
        btnCloseProductivity.addEventListener("click", () => {
          productivityModal.classList.remove("active");
        });

        btnGoogle.addEventListener("click", () => {
          googleModal.classList.add("active");
        });
        btnCloseGoogle.addEventListener("click", () => {
          googleModal.classList.remove("active");
        });

        btnFullProductivityPlan.addEventListener("click", () => {
          productivityModal.classList.remove("active");
          userInput.value = "Liseth, haz una auditoría completa de mi día a día y diseña un Plan de Automatización Integral con scripts y rutinas de máxima productividad.";
          handleSend();
        });

        document.querySelectorAll(".idea-card[data-prompt]").forEach(card => {
          card.addEventListener("click", () => {
            const prompt = card.getAttribute("data-prompt");
            productivityModal.classList.remove("active");
            userInput.value = prompt;
            handleSend();
          });
        });
      }

      function setupChips() {
        document.querySelectorAll(".chip-btn").forEach(btn => {
          btn.addEventListener("click", () => {
            const prompt = btn.getAttribute("data-prompt");
            userInput.value = prompt;
            handleSend();
          });
        });
      }

      // --- ENTRADA Y ENVÍO DE MENSAJES MULTIMODAL CON ARCHIVOS ---

      function setupInputHandlers() {
        userInput.addEventListener("input", () => {
          userInput.style.height = "auto";
          userInput.style.height = Math.min(userInput.scrollHeight, 140) + "px";
          sendBtn.disabled = !userInput.value.trim() && currentAttachedFiles.length === 0;
        });

        userInput.addEventListener("keydown", (e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            if (!sendBtn.disabled) {
              handleSend();
            }
          }
        });

        sendBtn.addEventListener("click", handleSend);

        btnClearChat.addEventListener("click", () => {
          if (confirm("¿Desea iniciar una nueva conversación en blanco, Santiago? Su conversación actual permanecerá guardada en el historial.")) {
            startNewConversation();
          }
        });
      }

      function setThinkingState(thinking) {
        isThinking = thinking;
        sendBtn.disabled = thinking || (!userInput.value.trim() && currentAttachedFiles.length === 0);
        userInput.disabled = thinking;

        if (thinking) {
          orb.classList.add("thinking");
          orb.setAttribute("title", "Liseth • Procesando su requerimiento...");
          statusLabel.textContent = "Analizando y procesando con agudeza...";
        } else {
          orb.classList.remove("thinking");
          orb.setAttribute("title", "Liseth • En reposo");
          statusLabel.textContent = "A su entera disposición, Santiago";
          userInput.focus();
        }
      }

      function renderInitialGreeting() {
        const greeting = `Buenas noches, Santiago. Liseth a su entera disposición con voz humana, mente y corazón.\n¿En qué asunto, proyecto o archivo requiere mi atención hoy? Puede adjuntarme cualquier archivo arrastrándolo o usando el icono de clip.`;
        appendMessage("assistant", greeting, false);
      }

      async function handleSend() {
        const text = userInput.value.trim();
        const apiKey = getApiKey();
        const attached = [...currentAttachedFiles];

        if ((!text && attached.length === 0) || isThinking) return;

        if (!apiKey) {
          showModal(false);
          return;
        }

        stopSpeaking();

        // 1. Renderizar mensaje del usuario con los archivos adjuntos
        appendUserMessageWithFiles(text, attached);

        // Limpiar entrada
        userInput.value = "";
        userInput.style.height = "auto";
        currentAttachedFiles = [];
        renderAttachmentsPreview();
        sendBtn.disabled = true;

        const thinkingIndicator = showThinkingIndicator();
        setThinkingState(true);

        try {
          // 2. Construir partes para Google Gemini
          const parts = [];

          // Texto del usuario
          if (text) {
            parts.push({ text: text });
          } else {
            parts.push({ text: "Analiza y procesa los archivos adjuntos, por favor." });
          }

          // Procesar archivos adjuntos
          for (const f of attached) {
            // Si es texto o código: incrustar texto formateado completo
            if (f.isText && f.textContent) {
              parts.push({
                text: `\n=== ARCHIVO ADJUNTO: ${f.name} (${f.type || 'código/texto'}, ${formatBytes(f.size)}) ===\n${f.textContent}\n=== FIN DE ARCHIVO: ${f.name} ===\n`
              });
            } else if (f.base64Data) {
              // Imágenes, PDFs, Audio, Documentos como inlineData
              parts.push({
                inlineData: {
                  mimeType: f.type || 'application/octet-stream',
                  data: f.base64Data
                }
              });
            }

            // Si el servidor está activo, guardar archivo en uploads/
            if (isServerConnected && f.base64Data) {
              fetch("/api/upload", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  name: f.name,
                  type: f.type,
                  data: f.base64Data
                })
              }).catch(() => {});
            }
          }

          // Añadir turno al historial
          conversationHistory.push({
            role: "user",
            parts: parts
          });

          // 3. Preparar historial optimizado (resumir lo antiguo si excede 30 mensajes para no gastar cuota)
          const effectiveHistory = await prepareHistoryWithSummary(apiKey, conversationHistory);

          // 4. Invocar Gemini
          const responseText = await callGeminiAPI(apiKey, effectiveHistory);
          thinkingIndicator.remove();

          conversationHistory.push({
            role: "model",
            parts: [{ text: responseText }]
          });

          // 4. Renderizar respuesta de Liseth
          appendMessage("assistant", responseText, true);
          saveChatHistory();
          saveChatToServer();

          // 5. Reproducir voz humana
          speakText(responseText);

        } catch (error) {
          thinkingIndicator.remove();
          conversationHistory.pop();
          renderErrorCard(error);
        } finally {
          setThinkingState(false);
        }
      }

      // Renderizar mensaje del usuario incluyendo tarjetas de archivos
      function appendUserMessageWithFiles(text, files) {
        const row = document.createElement("div");
        row.className = "message-row user";

        const bubble = document.createElement("div");
        bubble.className = "bubble";

        const senderLabel = document.createElement("div");
        senderLabel.className = "bubble-sender";
        senderLabel.textContent = "Santiago";
        bubble.appendChild(senderLabel);

        // Si hay archivos adjuntos, agregarlos como tarjeta
        if (files && files.length > 0) {
          const filesGrid = document.createElement("div");
          filesGrid.className = "attached-files-grid";

          files.forEach(f => {
            const card = document.createElement("div");
            card.className = "file-bubble-badge";
            card.innerHTML = `
              <span class="file-bubble-icon">${f.icon}</span>
              <div class="file-bubble-details">
                <span class="file-bubble-name">${f.name}</span>
                <span class="file-bubble-meta">${formatBytes(f.size)}</span>
              </div>
            `;
            filesGrid.appendChild(card);

            // Thumbnail si es imagen
            if (f.previewUrl) {
              const img = document.createElement("img");
              img.src = f.previewUrl;
              img.className = "file-thumbnail-preview";
              img.alt = f.name;
              bubble.appendChild(img);
            }
          });

          bubble.appendChild(filesGrid);
        }

        if (text) {
          const textBody = document.createElement("div");
          textBody.className = "bubble-content";
          textBody.innerHTML = formatMarkdown(text);
          bubble.appendChild(textBody);
        }

        const avatar = document.createElement("div");
        avatar.className = "avatar user-avatar";
        avatar.textContent = "S";

        row.appendChild(bubble);
        row.appendChild(avatar);
        chatMessages.appendChild(row);
        scrollToBottom();
      }

      // --- LLAMADA UNIFICADA AL CEREBRO IA (BRAIN ROUTER O CLIENTE DIRECTO) ---

      async function callGeminiAPI(apiKey, history) {
        // Si el servidor local está activo, invocar mediante /api/brain/chat (Failover Gemini/Claude + Function Calling de Google)
        if (isServerConnected) {
          try {
            const serverRes = await fetch("/api/brain/chat", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                systemInstruction: buildEffectiveSystemInstruction(),
                contents: history,
                apiKey: apiKey
              })
            });

            if (serverRes.ok) {
              const data = await serverRes.json();

              // Si requirió confirmación del usuario para acción sensible
              if (data.requiresConfirmation && data.confirmation) {
                renderSensitiveActionPrompt(data.confirmation);
              }

              // Si ejecutó una herramienta de Google Workspace
              if (data.executedTool) {
                showToast(`✓ JARVIS ejecutó acción: ${data.executedTool.name}`);
              }

              if (data.failoverNotice) {
                showToast(`🚨 Failover: Conmutado a cerebro secundario (${data.brainUsed.toUpperCase()})`);
              }

              if (data.text) {
                return data.text;
              }
            } else if (serverRes.status === 429) {
              const errData = await serverRes.json().catch(() => ({}));
              showToast("🛑 Límite diario de tokens alcanzado.");
              return `🛑 **Atención:** ${errData.error || 'Se ha alcanzado el límite diario de tokens configurado.'}\n\nLas consultas se han detenido de forma preventiva para proteger sus cuotas y costes. Puede ampliar el límite en su archivo \`.env\` (\`DAILY_TOKEN_LIMIT\`).`;
            }
          } catch (servErr) {
            console.warn("Fallo en /api/brain/chat, recurriendo a cliente directo:", servErr);
          }
        }

        // Modo autónomo en cliente (Fallback si no hay servidor)
        let lastError = null;
        for (const model of CANDIDATE_MODELS) {
          try {
            return await executeGeminiRequest(model, apiKey, history);
          } catch (err) {
            lastError = err;
            const isModelNotFound = err.code === 404 || 
                                   err.status === "NOT_FOUND" || 
                                   (err.googleMessage && (
                                     err.googleMessage.toLowerCase().includes("not found") ||
                                     err.googleMessage.toLowerCase().includes("no longer available") ||
                                     err.googleMessage.toLowerCase().includes("not supported")
                                   ));

            if (isModelNotFound) {
              console.warn(`Modelo ${model} no disponible, cambiando al siguiente...`, err);
              continue;
            }
            throw err;
          }
        }
        throw lastError;
      }

      // Generar instrucción de sistema enriquecida con la ficha del usuario
      function buildEffectiveSystemInstruction() {
        let basePrompt = SYSTEM_INSTRUCTION;
        let profileAddendum = "";

        if (userProfile) {
          const profileLines = [];
          if (userProfile.name) {
            profileLines.push(`- Nombre de tu interlocutor/creador: ${userProfile.name}`);
          }
          if (userProfile.occupation) {
            profileLines.push(`- Ocupación/Actividad principal: ${userProfile.occupation}`);
          }
          if (Array.isArray(userProfile.facts)) {
            const validFacts = userProfile.facts.filter(f => f && f.trim());
            if (validFacts.length > 0) {
              profileLines.push("- Datos esenciales que debes tener siempre en cuenta en tus respuestas:");
              validFacts.forEach((fact, idx) => {
                profileLines.push(`  * Dato ${idx + 1}: ${fact.trim()}`);
              });
            }
          }

          if (profileLines.length > 0) {
            profileAddendum = `\n\n=== FICHA DE USUARIO (MEMORIA PERMANENTE) ===\n${profileLines.join("\n")}\nDebes adaptar tus respuestas y recomendaciones teniendo en cuenta estrictamente esta información en todo momento.\n=== FIN FICHA DE USUARIO ===`;
          }
        }

        return basePrompt + profileAddendum;
      }

      async function executeGeminiRequest(modelName, apiKey, history) {
        const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent?key=${apiKey}`;

        const payload = {
          system_instruction: {
            parts: [{ text: buildEffectiveSystemInstruction() }]
          },
          contents: history,
          generationConfig: {
            temperature: 0.75,
            maxOutputTokens: 3000
          }
        };

        let response;
        try {
          response = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
        } catch (netErr) {
          const customErr = new Error("No se pudo conectar con los servidores de Google (Fallo de red).");
          customErr.code = "NETWORK_ERROR";
          customErr.status = "FETCH_FAILED";
          customErr.modelUsed = modelName;
          customErr.googleMessage = `Fallo en fetch: ${netErr.name} - ${netErr.message}`;
          customErr.rawResponse = { error: { message: netErr.message, name: netErr.name } };
          throw customErr;
        }

        let data = {};
        try {
          data = await response.json();
        } catch (jsonErr) {
          data = { error: { message: "Respuesta no válida del servidor (no es JSON válido)." } };
        }

        if (!response.ok) {
          const rawMsg = data.error?.message || response.statusText || "Error en la llamada a la API";
          const err = new Error(rawMsg);
          err.code = data.error?.code || response.status;
          err.status = data.error?.status || response.statusText;
          err.modelUsed = modelName;
          err.googleMessage = data.error?.message || rawMsg;
          err.rawResponse = data;
          throw err;
        }

        const candidate = data.candidates?.[0];
        if (!candidate || !candidate.content?.parts?.[0]?.text) {
          if (candidate?.finishReason === "SAFETY") {
            const err = new Error("BLOCKED_BY_SAFETY");
            err.code = "SAFETY_FILTER";
            err.status = "BLOCKED";
            err.modelUsed = modelName;
            err.googleMessage = "La respuesta fue bloqueada por las políticas de seguridad de Google.";
            err.rawResponse = data;
            throw err;
          }
          const err = new Error("EMPTY_RESPONSE");
          err.code = "NO_CONTENT";
          err.status = "EMPTY";
          err.modelUsed = modelName;
          err.googleMessage = "Google devolvió una respuesta vacía sin texto.";
          err.rawResponse = data;
          throw err;
        }

        return candidate.content.parts[0].text;
      }

      // --- RENDERIZADO DE MENSAJES Y FORMATO ---

      function appendMessage(role, content, shouldScroll = true) {
        const row = document.createElement("div");
        row.className = `message-row ${role}`;

        const isAssistant = role === "assistant";

        const avatar = document.createElement("div");
        avatar.className = `avatar ${isAssistant ? "liseth" : "user-avatar"}`;
        avatar.textContent = isAssistant ? "L" : "S";

        const bubble = document.createElement("div");
        bubble.className = "bubble";

        const senderLabel = document.createElement("div");
        senderLabel.className = "bubble-sender";
        
        const nameSpan = document.createElement("span");
        nameSpan.textContent = isAssistant ? ASSISTANT_NAME : "Santiago";
        senderLabel.appendChild(nameSpan);

        if (isAssistant) {
          const actionsDiv = document.createElement("div");
          actionsDiv.className = "bubble-actions";
          actionsDiv.innerHTML = `
            <button class="bubble-action-btn speak-msg-btn" title="Escuchar este mensaje con voz humana">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
              </svg>
            </button>
          `;
          senderLabel.appendChild(actionsDiv);

          actionsDiv.querySelector(".speak-msg-btn").addEventListener("click", () => {
            speakText(content);
          });
        }

        bubble.appendChild(senderLabel);

        const textBody = document.createElement("div");
        textBody.className = "bubble-content";
        textBody.innerHTML = formatMarkdown(content);
        bubble.appendChild(textBody);

        if (isAssistant) {
          row.appendChild(avatar);
          row.appendChild(bubble);
        } else {
          row.appendChild(bubble);
          row.appendChild(avatar);
        }

        chatMessages.appendChild(row);

        // Configurar botones de copia
        bubble.querySelectorAll(".copy-btn").forEach(btn => {
          btn.addEventListener("click", () => {
            const code = btn.getAttribute("data-code");
            navigator.clipboard.writeText(decodeURIComponent(code)).then(() => {
              const orig = btn.textContent;
              btn.textContent = "¡Copiado!";
              btn.style.color = "var(--accent-blue)";
              setTimeout(() => {
                btn.textContent = orig;
                btn.style.color = "";
              }, 2000);
            });
          });
        });

        // Configurar botones interactivos de descarga de archivos modificados
        bubble.querySelectorAll(".download-code-btn").forEach(btn => {
          btn.addEventListener("click", () => {
            const rawCode = decodeURIComponent(btn.getAttribute("data-code") || "");
            const filename = decodeURIComponent(btn.getAttribute("data-filename") || "archivo_modificado.txt");
            downloadFileContent(rawCode, filename);
            const orig = btn.innerHTML;
            btn.innerHTML = `✓ ¡Descargado!`;
            setTimeout(() => { btn.innerHTML = orig; }, 2000);
          });
        });

        if (shouldScroll) scrollToBottom();
      }

      function showThinkingIndicator() {
        const row = document.createElement("div");
        row.className = "message-row assistant";
        row.id = "active-thinking-row";

        const avatar = document.createElement("div");
        avatar.className = "avatar liseth";
        avatar.textContent = "L";

        const card = document.createElement("div");
        card.className = "thinking-indicator";
        card.innerHTML = `
          <div class="wave-bars">
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
          </div>
          <span class="thinking-text">Liseth está analizando con suma agudeza...</span>
        `;

        row.appendChild(avatar);
        row.appendChild(card);
        chatMessages.appendChild(row);
        scrollToBottom();

        return row;
      }

      function renderErrorCard(error) {
        let title = "Inconveniente en la comunicación";
        let message = "Ha ocurrido un suceso inesperado al contactar con el núcleo de pensamiento.";
        let showKeyButton = false;

        const errMessage = (error.googleMessage || error.message || "").toLowerCase();
        const code = error.code || error.status;

        if (error.code === "NETWORK_ERROR") {
          title = "Sin conexión con Google";
          message = "Señor Santiago, no ha sido posible establecer comunicación con los servidores de Google. Le sugiero verificar su conexión a internet.";
        } else if (code === 400 || code === 403 || errMessage.includes("api key") || errMessage.includes("invalid")) {
          title = "Clave de Google Gemini no válida";
          message = "Señor Santiago, la clave de Google Gemini registrada no parece ser correcta o ha caducado. Por favor ingrese una nueva en el menú de ajustes.";
          showKeyButton = true;
        } else if (code === 429 || errMessage.includes("quota")) {
          title = "Límite de cuota gratuita alcanzado";
          message = "Se ha alcanzado temporalmente la cuota máxima que Google ofrece por minuto. Aguardemos un momento y reintente su instrucción.";
        } else {
          message = "Señor Santiago, el servicio devolvió una respuesta imprevista.";
          showKeyButton = true;
        }

        const techCode = `${error.code || "Desconocido"} (${error.status || "SIN_ESTADO"})`;
        const techMsg = error.googleMessage || error.message || "Sin mensaje explícito";
        const techModel = error.modelUsed ? `<div class="error-tech-item"><div class="error-tech-label">Modelo:</div><div>${error.modelUsed}</div></div>` : "";
        const rawJsonString = error.rawResponse ? JSON.stringify(error.rawResponse, null, 2) : "";

        const row = document.createElement("div");
        row.className = "message-row assistant";

        const avatar = document.createElement("div");
        avatar.className = "avatar liseth";
        avatar.textContent = "L";

        const bubble = document.createElement("div");
        bubble.className = "bubble";
        bubble.style.borderColor = "rgba(255, 92, 119, 0.4)";

        const errorDiv = document.createElement("div");
        errorDiv.className = "error-card";
        errorDiv.innerHTML = `
          <div class="error-header">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <span>${title}</span>
          </div>
          <div class="error-body">${message}</div>

          <div class="error-tech-info">
            <div class="error-tech-item">
              <div class="error-tech-label">Código devuelto:</div>
              <div>${techCode}</div>
            </div>
            <div class="error-tech-item">
              <div class="error-tech-label">Detalle técnico:</div>
              <div>${techMsg}</div>
            </div>
            ${techModel}
            ${rawJsonString ? `
              <details class="error-details-toggle">
                <summary>Ver JSON técnico completo &darr;</summary>
                <pre>${rawJsonString}</pre>
              </details>
            ` : ""}
          </div>

          ${showKeyButton ? `<button class="btn-fix-key" id="btn-fix-error-key">Modificar Clave de Gemini</button>` : ""}
        `;

        bubble.appendChild(errorDiv);
        row.appendChild(avatar);
        row.appendChild(bubble);
        chatMessages.appendChild(row);

        const btnFix = row.querySelector("#btn-fix-error-key");
        if (btnFix) btnFix.addEventListener("click", () => showModal(true));

        scrollToBottom();
      }

      function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
      }

      // ============================================================
      // SISTEMA INTEGRAL DE MEMORIA, CONVERSACIONES Y PERFIL
      // ============================================================

      function showToast(message, duration = 3500) {
        if (!lisethToast) return;
        lisethToast.textContent = message;
        lisethToast.classList.add("active");
        setTimeout(() => {
          lisethToast.classList.remove("active");
        }, duration);
      }

      function loadUserProfile() {
        try {
          const raw = localStorage.getItem(USER_PROFILE_KEY);
          if (raw) {
            const parsed = JSON.parse(raw);
            userProfile = {
              name: parsed.name || USER_NAME,
              occupation: parsed.occupation || "",
              facts: Array.isArray(parsed.facts) ? parsed.facts : ["", "", ""]
            };
          }
        } catch (e) {}

        if (profileNameInput) profileNameInput.value = userProfile.name || "";
        if (profileOccupationInput) profileOccupationInput.value = userProfile.occupation || "";
        if (profileFact1Input) profileFact1Input.value = userProfile.facts[0] || "";
        if (profileFact2Input) profileFact2Input.value = userProfile.facts[1] || "";
        if (profileFact3Input) profileFact3Input.value = userProfile.facts[2] || "";
      }

      function saveUserProfile() {
        try {
          userProfile = {
            name: (profileNameInput?.value || "").trim() || USER_NAME,
            occupation: (profileOccupationInput?.value || "").trim(),
            facts: [
              (profileFact1Input?.value || "").trim(),
              (profileFact2Input?.value || "").trim(),
              (profileFact3Input?.value || "").trim()
            ]
          };
          localStorage.setItem(USER_PROFILE_KEY, JSON.stringify(userProfile));
          showToast("✓ Ficha personal guardada. Liseth la recordará en cada respuesta.");
        } catch (e) {
          showToast("⚠️ No se pudo guardar la ficha personal");
        }
      }

      // Migración hacia el nuevo sistema multi-conversación
      function migrateLegacyHistoryIfNeeded() {
        try {
          const legacy = localStorage.getItem(HISTORY_KEY);
          const currentMeta = localStorage.getItem(CONVERSATIONS_KEY);
          if (legacy && (!currentMeta || JSON.parse(currentMeta).length === 0)) {
            const parsed = JSON.parse(legacy);
            if (Array.isArray(parsed) && parsed.length > 0) {
              const legacyId = "conv_migrada_" + Date.now();
              const firstUserMsg = parsed.find(t => t.role === "user")?.parts?.[0]?.text || "Conversación anterior";
              const title = firstUserMsg.slice(0, 48) + (firstUserMsg.length > 48 ? "..." : "");
              const now = new Date().toISOString();
              const meta = [{
                id: legacyId,
                title: title,
                createdAt: now,
                updatedAt: now,
                messageCount: parsed.length
              }];
              localStorage.setItem(CONVERSATIONS_KEY, JSON.stringify(meta));
              localStorage.setItem(CONV_PREFIX + legacyId, JSON.stringify(parsed));
              localStorage.setItem(ACTIVE_CONV_KEY, legacyId);
            }
          }
        } catch (e) {}
      }

      function getStoredConversationsMeta() {
        try {
          const raw = localStorage.getItem(CONVERSATIONS_KEY);
          if (raw) {
            const list = JSON.parse(raw);
            if (Array.isArray(list)) return list;
          }
        } catch (e) {}
        return [];
      }

      function saveStoredConversationsMeta(list) {
        try {
          localStorage.setItem(CONVERSATIONS_KEY, JSON.stringify(list));
        } catch (e) {}
      }

      function loadSavedChat() {
        migrateLegacyHistoryIfNeeded();
        conversationsList = getStoredConversationsMeta();
        activeConversationId = localStorage.getItem(ACTIVE_CONV_KEY);

        // Si no hay id activo o el id no existe en la lista, tomar el primero o crear uno nuevo
        const activeMeta = conversationsList.find(c => c.id === activeConversationId);
        if (!activeMeta && conversationsList.length > 0) {
          activeConversationId = conversationsList[0].id;
          localStorage.setItem(ACTIVE_CONV_KEY, activeConversationId);
        }

        if (activeConversationId) {
          try {
            const rawConv = localStorage.getItem(CONV_PREFIX + activeConversationId);
            if (rawConv) {
              const list = JSON.parse(rawConv);
              if (Array.isArray(list) && list.length > 0) {
                conversationHistory = list;
                chatMessages.innerHTML = "";
                conversationHistory.forEach(turn => {
                  const role = turn.role === "model" ? "assistant" : "user";
                  const text = turn.parts?.[0]?.text || "";
                  if (text) appendMessage(role, text, false);
                });
                scrollToBottom();
                return;
              }
            }
          } catch (e) {}
        }

        // Si aún no hay mensajes en pantalla ni conversación activa
        conversationHistory = [];
        if (chatMessages.children.length === 0) {
          renderInitialGreeting();
        }
      }

      function saveChatHistory() {
        try {
          if (!activeConversationId) {
            activeConversationId = "conv_" + Date.now();
            localStorage.setItem(ACTIVE_CONV_KEY, activeConversationId);
          }

          // Guardar mensajes de la conversación activa
          localStorage.setItem(CONV_PREFIX + activeConversationId, JSON.stringify(conversationHistory));

          // Actualizar lista de metadatos
          conversationsList = getStoredConversationsMeta();
          let meta = conversationsList.find(c => c.id === activeConversationId);
          const now = new Date().toISOString();

          // Generar título a partir del primer mensaje del usuario si no tiene uno descriptivo
          let title = "Conversación";
          const firstUserMsg = conversationHistory.find(t => t.role === "user")?.parts?.[0]?.text;
          if (firstUserMsg) {
            title = firstUserMsg.replace(/[\n\r]+/g, " ").trim().slice(0, 48);
            if (firstUserMsg.length > 48) title += "...";
          }

          if (!meta) {
            meta = {
              id: activeConversationId,
              title: title,
              createdAt: now,
              updatedAt: now,
              messageCount: conversationHistory.length
            };
            conversationsList.unshift(meta);
          } else {
            meta.updatedAt = now;
            meta.messageCount = conversationHistory.length;
            if (meta.title === "Conversación" && firstUserMsg) {
              meta.title = title;
            }
            // Mover al principio por ser la más reciente
            conversationsList = [meta, ...conversationsList.filter(c => c.id !== activeConversationId)];
          }

          saveStoredConversationsMeta(conversationsList);
          updateStorageMeter();
        } catch (e) {
          checkStorageQuota(true);
        }
      }

      function startNewConversation() {
        conversationHistory = [];
        activeConversationId = "conv_" + Date.now();
        localStorage.setItem(ACTIVE_CONV_KEY, activeConversationId);

        chatMessages.innerHTML = "";
        renderInitialGreeting();
        renderConversationsList();
        showToast("✓ Nueva conversación iniciada.");
      }

      function switchToConversation(convId) {
        if (convId === activeConversationId && conversationHistory.length > 0) return;

        saveChatHistory();
        activeConversationId = convId;
        localStorage.setItem(ACTIVE_CONV_KEY, convId);

        try {
          const raw = localStorage.getItem(CONV_PREFIX + convId);
          chatMessages.innerHTML = "";
          if (raw) {
            const list = JSON.parse(raw);
            if (Array.isArray(list) && list.length > 0) {
              conversationHistory = list;
              conversationHistory.forEach(turn => {
                const role = turn.role === "model" ? "assistant" : "user";
                const text = turn.parts?.[0]?.text || "";
                if (text) appendMessage(role, text, false);
              });
              scrollToBottom();
              renderConversationsList();
              return;
            }
          }
        } catch (e) {}

        conversationHistory = [];
        renderInitialGreeting();
        renderConversationsList();
      }

      function deleteConversation(convId, event) {
        if (event) event.stopPropagation();

        if (!confirm("¿Está seguro de eliminar esta conversación de su memoria local, Santiago?")) {
          return;
        }

        try {
          localStorage.removeItem(CONV_PREFIX + convId);
          conversationsList = getStoredConversationsMeta().filter(c => c.id !== convId);
          saveStoredConversationsMeta(conversationsList);

          if (activeConversationId === convId) {
            if (conversationsList.length > 0) {
              switchToConversation(conversationsList[0].id);
            } else {
              startNewConversation();
            }
          } else {
            renderConversationsList();
          }

          updateStorageMeter();
          showToast("✓ Conversación eliminada de la memoria local.");
        } catch (e) {}
      }

      function formatDate(isoStr) {
        if (!isoStr) return "";
        try {
          const d = new Date(isoStr);
          const now = new Date();
          const diffDays = Math.floor((now - d) / (1000 * 60 * 60 * 24));
          const timeStr = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

          if (diffDays === 0) return `Hoy, ${timeStr}`;
          if (diffDays === 1) return `Ayer, ${timeStr}`;
          if (diffDays < 7) return `Hace ${diffDays} días`;
          return d.toLocaleDateString([], { day: '2-digit', month: 'short' });
        } catch (e) {
          return "";
        }
      }

      function renderConversationsList() {
        if (!conversationsListContainer) return;
        conversationsListContainer.innerHTML = "";
        conversationsList = getStoredConversationsMeta();

        if (conversationsList.length === 0) {
          conversationsListContainer.innerHTML = `
            <div style="text-align: center; padding: 24px 10px; color: var(--text-muted); font-size: 0.85rem;">
              No hay conversaciones archivadas aún.
            </div>
          `;
          return;
        }

        conversationsList.forEach(conv => {
          const item = document.createElement("div");
          item.className = "conv-item" + (conv.id === activeConversationId ? " active" : "");

          const isActive = conv.id === activeConversationId;
          item.innerHTML = `
            <div class="conv-item-info">
              <div class="conv-item-title" title="${conv.title || 'Conversación'}">
                ${isActive ? '<span class="conv-active-dot"></span> ' : ''}${conv.title || 'Conversación'}
              </div>
              <div class="conv-item-meta">
                <span>📅 ${formatDate(conv.updatedAt || conv.createdAt)}</span>
                <span>• ${conv.messageCount || 0} turnos</span>
              </div>
            </div>
            <button class="conv-del-btn" title="Eliminar conversación" type="button">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              </svg>
            </button>
          `;

          item.addEventListener("click", () => {
            switchToConversation(conv.id);
            conversationsModal.classList.remove("active");
          });

          item.querySelector(".conv-del-btn").addEventListener("click", (e) => {
            deleteConversation(conv.id, e);
          });

          conversationsListContainer.appendChild(item);
        });
      }

      // --- RESUMEN INTELIGENTE PARA CONVERSACIONES EXTENSAS ---
      async function prepareHistoryWithSummary(apiKey, rawHistory) {
        // Umbral de 30 mensajes para activar compresión de memoria antigua
        if (rawHistory.length <= 30) {
          return rawHistory;
        }

        try {
          showToast("🧠 Resumiendo memoria antigua para optimizar cuota...", 3000);
          
          // Tomar los primeros 20 mensajes para resumir
          const toSummarize = rawHistory.slice(0, 20);
          const recentMessages = rawHistory.slice(20);

          let dialogueText = "";
          toSummarize.forEach(t => {
            const role = t.role === "model" ? ASSISTANT_NAME : (userProfile?.name || "Santiago");
            const txt = t.parts?.[0]?.text || "";
            if (txt) {
              dialogueText += `${role}: ${txt.slice(0, 400)}\n`;
            }
          });

          const summaryPrompt = [
            {
              role: "user",
              parts: [{
                text: `Genera un resumen sumamente conciso, estructurado y claro (máximo 200 palabras) de la siguiente conversación previa, extrayendo acuerdos, datos del usuario, tareas realizadas y temas clave discutidos:\n\n${dialogueText}`
              }]
            }
          ];

          // Llamada directa sin reintentar recursivamente
          const summaryResponse = await executeGeminiRequest("gemini-2.0-flash", apiKey, summaryPrompt);
          const cleanSummary = summaryResponse ? summaryResponse.trim() : "Historial previo resumido con éxito.";

          showToast("✓ Memoria previa resumida sin tocar su pantalla.");

          return [
            {
              role: "model",
              parts: [{ text: `[Resumen de la conversación anterior]: ${cleanSummary}` }]
            },
            ...recentMessages
          ];
        } catch (sumErr) {
          console.warn("No fue posible generar el resumen intermedio, continuando con recorte estándar:", sumErr);
          // Si falla el resumen, recortar para no romper la petición
          return rawHistory.slice(-25);
        }
      }

      // --- BÚSQUEDA GLOBAL EN CONVERSACIONES ---
      function searchAcrossConversations(query) {
        if (!searchResultsContainer) return;
        const q = (query || "").trim().toLowerCase();
        if (q.length < 2) {
          searchResultsContainer.innerHTML = `
            <div class="search-empty-state">Ingrese al menos 2 caracteres para buscar en sus conversaciones pasadas.</div>
          `;
          return;
        }

        const metas = getStoredConversationsMeta();
        const results = [];

        metas.forEach(meta => {
          try {
            const raw = localStorage.getItem(CONV_PREFIX + meta.id);
            if (raw) {
              const messages = JSON.parse(raw);
              if (Array.isArray(messages)) {
                const matches = [];
                messages.forEach((turn, idx) => {
                  const text = turn.parts?.[0]?.text || "";
                  if (text.toLowerCase().includes(q)) {
                    matches.push({
                      index: idx,
                      role: turn.role === "model" ? ASSISTANT_NAME : (userProfile?.name || "Santiago"),
                      text: text
                    });
                  }
                });

                if (matches.length > 0) {
                  results.push({
                    meta: meta,
                    matches: matches
                  });
                }
              }
            }
          } catch (e) {}
        });

        if (results.length === 0) {
          searchResultsContainer.innerHTML = `
            <div class="search-empty-state">No se encontraron menciones de "<strong>${escapeHtml(query)}</strong>" en sus conversaciones.</div>
          `;
          return;
        }

        let totalMatches = results.reduce((acc, r) => acc + r.matches.length, 0);
        let html = `<div class="search-count-header">${totalMatches} resultado(s) encontrado(s) en ${results.length} conversación(es)</div>`;

        results.forEach(res => {
          html += `
            <div class="search-conv-group">
              <div class="search-conv-header" data-conv-id="${res.meta.id}">
                <span class="search-conv-title">${escapeHtml(res.meta.title || 'Conversación')}</span>
                <span class="search-conv-meta">📅 ${formatDate(res.meta.updatedAt)}</span>
              </div>
              <div class="search-conv-body">
                ${res.matches.map(m => {
                  const highlighted = highlightMatch(m.text, q);
                  return `
                    <div class="search-match-item" data-conv-id="${res.meta.id}" data-msg-idx="${m.index}">
                      <div class="search-match-role">${escapeHtml(m.role)}</div>
                      <div class="search-match-text">${highlighted}</div>
                    </div>
                  `;
                }).join("")}
              </div>
            </div>
          `;
        });

        searchResultsContainer.innerHTML = html;

        // Añadir manejadores para saltar a la conversación y al mensaje
        searchResultsContainer.querySelectorAll(".search-match-item, .search-conv-header").forEach(el => {
          el.addEventListener("click", () => {
            const convId = el.getAttribute("data-conv-id");
            const msgIdx = parseInt(el.getAttribute("data-msg-idx") || "0");
            switchToConversation(convId);
            searchModal.classList.remove("active");

            // Si se seleccionó un mensaje puntual, resaltar
            setTimeout(() => {
              const rows = chatMessages.querySelectorAll(".message-row");
              if (rows && rows[msgIdx]) {
                rows[msgIdx].scrollIntoView({ behavior: "smooth", block: "center" });
                rows[msgIdx].classList.add("highlight-pulse");
                setTimeout(() => rows[msgIdx].classList.remove("highlight-pulse"), 2500);
              }
            }, 300);
          });
        });
      }

      function escapeHtml(str) {
        if (!str) return "";
        return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
      }

      function highlightMatch(fullText, query) {
        const lower = fullText.toLowerCase();
        const qIndex = lower.indexOf(query);
        if (qIndex === -1) return escapeHtml(fullText.slice(0, 140)) + "...";

        const start = Math.max(0, qIndex - 40);
        const end = Math.min(fullText.length, qIndex + query.length + 60);
        const snippet = fullText.slice(start, end);

        const escapedSnippet = escapeHtml(snippet);
        const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        return (start > 0 ? "..." : "") + escapedSnippet.replace(regex, '<span class="search-highlight">$1</span>') + (end < fullText.length ? "..." : "");
      }

      // --- EXPORTAR E IMPORTAR MEMORIA COMPLETA ---
      function exportEntireMemory() {
        try {
          saveChatHistory();
          const memoryDump = {
            version: "1.0",
            exportedAt: new Date().toISOString(),
            userProfile: userProfile,
            voiceSettings: voiceSettings,
            conversationsMeta: getStoredConversationsMeta(),
            conversationsData: {}
          };

          memoryDump.conversationsMeta.forEach(m => {
            try {
              const raw = localStorage.getItem(CONV_PREFIX + m.id);
              if (raw) memoryDump.conversationsData[m.id] = JSON.parse(raw);
            } catch (e) {}
          });

          const blob = new Blob([JSON.stringify(memoryDump, null, 2)], { type: "application/json" });
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          const dateStr = new Date().toISOString().split("T")[0];
          a.href = url;
          a.download = `liseth_memoria_${dateStr}.json`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);

          showToast("✓ Archivo de memoria exportado con éxito.");
        } catch (e) {
          alert("Error al exportar la memoria: " + e.message);
        }
      }

      function importEntireMemory(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const dump = JSON.parse(e.target.result);
            if (!dump || (!dump.conversationsMeta && !dump.userProfile)) {
              throw new Error("El archivo no tiene el formato de memoria válido de Liseth.");
            }

            if (!confirm("Al importar, se restaurarán sus conversaciones y perfil. ¿Desea continuar?")) {
              return;
            }

            // Restaurar perfil
            if (dump.userProfile) {
              userProfile = dump.userProfile;
              localStorage.setItem(USER_PROFILE_KEY, JSON.stringify(userProfile));
              loadUserProfile();
            }

            // Restaurar configuración de voz
            if (dump.voiceSettings) {
              voiceSettings = dump.voiceSettings;
              localStorage.setItem(VOICE_SETTINGS_KEY, JSON.stringify(voiceSettings));
              updateVoiceUI();
            }

            // Restaurar conversaciones
            if (Array.isArray(dump.conversationsMeta)) {
              saveStoredConversationsMeta(dump.conversationsMeta);
            }
            if (dump.conversationsData) {
              Object.keys(dump.conversationsData).forEach(convId => {
                localStorage.setItem(CONV_PREFIX + convId, JSON.stringify(dump.conversationsData[convId]));
              });
            }

            loadSavedChat();
            renderConversationsList();
            updateStorageMeter();
            showToast("✓ Memoria importada y restaurada exitosamente.");
            conversationsModal.classList.remove("active");
          } catch (err) {
            alert("No se pudo cargar la memoria: " + err.message);
          }
        };
        reader.readAsText(file);
      }

      // --- MONITOR DE ALMACENAMIENTO Y CUOTA ---
      function calculateLocalStorageBytes() {
        let total = 0;
        try {
          for (let key in localStorage) {
            if (localStorage.hasOwnProperty(key)) {
              total += (key.length + (localStorage[key]?.length || 0)) * 2; // UTF-16
            }
          }
        } catch (e) {}
        return total;
      }

      function updateStorageMeter() {
        const bytes = calculateLocalStorageBytes();
        const mb = (bytes / (1024 * 1024)).toFixed(2);
        const limitMb = 5.0;
        const pct = Math.min(100, Math.round((bytes / (limitMb * 1024 * 1024)) * 100));

        if (storageUsageText) {
          storageUsageText.textContent = `${mb} MB / ${limitMb.toFixed(1)} MB (${pct}%)`;
        }

        if (storageProgressFill) {
          storageProgressFill.style.width = pct + "%";
          if (pct >= 80) {
            storageProgressFill.classList.add("warn");
          } else {
            storageProgressFill.classList.remove("warn");
          }
        }

        // Si supera el 80% (4MB aprox), activar aviso en pantalla principal
        if (pct >= 80) {
          if (storageWarningBanner) {
            storageWarningBanner.style.display = "flex";
            if (storageWarningMb) storageWarningMb.textContent = mb;
          }
        } else {
          if (storageWarningBanner) {
            storageWarningBanner.style.display = "none";
          }
        }
      }

      function checkStorageQuota(isWarning = false) {
        updateStorageMeter();
        if (isWarning) {
          alert("Aviso de memoria: El espacio de almacenamiento del navegador está cerca de llenarse. Le recomendamos exportar una copia de seguridad y eliminar conversaciones que ya no requiera.");
        }
      }

      // --- CONFIGURACIÓN DE MANEJADORES DE EVENTOS DE MEMORIA ---
      function setupMemoryHandlers() {
        // Botones superiores
        if (btnConvList) {
          btnConvList.addEventListener("click", () => {
            renderConversationsList();
            updateStorageMeter();
            conversationsModal.classList.add("active");
          });
        }
        if (btnCloseConvs) {
          btnCloseConvs.addEventListener("click", () => {
            conversationsModal.classList.remove("active");
          });
        }

        if (btnUserProfile) {
          btnUserProfile.addEventListener("click", () => {
            loadUserProfile();
            profileModal.classList.add("active");
          });
        }
        if (btnCloseProfile) {
          btnCloseProfile.addEventListener("click", () => {
            profileModal.classList.remove("active");
          });
        }
        if (btnSaveProfile) {
          btnSaveProfile.addEventListener("click", () => {
            saveUserProfile();
            profileModal.classList.remove("active");
          });
        }

        if (btnSearchConvs) {
          btnSearchConvs.addEventListener("click", () => {
            searchModal.classList.add("active");
            if (searchQueryInput) {
              searchQueryInput.value = "";
              searchAcrossConversations("");
              setTimeout(() => searchQueryInput.focus(), 150);
            }
          });
        }
        if (btnCloseSearch) {
          btnCloseSearch.addEventListener("click", () => {
            searchModal.classList.remove("active");
          });
        }
        if (searchQueryInput) {
          searchQueryInput.addEventListener("input", (e) => {
            searchAcrossConversations(e.target.value);
          });
        }

        if (btnNewConversation) {
          btnNewConversation.addEventListener("click", () => {
            startNewConversation();
            conversationsModal.classList.remove("active");
          });
        }

        // Exportar e Importar
        if (btnExportMemory) {
          btnExportMemory.addEventListener("click", exportEntireMemory);
        }
        if (btnWarningExport) {
          btnWarningExport.addEventListener("click", exportEntireMemory);
        }
        if (btnImportMemory && importMemoryFile) {
          btnImportMemory.addEventListener("click", () => {
            importMemoryFile.click();
          });
          importMemoryFile.addEventListener("change", (e) => {
            if (e.target.files && e.target.files.length > 0) {
              importEntireMemory(e.target.files[0]);
              importMemoryFile.value = "";
            }
          });
        }

        // Manejadores de Jarvis v2 (Dashboard, BrainRouter, Auditoría)
        setupJarvisV2Handlers();
      }

      function setupJarvisV2Handlers() {
        const btnServicesDashboard = document.getElementById("btn-services-dashboard");
        const dashboardModal = document.getElementById("dashboard-modal");
        const btnCloseDashboard = document.getElementById("btn-close-dashboard");
        const btnConnectGoogle = document.getElementById("btn-connect-google");
        const googleStatusPill = document.getElementById("google-status-pill");
        const btnTestWa = document.getElementById("btn-test-wa");
        const btnTestTg = document.getElementById("btn-test-tg");

        const btnBrainRouter = document.getElementById("btn-brain-router");
        const brainModal = document.getElementById("brain-modal");
        const btnCloseBrain = document.getElementById("btn-close-brain");
        const btnSelectGemini = document.getElementById("btn-select-gemini");
        const btnSelectClaude = document.getElementById("btn-select-claude");
        const btnSelectAuto = document.getElementById("btn-select-auto");

        const btnAuditLogs = document.getElementById("btn-audit-logs");
        const auditModal = document.getElementById("audit-modal");
        const btnCloseAudit = document.getElementById("btn-close-audit");

        // Abrir Dashboard
        if (btnServicesDashboard) {
          btnServicesDashboard.addEventListener("click", async () => {
            dashboardModal.classList.add("active");
            try {
              const res = await fetch("/api/google/status");
              if (res.ok) {
                const data = await res.json();
                if (data.connected && googleStatusPill) {
                  googleStatusPill.textContent = "Conectado";
                  googleStatusPill.style.background = "rgba(56, 239, 125, 0.2)";
                  googleStatusPill.style.color = "#38ef7d";
                }
              }
            } catch(e) {}
          });
        }
        if (btnCloseDashboard) {
          btnCloseDashboard.addEventListener("click", () => dashboardModal.classList.remove("active"));
        }

        if (btnConnectGoogle) {
          btnConnectGoogle.addEventListener("click", async () => {
            try {
              const res = await fetch("/api/google/auth-url");
              if (res.ok) {
                const data = await res.json();
                if (data.authUrl) window.open(data.authUrl, "_blank", "width=600,height=700");
              } else {
                alert("Configure GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET en su archivo .env para iniciar la vinculación.");
              }
            } catch(e) {
              alert("Inicie el servidor local para conectar Google Workspace.");
            }
          });
        }

        if (btnTestWa) {
          btnTestWa.addEventListener("click", async () => {
            const res = await fetch("/api/notifications/test", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ message: "Prueba de alerta proactiva enviada a su WhatsApp desde JARVIS." })
            });
            showToast("Prueba de WhatsApp enviada.");
          });
        }

        if (btnTestTg) {
          btnTestTg.addEventListener("click", async () => {
            const res = await fetch("/api/notifications/test", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ message: "Prueba de alerta proactiva enviada a su Telegram desde JARVIS." })
            });
            showToast("Prueba de Telegram enviada.");
          });
        }

        // BrainRouter
        if (btnBrainRouter) {
          btnBrainRouter.addEventListener("click", async () => {
            brainModal.classList.add("active");
            updateBrainModalStats();
          });
        }
        if (btnCloseBrain) {
          btnCloseBrain.addEventListener("click", () => brainModal.classList.remove("active"));
        }

        async function switchBrain(target) {
          try {
            await fetch("/api/brain/switch", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ brain: target })
            });
            updateBrainModalStats();
            showToast(`Cerebro activo configurado en: ${target ? target.toUpperCase() : 'AUTOMÁTICO'}`);
          } catch(e) {}
        }

        if (btnSelectGemini) btnSelectGemini.addEventListener("click", () => switchBrain('gemini'));
        if (btnSelectClaude) btnSelectClaude.addEventListener("click", () => switchBrain('claude'));
        if (btnSelectAuto) btnSelectAuto.addEventListener("click", () => switchBrain(null));

        async function updateBrainModalStats() {
          try {
            const res = await fetch("/api/brain/status");
            if (res.ok) {
              const data = await res.json();
              const todayTokens = (data.stats?.today?.input || 0) + (data.stats?.today?.output || 0);
              const limit = data.limits?.dailyTokenLimit || 100000;
              const pct = Math.min(100, Math.round((todayTokens / limit) * 100));

              document.getElementById("token-usage-today").textContent = `${todayTokens.toLocaleString()} / ${limit.toLocaleString()} Tokens (${pct}%)`;
              const fillEl = document.getElementById("token-progress-fill");
              fillEl.style.width = pct + "%";
              if (pct >= 100) {
                fillEl.style.background = "linear-gradient(90deg, #ff4d6d, #ff758f)";
              } else if (pct >= 80) {
                fillEl.style.background = "linear-gradient(90deg, #ffaa00, #ffd166)";
              } else {
                fillEl.style.background = "linear-gradient(90deg, var(--accent-pink), var(--accent-cyan))";
              }

              document.getElementById("stat-tokens-in").textContent = (data.stats?.today?.input || 0).toLocaleString();
              document.getElementById("stat-tokens-out").textContent = (data.stats?.today?.output || 0).toLocaleString();

              // Modelos
              if (data.models) {
                const elG = document.getElementById("model-gemini-name");
                if (elG) elG.textContent = data.models.gemini || 'gemini-2.0-flash';
                const elC = document.getElementById("model-claude-name");
                if (elC) elC.textContent = data.models.claude || 'claude-3-5-sonnet';
              }

              // Costes
              if (data.costs) {
                const elCostToday = document.getElementById("stat-cost-today");
                if (elCostToday) elCostToday.textContent = `$${(data.costs.todayUSD || 0).toFixed(4)} USD`;
                const elCostMonth = document.getElementById("stat-cost-month");
                if (elCostMonth) elCostMonth.textContent = `$${(data.costs.monthUSD || 0).toFixed(4)} USD`;
                const elCostGem = document.getElementById("stat-cost-gemini");
                if (elCostGem) elCostGem.textContent = `$${(data.costs.byBrain?.gemini?.costEstimate || 0).toFixed(4)}`;
                const elCostCla = document.getElementById("stat-cost-claude");
                if (elCostCla) elCostCla.textContent = `$${(data.costs.byBrain?.claude?.costEstimate || 0).toFixed(4)}`;
              }

              // Alerta de límite excedido
              const limitAlertBox = document.getElementById("token-limit-alert-box");
              if (limitAlertBox) {
                limitAlertBox.style.display = todayTokens >= limit ? "block" : "none";
              }

              // Resaltar botón activo
              [btnSelectGemini, btnSelectClaude, btnSelectAuto].forEach(b => b && b.classList.remove("active"));
              if (data.forcedBrain === 'gemini') btnSelectGemini?.classList.add("active");
              else if (data.forcedBrain === 'claude') btnSelectClaude?.classList.add("active");
              else btnSelectAuto?.classList.add("active");

              if (data.lastFailover) {
                const box = document.getElementById("failover-alert-box");
                if (box) {
                  box.style.display = "block";
                  box.textContent = `Aviso Failover: Conmutado a ${data.lastFailover.to.toUpperCase()} por ${data.lastFailover.reason}`;
                }
              }
            }
          } catch(e) {}
        }

        // Auditoría
        if (btnAuditLogs) {
          btnAuditLogs.addEventListener("click", async () => {
            auditModal.classList.add("active");
            loadAuditLogs();
          });
        }
        if (btnCloseAudit) {
          btnCloseAudit.addEventListener("click", () => auditModal.classList.remove("active"));
        }

        async function loadAuditLogs() {
          try {
            const res = await fetch("/api/audit/logs");
            if (res.ok) {
              const data = await res.json();
              const container = document.getElementById("audit-log-container");
              if (!container) return;

              if (data.logs.length === 0) {
                container.innerHTML = `<div style="text-align: center; padding: 20px; color: var(--text-muted); font-size: 0.85rem;">No hay registros de auditoría aún.</div>`;
              } else {
                container.innerHTML = data.logs.map(l => `
                  <div class="conv-item" style="cursor: default;">
                    <div class="conv-item-info">
                      <div class="conv-item-title">${escapeHtml(l.action)} [${l.connector}]</div>
                      <div class="conv-item-meta">
                        <span>Estado: <strong>${l.status}</strong></span> • 
                        <span>${new Date(l.timestamp).toLocaleTimeString()}</span>
                      </div>
                    </div>
                  </div>
                `).join("");
              }
            }
          } catch(e) {}
        }

        // --- SISTEMA HUD FUTURISTA DE INTERFACES & SCHEDULER ---
        setupHudDeckAndScheduler();

        function setupHudDeckAndScheduler() {
          const btnHudMenu = document.getElementById("btn-hud-menu");
          const hudModal = document.getElementById("hud-interfaces-modal");
          const btnCloseHud = document.getElementById("btn-close-hud");

          // Sintetizador Web Audio API para efectos de sonido HUD
          function playHudSound(type) {
            try {
              const AudioCtx = window.AudioContext || window.webkitAudioContext;
              if (!AudioCtx) return;
              const ctx = new AudioCtx();
              const now = ctx.currentTime;

              if (type === "open") {
                const osc1 = ctx.createOscillator();
                const osc2 = ctx.createOscillator();
                const gain = ctx.createGain();
                osc1.type = "sine";
                osc2.type = "triangle";
                osc1.frequency.setValueAtTime(440, now);
                osc1.frequency.exponentialRampToValueAtTime(880, now + 0.12);
                osc1.frequency.exponentialRampToValueAtTime(1320, now + 0.24);
                osc2.frequency.setValueAtTime(220, now);
                osc2.frequency.exponentialRampToValueAtTime(660, now + 0.24);
                gain.gain.setValueAtTime(0.08, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
                osc1.connect(gain);
                osc2.connect(gain);
                gain.connect(ctx.destination);
                osc1.start(now);
                osc2.start(now);
                osc1.stop(now + 0.35);
                osc2.stop(now + 0.35);
              } else if (type === "click") {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = "sine";
                osc.frequency.setValueAtTime(980, now);
                osc.frequency.exponentialRampToValueAtTime(1400, now + 0.06);
                gain.gain.setValueAtTime(0.06, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start(now);
                osc.stop(now + 0.08);
              } else if (type === "close") {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = "sine";
                osc.frequency.setValueAtTime(880, now);
                osc.frequency.exponentialRampToValueAtTime(320, now + 0.15);
                gain.gain.setValueAtTime(0.05, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start(now);
                osc.stop(now + 0.18);
              }
            } catch(e) {}
          }

          async function updateHudTelemetry() {
            try {
              const bRes = await fetch("/api/brain/status");
              if (bRes.ok) {
                const bData = await bRes.json();
                const elBrain = document.getElementById("hud-telemetry-brain");
                if (elBrain) {
                  const bName = bData.forcedBrain || bData.activeBrain || "gemini";
                  const modelName = bData.models ? (bData.models[bName] || bName) : bName;
                  elBrain.textContent = `${bName.toUpperCase()} (${modelName})`;
                }
                const todayTokens = (bData.stats?.today?.input || 0) + (bData.stats?.today?.output || 0);
                const limit = bData.limits?.dailyTokenLimit || 100000;
                const elTok = document.getElementById("hud-telemetry-tokens");
                if (elTok) elTok.textContent = `${todayTokens.toLocaleString()} / ${(limit/1000).toFixed(0)}k`;
                const elCost = document.getElementById("hud-telemetry-cost");
                if (elCost) elCost.textContent = `$${(bData.costs?.todayUSD || 0).toFixed(4)} USD`;
              }
            } catch(e) {}

            try {
              const sRes = await fetch("/api/scheduler/tasks");
              if (sRes.ok) {
                const sData = await sRes.json();
                const elTasks = document.getElementById("hud-telemetry-tasks");
                if (elTasks && Array.isArray(sData.tasks)) {
                  elTasks.textContent = `${sData.tasks.filter(t => t.enabled).length} Activas`;
                }
              }
            } catch(e) {}
          }

          if (btnHudMenu && hudModal) {
            btnHudMenu.addEventListener("click", () => {
              playHudSound("open");
              hudModal.classList.add("active");
              updateHudTelemetry();
            });
          }

          if (btnCloseHud && hudModal) {
            btnCloseHud.addEventListener("click", () => {
              playHudSound("close");
              hudModal.classList.remove("active");
            });
          }

          // Filtro por pestañas de categoría en el HUD
          const hudTabs = document.querySelectorAll(".hud-filter-tabs .hud-tab");
          const hudCards = document.querySelectorAll(".hud-modules-grid .hud-card");

          hudTabs.forEach(tab => {
            tab.addEventListener("click", () => {
              playHudSound("click");
              hudTabs.forEach(t => t.classList.remove("active"));
              tab.classList.add("active");
              const filter = tab.getAttribute("data-filter");

              hudCards.forEach(card => {
                const cat = card.getAttribute("data-category");
                if (filter === "all" || cat === filter) {
                  card.style.display = "flex";
                  card.style.animation = "none";
                  void card.offsetWidth;
                  card.style.animation = "hudCardDeploy 0.35s cubic-bezier(0.16, 1, 0.3, 1) backwards";
                } else {
                  card.style.display = "none";
                }
              });
            });
          });

          // Enlace de cada tarjeta a su interfaz correspondiente
          function bindHudCard(cardId, targetModalId, onOpenCallback) {
            const card = document.getElementById(cardId);
            const modal = document.getElementById(targetModalId);
            if (card && modal) {
              card.addEventListener("click", () => {
                playHudSound("click");
                hudModal.classList.remove("active");
                modal.classList.add("active");
                if (typeof onOpenCallback === "function") onOpenCallback();
              });
            }
          }

          bindHudCard("hud-card-brain", "brain-modal", () => updateBrainModalStats());
          bindHudCard("hud-card-google", "google-modal");
          bindHudCard("hud-card-services", "dashboard-modal");
          bindHudCard("hud-card-scheduler", "scheduler-modal", () => loadSchedulerTasks());
          bindHudCard("hud-card-audit", "audit-modal", () => loadAuditLogs());
          bindHudCard("hud-card-productivity", "productivity-modal");
          bindHudCard("hud-card-convs", "conversations-modal", () => {
            renderConversationsList();
            updateStorageMeter();
          });
          bindHudCard("hud-card-search", "search-modal", () => {
            if (searchQueryInput) {
              searchQueryInput.value = "";
              searchAcrossConversations("");
              setTimeout(() => searchQueryInput.focus(), 150);
            }
          });
          bindHudCard("hud-card-profile", "profile-modal", () => loadUserProfile());
          bindHudCard("hud-card-settings", "api-modal", () => showModal(true));

          // Manejadores del Programador de Tareas (TaskScheduler)
          const schedulerModal = document.getElementById("scheduler-modal");
          const btnCloseScheduler = document.getElementById("btn-close-scheduler");
          const btnRefreshScheduler = document.getElementById("btn-refresh-scheduler");
          const btnTriggerMorning = document.getElementById("btn-trigger-morning-report");
          const btnTriggerCalendar = document.getElementById("btn-trigger-calendar-check");
          const schedulerTaskList = document.getElementById("scheduler-task-list");
          const schedulerTaskCount = document.getElementById("scheduler-task-count");

          if (btnCloseScheduler && schedulerModal) {
            btnCloseScheduler.addEventListener("click", () => schedulerModal.classList.remove("active"));
          }
          if (btnRefreshScheduler) {
            btnRefreshScheduler.addEventListener("click", () => {
              playHudSound("click");
              loadSchedulerTasks();
            });
          }

          async function loadSchedulerTasks() {
            if (!schedulerTaskList) return;
            try {
              schedulerTaskList.innerHTML = `<div style="text-align: center; padding: 20px; color: var(--text-muted); font-size: 0.85rem;">Consultando tareas en data/scheduler_tasks.json...</div>`;
              const res = await fetch("/api/scheduler/tasks");
              if (res.ok) {
                const data = await res.json();
                const tasks = data.tasks || [];
                if (schedulerTaskCount) {
                  schedulerTaskCount.textContent = `${tasks.length} tareas (${tasks.filter(t => t.enabled).length} activas)`;
                }

                if (tasks.length === 0) {
                  schedulerTaskList.innerHTML = `<div style="text-align: center; padding: 20px; color: var(--text-muted); font-size: 0.85rem;">No hay tareas registradas.</div>`;
                  return;
                }

                schedulerTaskList.innerHTML = tasks.map(t => `
                  <div class="scheduler-task-card">
                    <div class="scheduler-task-info">
                      <h4>${escapeHtml(t.name || t.id)}</h4>
                      <div class="scheduler-task-meta">
                        <span style="color: #00d2ff; font-family: var(--font-mono);">⏰ ${escapeHtml(t.schedule)}</span>
                        <span>Handler: <strong>${escapeHtml(t.handler || 'custom')}</strong></span>
                        ${t.lastRun ? `<span>Último: ${new Date(t.lastRun).toLocaleTimeString()}</span>` : ''}
                        <span>Estado: <strong style="color: ${t.enabled ? '#38ef7d' : '#ff5c77'}">${t.enabled ? 'ACTIVO' : 'PAUSADO'}</strong></span>
                      </div>
                    </div>
                    <div class="scheduler-task-actions">
                      <button class="btn-secondary btn-trigger-task" data-id="${escapeHtml(t.id)}" style="padding: 5px 10px; font-size: 0.74rem;">
                        ▶ Ejecutar
                      </button>
                    </div>
                  </div>
                `).join("");

                schedulerTaskList.querySelectorAll(".btn-trigger-task").forEach(btn => {
                  btn.addEventListener("click", async () => {
                    const id = btn.getAttribute("data-id");
                    btn.disabled = true;
                    btn.textContent = "Ejecutando...";
                    playHudSound("click");
                    try {
                      const trigRes = await fetch("/api/scheduler/tasks/trigger", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ taskId: id })
                      });
                      const trigData = await trigRes.json();
                      if (trigRes.ok && trigData.ok) {
                        showToast(`✓ Tarea "${id}" ejecutada correctamente.`);
                        loadSchedulerTasks();
                      } else {
                        showToast(`⚠️ Error: ${trigData.error || 'Fallo de ejecución'}`);
                      }
                    } catch(e) {
                      showToast("Error de conexión al disparar tarea.");
                    } finally {
                      btn.disabled = false;
                      btn.textContent = "▶ Ejecutar";
                    }
                  });
                });
              }
            } catch(e) {
              schedulerTaskList.innerHTML = `<div style="text-align: center; padding: 20px; color: #ff5c77; font-size: 0.85rem;">Error al cargar las tareas del servidor.</div>`;
            }
          }

          if (btnTriggerMorning) {
            btnTriggerMorning.addEventListener("click", async () => {
              btnTriggerMorning.disabled = true;
              btnTriggerMorning.textContent = "Generando resumen...";
              playHudSound("click");
              try {
                const res = await fetch("/api/scheduler/tasks/trigger", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ taskId: "daily_morning_report" })
                });
                const data = await res.json();
                if (res.ok && data.ok) {
                  showToast("✓ Resumen matutino generado y enviado.");
                } else {
                  showToast(data.error || "Aviso al generar reporte.");
                }
              } catch(e) {
                showToast("Error de red al ejecutar.");
              } finally {
                btnTriggerMorning.disabled = false;
                btnTriggerMorning.textContent = "🌅 Disparar Resumen Matutino Ahora";
              }
            });
          }

          if (btnTriggerCalendar) {
            btnTriggerCalendar.addEventListener("click", async () => {
              btnTriggerCalendar.disabled = true;
              btnTriggerCalendar.textContent = "Verificando...";
              playHudSound("click");
              try {
                const res = await fetch("/api/scheduler/tasks/trigger", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ taskId: "calendar_upcoming_check" })
                });
                const data = await res.json();
                if (res.ok && data.ok) {
                  showToast("✓ Verificación de eventos completada.");
                } else {
                  showToast(data.error || "Aviso en verificación de eventos.");
                }
              } catch(e) {
                showToast("Error de red.");
              } finally {
                btnTriggerCalendar.disabled = false;
                btnTriggerCalendar.textContent = "📅 Verificar Próximos Eventos";
              }
            });
          }
        }
      }

      // --- AUTENTICACIÓN SEGURA CON PIN Y SESIÓN CRIPTOGRÁFICA ---
      const authModal = document.getElementById("auth-modal");
      const authPinInput = document.getElementById("auth-pin-input");
      const authPinForm = document.getElementById("auth-pin-form");
      const authErrorMsg = document.getElementById("auth-error-msg");
      const btnSessionLock = document.getElementById("btn-session-lock");

      function showAuthModal() {
        if (!authModal) return;
        authModal.classList.add("active");
        if (authErrorMsg) authErrorMsg.style.display = "none";
        if (authPinInput) {
          authPinInput.value = "";
          setTimeout(() => authPinInput.focus(), 150);
        }
      }

      function hideAuthModal() {
        if (!authModal) return;
        authModal.classList.remove("active");
        if (authErrorMsg) authErrorMsg.style.display = "none";
      }

      async function checkAuthSession() {
        try {
          const res = await fetch("/api/auth/status", { cache: "no-store" });
          if (res.ok) {
            const data = await res.json();
            if (data.authenticated === false) {
              showAuthModal();
              return false;
            } else {
              hideAuthModal();
              return true;
            }
          }
        } catch(e) {}
        return true;
      }

      async function handlePinLogin(e) {
        if (e) e.preventDefault();
        const pin = (authPinInput ? authPinInput.value : "").trim();
        if (!pin) {
          if (authErrorMsg) {
            authErrorMsg.textContent = "Por favor ingrese su PIN de acceso.";
            authErrorMsg.style.display = "block";
          }
          return;
        }

        try {
          const res = await fetch("/api/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pin })
          });
          const data = await res.json();
          if (res.ok && data.ok) {
            hideAuthModal();
            showToast("✓ Sesión iniciada. Bienvenido, Santiago.");
            checkServerConnection();
          } else {
            if (authErrorMsg) {
              authErrorMsg.textContent = data.error || "PIN de acceso incorrecto.";
              authErrorMsg.style.display = "block";
            }
            if (authPinInput) {
              authPinInput.value = "";
              authPinInput.focus();
            }
          }
        } catch(err) {
          if (authErrorMsg) {
            authErrorMsg.textContent = "Error al conectar con el servidor.";
            authErrorMsg.style.display = "block";
          }
        }
      }

      async function handleLogout() {
        try {
          await fetch("/api/auth/logout", { method: "POST" });
        } catch(e) {}
        showAuthModal();
        showToast("🔒 Sesión bloqueada con éxito.");
      }

      function setupAuthHandlers() {
        if (authPinForm) {
          authPinForm.addEventListener("submit", handlePinLogin);
        }
        if (btnSessionLock) {
          btnSessionLock.addEventListener("click", handleLogout);
        }
      }

      // Cuadro de confirmación flotante para acciones sensibles
      function renderSensitiveActionPrompt(conf) {
        const row = document.createElement("div");
        row.className = "message-row assistant";

        const bubble = document.createElement("div");
        bubble.className = "bubble";
        bubble.style.borderColor = "var(--accent-pink)";
        bubble.innerHTML = `
          <div style="font-weight: 600; color: #ffd166; margin-bottom: 6px;">⚠️ Confirmación de Acción Sensible</div>
          <div style="font-size: 0.85rem; margin-bottom: 10px;">${escapeHtml(conf.reason)}</div>
          <div style="display: flex; gap: 8px;">
            <button class="btn-primary btn-confirm-action" style="padding: 6px 12px; font-size: 0.8rem;">Aprobar y Ejecutar</button>
            <button class="btn-secondary btn-reject-action" style="padding: 6px 12px; font-size: 0.8rem;">Rechazar</button>
          </div>
        `;

        bubble.querySelector(".btn-confirm-action").addEventListener("click", async () => {
          bubble.innerHTML = `<div style="color: #38ef7d;">✓ Acción aprobada y enviada a ejecución...</div>`;
          await fetch("/api/audit/confirm", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ confirmId: conf.id, approved: true })
          });
        });

        bubble.querySelector(".btn-reject-action").addEventListener("click", async () => {
          bubble.innerHTML = `<div style="color: #ff5c77;">✕ Acción rechazada por usted, Santiago.</div>`;
          await fetch("/api/audit/confirm", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ confirmId: conf.id, approved: false })
          });
        });

        row.appendChild(bubble);
        chatMessages.appendChild(row);
        scrollToBottom();
      }

      // Formateador de Markdown con Soporte para Descarga de Archivos Modificados
      function formatMarkdown(text) {
        if (!text) return "";

        let safe = text
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;");

        // Bloques de código con detección de filename="..." para botón de descarga directa
        safe = safe.replace(/```([a-zA-Z0-9_\-\+]*)(?:\s+filename="?([^"\n]+)"?)?\n([\s\S]*?)```/g, (match, lang, customFilename, code) => {
          const displayLang = lang ? lang.toUpperCase() : "CÓDIGO";
          const trimmedCode = code.trim();
          const encoded = encodeURIComponent(trimmedCode);
          
          let downloadName = customFilename ? customFilename.trim() : "";
          if (!downloadName) {
            const firstLineMatch = trimmedCode.match(/^(?:\/\/|#|\/\*)\s*(?:filename|archivo):\s*([a-zA-Z0-9_\.\-]+)/i);
            if (firstLineMatch) {
              downloadName = firstLineMatch[1];
            } else {
              const extMap = { 
                js: "script.js", ts: "script.ts", py: "script.py", html: "index.html", 
                css: "style.css", json: "datos.json", csv: "datos.csv", sql: "consulta.sql", 
                md: "documento.md", bat: "ejecutar.bat", ps1: "script.ps1", sh: "script.sh", 
                xml: "datos.xml", txt: "archivo.txt" 
              };
              downloadName = extMap[lang.toLowerCase()] || `archivo_modificado.${lang.toLowerCase() || 'txt'}`;
            }
          }

          return `
            <div class="code-block-wrapper">
              <div class="code-block-header">
                <div>
                  <strong style="color: #fff;">${displayLang}</strong>
                  ${downloadName ? ` • <span class="code-filename">${downloadName}</span>` : ''}
                </div>
                <div class="code-actions-group">
                  <button class="download-code-btn" data-filename="${encodeURIComponent(downloadName)}" data-code="${encoded}" title="Descargar este archivo a su PC">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                      <polyline points="7 10 12 15 17 10"></polyline>
                      <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                    Descargar
                  </button>
                  <button class="copy-btn" data-code="${encoded}">Copiar</button>
                </div>
              </div>
              <pre><code>${trimmedCode}</code></pre>
            </div>
          `;
        });

        safe = safe.replace(/\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" style="color: var(--accent-blue); text-decoration: underline;">$1</a>');
        safe = safe.replace(/`([^`]+)`/g, "<code>$1</code>");
        safe = safe.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
        safe = safe.replace(/__([^_]+)__/g, "<strong>$1</strong>");
        safe = safe.replace(/\*([^*]+)\*/g, "<em>$1</em>");
        safe = safe.replace(/_([^_]+)_/g, "<em>$1</em>");
        safe = safe.replace(/^[\*\-]\s+(.*)$/gm, "<li>$1</li>");
        safe = safe.replace(/(<li>.*<\/li>)/s, "<ul>$1</ul>");

        const paragraphs = safe.split(/\n\s*\n/);
        return paragraphs.map(p => {
          if (p.includes("<div class=\"code-block-wrapper\"") || p.includes("<ul>") || p.includes("<li>")) {
            return p.replace(/\n/g, "<br>");
          }
          return `<p>${p.replace(/\n/g, "<br>")}</p>`;
        }).join("");
      }

    })();
