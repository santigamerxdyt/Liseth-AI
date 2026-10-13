/**
 * Registro de Auditoría y Control de Acciones Sensibles
 * Registra todo lo que JARVIS ejecuta y gestiona aprobaciones
 */
const fs = require('fs');
const path = require('path');

const AUDIT_LOG_FILE = path.join(__dirname, '..', '..', 'data', 'audit_log.json');

class AuditManager {
  constructor() {
    this.logs = [];
    this.pendingConfirmations = new Map();
    this.init();
  }

  init() {
    try {
      if (fs.existsSync(AUDIT_LOG_FILE)) {
        const raw = fs.readFileSync(AUDIT_LOG_FILE, 'utf8');
        this.logs = JSON.parse(raw);
      } else {
        this.save();
      }
    } catch (e) {
      this.logs = [];
    }
  }

  save() {
    try {
      const dir = path.dirname(AUDIT_LOG_FILE);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(AUDIT_LOG_FILE, JSON.stringify(this.logs.slice(-300), null, 2), 'utf8');
    } catch (e) {
      console.error('Error guardando audit log:', e.message);
    }
  }

  logAction({ connector, action, params, status, result, userConfirmed = false, autoApproved = false }) {
    const entry = {
      id: 'audit_' + Date.now() + '_' + Math.random().toString(36).substr(2, 5),
      timestamp: new Date().toISOString(),
      connector,
      action,
      params,
      status, // 'success', 'pending_confirmation', 'rejected', 'failed'
      result,
      userConfirmed,
      autoApproved
    };
    this.logs.unshift(entry);
    this.save();
    return entry;
  }

  createPendingConfirmation(connector, action, params, reason) {
    const confirmId = 'req_' + Date.now() + '_' + Math.random().toString(36).substr(2, 5);
    const item = {
      id: confirmId,
      connector,
      action,
      params,
      reason,
      createdAt: new Date().toISOString()
    };
    this.pendingConfirmations.set(confirmId, item);
    this.logAction({
      connector,
      action,
      params,
      status: 'pending_confirmation',
      result: { reason, confirmId }
    });
    return item;
  }

  resolveConfirmation(confirmId, approved) {
    const pending = this.pendingConfirmations.get(confirmId);
    if (!pending) return null;
    this.pendingConfirmations.delete(confirmId);

    const logEntry = this.logs.find(l => l.result && l.result.confirmId === confirmId);
    if (logEntry) {
      logEntry.status = approved ? 'approved' : 'rejected';
      logEntry.userConfirmed = approved;
      this.save();
    }
    return { ...pending, approved };
  }

  getLogs(limit = 100) {
    return this.logs.slice(0, limit);
  }

  getPendingConfirmations() {
    return Array.from(this.pendingConfirmations.values());
  }
}

module.exports = new AuditManager();
