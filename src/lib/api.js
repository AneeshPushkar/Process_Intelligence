function resolveApiBaseUrl() {
  let raw = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
  raw = raw.trim()
  if (raw && !raw.startsWith('http://') && !raw.startsWith('https://')) {
    raw = `https://${raw}`
  }
  const trimmed = raw.replace(/\/+$/, '')
  return trimmed.endsWith('/api') ? trimmed : `${trimmed}/api`
}

const API_BASE_URL = resolveApiBaseUrl()

export function getStoredToken() {
  return localStorage.getItem('processiq_token')
}

export function setStoredToken(token) {
  if (token) {
    localStorage.setItem('processiq_token', token)
  } else {
    localStorage.removeItem('processiq_token')
  }
}

export function getStoredUser() {
  try {
    const u = localStorage.getItem('processiq_user')
    return u ? JSON.parse(u) : null
  } catch {
    return null
  }
}

export function setStoredUser(user) {
  if (user) {
    localStorage.setItem('processiq_user', JSON.stringify(user))
  } else {
    localStorage.removeItem('processiq_user')
  }
}

async function request(endpoint, options = {}) {
  const token = getStoredToken()
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }

  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  })

  if (res.status === 204) {
    return null
  }

  const data = await res.json().catch(() => ({}))

  if (!res.ok) {
    const errorMsg = data.detail || 'An unexpected error occurred.'
    const error = new Error(errorMsg)
    error.status = res.status
    error.data = data
    throw error
  }

  return data
}

export const api = {
  auth: {
    register: (data) => request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
    login: (data) => request('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
    getMe: () => request('/auth/me'),
    logout: () => request('/auth/logout', { method: 'POST' }),
  },
  processes: {
    list: (params = {}) => {
      const qs = new URLSearchParams()
      if (params.search) qs.append('search', params.search)
      if (params.status && params.status !== 'all') qs.append('status', params.status)
      if (params.validation && params.validation !== 'all') qs.append('validation', params.validation)
      const query = qs.toString() ? `?${qs.toString()}` : ''
      return request(`/processes${query}`)
    },
    create: (data) => request('/processes', { method: 'POST', body: JSON.stringify(data) }),
    get: (id) => request(`/processes/${id}`),
    delete: (id) => request(`/processes/${id}`, { method: 'DELETE' }),
    analyze: (id) => request(`/processes/${id}/analyze`, { method: 'POST' }),
  },
  dashboard: {
    getStats: () => request('/dashboard/stats'),
  },
  health: {
    get: () => request('/health'),
  },
}
