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
  permissions?: string[]
  accessible_systems?: string[]
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
  
  // 权限相关
  const permissions = computed(() => user.value?.permissions || [])
  const accessibleSystems = computed(() => user.value?.accessible_systems || [])
  
  const hasPermission = (permission: string) => {
    return accessibleSystems.value.includes(permission)
  }

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

  // 通过 token 自动登录（用于 iframe 门户单点登录）
  const autoLoginFromToken = async (token: string) => {
    try {
      // 先设置 token，以便验证请求能带上
      accessToken.value = token
      localStorage.setItem('access_token', token)
      
      // 调用用户信息接口验证 token 有效性
      const response = await api.get('/api/me/')
      
      if (response.data) {
        const userData: User = {
          id: response.data.id,
          username: response.data.username,
          email: response.data.email,
          name: response.data.name,
          mobile: response.data.mobile,
          is_admin: response.data.is_admin,
          is_staff: response.data.is_staff,
          permissions: response.data.permissions || [],
          accessible_systems: response.data.accessible_systems || [],
        }
        user.value = userData
        localStorage.setItem('user_info', JSON.stringify(userData))
        
        // 检查是否有后台管理权限
        if (!userData.is_admin && !userData.is_staff) {
          ElMessage.error('您没有权限访问后台管理系统')
          logout()
          return false
        }
        
        return true
      }
      return false
    } catch (error: any) {
      console.error('Token 自动登录失败:', error)
      logout()
      return false
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
    permissions,
    accessibleSystems,
    hasPermission,
    login,
    autoLoginFromToken,
    logout,
    refreshAccessToken,
    initAuth,
    fetchUserInfo
  }
})
