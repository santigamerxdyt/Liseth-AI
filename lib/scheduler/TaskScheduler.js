/**
 * TaskScheduler - Programador Persistente de Tareas y Rutinas de JARVIS
 * Gestiona recordatorios, resúmenes diarios/semanales, verificación de eventos y reportes de procesos
 * Persistencia en data/scheduled_tasks.json con supervivencia a reinicios del servidor
 */

const fs = require('fs');
const path = require('path');
const NotificationManager = require('../notifications/NotificationManager');

const TASKS_FILE = path.join(__dirname, '..', '..', 'data', 'scheduled_tasks.json');

const DEFAULT_TASKS = [
  {
    id: 'task_daily_morning_summary',
    title: 'Resumen Matutino Diario',
    type: 'daily_summary',
    schedule: 'cron:0 8 * * *', // Todos los días a las 08:00 AM
    timeOfDay: '08:00',
    enabled: true,
    lastRun: null,
    nextRun: null,
    params: { channel: 'all' }
  },
  {
    id: 'task_weekly_summary',
    title: 'Resumen Estratégico Semanal',
    type: 'weekly_summary',
    schedule: 'cron:30 8 * * 1', // Lunes a las 08:30 AM
    dayOfWeek: 1,
    timeOfDay: '08:30',
    enabled: true,
    lastRun: null,
    nextRun: null,
    params: { channel: 'all' }
  },
  {
    id: 'task_calendar_event_check',
    title: 'Verificación Periódica de Calendario y Citas',
    type: 'event_check',
    schedule: 'interval:15m', // Cada 15 minutos
    intervalMinutes: 15,
    enabled: true,
    lastRun: null,
    nextRun: null,
    params: { leadTimeMinutes: 30 }
  },
  {
    id: 'task_system_process_report',
    title: 'Reporte de Salud del Sistema y Consumo',
    type: 'process_report',
    schedule: 'interval:60m', // Cada 60 minutos
    intervalMinutes: 60,
    enabled: true,
    lastRun: null,
    nextRun: null,
    params: { channel: 'telegram' }
  }
];

class TaskScheduler {
  constructor() {
    this.tasks = [];
    this.timer = null;
    this.tickerIntervalMs = 30 * 1000; // Evaluar cada 30 segundos
    this.init();
  }

  init() {
    try {
      if (fs.existsSync(TASKS_FILE)) {
        const raw = fs.readFileSync(TASKS_FILE, 'utf8');
        this.tasks = JSON.parse(raw);
      } else {
        this.tasks = JSON.parse(JSON.stringify(DEFAULT_TASKS));
        this.save();
      }
    } catch (e) {
      console.warn('Error leyendo scheduled_tasks.json, cargando tareas por defecto:', e.message);
      this.tasks = JSON.parse(JSON.stringify(DEFAULT_TASKS));
    }

    // Inicializar fechas de nextRun para tareas activas que no tengan una
    this.tasks.forEach(t => {
      if (t.enabled && !t.nextRun) {
        t.nextRun = this.calculateNextRun(t);
      }
    });
    this.save();
  }

  save() {
    try {
      const dir = path.dirname(TASKS_FILE);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(TASKS_FILE, JSON.stringify(this.tasks, null, 2), 'utf8');
    } catch (e) {
      console.error('Error guardando tareas programadas en disco:', e.message);
    }
  }

  start() {
    if (this.timer) return;
    this.timer = setInterval(() => this.tick(), this.tickerIntervalMs);
    console.log('✓ Programador de tareas persistente (TaskScheduler) INICIADO');
  }

