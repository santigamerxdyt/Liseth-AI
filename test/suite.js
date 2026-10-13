/**
 * Suite de Pruebas Automatizadas de JARVIS / Liseth
 * Ejecutable nativamente con Node.js (node:test y node:assert)
 */

const test = require('node:test');
const assert = require('node:assert');
const path = require('path');
const fs = require('fs');

// Configuración de entorno de prueba para evitar fugas de producción
process.env.MASTER_ENCRYPTION_KEY = 'test-master-encryption-key-32-chars-ok';
process.env.JARVIS_ACCESS_PIN = '987654';

const Auth = require('../lib/auth');
const Crypto = require('../lib/crypto');
const { BrainRouter } = require('../lib/ai/BrainRouter');
const GoogleWorkspaceConnector = require('../lib/connectors/GoogleWorkspaceConnector');

// ==========================================
// 1. PRUEBAS DEL MÓDULO DE AUTENTICACIÓN (lib/auth.js)
// ==========================================
test('Auth: Hash y verificación de PIN con scrypt', async () => {
  const pin = '987654';
  const hash = await Auth.hashPin(pin);

  assert.ok(hash.includes(':'), 'El hash debe contener salt y clave derivados separados por dos puntos');
  const [salt, keyHex] = hash.split(':');
  assert.strictEqual(salt.length, 32, 'El salt aleatorio debe ser de 16 bytes hex (32 caracteres)');
  assert.strictEqual(keyHex.length, 128, 'La clave derivada debe ser de 64 bytes hex (128 caracteres)');

  const isValid = await Auth.verifyPin(pin, hash);
  assert.strictEqual(isValid, true, 'El PIN correcto debe ser verificado exitosamente');

  const isInvalid = await Auth.verifyPin('123456', hash);
  assert.strictEqual(isInvalid, false, 'Un PIN incorrecto debe ser rechazado');
});

test('Auth: Tokens de sesión firmados con HMAC y verificación criptográfica', () => {
  const token = Auth.createSessionToken(60 * 1000); // 1 minuto de vida
  assert.ok(typeof token === 'string', 'El token debe ser un string');
  const parts = token.split('.');
  assert.strictEqual(parts.length, 3, 'El token debe tener 3 partes: sessionId.expiresAt.signature');

  // Token válido
  assert.strictEqual(Auth.verifySessionToken(token), true, 'El token recién emitido debe ser válido');

  // Token alterado (manipulación de payload)
  const tamperedToken = `fakeSessionId.${parts[1]}.${parts[2]}`;
  assert.strictEqual(Auth.verifySessionToken(tamperedToken), false, 'Un token alterado debe ser rechazado');

  // Token expirado
  const expiredToken = Auth.createSessionToken(-1000); // Ya vencido
  assert.strictEqual(Auth.verifySessionToken(expiredToken), false, 'Un token vencido debe ser rechazado');
});

test('Auth: Rate Limiting por IP contra ataques de fuerza bruta', () => {
  const testIp = '192.168.1.99';
  Auth.clearAttempts(testIp);

  // Primeros 4 intentos permitidos
  for (let i = 0; i < 4; i++) {
    const check = Auth.checkRateLimit(testIp);
    assert.strictEqual(check.allowed, true, `Intento ${i + 1} debe permitirse`);
    Auth.recordFailedAttempt(testIp);
  }

  // Quinto intento fallido (alcanza el límite de 5)
  Auth.recordFailedAttempt(testIp);
  const blockedCheck = Auth.checkRateLimit(testIp);
  assert.strictEqual(blockedCheck.allowed, false, 'Debe bloquear la IP tras 5 intentos fallidos');
  assert.ok(blockedCheck.remainingSec > 0, 'Debe indicar los segundos restantes de bloqueo');

  // Limpieza de intentos al loguearse exitosamente
  Auth.clearAttempts(testIp);
  assert.strictEqual(Auth.checkRateLimit(testIp).allowed, true, 'Debe permitir el acceso tras limpiar intentos');
});

test('Auth: Parser de cookies HTTP', () => {
  const fakeReq = {
    headers: {
      cookie: 'jarvis_session=xyz123; user_theme=dark; other=value'
    }
  };
  const cookies = Auth.parseCookies(fakeReq);
  assert.strictEqual(cookies.jarvis_session, 'xyz123');
  assert.strictEqual(cookies.user_theme, 'dark');
  assert.strictEqual(cookies.other, 'value');

  const emptyReq = { headers: {} };
  assert.deepStrictEqual(Auth.parseCookies(emptyReq), {});
});

