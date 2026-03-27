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
      // 登录接口的 401 不需要刷新 token，直接抛出错误让业务层处理
      const isLoginRequest = error.config?.url?.includes('/token/')
      if (!isLoginRequest && authStore.refreshToken) {
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
      } else if (!isLoginRequest) {
        authStore.logout()
        window.location.href = '/login'
      }
    }
    
    return Promise.reject(error)
  }
)

export default api
