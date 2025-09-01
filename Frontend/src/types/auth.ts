/**
 * 用户认证相关的类型定义
 */

export interface User {
  id: number
  username: string
  email: string
  age?: number
  gender?: 'male' | 'female' | 'other'
  favorites?: string  // JSON 字符串
  watch_history?: string  // JSON 字符串
  preferences?: string  // JSON 字符串
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  age?: number
  gender?: 'male' | 'female' | 'other'
}

export interface AuthResponse {
  access_token: string
  refresh_token?: string
  token_type: 'bearer'
  user?: User
}
