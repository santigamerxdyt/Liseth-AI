/**
 * Módulo de Cifrado y Seguridad Local
 * AES-256-GCM para tokens de OAuth y credenciales sensibles
 */
const crypto = require('crypto');

const ALGORITHM = 'aes-256-gcm';

function getMasterKey() {
  const secret = process.env.MASTER_ENCRYPTION_KEY || 'jarvis-liseth-default-secure-key-32b';
  return crypto.createHash('sha256').update(secret).digest();
}

function encrypt(text) {
  if (!text) return '';
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(ALGORITHM, getMasterKey(), iv);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  const tag = cipher.getAuthTag().toString('hex');
  return `${iv.toString('hex')}:${tag}:${encrypted}`;
}

function decrypt(cipherText) {
  if (!cipherText || !cipherText.includes(':')) return cipherText;
  try {
    const [ivHex, tagHex, encryptedHex] = cipherText.split(':');
    const iv = Buffer.from(ivHex, 'hex');
    const tag = Buffer.from(tagHex, 'hex');
    const decipher = crypto.createDecipheriv(ALGORITHM, getMasterKey(), iv);
    decipher.setAuthTag(tag);
    let decrypted = decipher.update(encryptedHex, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return decrypted;
  } catch (err) {
    console.error('Error descifrando dato sensible:', err.message);
    return null;
  }
}

module.exports = {
  encrypt,
  decrypt
};
