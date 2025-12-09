/**
 * API client for backend communication
 * Based on OpenAPI specification
 */

// Auto-detect API URL for Codespaces or local development
function getApiBaseUrl() {
  // Use environment variable if set
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // Auto-detect Codespaces environment
  if (window.location.hostname.includes('github.dev') || window.location.hostname.includes('githubpreview.dev')) {
    // Codespaces URL format: https://<name>-<port>.app.github.dev
    // Replace any port with 8000 for backend
    const backendUrl = window.location.origin.replace(/-\d+\.app\.github\.dev/, '-8000.app.github.dev');
    return `${backendUrl}/api`;
  }
  
  // Default to localhost for local development
  return 'http://localhost:8000/api';
}

const API_BASE_URL = getApiBaseUrl();

// Debug logging
console.log('[API] Base URL:', API_BASE_URL);
console.log('[API] Current hostname:', window.location.hostname);

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include', // Include credentials for Codespaces authentication
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        errorData
      );
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return null;
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(`Network error: ${error.message}`, 0, null);
  }
}

// Session Management

export async function createSession(data = {}) {
  return fetchAPI('/sessions', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getSession(sessionId) {
  return fetchAPI(`/sessions/${sessionId}`);
}

export async function updateSession(sessionId, data) {
  return fetchAPI(`/sessions/${sessionId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteSession(sessionId) {
  return fetchAPI(`/sessions/${sessionId}`, {
    method: 'DELETE',
  });
}

// Code Management

export async function getCode(sessionId) {
  return fetchAPI(`/sessions/${sessionId}/code`);
}

export async function saveCode(sessionId, code, language) {
  return fetchAPI(`/sessions/${sessionId}/code`, {
    method: 'POST',
    body: JSON.stringify({ code, language }),
  });
}

// Code Execution

export async function executeCode(code, language, timeout = 5) {
  return fetchAPI('/execute', {
    method: 'POST',
    body: JSON.stringify({ code, language, timeout }),
  });
}

// Collaboration

export async function getParticipants(sessionId) {
  return fetchAPI(`/sessions/${sessionId}/participants`);
}

export async function getHistory(sessionId, limit = 50) {
  const params = new URLSearchParams({ limit: limit.toString() });
  return fetchAPI(`/sessions/${sessionId}/history?${params}`);
}

// Health Check

export async function checkHealth() {
  return fetchAPI('/health');
}

export { ApiError };
