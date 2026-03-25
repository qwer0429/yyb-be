import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const authStore = useAuthStore()
    
    if (error.response?.status === 401) {
      // Token 过期，尝试刷新
      if (authStore.refreshToken) {
        try {
          await authStore.refreshAccessToken()
          // 重试原请求
          const config = error.config
          config.headers.Authorization = `Bearer ${authStore.accessToken}`
          return api(config)
        } catch (refreshError) {
          // 刷新失败，登出
          authStore.logout()
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      } else {
        authStore.logout()
        window.location.href = '/login'
      }
    }
    
    // 显示错误信息
    const msg = error.response?.data?.detail || error.response?.data?.error || '请求失败'
    ElMessage.error(msg)
    
    return Promise.reject(error)
  }
)

export default api
