/**
 * API service layer for the fraud detection backend.
 */
const API_BASE = '/api';

// ─── Token management ──────────────────────────────────────
function getToken() {
  return localStorage.getItem('auth_token');
}

function setToken(token) {
  localStorage.setItem('auth_token', token);
}

function clearToken() {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('auth_user');
}

function getAuthUser() {
  try {
    return JSON.parse(localStorage.getItem('auth_user') || 'null');
  } catch {
    return null;
  }
}

function setAuthUser(user) {
  localStorage.setItem('auth_user', JSON.stringify(user));
}

// ─── Base request helper ────────────────────────────────────
async function request(url, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${url}`, {
    headers,
    ...options,
  });
  if (!res.ok) {
    if (res.status === 401) {
      clearToken();
    }
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

// ─── Authentication ────────────────────────────────────────
export const registerUser = async (data) => {
  const result = await request('/auth/register', { method: 'POST', body: JSON.stringify(data) });
  setToken(result.access_token);
  setAuthUser({ id: result.user_id, username: result.username, role: result.role });
  return result;
};

export const loginUser = async (data) => {
  const result = await request('/auth/login', { method: 'POST', body: JSON.stringify(data) });
  setToken(result.access_token);
  setAuthUser({ id: result.user_id, username: result.username, role: result.role });
  return result;
};

export const loginWithGoogle = async (credential) => {
  const result = await request('/auth/google', { method: 'POST', body: JSON.stringify({ credential }) });
  setToken(result.access_token);
  setAuthUser({ id: result.user_id, username: result.username, role: result.role });
  return result;
};

export const loginWithGithub = async (code) => {
  const result = await request('/auth/github', { method: 'POST', body: JSON.stringify({ code }) });
  setToken(result.access_token);
  setAuthUser({ id: result.user_id, username: result.username, role: result.role });
  return result;
};

export const logoutUser = () => {
  clearToken();
  window.location.href = '/login';
};

export const fetchProfile = () => request('/auth/profile');
export { getToken, getAuthUser, clearToken };

// ─── Analytics ─────────────────────────────────────────────
export const fetchDashboardStats = () => request('/analytics/dashboard-stats');
export const fetchFraudsByHour = (hours = 24) => request(`/analytics/frauds-per-hour?hours=${hours}`);
export const fetchFraudsByLocation = (limit = 10) => request(`/analytics/frauds-per-location?limit=${limit}`);
export const fetchFraudsByUser = (limit = 10) => request(`/analytics/frauds-per-user?limit=${limit}`);
export const fetchConfidenceDistribution = () => request('/analytics/confidence-distribution');
export const fetchAlerts = (limit = 20) => request(`/analytics/alerts?limit=${limit}`);
export const triggerModelTraining = () => request('/analytics/model-training');

// ─── Transactions ──────────────────────────────────────────
export const fetchTransactions = (skip = 0, limit = 50, filterType = 'all') => {
  let url = `/transactions/?skip=${skip}&limit=${limit}`;
  if (filterType === 'fraud') url += '&fraud_only=true';
  if (filterType === 'legit') url += '&legit_only=true';
  return request(url);
};

export const fetchTransaction = (id) => request(`/transactions/${id}`);

export const createTransaction = (data) =>
  request('/transactions/', { method: 'POST', body: JSON.stringify(data) });

export const simulateTransaction = (data) =>
  request('/transactions/simulate', { method: 'POST', body: JSON.stringify(data) });

// ─── Users ─────────────────────────────────────────────────
export const fetchUsers = (skip = 0, limit = 50) => request(`/users/?skip=${skip}&limit=${limit}`);
export const createUser = (data) => request('/users/', { method: 'POST', body: JSON.stringify(data) });

// ─── Fraud Intelligence ───────────────────────────────────
export const explainFraud = (transactionId, question) =>
  request('/explain-fraud', {
    method: 'POST',
    body: JSON.stringify({ transaction_id: transactionId, question }),
  });

export const chatQuery = (message, sessionId = 'default') =>
  request('/chatbot/query', {
    method: 'POST',
    body: JSON.stringify({ message, session_id: sessionId }),
  });

export const generateReport = (transactionId) => request(`/generate-report/${transactionId}`);

export const downloadReport = (transactionId) =>
  `${API_BASE}/download-report/${transactionId}`;

export const fetchBehavioralAnalysis = (userId) =>
  request(`/behavioral-analysis/${userId}`);

// ─── Datasets ──────────────────────────────────────────────
export const uploadDataset = async (file, name, domain) => {
  const formData = new FormData();
  formData.append('file', file);
  if (name) formData.append('name', name);
  if (domain) formData.append('domain', domain);

  const token = getToken();
  const headers = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/datasets/upload`, {
    method: 'POST',
    headers,
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Upload failed');
  }
  return res.json();
};

export const fetchDatasets = () => request('/datasets/');

export const trainOnDataset = (datasetId) =>
  request(`/datasets/train/${datasetId}`, { method: 'POST' });

export const deleteDataset = (datasetId) =>
  request(`/datasets/${datasetId}`, { method: 'DELETE' });

export const streamOnDataset = (datasetId) =>
  request(`/datasets/stream/${datasetId}`, { method: 'POST' });

// ─── WebSocket ─────────────────────────────────────────────
export function connectWebSocket(onMessage) {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const ws = new WebSocket(`${protocol}//${window.location.host}/ws/alerts`);

  ws.onopen = () => console.log('[WS] Connected to fraud alerts stream');
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (e) {
      console.error('[WS] Parse error:', e);
    }
  };
  ws.onerror = (e) => console.error('[WS] Error:', e);
  ws.onclose = () => {
    console.log('[WS] Disconnected. Reconnecting in 3s...');
    setTimeout(() => connectWebSocket(onMessage), 3000);
  };

  // Keep alive
  const pingInterval = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) ws.send('ping');
  }, 30000);

  return () => {
    clearInterval(pingInterval);
    ws.close();
  };
}
