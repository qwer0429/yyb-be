import axios from 'axios';
import type { AxiosError, AxiosRequestConfig } from 'axios';
import { ElMessage } from 'element-plus';
import { useAuthStore } from '../stores/auth';

// 扩展 AxiosRequestConfig 类型以支持 _retry 属性
interface CustomAxiosRequestConfig extends AxiosRequestConfig {
  _retry?: boolean;
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 30000,
});

// 请求拦截器 - 自动添加 Token
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理错误和 Token 刷新
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as CustomAxiosRequestConfig;
    
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;
      const authStore = useAuthStore();
      
      try {
        // 尝试刷新 token
        const newToken = await authStore.refreshAccessToken();
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
        }
        return api(originalRequest);
      } catch (refreshError) {
        // 刷新失败，退出登录
        authStore.logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    // 处理其他错误
    const errorMsg = (error.response?.data as any)?.detail || 
                     (error.response?.data as any)?.message || 
                     '请求失败，请稍后重试';
    
    if (error.response?.status !== 401) {
      ElMessage.error(errorMsg);
    }
    
    return Promise.reject(error);
  }
);

export default api;
