import { create } from 'zustand'
import { login as apiLogin, register as apiRegister, getMe } from '../utils/api'

export const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem('token') || null,
  
  login: async (email, password) => {
    const response = await apiLogin(email, password)
    localStorage.setItem('token', response.token)
    if (response.refreshToken) {
      localStorage.setItem('refreshToken', response.refreshToken)
    }
    set({ token: response.token, user: response.user })
    return response
  },
  
  register: async (email, password) => {
    const response = await apiRegister(email, password)
    localStorage.setItem('token', response.token)
    if (response.refreshToken) {
      localStorage.setItem('refreshToken', response.refreshToken)
    }
    set({ token: response.token, user: response.user })
    return response
  },
  
  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    set({ token: null, user: null })
  },
  
  loadUser: async () => {
    const token = localStorage.getItem('token')
    if (token) {
      try {
        const user = await getMe()
        set({ user, token })
      } catch (error) {
        localStorage.removeItem('token')
        set({ token: null, user: null })
      }
    }
  },
}))

