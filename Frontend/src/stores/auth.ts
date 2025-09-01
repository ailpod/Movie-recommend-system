/**
 * 用户认证状态管理
 * 使用 Pinia 进行状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginCredentials, RegisterData } from '@/types/auth'
import { authApi } from '@/api/modules/auth'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const userInfo = computed(() => user.value)
  const token = computed(() => accessToken.value) // 添加 token getter 以保持向后兼容

  // 动作
  const login = async (credentials: LoginCredentials) => {
    try {
      isLoading.value = true
      error.value = null

      const response = await authApi.login(credentials)
      
      // 保存 token
      accessToken.value = response.access_token
      if (response.refresh_token) {
        refreshToken.value = response.refresh_token
        localStorage.setItem('refresh_token', response.refresh_token)
      }
      
      localStorage.setItem('access_token', response.access_token)

      // 获取用户信息
      await fetchUserInfo()

      return response
    } catch (err: any) {
      error.value = err.response?.data?.detail || '登录失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const register = async (data: RegisterData) => {
    try {
      isLoading.value = true
      error.value = null

      const response = await authApi.register(data)
      return response
    } catch (err: any) {
      error.value = err.response?.data?.detail || '注册失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      if (accessToken.value) {
        await authApi.logout()
      }
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      // 清除本地数据
      user.value = null
      accessToken.value = null
      refreshToken.value = null
      
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      
      // 重定向到登录页
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
  }

  const fetchUserInfo = async () => {
    try {
      if (!accessToken.value) return

      const userInfo = await authApi.getCurrentUser()
      user.value = userInfo
    } catch (err: any) {
      console.error('Failed to fetch user info:', err)
      // 只在初始化时抛出错误，由调用者决定如何处理
      throw err
    }
  }

  const refreshAccessToken = async () => {
    try {
      if (!refreshToken.value) {
        throw new Error('No refresh token available')
      }

      // TODO: 实现 token 刷新 API 调用
      // const response = await authApi.refreshToken(refreshToken.value)
      
      // 暂时先退出登录，后续需要实现 refresh token API
      await logout()
      throw new Error('Token refresh not implemented yet')
    } catch (err) {
      console.error('Token refresh failed:', err)
      await logout()
      throw err
    }
  }

  const updateProfile = async (data: Partial<User>) => {
    try {
      isLoading.value = true
      error.value = null

      const updatedUser = await authApi.updateProfile(data)
      user.value = { ...user.value, ...updatedUser }

      return updatedUser
    } catch (err: any) {
      error.value = err.response?.data?.detail || '更新个人信息失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const changePassword = async (oldPassword: string, newPassword: string) => {
    try {
      isLoading.value = true
      error.value = null

      // TODO: 实现修改密码 API 调用
      // await authApi.changePassword(oldPassword, newPassword)
      
      throw new Error('Change password not implemented yet')
    } catch (err: any) {
      error.value = err.response?.data?.detail || '修改密码失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 初始化 - 静默检查认证状态
  const initialize = async () => {
    try {
      if (accessToken.value) {
        await fetchUserInfo()
      }
    } catch (error) {
      // 静默处理错误，不要重定向
      console.warn('认证状态检查失败，清除本地 token:', error)
      accessToken.value = null
      refreshToken.value = null
      user.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  // 清除错误
  const clearError = () => {
    error.value = null
  }

  return {
    // 状态
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,
    
    // 计算属性
    isAuthenticated,
    userInfo,
    token,
    
    // 动作
    login,
    register,
    logout,
    fetchUserInfo,
    refreshAccessToken,
    updateProfile,
    changePassword,
    initialize,
    clearError
  }
})
