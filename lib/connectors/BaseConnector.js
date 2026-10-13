/**
 * BaseConnector - Interfaz Común para Conectores y Servicios
 * Cumple con el requisito 2: authenticate, list_actions, execute_action
 */
class BaseConnector {
  constructor(id, name, description) {
    this.id = id;
    this.name = name;
    this.description = description;
    this.connected = false;
  }

  /**
   * Autenticación con el servicio
   * @param {Object} credentials 
   * @returns {Promise<boolean>}
   */
  async authenticate(credentials) {
    throw new Error(`authenticate() no implementado en ${this.name}`);
  }

  /**
   * Lista las acciones disponibles que JARVIS puede invocar
   * @returns {Array<{name: string, description: string, parameters: Object, sensitive: boolean}>}
   */
  list_actions() {
    throw new Error(`list_actions() no implementado en ${this.name}`);
  }

  /**
   * Ejecuta una acción puntual
   * @param {string} actionName 
   * @param {Object} params 
   * @returns {Promise<Object>}
   */
  async execute_action(actionName, params) {
    throw new Error(`execute_action() no implementado en ${this.name}`);
  }

  /**
   * Retorna el estado actual de conexión y metadatos
   */
  getStatus() {
    return {
      id: this.id,
      name: this.name,
      description: this.description,
      connected: this.connected
    };
  }
}

module.exports = BaseConnector;
