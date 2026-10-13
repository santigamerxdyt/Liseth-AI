/**
 * LISETH - Servidor Local de Inteligencia, Persistencia y Síntesis de Voz Neuronal
 * Desarrollado para Santiago Huerfano Lopez
 * 
 * Permite acceder a Liseth en local (PC), en tu red Wi-Fi (celular, tablet)
 * con voces neuronales ultra realistas (Edge TTS, ElevenLabs, OpenAI)
 * y persistencia completa tras reiniciar el equipo.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');
const url = require('url');
const https = require('https');

// Carga de variables de entorno desde .env si existe
const envPath = path.join(__dirname, '.env');
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf8');
  envContent.split('\n').forEach(line => {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('#') && trimmed.includes('=')) {
      const idx = trimmed.indexOf('=');
      const key = trimmed.slice(0, idx).trim();
      const val = trimmed.slice(idx + 1).trim();
      if (!process.env[key]) process.env[key] = val;
    }
  });
}

// Módulos de Arquitectura JARVIS v2
const BrainRouter = require('./lib/ai/BrainRouter');
const GoogleWorkspaceConnector = require('./lib/connectors/GoogleWorkspaceConnector');
const AuditManager = require('./lib/audit/AuditManager');
const NotificationManager = require('./lib/notifications/NotificationManager');

let Communicate = null;
try {
  const edgeTts = require('edge-tts-universal');
  Communicate = edgeTts.Communicate;
} catch (e) {
  // Edge-TTS opcional
}

const PORT = process.env.PORT || 3000;
const DATA_DIR = path.join(__dirname, 'data');
const DB_FILE = path.join(DATA_DIR, 'liseth_db.json');
const UPLOADS_DIR = path.join(__dirname, 'uploads');
const CREATED_FILES_DIR = path.join(__dirname, 'archivos_creados');

// Catálogo curado de voces femeninas ultra realistas similares a humanas
const REALISTIC_VOICES_CATALOG = [
  {
    id: "es-MX-DaliaNeural",
    provider: "edge",
    name: "Dalia (México) • Dulce y Juvenil (Estilo Anime)",
    description: "Una de las voces más humanas y expresivas en español. Tono dulce, juvenil, cálido y con modulación natural.",
    tag: "Recomendada Anime",
    badgeColor: "#ff66aa",
    lang: "es-MX",
    sample: "Hola Santiago, soy Liseth a su entera disposición. Es un verdadero placer asistirle hoy con mi voz viva."
  },
  {
    id: "es-CO-SalomeNeural",
    provider: "edge",
    name: "Salomé (Colombia) • Cálida y Melodiosa",
    description: "Entonación sumamente humana, suave, tranquila y respetuosa. Ideal para una asistente cercana y afectuosa.",
    tag: "Cálida y Humana",
    badgeColor: "#38ef7d",
    lang: "es-CO",
    sample: "Hola Santiago, estoy lista para ayudarle a planificar y organizar su jornada con total tranquilidad y eficiencia."
  },
  {
    id: "es-ES-ElviraNeural",
    provider: "edge",
    name: "Elvira (España) • Elegante y Aristocrática",
    description: "Dicción castellana pulcra, distinguida y de alta sociedad. Perfecta para un mayordomo refinado.",
    tag: "Elegante y Formal",
    badgeColor: "#00d2ff",
    lang: "es-ES",
    sample: "Buenas noches, Santiago. Liseth a su servicio con la máxima pulcritud, criterio y distinción."
  },
  {
    id: "es-US-PalomaNeural",
    provider: "edge",
    name: "Paloma (Hispanoamérica) • Moderna y Enérgica",
    description: "Voz juvenil, moderna, alegre y resolutiva, ideal para días de trabajo intenso.",
    tag: "Moderna y Ágil",
    badgeColor: "#ffd166",
    lang: "es-US",
    sample: "¡Hola Santiago! Todo listo para optimizar tu día y llevar tu productividad al máximo nivel."
  },
  {
    id: "es-PE-CamilaNeural",
    provider: "edge",
    name: "Camila (Perú) • Clara, Neutra y Dulce",
    description: "Acento sumamente neutro, claro, limpio y agradable al oído.",
    tag: "Neutra y Clara",
    badgeColor: "#a78bfa",
    lang: "es-PE",
    sample: "Hola Santiago, he organizado toda su información con precisión para su revisión inmediata."
  },
  {
    id: "es-AR-ElenaNeural",
    provider: "edge",
    name: "Elena (Argentina) • Expresiva y Natural",
    description: "Tono empático, expresivo y con calidez humana natural.",
    tag: "Expresiva",
    badgeColor: "#38bdf8",
    lang: "es-AR",
    sample: "Hola Santiago, contá conmigo para lo que necesites hoy. Estoy a tu completa disposición."
  },
  {
    id: "ja-JP-NanamiNeural",
    provider: "edge",
    name: "Nanami (Japón) • Voz Anime Original",
    description: "Voz japonesa dulce original para frases o ambientación de anime auténtico.",
    tag: "Anime Puro",
    badgeColor: "#f43f5e",
    lang: "ja-JP",
    sample: "こんにちは、サンティアゴ様。リセットです、よろしくお願いします。"
  },
  {
    id: "elevenlabs-custom",
    provider: "elevenlabs",
    name: "ElevenLabs (Rachel / Sarah / Nicole)",
    description: "Clonación e hiperrealismo de estudio cinematográfico mediante tu propia clave de ElevenLabs.",
    tag: "Hiperrealista Premium",
    badgeColor: "#f59e0b",
    lang: "multilingual",
    sample: "Hola Santiago, esta es la voz de ultra definición de ElevenLabs."
  },
  {
    id: "openai-nova",
    provider: "openai",
    name: "OpenAI Nova / Shimmer",
    description: "Voz conversacional cálida generada mediante la API de OpenAI Speech.",
    tag: "OpenAI Neural",
    badgeColor: "#10b981",
    lang: "multilingual",
    sample: "Hola Santiago, voz sintetizada mediante el modelo de audio de OpenAI."
  }
];

// Estructura de base de datos inicial
const DEFAULT_DB = {
  user: {
    name: "Santiago Huerfano Lopez",
    nickname: "Santiago",
    created_at: new Date().toISOString(),
    memoryFacts: [
      "Señor y creador de Liseth.",
      "Le gusta la máxima eficiencia y automatizar su rutina diaria.",
      "Utiliza Google Workspace (Gmail, Calendar, Tasks) y Windows."
    ],
    preferences: {
      voiceId: "es-MX-DaliaNeural",
      voiceProvider: "edge",
      pitch: "+15Hz",
      rate: "+5%"
    }
  },
  chat_history: [],
  config: {
    apiKey: "",
    elevenLabsKey: "",
    openAiKey: "",
    voiceSettings: {
      voiceId: "es-MX-DaliaNeural",
      provider: "edge",
      pitch: "+15Hz",
      rate: "+5%",
      enabled: true
    }
  },
  google: {
    connected: false,
    clientId: "",
    clientEmail: "",
    lastSync: null
  },
  productivity: {
    routines: [
      { id: 1, title: "Revisión matutina", time: "08:00", active: true, desc: "Agenda de Google Calendar y 3 prioridades del día." },
      { id: 2, title: "Depuración de descargas", time: "18:00", active: true, desc: "Organizar automáticamente la carpeta Downloads." }
    ],
    automations: [
      { name: "Organizador de Descargas", type: "Script PowerShell/Batch", status: "Disponible" },
      { name: "Resumen de Correo Gmail", type: "API Google", status: "Configurable" },
      { name: "Time-blocking con Calendar", type: "Productividad", status: "Activo" }
    ]
  },
  whatsapp_module: {
    status: "fase_2_planificada",
    notes: "Preparado para integración mediante Baileys / Meta Cloud API"
  }
};

// Asegurar carpeta de datos y base de datos local
function initDatabase() {
  try {
    if (!fs.existsSync(DATA_DIR)) {
      fs.mkdirSync(DATA_DIR, { recursive: true });
    }
    if (!fs.existsSync(UPLOADS_DIR)) {
      fs.mkdirSync(UPLOADS_DIR, { recursive: true });
      console.log('✓ Carpeta de uploads persistente creada en:', UPLOADS_DIR);
    }
    if (!fs.existsSync(CREATED_FILES_DIR)) {
      fs.mkdirSync(CREATED_FILES_DIR, { recursive: true });
      console.log('✓ Carpeta de archivos creados establecida en:', CREATED_FILES_DIR);
    }
    if (!fs.existsSync(DB_FILE)) {
      fs.writeFileSync(DB_FILE, JSON.stringify(DEFAULT_DB, null, 2), 'utf-8');
      console.log('✓ Base de datos persistente creada en:', DB_FILE);
    }
  } catch (err) {
    console.error('Error inicializando base de datos:', err);
  }
}

function readDatabase() {
  try {
    if (!fs.existsSync(DB_FILE)) {
      initDatabase();
    }
    const data = fs.readFileSync(DB_FILE, 'utf-8');
    return JSON.parse(data);
  } catch (err) {
    console.error('Error leyendo base de datos, usando respaldo:', err);
    return DEFAULT_DB;
  }
}

function saveDatabase(db) {
  try {
    fs.writeFileSync(DB_FILE, JSON.stringify(db, null, 2), 'utf-8');
    return true;
  } catch (err) {
    console.error('Error guardando en base de datos:', err);
    return false;
  }
}

// Obtener IPs locales de la red (para celular / tablet)
function getLocalNetworkIPs() {
  const interfaces = os.networkInterfaces();
  const addresses = [];
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      if (iface.family === 'IPv4' && !iface.internal) {
        addresses.push({ interface: name, address: iface.address });
      }
    }
  }
  return addresses;
}

// Helper para parsear JSON en peticiones POST
function parseJsonBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
      if (body.length > 5 * 1024 * 1024) {
        req.destroy();
        reject(new Error('Payload demasiado grande'));
      }
    });
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (e) {
        reject(e);
      }
    });
    req.on('error', reject);
  });
}

// Envío de respuestas JSON con CORS
function sendJson(res, statusCode, data) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
  });
  res.end(JSON.stringify(data));
}

// Servir archivos estáticos
function serveStaticFile(res, filePath, contentType) {
  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
        res.end('404: Archivo no encontrado');
      } else {
        res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
        res.end('500: Error interno del servidor');
      }
    } else {
      res.writeHead(200, {
        'Content-Type': contentType,
        'Cache-Control': 'no-cache',
        'Access-Control-Allow-Origin': '*'
      });
      res.end(content);
    }
  });
}

// Sintetizar voz con ElevenLabs si el usuario proporciona clave
function synthesizeElevenLabs(text, voiceId, apiKey, res) {
  const targetVoice = voiceId && voiceId !== 'elevenlabs-custom' ? voiceId : '21m00Tcm4TlvDq8ikWAM'; // Rachel por defecto
  const reqData = JSON.stringify({
    text: text,
    model_id: "eleven_multilingual_v2",
    voice_settings: { stability: 0.5, similarity_boost: 0.8 }
  });

  const options = {
    hostname: 'api.elevenlabs.io',
    path: `/v1/text-to-speech/${targetVoice}/stream`,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'xi-api-key': apiKey,
      'Content-Length': Buffer.byteLength(reqData)
    }
  };

  const req = https.request(options, (apiRes) => {
    if (apiRes.statusCode !== 200) {
      res.writeHead(apiRes.statusCode, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
      return apiRes.pipe(res);
    }
    res.writeHead(200, {
      'Content-Type': 'audio/mpeg',
      'Cache-Control': 'no-cache',
      'Access-Control-Allow-Origin': '*'
    });
    apiRes.pipe(res);
  });

  req.on('error', (err) => {
    console.error('Error ElevenLabs:', err);
    sendJson(res, 500, { error: 'Error conectando con ElevenLabs' });
  });

  req.write(reqData);
  req.end();
}

// Sintetizar voz con OpenAI TTS si el usuario proporciona clave
function synthesizeOpenAI(text, voiceName, apiKey, res) {
  const voice = voiceName && ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'].includes(voiceName) ? voiceName : 'nova';
  const reqData = JSON.stringify({
    model: "tts-1",
    input: text,
    voice: voice
  });

  const options = {
    hostname: 'api.openai.com',
    path: '/v1/audio/speech',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
      'Content-Length': Buffer.byteLength(reqData)
    }
  };

  const req = https.request(options, (apiRes) => {
    if (apiRes.statusCode !== 200) {
      res.writeHead(apiRes.statusCode, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
      return apiRes.pipe(res);
    }
    res.writeHead(200, {
      'Content-Type': 'audio/mpeg',
      'Cache-Control': 'no-cache',
      'Access-Control-Allow-Origin': '*'
    });
    apiRes.pipe(res);
  });

  req.on('error', (err) => {
    console.error('Error OpenAI TTS:', err);
    sendJson(res, 500, { error: 'Error conectando con OpenAI' });
  });

  req.write(reqData);
  req.end();
}

// Creación del servidor HTTP
const server = http.createServer(async (req, res) => {
  const parsedUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const pathname = parsedUrl.pathname;
  const method = req.method;

  // Manejo de preflight CORS (OPTIONS)
  if (method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
    });
    return res.end();
  }

  // --- RUTAS DE API ---

  // Catálogo de Voces Femeninas Humanas
  if (pathname === '/api/voices' && method === 'GET') {
    return sendJson(res, 200, {
      voices: REALISTIC_VOICES_CATALOG
    });
  }

  // SÍNTESIS DE VOZ NEURONAL (EDGE TTS / ELEVENLABS / OPENAI)
  if (pathname === '/api/tts') {
    let text = parsedUrl.searchParams.get('text') || '';
    let voice = parsedUrl.searchParams.get('voice') || 'es-MX-DaliaNeural';
    let rate = parsedUrl.searchParams.get('rate') || '+5%';
    let pitch = parsedUrl.searchParams.get('pitch') || '+15Hz';
    let provider = parsedUrl.searchParams.get('provider') || 'edge';

    if (method === 'POST') {
      try {
        const body = await parseJsonBody(req);
        if (body.text) text = body.text;
        if (body.voice) voice = body.voice;
        if (body.rate) rate = body.rate;
        if (body.pitch) pitch = body.pitch;
        if (body.provider) provider = body.provider;
      } catch (e) {}
    }

    if (!text.trim()) {
      return sendJson(res, 400, { error: 'El parámetro text es requerido' });
    }

    const db = readDatabase();

    // 1. ElevenLabs
    if (provider === 'elevenlabs') {
      const apiKey = db.config?.elevenLabsKey || parsedUrl.searchParams.get('key');
      if (!apiKey) {
        return sendJson(res, 401, { error: 'Se requiere una API Key de ElevenLabs configurada en Ajustes.' });
      }
      return synthesizeElevenLabs(text, voice, apiKey, res);
    }

    // 2. OpenAI TTS
    if (provider === 'openai') {
      const apiKey = db.config?.openAiKey || parsedUrl.searchParams.get('key');
      if (!apiKey) {
        return sendJson(res, 401, { error: 'Se requiere una API Key de OpenAI configurada en Ajustes.' });
      }
      return synthesizeOpenAI(text, voice, apiKey, res);
    }

    // 3. Edge TTS (Por defecto: Gratis, Ultra Realista, Calidad Humana)
    if (Communicate) {
      try {
        const comm = new Communicate(text, { voice, rate, pitch });
        const stream = await comm.stream();

        res.writeHead(200, {
          'Content-Type': 'audio/mpeg',
          'Cache-Control': 'no-cache',
          'Access-Control-Allow-Origin': '*'
        });

        for await (const chunk of stream) {
          if (chunk.type === 'audio') {
            res.write(chunk.data);
          }
        }
        return res.end();
      } catch (err) {
        console.error('Error generando audio con Edge TTS:', err);
        return sendJson(res, 500, { error: 'Fallo al generar audio con Edge TTS' });
      }
    } else {
      return sendJson(res, 503, { error: 'Módulo de voz neuronal no inicializado' });
    }
  }

  // Estado del servidor e IPs locales
  if (pathname === '/api/status' && method === 'GET') {
    const localIPs = getLocalNetworkIPs();
    return sendJson(res, 200, {
      status: 'online',
      assistant: 'Liseth',
      user: 'Santiago Huerfano Lopez',
      uptime: process.uptime(),
      timestamp: new Date().toISOString(),
      port: PORT,
      localIPs: localIPs,
      neuralTtsActive: Boolean(Communicate)
    });
  }

  // Historial de conversación (Persistencia entre reinicios y dispositivos)
  if (pathname === '/api/history') {
    const db = readDatabase();
    if (method === 'GET') {
      return sendJson(res, 200, {
        history: db.chat_history || []
      });
    }

    if (method === 'POST') {
      try {
        const body = await parseJsonBody(req);
        if (Array.isArray(body.history)) {
          db.chat_history = body.history.slice(-80);
          saveDatabase(db);
          return sendJson(res, 200, { ok: true, count: db.chat_history.length });
        } else {
          return sendJson(res, 400, { error: 'Se esperaba un arreglo en history' });
        }
      } catch (err) {
        return sendJson(res, 400, { error: 'JSON inválido' });
      }
    }

    if (method === 'DELETE') {
      db.chat_history = [];
      saveDatabase(db);
      return sendJson(res, 200, { ok: true, message: 'Historial reiniciado' });
    }
  }

  // Perfil y Memoria sobre Santiago
  if (pathname === '/api/profile') {
    const db = readDatabase();
    if (method === 'GET') {
      return sendJson(res, 200, {
        user: db.user || DEFAULT_DB.user
      });
    }

    if (method === 'POST') {
      try {
        const body = await parseJsonBody(req);
        if (body.memoryFact) {
          if (!db.user.memoryFacts.includes(body.memoryFact)) {
            db.user.memoryFacts.push(body.memoryFact);
          }
        }
        if (body.preferences) {
          db.user.preferences = { ...db.user.preferences, ...body.preferences };
        }
        saveDatabase(db);
        return sendJson(res, 200, { ok: true, user: db.user });
      } catch (err) {
        return sendJson(res, 400, { error: 'Error actualizando perfil' });
      }
    }
  }

  // Configuración
  if (pathname === '/api/config') {
    const db = readDatabase();
    if (method === 'GET') {
      return sendJson(res, 200, {
        config: db.config || DEFAULT_DB.config
      });
    }

    if (method === 'POST') {
      try {
        const body = await parseJsonBody(req);
        if (body.apiKey !== undefined) db.config.apiKey = body.apiKey;
        if (body.elevenLabsKey !== undefined) db.config.elevenLabsKey = body.elevenLabsKey;
        if (body.openAiKey !== undefined) db.config.openAiKey = body.openAiKey;
        if (body.voiceSettings !== undefined) {
          db.config.voiceSettings = { ...db.config.voiceSettings, ...body.voiceSettings };
        }
        saveDatabase(db);
        return sendJson(res, 200, { ok: true, config: db.config });
      } catch (err) {
        return sendJson(res, 400, { error: 'Error guardando configuración' });
      }
    }
  }

  // ============================================================
  // ENDPOINTS DE ARQUITECTURA JARVIS V2
  // ============================================================

  // 1. BRAIN ROUTER (Cerebro Dual Gemini & Claude + Monitor de Tokens)
  if (pathname === '/api/brain/status' && method === 'GET') {
    return sendJson(res, 200, {
      activeBrain: BrainRouter.getEffectiveBrain(),
      forcedBrain: BrainRouter.forcedBrain,
      lastFailover: BrainRouter.lastFailover,
      stats: BrainRouter.tokenStats,
      limits: BrainRouter.limits
    });
  }

  if (pathname === '/api/brain/switch' && method === 'POST') {
    try {
      const body = await parseJsonBody(req);
      const success = BrainRouter.setForcedBrain(body.brain !== undefined ? body.brain : null);
      return sendJson(res, 200, { ok: success, activeBrain: BrainRouter.getEffectiveBrain(), forcedBrain: BrainRouter.forcedBrain });
    } catch (e) {
      return sendJson(res, 400, { error: e.message });
    }
  }

  // Ejecución de Inteligencia Unificada en el Servidor (Protege las API Keys)
  if (pathname === '/api/brain/chat' && method === 'POST') {
    try {
      const body = await parseJsonBody(req);
      const db = readDatabase();
      const apiKeyGemini = body.apiKey || process.env.GEMINI_API_KEY || db.config?.apiKey;
      const apiKeyClaude = process.env.ANTHROPIC_API_KEY || db.config?.claudeKey;

      // Obtener herramientas disponibles de Google Workspace y otros conectores
      const tools = GoogleWorkspaceConnector.connected ? GoogleWorkspaceConnector.list_actions() : [];

      const aiResponse = await BrainRouter.generateResponse({
        systemInstruction: body.systemInstruction,
        contents: body.contents,
        tools: tools,
        apiKeyGemini,
        apiKeyClaude
      });

      // Si el LLM devolvió una llamada a herramienta (Function Calling)
      if (aiResponse.functionCall) {
        const fnName = aiResponse.functionCall.name;
        const fnArgs = aiResponse.functionCall.args || {};
        
        // Determinar si la acción es sensible
        const actionDef = tools.find(t => t.name === fnName);
        if (actionDef && actionDef.sensitive) {
          const pending = AuditManager.createPendingConfirmation(
            'google_workspace',
            fnName,
            fnArgs,
            `JARVIS solicita ejecutar ${fnName} con parámetros: ${JSON.stringify(fnArgs)}`
          );
          return sendJson(res, 200, {
            ...aiResponse,
            requiresConfirmation: true,
            confirmation: pending
          });
        }

        // Ejecutar acción directamente
        try {
          const toolResult = await GoogleWorkspaceConnector.execute_action(fnName, fnArgs);
          AuditManager.logAction({
            connector: 'google_workspace',
            action: fnName,
            params: fnArgs,
            status: 'success',
            result: toolResult,
            autoApproved: true
          });
          return sendJson(res, 200, {
            ...aiResponse,
            executedTool: { name: fnName, result: toolResult }
          });
        } catch (toolErr) {
          AuditManager.logAction({
            connector: 'google_workspace',
            action: fnName,
            params: fnArgs,
            status: 'failed',
            result: { error: toolErr.message }
          });
          return sendJson(res, 200, {
            ...aiResponse,
            executedTool: { name: fnName, error: toolErr.message }
          });
        }
      }

      return sendJson(res, 200, aiResponse);
    } catch (e) {
      console.error('Error en /api/brain/chat:', e);
      return sendJson(res, 500, { error: e.message });
    }
  }

  // 2. GOOGLE WORKSPACE OAUTH 2.0 & ESTADO
  if (pathname === '/api/google/status' && method === 'GET') {
    const db = readDatabase();
    if (db.google_tokens) {
      GoogleWorkspaceConnector.loadEncryptedTokens(db.google_tokens);
    }
    return sendJson(res, 200, {
      connected: GoogleWorkspaceConnector.connected,
      clientId: GoogleWorkspaceConnector.clientId ? 'Configurado' : 'Pendiente',
      actions: GoogleWorkspaceConnector.list_actions().map(a => a.name)
    });
  }

  if (pathname === '/api/google/auth-url' && method === 'GET') {
    const clientId = parsedUrl.searchParams.get('clientId') || process.env.GOOGLE_CLIENT_ID;
    const clientSecret = parsedUrl.searchParams.get('clientSecret') || process.env.GOOGLE_CLIENT_SECRET;
    if (clientId) GoogleWorkspaceConnector.clientId = clientId;
    if (clientSecret) GoogleWorkspaceConnector.clientSecret = clientSecret;
    if (!GoogleWorkspaceConnector.clientId) {
      return sendJson(res, 400, { error: 'Falta Google Client ID' });
    }
    return sendJson(res, 200, { authUrl: GoogleWorkspaceConnector.getAuthUrl() });
  }

  if (pathname === '/api/google/oauth2callback' && method === 'GET') {
    const code = parsedUrl.searchParams.get('code');
    if (!code) {
      res.writeHead(400, { 'Content-Type': 'text/html; charset=utf-8' });
      return res.end('<h2>Error: No se recibió código de autorización</h2>');
    }
    try {
      const tokens = await GoogleWorkspaceConnector.exchangeCodeForTokens(code);
      const db = readDatabase();
      db.google_tokens = tokens;
      db.google = { connected: true, lastSync: new Date().toISOString() };
      saveDatabase(db);
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      return res.end(`
        <body style="background:#090d16; color:#00d2ff; font-family:sans-serif; text-align:center; padding-top:60px;">
          <h2>✓ Google Workspace Conectado con Éxito</h2>
          <p style="color:#cbd5e1;">Puede cerrar esta ventana y regresar al panel de Liseth.</p>
          <script>window.opener && window.opener.location.reload(); setTimeout(() => window.close(), 2500);</script>
        </body>
      `);
    } catch (e) {
      res.writeHead(500, { 'Content-Type': 'text/html; charset=utf-8' });
      return res.end(`<h2>Error vinculando Google: ${e.message}</h2>`);
    }
  }

  // 3. AUDITORÍA Y ACCIONES SENSIBLES
  if (pathname === '/api/audit/logs' && method === 'GET') {
    return sendJson(res, 200, {
      logs: AuditManager.getLogs(),
      pendingConfirmations: AuditManager.getPendingConfirmations()
    });
  }

  if (pathname === '/api/audit/confirm' && method === 'POST') {
    try {
      const body = await parseJsonBody(req);
      const resolution = AuditManager.resolveConfirmation(body.confirmId, Boolean(body.approved));
      if (!resolution) return sendJson(res, 404, { error: 'Confirmación no encontrada' });

      // Si fue aprobada, ejecutar la acción pendiente
      if (body.approved && resolution.connector === 'google_workspace') {
        const result = await GoogleWorkspaceConnector.execute_action(resolution.action, resolution.params);
        AuditManager.logAction({
          connector: resolution.connector,
          action: resolution.action,
          params: resolution.params,
          status: 'success',
          result: result,
          userConfirmed: true
        });
        return sendJson(res, 200, { ok: true, result });
      }
      return sendJson(res, 200, { ok: true, resolution });
    } catch (e) {
      return sendJson(res, 500, { error: e.message });
    }
  }

  // 4. NOTIFICACIONES & WEBHOOKS (WhatsApp Meta & Telegram)
  if (pathname === '/api/notifications/test' && method === 'POST') {
    try {
      const body = await parseJsonBody(req);
      const resSend = await NotificationManager.sendAlert(body.message || 'Prueba de alerta desde JARVIS', true);
      return sendJson(res, 200, { ok: true, result: resSend });
    } catch (e) {
      return sendJson(res, 500, { error: e.message });
    }
  }

  if (pathname === '/api/notifications/config' && method === 'POST') {
    try {
      const body = await parseJsonBody(req);
      NotificationManager.setConfig(body);
      return sendJson(res, 200, { ok: true, config: NotificationManager.config });
    } catch (e) {
      return sendJson(res, 400, { error: e.message });
    }
  }

  // Webhook para Meta WhatsApp Cloud API (Verificación GET)
  if (pathname === '/api/webhook/whatsapp' && method === 'GET') {
    const mode = parsedUrl.searchParams.get('hub.mode');
    const token = parsedUrl.searchParams.get('hub.verify_token');
    const challenge = parsedUrl.searchParams.get('hub.challenge');
    const expectedToken = process.env.META_WA_VERIFY_TOKEN || 'jarvis_webhook_verify_token';
    if (mode === 'subscribe' && token === expectedToken) {
      res.writeHead(200, { 'Content-Type': 'text/plain' });
      return res.end(challenge);
    }
    res.writeHead(403, { 'Content-Type': 'text/plain' });
    return res.end('Verificación de webhook fallida');
  }

  // Webhook para Meta WhatsApp Cloud API (Recepción de mensajes POST)
  if (pathname === '/api/webhook/whatsapp' && method === 'POST') {
    try {
      const body = await parseJsonBody(req);
      const message = body.entry?.[0]?.changes?.[0]?.value?.messages?.[0];
      if (message && message.text) {
        const from = message.from;
        const userMsg = message.text.body;
        console.log(`[WhatsApp Recibido de ${from}]: ${userMsg}`);
        // Procesar con BrainRouter y responder
        const aiRes = await BrainRouter.generateResponse({
          systemInstruction: 'Eres Liseth, asistente personal en WhatsApp. Sé concisa y resolutiva.',
          contents: [{ role: 'user', parts: [{ text: userMsg }] }]
        });
        if (aiRes.text) {
          await NotificationManager.sendWhatsApp(aiRes.text);
        }
      }
      return sendJson(res, 200, { status: 'EVENT_RECEIVED' });
    } catch (e) {
      return sendJson(res, 200, { status: 'PROCESSED_WITH_WARNING' });
    }
  }

  // Productividad y Automatizaciones del Día a Día
  if (pathname === '/api/productivity/ideas' && method === 'GET') {
    const db = readDatabase();
    return sendJson(res, 200, {
      ideas: [
        {
          categoria: "⚡ Automatización de Windows / PC",
          titulo: "Script de Arranque de Trabajo con 1 Clic",
          descripcion: "Un script que abre automáticamente tu navegador, pestañas de proyectos, herramientas y correo con un solo atajo.",
          accion: "prompt: Genera un script en Batch para abrir mis aplicaciones de productividad cada mañana."
        },
        {
          categoria: "📂 Organización de Archivos",
          titulo: "Limpiador Automático de Descargas",
          descripcion: "Mueve automáticamente capturas a Imágenes, PDFs a Documentos y comprimidos a Archivos cada semana.",
          accion: "prompt: Dame un script en PowerShell para organizar mi carpeta de Descargas automáticamente según la extensión del archivo."
        },
        {
          categoria: "✉️ Gestión Inteligente de Correos",
          titulo: "Filtros y Plantillas de Respuesta en Gmail",
          descripcion: "Clasifica automáticamente boletines, facturas y correos urgentes en etiquetas con reglas inteligentes.",
          accion: "prompt: ¿Cómo puedo crear filtros avanzados en Gmail para que los correos clave nunca se pierdan?"
        },
        {
          categoria: "⏱️ Rutina de Alto Rendimiento",
          titulo: "Time-Blocking con Google Calendar",
          descripcion: "Divide tu jornada en 3 bloques de foco profundo de 90 minutos y asigna descansos intencionales.",
          accion: "prompt: Ayúdame a diseñar un horario de time-blocking para mi jornada de hoy."
        },
        {
          categoria: "🤖 Automatizaciones No-Code (Make / Zapier)",
          titulo: "Conexión de Formularios y Notificaciones",
          descripcion: "Envía alertas a tu correo o genera tareas automáticamente cada vez que recibes un aviso importante.",
          accion: "prompt: Explícame cómo crear una automatización en Make.com sin saber programar."
        }
      ],
      userRoutines: db.productivity?.routines || []
    });
  }

  // Roadmap y Estado del Módulo de WhatsApp
  if (pathname === '/api/whatsapp/info' && method === 'GET') {
    return sendJson(res, 200, {
      status: "fase_2_planificada",
      descripcion: "Integración de recordatorios de Liseth a WhatsApp",
      opciones: [
        {
          metodo: "Baileys / Venom-bot (Recomendado y Gratis)",
          requisitos: "Escanear un código QR desde WhatsApp en el teléfono una sola vez. No requiere tarjeta ni pago de API.",
          ventajas: "100% privado, corre en este mismo servidor, envía mensajes a tu propio chat personal.",
          fase: "Próxima actualización"
        },
        {
          metodo: "Meta Cloud API (Oficial)",
          requisitos: "Cuenta de Facebook Developer, número de teléfono empresarial verificado y tarjeta registrada en Meta.",
          ventajas: "Estabilidad oficial empresarial pero con costos tras superar conversaciones gratuitas y configuración más compleja.",
          fase: "Alternativa"
        }
      ]
    });
  }

  // Subida y Almacenamiento de Archivos (cualquier formato)
  if (pathname === '/api/upload' && method === 'POST') {
    try {
      const body = await parseJsonBody(req);
      if (!body.data) {
        return sendJson(res, 400, { error: 'Falta campo data (base64)' });
      }
      const rawName = body.name || `archivo_${Date.now()}`;
      const safeName = path.basename(rawName).replace(/[^a-zA-Z0-9_\.\-\(\)\s]/g, '_');
      const filePath = path.join(UPLOADS_DIR, safeName);
      const buffer = Buffer.from(body.data, 'base64');
      fs.writeFileSync(filePath, buffer);

      const db = readDatabase();
      if (!db.files) db.files = [];
      const fileInfo = {
        id: Date.now().toString(),
        name: safeName,
        originalName: body.name || safeName,
        size: buffer.length,
        type: body.type || 'application/octet-stream',
        uploadedAt: new Date().toISOString(),
        url: `/uploads/${encodeURIComponent(safeName)}`
      };
      db.files.push(fileInfo);
      saveDatabase(db);

      return sendJson(res, 200, { ok: true, file: fileInfo });
    } catch(err) {
      console.error('Error guardando archivo en servidor:', err);
      return sendJson(res, 500, { error: 'Error procesando archivo' });
    }
  }

  // Lista de archivos almacenados
  if (pathname === '/api/files' && method === 'GET') {
    const db = readDatabase();
    return sendJson(res, 200, { files: db.files || [] });
  }

  // Servir / Descargar archivos subidos
  if (pathname.startsWith('/uploads/') && method === 'GET') {
    const fileName = path.basename(decodeURIComponent(pathname.replace('/uploads/', '')));
    const filePath = path.join(UPLOADS_DIR, fileName);
    if (fs.existsSync(filePath)) {
      return serveStaticFile(res, filePath, 'application/octet-stream');
    } else {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      return res.end('404: Archivo no encontrado');
    }
  }

  // Guardado de Archivos Creados e Investigaciones por Liseth
  if (pathname === '/api/save-generated-file' && method === 'POST') {
    try {
      const body = await parseJsonBody(req);
      if (!body.content && body.content !== '') {
        return sendJson(res, 400, { error: 'Falta campo content' });
      }
      const rawName = body.filename || `investigacion_${Date.now()}.md`;
      const safeName = path.basename(rawName).replace(/[^a-zA-Z0-9_\.\-\(\)\s]/g, '_');
      const filePath = path.join(CREATED_FILES_DIR, safeName);
      
      fs.writeFileSync(filePath, body.content, 'utf-8');

      const db = readDatabase();
      if (!db.generated_files) db.generated_files = [];
      const fileInfo = {
        id: Date.now().toString(),
        name: safeName,
        size: Buffer.byteLength(body.content, 'utf-8'),
        createdAt: new Date().toISOString(),
        url: `/archivos_creados/${encodeURIComponent(safeName)}`
      };
      db.generated_files.push(fileInfo);
      saveDatabase(db);

      return sendJson(res, 200, { ok: true, file: fileInfo });
    } catch(err) {
      console.error('Error guardando archivo generado:', err);
      return sendJson(res, 500, { error: 'Error al guardar archivo en disco' });
    }
  }

  // Lista de archivos creados e investigaciones
  if (pathname === '/api/generated-files' && method === 'GET') {
    const db = readDatabase();
    return sendJson(res, 200, { files: db.generated_files || [] });
  }

  // Servir / Descargar archivos creados directamente
  if (pathname.startsWith('/archivos_creados/') && method === 'GET') {
    const fileName = path.basename(decodeURIComponent(pathname.replace('/archivos_creados/', '')));
    const filePath = path.join(CREATED_FILES_DIR, fileName);
    if (fs.existsSync(filePath)) {
      return serveStaticFile(res, filePath, 'application/octet-stream');
    } else {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      return res.end('404: Archivo no encontrado');
    }
  }

  // --- SERVIDO DE ARCHIVOS WEB (FRONTEND) ---

  if (pathname === '/' || pathname === '/jarvis.html' || pathname === '/index.html') {
    const jarvisPath = path.join(__dirname, 'jarvis.html');
    return serveStaticFile(res, jarvisPath, 'text/html; charset=utf-8');
  }

  if (pathname === '/liseth.ico' || pathname === '/favicon.ico') {
    const iconPath = path.join(__dirname, 'liseth.ico');
    return serveStaticFile(res, iconPath, 'image/x-icon');
  }

  res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
  res.end('404: Recurso no encontrado en el servidor de Liseth');
});

// Inicializar y arrancar
initDatabase();

server.listen(PORT, '0.0.0.0', () => {
  const localIPs = getLocalNetworkIPs();
  console.log('\n======================================================');
  console.log('   👑 LISETH • ASISTENTE PERSONAL (VOCES NEURONALES ACTIVAS)');
  console.log('======================================================');
  console.log(`✓ Servidor corriendo en puerto: ${PORT}`);
  console.log(`✓ Motor de Voz Neuronal: Edge TTS (Humana / Estudio) HABILITADO`);
  console.log(`\n💻 Acceso local en este PC:`);
  console.log(`   http://localhost:${PORT}`);
  console.log(`   http://127.0.0.1:${PORT}`);
  
  if (localIPs.length > 0) {
    console.log(`\n📱 Acceso desde tu Celular / Tablet (en la misma red Wi-Fi):`);
    localIPs.forEach(item => {
      console.log(`   http://${item.address}:${PORT}  (${item.interface})`);
    });
  }
  
  console.log('\n💾 Persistencia activada en: data/liseth_db.json');
  console.log('======================================================\n');
});
