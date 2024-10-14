import api from './api'
import { setItem, removeItem, getItem } from './storage'

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface User {
  id: number
  username: string
  role: string
}

export const login = async (username: string, password: string): Promise<boolean> => {
  try {
    const response = await api.post<LoginResponse>('/api/v1/auth/login', {
      username,
      password,
    })

    const { access_token, refresh_token } = response.data
    setItem('access_token', access_token)
    setItem('refresh_token', refresh_token)

    // Also fetch and store user info
    const userResponse = await api.get<User>('/api/v1/auth/me')
    setItem('user', JSON.stringify(userResponse.data))

    return true
  } catch (error) {
    console.error('Login failed:', error)
    return false
  }
}

export const logout = (): void => {
  removeItem('access_token')
  removeItem('refresh_token')
  removeItem('user')
  window.location.href = '/login'
}

export const getCurrentUser = (): User | null => {
  const userStr = getItem('user')
  if (!userStr) return null
  try {
    return JSON.parse(userStr)
  } catch {
    return null
  }
}

export const fetchCurrentUser = async (): Promise<User> => {
  const response = await api.get<User>('/api/v1/auth/me')
  setItem('user', JSON.stringify(response.data))
  return response.data
}

export const isAuthenticated = (): boolean => {
  return !!getItem('access_token')
}
