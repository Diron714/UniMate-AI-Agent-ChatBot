import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors with token refresh
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // If 401 and not already retrying, attempt token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // If already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        }).catch(err => {
          return Promise.reject(err)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem('refreshToken')
      
      if (!refreshToken) {
        // No refresh token, logout
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        processQueue(error, null)
        window.location.href = '/login'
        return Promise.reject(error)
      }

      try {
        const { data } = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
          refreshToken
        })
        
        const { token: newToken, refreshToken: newRefreshToken } = data
        localStorage.setItem('token', newToken)
        if (newRefreshToken) {
          localStorage.setItem('refreshToken', newRefreshToken)
        }
        
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        processQueue(null, newToken)
        
        return api(originalRequest)
      } catch (refreshError) {
        // Refresh failed, logout
        processQueue(refreshError, null)
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export const auth = {
  login: async (email, password) => {
    const { data } = await api.post('/api/auth/login', { email, password })
    return data
  },
  
  register: async (email, password) => {
    const { data } = await api.post('/api/auth/register', { email, password })
    return data
  },
  
  getMe: async () => {
    const { data } = await api.get('/api/auth/me')
    return data
  },
}

export const chat = {
  sendMessage: async (message, context = {}) => {
    const { data } = await api.post('/api/chat/send', { message, context })
    return data
  },
  
  getHistory: async (page = 1) => {
    const { data } = await api.get(`/api/chat/history?page=${page}`)
    return data
  },
}

// Export for convenience
export const login = auth.login
export const register = auth.register
export const getMe = auth.getMe
export const sendMessage = chat.sendMessage

export default api

