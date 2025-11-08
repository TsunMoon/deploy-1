import axiosInstance from './axiosConfig'

class AuthService {
  async login(email, password) {
    if (!email || !password) {
      throw new Error('Email and password are required')
    }

    try {
      const response = await axiosInstance.post('/api/auth/login', {
        email,
        password
      })

      const userInfo = {
        id: response.data.id,
        email: response.data.email,
        name: response.data.name,
        role: response.data.role
      }

      localStorage.setItem('userInfo', JSON.stringify(userInfo))
      localStorage.setItem('accessToken', response.data.accessToken)
      localStorage.setItem('refreshToken', response.data.refreshToken || '')
      localStorage.setItem('isAuthenticated', 'true')

      return userInfo
    } catch (error) {
      const message = error.response?.data?.detail || error.message || 'Login failed'
      throw new Error(message)
    }
  }

  async logout() {
    try {
      await axiosInstance.post('/api/auth/logout')
    } catch (error) {
      console.error('Logout API error:', error)
    } finally {
      localStorage.removeItem('userInfo')
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('isAuthenticated')
      window.location.href = '/login'
    }
  }

  isAuthenticated() {
    return localStorage.getItem('isAuthenticated') === 'true'
  }

  getUserInfo() {
    const userInfo = localStorage.getItem('userInfo')
    return userInfo ? JSON.parse(userInfo) : null
  }

  getAccessToken() {
    return localStorage.getItem('accessToken')
  }
}

export const authService = new AuthService()