  stop() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }

  calculateNextRun(task) {
    const now = new Date();

    // 1. Intervalo relativo (ej. interval:15m)
    if (task.intervalMinutes || (task.schedule && task.schedule.startsWith('interval:'))) {
      const mins = task.intervalMinutes || parseInt(task.schedule.replace('interval:', '').replace('m', ''), 10) || 15;
      return new Date(now.getTime() + mins * 60 * 1000).toISOString();
    }

    // 2. Fecha y hora fija puntual (ej. at:2026-10-15T10:00:00Z o timestamp ISO)
    if (task.type === 'reminder' && task.at) {
      return new Date(task.at).toISOString();
    }

    // 3. Resumen diario (ej. timeOfDay: "08:00")
    if (task.timeOfDay) {
      const [h, m] = task.timeOfDay.split(':').map(Number);
      const target = new Date(now);
      target.setHours(h, m, 0, 0);

      // Si es semanal, ajustar al día de la semana específico (0=Domingo, 1=Lunes, ...)
      if (task.type === 'weekly_summary' && task.dayOfWeek !== undefined) {
        const currentDay = now.getDay();
        let diff = task.dayOfWeek - currentDay;
        if (diff < 0 || (diff === 0 && now >= target)) {
          diff += 7;
        }
        target.setDate(now.getDate() + diff);
      } else {
        // Diario
        if (now >= target) {
          target.setDate(target.getDate() + 1);
        }
      }
      return target.toISOString();
    }

    // Por defecto, 60 minutos
    return new Date(now.getTime() + 60 * 60 * 1000).toISOString();
  }

  async tick() {
    const nowIso = new Date().toISOString();
    const nowMs = Date.now();

    for (const task of this.tasks) {
      if (!task.enabled) continue;

      const nextRunMs = task.nextRun ? new Date(task.nextRun).getTime() : 0;
      if (nowMs >= nextRunMs) {
        try {
          await this.executeTask(task);
          task.lastRun = nowIso;
        } catch (err) {
          console.error(`[TaskScheduler] Error ejecutando tarea ${task.id} (${task.title}):`, err.message);
        }

        // Si era un recordatorio puntual sin recurrencia, desactivar
        if (task.type === 'reminder' && !task.recurring) {
          task.enabled = false;
        } else {
          task.nextRun = this.calculateNextRun(task);
        }
        this.save();
      }
    }
  }

  async executeTask(task) {
    console.log(`[TaskScheduler] Ejecutando tarea programada: [${task.id}] ${task.title}`);

    switch (task.type) {
      case 'reminder': {
        const message = task.params?.message || task.title;
        await NotificationManager.sendAlert(`⏰ *Recordatorio de Liseth*:\n${message}`);
        break;
      }

      case 'daily_summary': {
        await this._handleDailySummary(task);
        break;
      }

      case 'weekly_summary': {
        await this._handleWeeklySummary(task);
        break;
      }

      case 'event_check': {
        await this._handleEventCheck(task);
        break;
      }

      case 'process_report': {
        await this._handleProcessReport(task);
        break;
      }

      default: {
        if (task.params?.message) {
          await NotificationManager.sendAlert(task.params.message);
        }
      }
    }
  }

  async _handleDailySummary(task) {
    let agendaText = '• No hay eventos programados en su agenda inmediata.';
    try {
      const GoogleWorkspace = require('../connectors/GoogleWorkspaceConnector');
      if (GoogleWorkspace.connected) {
        const eventsData = await GoogleWorkspace.execute_action('google_list_events', { maxResults: 5 });
        if (eventsData.events && eventsData.events.length > 0) {
          agendaText = eventsData.events.map(e => `• ${e.summary} (${e.start})`).join('\n');
        }
      }
    } catch (e) {}

    const text = `🌅 *Buenos días, Santiago. Resumen Matutino de Liseth*:\n\n*Agenda para hoy*:\n${agendaText}\n\nEstoy a su entera disposición para una jornada altamente productiva.`;
    await NotificationManager.sendAlert(text);
  }

  async _handleWeeklySummary(task) {
    const text = `📊 *Resumen Semanal de Liseth*:\n\nIniciamos una nueva semana de alto rendimiento, Santiago.\nHe verificado sus tareas y procesos pre-asignados. Todo listo para maximizar sus resultados.`;
    await NotificationManager.sendAlert(text);
  }

  async _handleEventCheck(task) {
    try {
      const GoogleWorkspace = require('../connectors/GoogleWorkspaceConnector');
      if (!GoogleWorkspace.connected) return;

      const eventsData = await GoogleWorkspace.execute_action('google_list_events', { maxResults: 3 });
      if (eventsData.events && eventsData.events.length > 0) {
        const leadMs = (task.params?.leadTimeMinutes || 30) * 60 * 1000;
        const now = Date.now();

        for (const ev of eventsData.events) {
          if (!ev.start) continue;
          const startMs = new Date(ev.start).getTime();
          const diffMs = startMs - now;

          // Si el evento está a menos de leadTimeMinutes y no ha comenzado
          if (diffMs > 0 && diffMs <= leadMs) {
            const minutesLeft = Math.round(diffMs / 60000);
            await NotificationManager.sendAlert(`📅 *Aviso de Reunión Inminente*:\n"${ev.summary}" comienza en ${minutesLeft} minutos.`);
            break; // Evitar spam de múltiples eventos en una sola pasada
          }
        }
      }
    } catch (e) {}
  }

  async _handleProcessReport(task) {
    const uptimeHours = (process.uptime() / 3600).toFixed(1);
    const memUsageMb = Math.round(process.memoryUsage().rss / (1024 * 1024));
    const BrainRouter = require('../ai/BrainRouter');
    const todayTokens = (BrainRouter.tokenStats?.today?.input || 0) + (BrainRouter.tokenStats?.today?.output || 0);

    const report = `💻 *Reporte de Procesos & Salud de JARVIS*:\n• Uptime del servidor: ${uptimeHours} horas\n• Consumo de Memoria: ${memUsageMb} MB\n• Consumo de Tokens Hoy: ${todayTokens.toLocaleString()} tokens\n• Estado: Operativo y Estable`;
    await NotificationManager.sendAlert(report);
  }

  // --- MÉTODOS CRUD ---
  listTasks() {
    return this.tasks;
  }

  getTask(id) {
    return this.tasks.find(t => t.id === id);
  }

  createTask(data) {
    const id = data.id || `task_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
    const newTask = {
      id,
      title: data.title || 'Nueva Tarea Programada',
      type: data.type || 'reminder',
      schedule: data.schedule || 'interval:60m',
      timeOfDay: data.timeOfDay || null,
      dayOfWeek: data.dayOfWeek !== undefined ? data.dayOfWeek : null,
      intervalMinutes: data.intervalMinutes || null,
      at: data.at || null,
      recurring: Boolean(data.recurring),
      enabled: data.enabled !== false,
      lastRun: null,
      nextRun: null,
      params: data.params || {},
      createdAt: new Date().toISOString()
    };

    newTask.nextRun = this.calculateNextRun(newTask);
    this.tasks.push(newTask);
    this.save();
    return newTask;
  }

  updateTask(id, updates) {
    const idx = this.tasks.findIndex(t => t.id === id);
    if (idx === -1) return null;

    this.tasks[idx] = { ...this.tasks[idx], ...updates };
    if (updates.schedule || updates.timeOfDay || updates.intervalMinutes || updates.at || updates.enabled) {
      this.tasks[idx].nextRun = this.calculateNextRun(this.tasks[idx]);
    }
    this.save();
    return this.tasks[idx];
  }

  deleteTask(id) {
    const idx = this.tasks.findIndex(t => t.id === id);
    if (idx === -1) return false;
    this.tasks.splice(idx, 1);
    this.save();
    return true;
  }

  async triggerTask(id) {
    const task = this.getTask(id);
    if (!task) throw new Error(`Tarea ${id} no encontrada`);
    await this.executeTask(task);
    task.lastRun = new Date().toISOString();
    task.nextRun = this.calculateNextRun(task);
    this.save();
    return task;
  }
}

const schedulerInstance = new TaskScheduler();
schedulerInstance.TaskScheduler = TaskScheduler;
module.exports = schedulerInstance;
