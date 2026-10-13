/**
 * lib/tts/EdgeTTS.js
 * Motor de Síntesis de Voz Neuronal Ultra-Realista (Microsoft Edge TTS)
 * Conexión WebSocket moderna a api.msedgeservices.com con token Sec-MS-GEC dinámico.
 */

const crypto = require('crypto');
const WebSocket = require('ws');

const TRUSTED_CLIENT_TOKEN = '6A5AA1D4EAFF4E9FB37E23D68491D6F4';
const WIN_EPOCH = 11644473600;
const S_TO_NS = 1e9;
const CHROMIUM_FULL_VERSION = '130.0.2849.68';
const SEC_MS_GEC_VERSION = `1-${CHROMIUM_FULL_VERSION}`;
const EXTENSION_ORIGIN = 'chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold';

// Caché en memoria para frases frecuentes (máx 50 audios)
const audioCache = new Map();
const MAX_CACHE_SIZE = 50;

/**
 * Genera el token de seguridad Sec-MS-GEC requerido por Microsoft
 */
function generateSecMsGec() {
  let ticks = Date.now() / 1000;
  ticks += WIN_EPOCH;
  ticks -= ticks % 300; // Bloques de 5 minutos
  const ticksNs = Math.floor(ticks * (S_TO_NS / 100));
  const strToHash = `${ticksNs}${TRUSTED_CLIENT_TOKEN}`;
  return crypto.createHash('sha256').update(strToHash, 'ascii').digest('hex').toUpperCase();
}

/**
 * Genera el SSML para la síntesis de voz
 */
function buildSsml(text, voice = 'es-MX-DaliaNeural', pitch = '+15Hz', rate = '+5%') {
  const clean = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');

  const lang = voice.split('-').slice(0, 2).join('-');
  return `<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='${lang}'>` +
    `<voice name='${voice}'>` +
    `<prosody pitch='${pitch}' rate='${rate}' volume='+0%'>` +
    `${clean}` +
    `</prosody></voice></speak>`;
}

/**
 * Sintetiza texto a voz retornando un Buffer de audio MP3 completo.
 * @param {string} text - Texto a sintetizar
 * @param {object} options - { voice, pitch, rate, timeoutMs }
 * @returns {Promise<Buffer>}
 */
function synthesize(text, options = {}) {
  const voice = options.voice || 'es-MX-DaliaNeural';
  const pitch = options.pitch || '+15Hz';
  const rate = options.rate || '+5%';
  const timeoutMs = options.timeoutMs || 15000;

  // Clave de caché para respuestas inmediatas
  const cacheKey = `${voice}_${pitch}_${rate}_${text.trim()}`;
  if (audioCache.has(cacheKey)) {
    return Promise.resolve(audioCache.get(cacheKey));
  }

  return new Promise((resolve, reject) => {
    const secMsGec = generateSecMsGec();
    const connId = crypto.randomUUID().replace(/-/g, '');
    const url = `wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1?Ocp-Apim-Subscription-Key=${TRUSTED_CLIENT_TOKEN}&Sec-MS-GEC=${secMsGec}&Sec-MS-GEC-Version=${SEC_MS_GEC_VERSION}&ConnectionId=${connId}`;

    let ws = null;
    let timer = null;
    const audioBuffers = [];

    const cleanup = () => {
      if (timer) clearTimeout(timer);
      if (ws) {
        try {
          ws.removeAllListeners();
          if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
            ws.close();
          }
        } catch (e) {}
      }
    };

    timer = setTimeout(() => {
      cleanup();
      reject(new Error(`Timeout al sintetizar voz con Edge TTS (${timeoutMs}ms)`));
    }, timeoutMs);

    try {
      ws = new WebSocket(url, {
        headers: {
          'Pragma': 'no-cache',
          'Cache-Control': 'no-cache',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
          'Origin': EXTENSION_ORIGIN
        }
      });
    } catch (wsInitErr) {
      cleanup();
      return reject(wsInitErr);
    }

    ws.on('open', () => {
      const ts = new Date().toISOString();
      const configJson = JSON.stringify({
        context: {
          synthesis: {
            audio: {
              metadataoptions: {
                sentenceBoundaryEnabled: "false",
                wordBoundaryEnabled: "false"
              },
              outputFormat: "audio-24khz-48kbitrate-mono-mp3"
            }
          }
        }
      });
      const configMsg = `X-Timestamp:${ts}\r\nContent-Type:application/json; charset=utf-8\r\nPath:speech.config\r\n\r\n${configJson}`;
      ws.send(configMsg);

      const reqId = crypto.randomUUID().replace(/-/g, '');
      const ssml = buildSsml(text, voice, pitch, rate);
      const ssmlMsg = `X-RequestId:${reqId}\r\nX-Timestamp:${ts}\r\nContent-Type:application/ssml+xml\r\nPath:ssml\r\n\r\n${ssml}`;
      ws.send(ssmlMsg);
    });

    ws.on('message', (data, isBinary) => {
      if (isBinary) {
        if (data.length > 2) {
          const headerLen = data.readUInt16BE(0);
          if (headerLen <= data.length - 2) {
            const headerStr = data.subarray(2, 2 + headerLen).toString('utf8');
            if (headerStr.includes('Path:audio')) {
              const audioChunk = data.subarray(2 + headerLen);
              if (audioChunk.length > 0) {
                audioBuffers.push(audioChunk);
              }
            }
          }
        }
      } else {
        const textMsg = data.toString('utf8');
        if (textMsg.includes('Path:turn.end')) {
          cleanup();
          const finalBuffer = Buffer.concat(audioBuffers);
          if (finalBuffer.length === 0) {
            return reject(new Error('No se recibieron datos de audio de Edge TTS'));
          }

          // Guardar en caché si no es excesivamente grande
          if (audioCache.size >= MAX_CACHE_SIZE) {
            const oldestKey = audioCache.keys().next().value;
            audioCache.delete(oldestKey);
          }
          audioCache.set(cacheKey, finalBuffer);

          resolve(finalBuffer);
        }
      }
    });

    ws.on('error', (err) => {
      cleanup();
      reject(new Error(`Error de WebSocket en Edge TTS: ${err.message}`));
    });

    ws.on('unexpected-response', (req, res) => {
      cleanup();
      reject(new Error(`Respuesta inesperada de Edge TTS: HTTP ${res.statusCode}`));
    });
  });
}

module.exports = {
  synthesize,
  generateSecMsGec,
  buildSsml,
  TRUSTED_CLIENT_TOKEN
};
