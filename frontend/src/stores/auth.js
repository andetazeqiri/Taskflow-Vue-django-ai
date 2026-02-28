import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/axios'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!accessToken.value)

  const login = async (username, password) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/token/', {
        username,
        password
      })
      accessToken.value = response.data.access
      refreshToken.value = response.data.refresh
      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Login failed'
      console.error('Login error:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    router.push('/login')
  }

  const register = async (username, password, email) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/register/', {
        username,
        password,
        password_confirm: password,
        email
      })
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Registration failed'
      console.error('Register error:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  const refreshAccessToken = async () => {
    try {
      const response = await api.post('/token/refresh/', {
        refresh: refreshToken.value
      })
      accessToken.value = response.data.access
      localStorage.setItem('access_token', response.data.access)
      return true
    } catch (err) {
      logout()
      return false
    }
  }

  return {
    
    user,
    accessToken,
    refreshToken,
    loading,
    error,
    
    isAuthenticated,
    
    login,
    logout,
    register,
    refreshAccessToken
  }
})
