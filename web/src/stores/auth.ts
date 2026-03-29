import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'
import { ElMessage } from 'element-plus'
import { encryptPassword } from '../utils/crypto'

interface User {
  id: number
  username: string
  email: string
  name?: string
  mobile?: string
  is_admin: boolean
  is_staff: boolean
}

interface TokenResponse {
  access: string
  refresh: string
  user: User
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const accessToken = ref<string>(localStorage.getItem('access_token') || '')
  const refreshToken = ref<string>(localStorage.getItem('refresh_token') || '')
  const user = ref<User | null>(null)
  const isLoading = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value)
  const username = computed(() => user.value?.username || '')
  const isAdmin = computed(() => user.value?.is_admin || false)
  const isRegularUser = computed(() => !user.value?.is_admin)

  // Actions
  const login = async (username: string, password: string) => {
    isLoading.value = true
    try {
      // 加密密码
      const response = await api.post<TokenResponse>('/api/token/', {
        username,
        password: encryptPassword(password)
      })
      
      accessToken.value = response.data.access
      refreshToken.value = response.data.refresh
      
      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)
      
      // 保存用户信息（包括角色）
      if (response.data.user) {
        user.value = response.data.user
        localStorage.setItem('user_info', JSON.stringify(response.data.user))
      }
      
      ElMessage.success('登录成功')
      return true
    } catch (error: any) {
      const msg = error.response?.data?.detail || '登录失败，请检查用户名和密码'
      ElMessage.error(msg)
      return false
    } finally {
      isLoading.value = false
    }
  }

  const fetchUserInfo = async () => {
    try {
      // 从本地存储获取用户信息
      const storedUser = localStorage.getItem('user_info')
      if (storedUser) {
        user.value = JSON.parse(storedUser)
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }

  const refreshAccessToken = async () => {
    try {
      const response = await api.post<TokenResponse>('/api/refresh/', {
        refresh: refreshToken.value
      })
      accessToken.value = response.data.access
      localStorage.setItem('access_token', response.data.access)
      return response.data.access
    } catch (error) {
      logout()
      throw error
    }
  }

  const logout = () => {
    accessToken.value = ''
    refreshToken.value = ''
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
    ElMessage.success('已退出登录')
  }

  const initAuth = () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      accessToken.value = token
      fetchUserInfo()
    }
  }

  return {
    accessToken,
    refreshToken,
    user,
    isLoading,
    isAuthenticated,
    username,
    isAdmin,
    isRegularUser,
    login,
    logout,
    refreshAccessToken,
    initAuth,
    fetchUserInfo
  }
})
