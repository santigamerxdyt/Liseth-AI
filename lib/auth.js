/**
 * Módulo de Autenticación, Hashing con scrypt y Sesiones Criptográficas
 * Para JARVIS / Liseth
 */
const crypto = require('crypto');

// Almacén en memoria de intentos fallidos para Rate Limiting
const loginAttempts = new Map();
const MAX_ATTEMPTS = 5;
const LOCKOUT_PERIOD_MS = 15 * 60 * 1000; // 15 minutos

function getMasterKey() {
  const secret = process.env.MASTER_ENCRYPTION_KEY || '';
  return crypto.createHash('sha256').update(secret).digest();
}

/**
 * Deriva un hash seguro del PIN usando scrypt con salt aleatorio
 */
function hashPin(pin) {
  return new Promise((resolve, reject) => {
    const salt = crypto.randomBytes(16).toString('hex');
    crypto.scrypt(pin, salt, 64, (err, derivedKey) => {
      if (err) return reject(err);
      resolve(`${salt}:${derivedKey.toString('hex')}`);
    });
  });
}

/**
 * Verifica un PIN contra un hash scrypt (salt:derivedHex)
 */
function verifyPin(pin, storedHash) {
  return new Promise((resolve, reject) => {
    if (!storedHash || !storedHash.includes(':')) {
      return resolve(false);
    }
    const [salt, keyHex] = storedHash.split(':');
    const storedBuffer = Buffer.from(keyHex, 'hex');

    crypto.scrypt(pin, salt, 64, (err, derivedKey) => {
      if (err) return reject(err);
      // Comparación en tiempo constante para evitar ataques de temporización
      if (derivedKey.length !== storedBuffer.length) {
        return resolve(false);
      }
      resolve(crypto.timingSafeEqual(derivedKey, storedBuffer));
    });
  });
}

/**
 * Crea un token de sesión firmado: sessionId.expiresAt.signature
 */
function createSessionToken(ttlMs = 24 * 60 * 60 * 1000) {
  const sessionId = crypto.randomBytes(18).toString('hex');
  const expiresAt = Date.now() + ttlMs;
  const payload = `${sessionId}.${expiresAt}`;
  const signature = crypto.createHmac('sha256', getMasterKey()).update(payload).digest('hex');
  return `${payload}.${signature}`;
}

/**
 * Valida un token de sesión firmado
 */
function verifySessionToken(token) {
  if (!token || typeof token !== 'string') return false;
  const parts = token.split('.');
  if (parts.length !== 3) return false;

  const [sessionId, expiresAtStr, receivedSig] = parts;
  const expiresAt = parseInt(expiresAtStr, 10);
  if (isNaN(expiresAt) || Date.now() > expiresAt) {
    return false; // Expirado
  }

  const payload = `${sessionId}.${expiresAtStr}`;
  const expectedSig = crypto.createHmac('sha256', getMasterKey()).update(payload).digest('hex');
  
  const expectedBuf = Buffer.from(expectedSig, 'hex');
  const receivedBuf = Buffer.from(receivedSig, 'hex');
  if (expectedBuf.length !== receivedBuf.length) return false;

  return crypto.timingSafeEqual(expectedBuf, receivedBuf);
}

/**
 * Rate Limiting contra ataques de fuerza bruta por IP
 */
function checkRateLimit(ip) {
  const now = Date.now();
  const record = loginAttempts.get(ip);
  if (!record) return { allowed: true };

  if (now > record.resetTime) {
    loginAttempts.delete(ip);
    return { allowed: true };
  }

  if (record.count >= MAX_ATTEMPTS) {
    const remainingSec = Math.ceil((record.resetTime - now) / 1000);
    return { allowed: false, remainingSec };
  }

  return { allowed: true };
}

function recordFailedAttempt(ip) {
  const now = Date.now();
  const record = loginAttempts.get(ip) || { count: 0, resetTime: now + LOCKOUT_PERIOD_MS };
  record.count += 1;
  loginAttempts.set(ip, record);
}

function clearAttempts(ip) {
  loginAttempts.delete(ip);
}

/**
 * Helper para extraer cookies del header
 */
function parseCookies(req) {
  const list = {};
  const cookieHeader = req.headers.cookie;
  if (!cookieHeader) return list;

  cookieHeader.split(';').forEach(cookie => {
    const parts = cookie.split('=');
    if (parts.length >= 2) {
      list[parts[0].trim()] = decodeURIComponent(parts.slice(1).join('=').trim());
    }
  });
  return list;
}

module.exports = {
  hashPin,
  verifyPin,
  createSessionToken,
  verifySessionToken,
  checkRateLimit,
  recordFailedAttempt,
  clearAttempts,
  parseCookies
};
