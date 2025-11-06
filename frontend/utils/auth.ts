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
    console.log('Attempting login for user:', username)
    console.log('API baseURL:', process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')

    const response = await api.post<LoginResponse>('/api/v1/auth/login', {
      username,
      password,
    })

    console.log('Login response received:', response.status)

    const { access_token, refresh_token } = response.data
    setItem('access_token', access_token)
    setItem('refresh_token', refresh_token)

    // Also fetch and store user info
    const userResponse = await api.get<User>('/api/v1/auth/me')
    setItem('user', JSON.stringify(userResponse.data))

    console.log('Login successful!')
    return true
  } catch (error: any) {
    console.error('Login failed:', error)
    console.error('Error response:', error.response?.data)
    console.error('Error status:', error.response?.status)
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