// ==========================================
// 2. PRUEBAS DEL MÓDULO CRIPTOGRÁFICO (lib/crypto.js)
// ==========================================
test('Crypto: Cifrado y descifrado AES-256-GCM', () => {
  const secretText = 'OAuth-Refresh-Token-9874523412';
  const encrypted = Crypto.encrypt(secretText);

  assert.ok(encrypted.includes(':'), 'El texto cifrado debe tener formato iv:tag:data');
  const parts = encrypted.split(':');
  assert.strictEqual(parts.length, 3, 'Debe contener IV, Auth Tag y Payload');

  const decrypted = Crypto.decrypt(encrypted);
  assert.strictEqual(decrypted, secretText, 'El texto descifrado debe coincidir con el original');
});

test('Crypto: Detección de manipulación o alteración (Auth Tag inválido)', () => {
  const secretText = 'Mensaje confidencial';
  const encrypted = Crypto.encrypt(secretText);
  const [iv, tag, data] = encrypted.split(':');

  // Alterar un byte completo (2 caracteres hex) del payload cifrado
  const lastByte = data.slice(-2);
  const corruptedByte = lastByte === '00' ? 'ff' : '00';
  const corruptedData = data.slice(0, -2) + corruptedByte;
  const tampered = `${iv}:${tag}:${corruptedData}`;

  const result = Crypto.decrypt(tampered);
  assert.strictEqual(result, null, 'Un payload manipulado debe fallar la verificación y retornar null');
});

// ==========================================
// 3. PRUEBAS DE BRAINROUTER CON MOCKS (lib/ai/BrainRouter.js)
// ==========================================
test('BrainRouter: Ejecución exitosa con Gemini (Cerebro Primario)', async () => {
  const router = new BrainRouter();
  router.setForcedBrain(null);

  // Mock de _callGemini
  router._callGemini = async (key, opts) => {
    return {
      text: 'Respuesta generada por Gemini',
      usage: { inputTokens: 50, outputTokens: 25 }
    };
  };

  const response = await router.generateResponse({
    apiKeyGemini: 'mock-gemini-key',
    apiKeyClaude: 'mock-claude-key',
    contents: [{ role: 'user', parts: [{ text: 'Hola' }] }]
  });

  assert.strictEqual(response.brainUsed, 'gemini');
  assert.strictEqual(response.text, 'Respuesta generada por Gemini');
  assert.strictEqual(router.activeBrain, 'gemini');
});

test('BrainRouter: Failover automático a Claude ante error 429 de cuota en Gemini', async () => {
  const router = new BrainRouter();
  router.setForcedBrain(null);

  // Mock de fallo 429 en Gemini
  router._callGemini = async () => {
    const error = new Error('Quota exceeded for quota metric');
    error.code = 429;
    throw error;
  };

  // Mock de respuesta exitosa en Claude
  router._callClaude = async (key, opts) => {
    return {
      text: 'Respuesta generada por Claude tras failover',
      usage: { inputTokens: 60, outputTokens: 30 }
    };
  };

  const response = await router.generateResponse({
    apiKeyGemini: 'mock-gemini-key',
    apiKeyClaude: 'mock-claude-key',
    contents: [{ role: 'user', parts: [{ text: 'Consulta urgente' }] }]
  });

  assert.strictEqual(response.brainUsed, 'claude', 'Debe haber conmutado a Claude');
  assert.strictEqual(response.failoverNotice, true, 'Debe reportar failoverNotice');
  assert.strictEqual(response.text, 'Respuesta generada por Claude tras failover');
  assert.strictEqual(router.activeBrain, 'claude');
  assert.ok(router.lastFailover, 'Debe haber registrado los detalles del último failover');
  assert.strictEqual(router.lastFailover.from, 'gemini');
  assert.strictEqual(router.lastFailover.to, 'claude');
});

test('BrainRouter: Forzado de cerebro específico', async () => {
  const router = new BrainRouter();
  router.setForcedBrain('claude');

  router._callClaude = async () => {
    return { text: 'Forzado en Claude', usage: { inputTokens: 10, outputTokens: 10 } };
  };

  const response = await router.generateResponse({
    apiKeyGemini: 'mock-gemini-key',
    apiKeyClaude: 'mock-claude-key',
    contents: []
  });

  assert.strictEqual(response.brainUsed, 'claude');
  assert.strictEqual(router.getEffectiveBrain(), 'claude');
});

