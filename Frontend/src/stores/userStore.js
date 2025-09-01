import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref(null)
  const isLoggedIn = ref(false)
  const token = ref('')

  // 计算属性
  const userInfo = computed(() => user.value)
  const isAuthenticated = computed(() => isLoggedIn.value && !!user.value)

  // 登录
  const login = (userData) => {
    user.value = userData
    isLoggedIn.value = true
    token.value = `token_${userData.id}_${Date.now()}`
    
    // 存储到localStorage
    localStorage.setItem('user', JSON.stringify(userData))
    localStorage.setItem('token', token.value)
    localStorage.setItem('isLoggedIn', 'true')
  }

  // 登出
  const logout = () => {
    user.value = null
    isLoggedIn.value = false
    token.value = ''
    
    // 清除localStorage
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    localStorage.removeItem('isLoggedIn')
  }

  // 从localStorage恢复用户状态
  const restoreUser = () => {
    const savedUser = localStorage.getItem('user')
    const savedToken = localStorage.getItem('token')
    const savedLoginStatus = localStorage.getItem('isLoggedIn')

    if (savedUser && savedToken && savedLoginStatus === 'true') {
      user.value = JSON.parse(savedUser)
      token.value = savedToken
      isLoggedIn.value = true
    }
  }

  // 更新用户信息
  const updateUser = (userData) => {
    if (user.value) {
      user.value = { ...user.value, ...userData }
      localStorage.setItem('user', JSON.stringify(user.value))
    }
  }

  // 初始化时恢复用户状态
  restoreUser()

  return {
    user,
    isLoggedIn,
    token,
    userInfo,
    isAuthenticated,
    login,
    logout,
    restoreUser,
    updateUser
  }
})
