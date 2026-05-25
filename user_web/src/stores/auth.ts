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
  
  // 用户权限相关
  const permissions = computed(() => user.value?.permissions || [])
  const accessibleSystems = computed(() => {
    let systems = user.value?.accessible_systems || []
    // 兼容旧数据：所有已登录用户默认拥有 user_portal 和 smart_doctor
    if (!systems.includes('user_portal')) {
      systems = [...systems, 'user_portal']
    }
    if (!systems.includes('smart_doctor')) {
      systems = [...systems, 'smart_doctor']
    }
    // 兼容旧数据：管理员额外拥有 admin_system
    if (user.value?.is_admin && !systems.includes('admin_system')) {
      systems = [...systems, 'admin_system']
    }
    return systems.length > 0 ? systems : ['user_portal']
  })
  
  // 检查是否有指定权限
  const hasPermission = (permission: string) => {
    return accessibleSystems.value.includes(permission)
  }

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
      const msg = error.response?.data?.detail || '用户名或密码错误，请重新输入'
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
    if (!refreshToken.value) {
      logout()
      throw new Error('Refresh token 不存在，请重新登录')
    }
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

  // 解析 JWT 的 exp 字段，判断 token 是否过期
  const isTokenExpired = (token: string): boolean => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      return payload.exp * 1000 < Date.now()
    } catch {
      return true
    }
  }

  const initAuth = () => {
    const token = localStorage.getItem('access_token')
    const refresh = localStorage.getItem('refresh_token')

    if (token && !isTokenExpired(token)) {
      accessToken.value = token
      if (refresh) refreshToken.value = refresh
      fetchUserInfo()
    } else if (refresh && !isTokenExpired(refresh)) {
      // access token 过期但 refresh token 仍有效，保留状态让后续请求触发刷新
      accessToken.value = token || ''
      refreshToken.value = refresh
    } else {
      // access token 和 refresh token 都过期或不存在，彻底清理
      logout()
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
    register,
    login,
    logout,
    refreshAccessToken,
    initAuth,
    fetchUserInfo
  }
})