// ==========================================
// 4. PRUEBAS DE POLÍTICAS DE BLOQUEO DE SEGURIDAD
// ==========================================
test('Seguridad: Lista de PINs y Claves prohibidas por defecto', () => {
  const FORBIDDEN_PINS = ['1234', '0000', '1111', '123456', 'admin'];
  const FORBIDDEN_KEYS = [
    'jarvis-secret-key-32-chars-change-me',
    'jarvis-liseth-master-key-2026-safe-encrypt',
    'default',
    'secret'
  ];

  assert.ok(FORBIDDEN_PINS.includes('1234'), '1234 debe estar en lista prohibida');
  assert.ok(FORBIDDEN_PINS.includes('0000'), '0000 debe estar en lista prohibida');
  assert.ok(FORBIDDEN_KEYS.includes('jarvis-secret-key-32-chars-change-me'), 'Clave por defecto debe estar prohibida');
});

// ==========================================
// 5. PRUEBAS DE GOOGLE WORKSPACE CONNECTOR (lib/connectors/GoogleWorkspaceConnector.js)
// ==========================================
test('GoogleWorkspace: Catálogo de acciones y validación de marcas sensitive', () => {
  const actions = GoogleWorkspaceConnector.list_actions();
  assert.ok(Array.isArray(actions), 'list_actions debe retornar un array');
  assert.ok(actions.length >= 25, `Debe contener al menos 25 acciones (actual: ${actions.length})`);

  const actionMap = new Map(actions.map(a => [a.name, a]));

  // Gmail
  assert.ok(actionMap.has('google_list_emails'), 'Debe incluir google_list_emails');
  assert.ok(actionMap.has('google_search_emails'), 'Debe incluir google_search_emails');
  assert.ok(actionMap.has('google_read_email'), 'Debe incluir google_read_email');
  assert.strictEqual(actionMap.get('google_send_email').sensitive, true, 'google_send_email debe ser sensitive');
  assert.strictEqual(actionMap.get('google_reply_email').sensitive, true, 'google_reply_email debe ser sensitive');
  assert.strictEqual(actionMap.get('google_delete_email').sensitive, true, 'google_delete_email debe ser sensitive');
  assert.ok(actionMap.has('google_archive_email'), 'Debe incluir google_archive_email');
  assert.ok(actionMap.has('google_label_email'), 'Debe incluir google_label_email');

  // Calendar
  assert.ok(actionMap.has('google_list_events'), 'Debe incluir google_list_events');
  assert.strictEqual(actionMap.get('google_create_event').sensitive, true, 'google_create_event debe ser sensitive');
  assert.strictEqual(actionMap.get('google_update_event').sensitive, true, 'google_update_event debe ser sensitive');
  assert.strictEqual(actionMap.get('google_delete_event').sensitive, true, 'google_delete_event debe ser sensitive');

  // Tasks
  assert.ok(actionMap.has('google_list_tasks'), 'Debe incluir google_list_tasks');
  assert.ok(actionMap.has('google_create_task'), 'Debe incluir google_create_task');
  assert.ok(actionMap.has('google_complete_task'), 'Debe incluir google_complete_task');
  assert.strictEqual(actionMap.get('google_delete_task').sensitive, true, 'google_delete_task debe ser sensitive');

  // Drive
  assert.ok(actionMap.has('google_list_drive_files'), 'Debe incluir google_list_drive_files');
  assert.ok(actionMap.has('google_search_drive_files'), 'Debe incluir google_search_drive_files');
  assert.ok(actionMap.has('google_read_drive_file'), 'Debe incluir google_read_drive_file');
  assert.strictEqual(actionMap.get('google_upload_drive_file').sensitive, true, 'google_upload_drive_file debe ser sensitive');
  assert.strictEqual(actionMap.get('google_move_drive_file').sensitive, true, 'google_move_drive_file debe ser sensitive');

  // Docs, Sheets, Slides
  assert.ok(actionMap.has('google_read_doc'), 'Debe incluir google_read_doc');
  assert.strictEqual(actionMap.get('google_create_doc').sensitive, true, 'google_create_doc debe ser sensitive');
  assert.strictEqual(actionMap.get('google_append_doc').sensitive, true, 'google_append_doc debe ser sensitive');
  assert.ok(actionMap.has('google_read_sheet'), 'Debe incluir google_read_sheet');
  assert.strictEqual(actionMap.get('google_create_sheet').sensitive, true, 'google_create_sheet debe ser sensitive');
  assert.strictEqual(actionMap.get('google_append_sheet_row').sensitive, true, 'google_append_sheet_row debe ser sensitive');
  assert.ok(actionMap.has('google_read_slides'), 'Debe incluir google_read_slides');
  assert.strictEqual(actionMap.get('google_create_slides').sensitive, true, 'google_create_slides debe ser sensitive');
  assert.strictEqual(actionMap.get('google_add_slide').sensitive, true, 'google_add_slide debe ser sensitive');

  // Contacts & YouTube
  assert.ok(actionMap.has('google_search_contacts'), 'Debe incluir google_search_contacts');
  assert.ok(actionMap.has('google_search_youtube'), 'Debe incluir google_search_youtube');
  assert.ok(actionMap.has('google_list_my_youtube_videos'), 'Debe incluir google_list_my_youtube_videos');
  assert.ok(actionMap.has('google_get_youtube_video_stats'), 'Debe incluir google_get_youtube_video_stats');
});

