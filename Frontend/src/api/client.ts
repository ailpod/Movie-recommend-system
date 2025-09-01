/**
 * API 客户端配置
 * 基于 axios 的 HTTP 客户端封装
 */
import axios, { 
  AxiosInstance, 
  AxiosError,
  InternalAxiosRequestConfig
} from 'axios'

// 环境配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const API_TIMEOUT = Number(import.meta.env.VITE_API_TIMEOUT) || 10000

// API 错误接口
export interface ApiError {
  message: string
  code?: number
  details?: any
}

// 创建 axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 自动添加 Authorization header
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    console.log('🚀 API Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error: AxiosError) => {
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.status, response.config.url)
    return response.data
  },
  (error: AxiosError) => {
    console.error('❌ Response Error:', error.response?.status, error.config?.url)
    
    // 处理认证错误 - 但不自动重定向
    if (error.response?.status === 401) {
      // Token 过期或无效，只清除本地存储
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      
      // 只在特定页面才重定向，避免在公共页面也重定向
      const currentPath = window.location.pathname
      if (currentPath.includes('/profile') || 
          currentPath.includes('/favorites') || 
          currentPath.includes('/history')) {
        window.location.href = '/login'
      }
    }
    
    // 统一错误格式
    const apiError: ApiError = {
      message: (error.response?.data as any)?.detail || 
               (error.response?.data as any)?.message || 
               error.message || 
               '请求失败',
      code: error.response?.status,
      details: error.response?.data
    }
    
    return Promise.reject(apiError)
  }
)

export { apiClient }
export default apiClient
