/**
 * 认证相关 API
 */
import { apiClient } from '../client'
import type { LoginCredentials, RegisterData, AuthResponse, User } from '@/types/auth'

export const authApi = {
  // 用户注册
  register: (data: RegisterData): Promise<User> => {
    return apiClient.post('/auth/register', data)
  },

  // 用户登录
  login: (credentials: LoginCredentials): Promise<AuthResponse> => {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)
    
    return apiClient.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
  },

  // 获取当前用户信息
  getCurrentUser: (): Promise<User> => {
    return apiClient.get('/users/me')
  },

  // 更新用户信息
  updateProfile: (data: Partial<User>): Promise<User> => {
    return apiClient.put('/users/me', data)
  },

  // 退出登录
  logout: (): Promise<void> => {
    return apiClient.post('/auth/logout')
  }
}