test('GoogleWorkspace: Comportamiento seguro cuando Google no está conectado', async () => {
  const { GoogleWorkspaceConnector: ConnectorClass } = GoogleWorkspaceConnector;
  const testConnector = new ConnectorClass();
  testConnector.connected = false;
  testConnector.tokens = null;

  const result = await testConnector.execute_action('google_list_emails', { maxResults: 3 });
  assert.ok(result.error, 'Debe devolver un objeto con mensaje de error informativo');
  assert.strictEqual(result.requiresConnection, true, 'Debe indicar que requiere conexión');
  assert.ok(result.error.includes('Google Workspace no está conectado'), 'Debe explicar que Google no está conectado');
});

test('GoogleWorkspace: Generación de URL de OAuth con scopes mínimos y offline', () => {
  GoogleWorkspaceConnector.setCredentials({
    clientId: 'test-client-id.apps.googleusercontent.com',
    redirectUri: 'http://localhost:3000/api/google/oauth2callback'
  });

  const authUrl = GoogleWorkspaceConnector.getAuthUrl();
  assert.ok(authUrl.startsWith('https://accounts.google.com/o/oauth2/v2/auth'), 'Debe ser URL oficial de Google OAuth');
  assert.ok(authUrl.includes('test-client-id'), 'Debe contener el clientId configurado');
  assert.ok(authUrl.includes('access_type=offline'), 'Debe solicitar access_type offline para refresh tokens');
  assert.ok(authUrl.includes('gmail.modify'), 'Debe incluir scope de Gmail');
  assert.ok(authUrl.includes('calendar.events'), 'Debe incluir scope de Calendar');
  assert.ok(authUrl.includes('tasks'), 'Debe incluir scope de Tasks');
  assert.ok(authUrl.includes('documents'), 'Debe incluir scope de Docs');
  assert.ok(authUrl.includes('spreadsheets'), 'Debe incluir scope de Sheets');
  assert.ok(authUrl.includes('presentations'), 'Debe incluir scope de Slides');
  assert.ok(authUrl.includes('contacts.readonly'), 'Debe incluir scope de Contacts');
  assert.ok(authUrl.includes('youtube.readonly'), 'Debe incluir scope de YouTube');
});

test('GoogleWorkspace: Ejecución con mock de API de YouTube Stats y Google Docs', async () => {
  const { GoogleWorkspaceConnector: ConnectorClass } = GoogleWorkspaceConnector;
  const mockConnector = new ConnectorClass();
  mockConnector.connected = true;
  mockConnector.tokens = {
    access_token: 'fake-valid-token',
    refresh_token_encrypted: 'fake:tag:data',
    expiry_date: Date.now() + 3600000
  };

  // Mock de _httpRequest para YouTube Video Stats
  mockConnector._httpRequest = async (hostname, path, method) => {
    if (path.includes('/youtube/v3/videos')) {
      return {
        items: [{
          id: 'testVideo123',
          snippet: { title: 'Tutorial de Liseth AI', channelTitle: 'Santiago Tech' },
          statistics: { viewCount: '1540', likeCount: '230', commentCount: '45' }
        }]
      };
    }
    if (path.includes('/v1/documents/testDocId')) {
      return {
        documentId: 'testDocId',
        title: 'Plan Semanal de Liseth',
        body: {
          content: [
            { paragraph: { elements: [{ textRun: { content: 'Objetivo: Máxima productividad con IA.\n' } }] } }
          ]
        }
      };
    }
    return {};
  };

  const ytResult = await mockConnector.execute_action('google_get_youtube_video_stats', { videoId: 'testVideo123' });
  assert.strictEqual(ytResult.title, 'Tutorial de Liseth AI');
  assert.strictEqual(ytResult.statistics.views, 1540);
  assert.strictEqual(ytResult.statistics.likes, 230);

  const docResult = await mockConnector.execute_action('google_read_doc', { documentId: 'testDocId' });
  assert.strictEqual(docResult.title, 'Plan Semanal de Liseth');
  assert.ok(docResult.text.includes('Objetivo: Máxima productividad'));
});

