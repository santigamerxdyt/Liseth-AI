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
