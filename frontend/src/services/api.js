const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000';

async function request(path, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Request failed');
    return data;
  } catch (err) {
    console.error(`API Error: ${path}`, err);
    throw err;
  }
}

// Tools API
export const toolsApi = {
  list: (params = '') => request(`/api/tools${params ? '?' + params : ''}`),
  get: (id) => request(`/api/tools/${id}`),
  create: (data) => request('/api/tools', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => request(`/api/tools/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => request(`/api/tools/${id}`, { method: 'DELETE' }),
};

// Users API
export const usersApi = {
  list: (params = '') => request(`/api/users${params ? '?' + params : ''}`),
  get: (id) => request(`/api/users/${id}`),
  create: (data) => request('/api/users', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => request(`/api/users/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => request(`/api/users/${id}`, { method: 'DELETE' }),
};

// Lendings API
export const lendingsApi = {
  list: (params = '') => request(`/api/lendings${params ? '?' + params : ''}`),
  get: (id) => request(`/api/lendings/${id}`),
  create: (data) => request('/api/lendings', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => request(`/api/lendings/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => request(`/api/lendings/${id}`, { method: 'DELETE' }),
  approve: (id) => request(`/api/lendings/${id}/approve`, { method: 'POST' }),
  activate: (id) => request(`/api/lendings/${id}/activate`, { method: 'POST' }),
  return_tool: (id) => request(`/api/lendings/${id}/return`, { method: 'POST' }),
};

// AWS Status API
export const awsApi = {
  status: () => request('/api/aws/status'),
  metrics: () => request('/api/aws/metrics'),
  workflow: () => request('/api/aws/workflow'),
};
