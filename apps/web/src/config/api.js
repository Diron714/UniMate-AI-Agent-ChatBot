export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export const config = {
  API_BASE_URL,
  WS_URL: import.meta.env.VITE_WS_URL || 'ws://localhost:5000',
}

