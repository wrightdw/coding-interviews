/**
 * WebSocket client for real-time collaboration
 * Based on WebSocket Protocol specification
 */

// Auto-detect WebSocket URL for Codespaces or local development
function getWebSocketUrl() {
  // Use environment variable if set
  if (import.meta.env.VITE_WS_URL) {
    return import.meta.env.VITE_WS_URL;
  }
  
  // Auto-detect Codespaces environment
  if (window.location.hostname.includes('github.dev') || window.location.hostname.includes('githubpreview.dev')) {
    // Codespaces URL format: https://<name>-<port>.app.github.dev
    // Replace any port with 8000 for backend and use wss://
    const currentHostname = window.location.hostname;
    const backendHostname = currentHostname.replace(/-\d+\.app\.github\.dev/, '-8000.app.github.dev');
    return `wss://${backendHostname}`;
  }
  
  // Default to localhost for local development
  return 'ws://localhost:8000';
}

const WS_BASE_URL = getWebSocketUrl();

export class WebSocketClient {
  constructor(sessionId, userId, userName) {
    this.sessionId = sessionId;
    this.userId = userId;
    this.userName = userName;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.messageHandlers = new Map();
    this.isConnecting = false;
    this.isIntentionallyClosed = false;
  }

  connect() {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return Promise.resolve();
    }

    this.isConnecting = true;
    this.isIntentionallyClosed = false;

    return new Promise((resolve, reject) => {
      try {
        const url = `${WS_BASE_URL}/ws/sessions/${this.sessionId}`;
        console.log('Connecting to WebSocket:', url);
        
        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          
          // Send join message
          this.send({
            type: 'join',
            userId: this.userId,
            data: {
              name: this.userName
            }
          });

          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnecting = false;
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket closed:', event.code, event.reason);
          this.isConnecting = false;

          if (!this.isIntentionallyClosed && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Reconnecting... (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
              this.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
          }
        };

      } catch (error) {
        console.error('Failed to create WebSocket:', error);
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  handleMessage(message) {
    const { type } = message;
    
    // Call all registered handlers for this message type
    const handlers = this.messageHandlers.get(type) || [];
    handlers.forEach(handler => {
      try {
        handler(message);
      } catch (error) {
        console.error(`Error in message handler for ${type}:`, error);
      }
    });

    // Also call generic message handler
    const allHandlers = this.messageHandlers.get('*') || [];
    allHandlers.forEach(handler => {
      try {
        handler(message);
      } catch (error) {
        console.error('Error in generic message handler:', error);
      }
    });
  }

  on(messageType, handler) {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, []);
    }
    this.messageHandlers.get(messageType).push(handler);
    
    // Return unsubscribe function
    return () => {
      const handlers = this.messageHandlers.get(messageType);
      if (handlers) {
        const index = handlers.indexOf(handler);
        if (index > -1) {
          handlers.splice(index, 1);
        }
      }
    };
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Message not sent:', message);
    }
  }

  sendCodeUpdate(code, changes = []) {
    this.send({
      type: 'code-update',
      userId: this.userId,
      data: {
        code,
        changes
      }
    });
  }

  sendCursorPosition(line, column) {
    this.send({
      type: 'cursor-position',
      userId: this.userId,
      data: {
        line,
        column
      }
    });
  }

  sendLanguageChange(language) {
    this.send({
      type: 'language-change',
      userId: this.userId,
      data: {
        language
      }
    });
  }

  startHeartbeat(interval = 30000) {
    this.stopHeartbeat();
    
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' });
      }
    }, interval);
  }

  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  disconnect() {
    this.isIntentionallyClosed = true;
    this.stopHeartbeat();
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.messageHandlers.clear();
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}
