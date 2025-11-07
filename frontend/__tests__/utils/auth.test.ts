import { login, logout, isAuthenticated, getCurrentUser } from '../../utils/auth'
import api from '../../utils/api'
import * as storage from '../../utils/storage'

jest.mock('../../utils/api')
jest.mock('../../utils/storage')

describe('Auth Utils', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('login', () => {
    it('should login successfully and store tokens', async () => {
      const mockResponse = {
        data: {
          access_token: 'mock_access_token',
          refresh_token: 'mock_refresh_token',
          token_type: 'bearer',
        },
      }
      ;(api.post as jest.Mock).mockResolvedValue(mockResponse)

      const result = await login('testuser', 'password123')

      expect(result).toBe(true)
      expect(api.post).toHaveBeenCalledWith('/api/v1/auth/login', {
        username: 'testuser',
        password: 'password123',
      })
      expect(storage.setItem).toHaveBeenCalledWith('access_token', 'mock_access_token')
      expect(storage.setItem).toHaveBeenCalledWith('refresh_token', 'mock_refresh_token')
    })

    it('should return false on login failure', async () => {
      ;(api.post as jest.Mock).mockRejectedValue(new Error('Invalid credentials'))

      const result = await login('testuser', 'wrongpassword')

      expect(result).toBe(false)
    })
  })

  describe('logout', () => {
    it('should clear all auth data', () => {
      logout()

      expect(storage.removeItem).toHaveBeenCalledWith('access_token')
      expect(storage.removeItem).toHaveBeenCalledWith('refresh_token')
      expect(storage.removeItem).toHaveBeenCalledWith('user')
    })
  })

  describe('isAuthenticated', () => {
    it('should return true when token exists', () => {
      ;(storage.getItem as jest.Mock).mockReturnValue('mock_token')

      expect(isAuthenticated()).toBe(true)
    })

    it('should return false when token does not exist', () => {
      ;(storage.getItem as jest.Mock).mockReturnValue(null)

      expect(isAuthenticated()).toBe(false)
    })
  })

  describe('getCurrentUser', () => {
    it('should return parsed user object', () => {
      const mockUser = { id: 1, username: 'testuser', role: 'doctor' }
      ;(storage.getItem as jest.Mock).mockReturnValue(JSON.stringify(mockUser))

      const user = getCurrentUser()

      expect(user).toEqual(mockUser)
    })

    it('should return null for invalid JSON', () => {
      ;(storage.getItem as jest.Mock).mockReturnValue('invalid json')

      const user = getCurrentUser()

      expect(user).toBeNull()
    })
  })
})

