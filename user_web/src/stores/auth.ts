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
  const isRegularUser = computed(() => user.value?.is_admin === false)

  // Actions
  const register = async (userData: {
    username: string
    password: string
    password_confirm: string
    mobile?: string
    name?: string
  }) => {
    isLoading.value = true
    try {
      // 加密密码
      const encryptedData = {
        ...userData,
        password: encryptPassword(userData.password),
        password_confirm: encryptPassword(userData.password_confirm)
      }
      const response = await api.post<TokenResponse>('/api/register/', encryptedData)
      
      accessToken.value = response.data.access
      refreshToken.value = response.data.refresh
      
      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)
      
      // 保存用户信息
      if (response.data.user) {
        user.value = response.data.user
        localStorage.setItem('user_info', JSON.stringify(response.data.user))
      }
      
      ElMessage.success('注册成功')
      return true
    } catch (error: any) {
      const msg = error.response?.data?.error || '注册失败，请稍后重试'
      ElMessage.error(msg)
      return false
    } finally {
      isLoading.value = false
    }
  }

  const login = async (username: string, password: string) => {
    isLoading.value = true
    try {
      // 加密密码
      const response = await api.post<TokenResponse>('/api/token/', {
        username,
        password: encryptPassword(password)
      })
      
      // 检查是否为管理员，管理员不能登录用户端
      if (response.data.user.is_admin) {
        ElMessage.error('管理员请使用后台管理系统登录')
        return false
      }
      
      accessToken.value = response.data.access
      refreshToken.value = response.data.refresh
      
      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)
      
      // 保存用户信息
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
    isRegularUser,
    register,
    login,
    logout,
    refreshAccessToken,
    initAuth,
    fetchUserInfo
  }
})
