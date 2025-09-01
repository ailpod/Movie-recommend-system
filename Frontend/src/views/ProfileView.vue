<template>
  <div class="profile-view">
    <!-- 英雄区域 -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="user-avatar-large">
          <img 
            :src="getUserAvatar()" 
            :alt="userInfo?.username"
            @error="onAvatarError"
          >
          <div class="avatar-glow"></div>
        </div>
        <h1 class="hero-title">{{ userInfo?.username || '加载中...' }}</h1>
        <p class="hero-subtitle">{{ userInfo?.email || '获取用户信息中...' }}</p>
      </div>
      <div class="hero-background">
        <div class="background-overlay"></div>
      </div>
    </section>

    <!-- 用户信息卡片 -->
    <div class="content-container">
      <div class="info-grid">
        <div class="info-card">
          <div class="info-icon">👤</div>
          <div class="info-content">
            <div class="info-label">年龄</div>
            <div class="info-value">{{ userInfo?.age || '未设置' }}</div>
          </div>
        </div>
        
        <div class="info-card">
          <div class="info-icon">⚤</div>
          <div class="info-content">
            <div class="info-label">性别</div>
            <div class="info-value">{{ getGenderText(userInfo?.gender) }}</div>
          </div>
        </div>
        
        <div class="info-card">
          <div class="info-icon">📅</div>
          <div class="info-content">
            <div class="info-label">注册时间</div>
            <div class="info-value">{{ formatDate(userInfo?.created_at) }}</div>
          </div>
        </div>
        
        <div class="info-card">
          <div class="info-icon">❤️</div>
          <div class="info-content">
            <div class="info-label">收藏电影</div>
            <div class="info-value">{{ favoriteCount }} 部</div>
          </div>
        </div>
        
        <div class="info-card" v-if="userInfo?.updated_at">
          <div class="info-icon">🔄</div>
          <div class="info-content">
            <div class="info-label">最后更新</div>
            <div class="info-value">{{ formatDate(userInfo?.updated_at) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { fetchFavorites } from '@/api/userActions.js'

const router = useRouter()
const authStore = useAuthStore()

// 用户信息
const userInfo = ref(null)
// 收藏电影数
const favoriteCount = ref(0)

// 获取用户头像
const getUserAvatar = () => {
  // 直接使用指定的头像路径
  return 'http://localhost:8000/static/identify.jpg'
}

// 头像加载错误处理
const onAvatarError = (event) => {
  // 如果加载失败，也使用指定的默认头像
  event.target.src = 'http://localhost:8000/static/identify.jpg'
}

// 性别文本转换
const getGenderText = (gender) => {
  switch (gender) {
    case 'male': return '男'
    case 'female': return '女'
    case 'other': return '其他'
    default: return '未设置'
  }
}

// 日期格式化
const formatDate = (dateString) => {
  if (!dateString) return '未设置'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return '无效日期'
  }
}

// 获取收藏电影数
const fetchFavoriteCount = async () => {
  try {
    if (!authStore.isAuthenticated) {
      favoriteCount.value = 0
      return
    }
    
    const response = await fetchFavorites()
    const favorites = response || []
    favoriteCount.value = favorites.length
    console.log('收藏电影数:', favoriteCount.value)
  } catch (error) {
    console.error('获取收藏电影数失败:', error)
    favoriteCount.value = 0
  }
}

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    // 检查用户是否已登录
    if (!authStore.isAuthenticated) {
      console.warn('用户未登录，跳转到登录页面')
      router.push('/login')
      return
    }

    // 如果 store 中已有用户信息，直接使用
    if (authStore.userInfo) {
      userInfo.value = authStore.userInfo
      console.log('从 store 获取的用户信息:', userInfo.value)
      return
    }

    // 从 auth store 重新获取用户信息
    await authStore.fetchUserInfo()
    userInfo.value = authStore.userInfo
    console.log('从后端数据库获取的真实用户信息:', userInfo.value)
    
  } catch (error) {
    console.error('获取用户信息失败:', error)
    
    // 如果是认证错误，跳转到登录页面
    if (error.code === 401 || error.message?.includes('401')) {
      console.warn('认证失败，跳转到登录页面')
      await authStore.logout()
    } else {
      console.error('获取用户信息时发生其他错误:', error)
    }
  }
}                                           

// 组件挂载时获取数据
onMounted(async () => {
  // 初始化 auth store（如果还未初始化）
  await authStore.initialize()
  
  // 获取用户信息
  await fetchUserInfo()
  
  // 获取收藏电影数
  await fetchFavoriteCount()
})

// 监听认证状态变化
watch(() => authStore.isAuthenticated, (newValue) => {
  if (!newValue) {
    // 如果用户退出登录，跳转到登录页面
    router.push('/login')
  }
}, { immediate: true })

// 监听用户信息变化，自动更新本地显示
watch(() => authStore.userInfo, (newUserInfo) => {
  if (newUserInfo) {
    userInfo.value = newUserInfo
  }
}, { immediate: true, deep: true })
</script>

<style scoped>
/* 全局重置确保无边距 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.profile-view {
  min-height: 100vh;
  position: relative;
  padding-top: 100px; /* 为固定导航栏留出空间 */
  /* 与 HomeView 相同的科技感背景 */
  background: 
    linear-gradient(
      135deg,
      rgba(0, 0, 0, 0.85) 0%,
      rgba(13, 25, 43, 0.9) 25%,
      rgba(27, 38, 59, 0.9) 50%,
      rgba(65, 84, 118, 0.9) 75%,
      rgba(0, 0, 0, 0.95) 100%
    ),
    url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920&h=1080&fit=crop&crop=center') center/cover;
  background-attachment: fixed;
  background-repeat: no-repeat;
  background-size: cover;
  width: 100vw;
  margin: 0 !important;
  padding: 0 !important;
  overflow-x: hidden;
  position: relative;
  left: 50%;
  right: 50%;
  margin-left: -50vw !important;
  margin-right: -50vw !important;
}

/* 英雄区域 */
.hero-section {
  position: relative;
  height: 50vh;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  overflow: hidden;
  margin-bottom: 5vh;
}

.hero-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: transparent;
  z-index: -1;
}

.background-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(
      ellipse at center,
      rgba(0, 0, 0, 0.3) 0%,
      rgba(0, 0, 0, 0.7) 100%
    );
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 600px;
  padding: 0 20px;
}

/* 用户头像 */
.user-avatar-large {
  position: relative;
  width: 150px;
  height: 150px;
  margin: 0 auto 30px;
}

.user-avatar-large img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid rgba(0, 255, 255, 0.6);
  box-shadow: 
    0 0 30px rgba(0, 255, 255, 0.4),
    0 0 60px rgba(0, 255, 255, 0.2);
  position: relative;
  z-index: 2;
}

.avatar-glow {
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  border-radius: 50%;
  background: 
    radial-gradient(
      circle,
      rgba(0, 255, 255, 0.3) 0%,
      rgba(0, 255, 255, 0.1) 50%,
      transparent 100%
    );
  animation: pulse 2s ease-in-out infinite;
  z-index: 1;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.1);
    opacity: 1;
  }
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  color: white;
  margin-bottom: 15px;
  text-shadow: 
    0 0 10px rgba(0, 255, 255, 0.5),
    0 0 20px rgba(0, 255, 255, 0.3),
    0 2px 20px rgba(0, 0, 0, 0.8);
  background: linear-gradient(
    45deg, 
    #ffffff 0%, 
    #00ffff 50%, 
    #ffffff 100%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.2rem;
  color: rgba(0, 255, 255, 0.8);
  font-weight: 300;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

/* 内容容器 */
.content-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

/* 信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.info-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 255, 255, 0.2);
  border-radius: 15px;
  padding: 25px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.info-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(0, 255, 255, 0.4);
  transform: translateY(-5px);
  box-shadow: 
    0 10px 30px rgba(0, 255, 255, 0.1),
    0 0 20px rgba(0, 255, 255, 0.1);
}

.info-icon {
  font-size: 2.5rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(0, 255, 255, 0.2), rgba(123, 104, 238, 0.2));
  border-radius: 50%;
  border: 2px solid rgba(0, 255, 255, 0.3);
  flex-shrink: 0;
}

.info-content {
  flex: 1;
}

.info-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 5px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.info-value {
  font-size: 1.3rem;
  color: white;
  font-weight: 600;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .user-avatar-large {
    width: 120px;
    height: 120px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .info-card {
    padding: 20px;
  }
  
  .info-icon {
    font-size: 2rem;
    width: 50px;
    height: 50px;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 1.8rem;
  }
  
  .content-container {
    margin: 0 10px;
    padding: 20px 15px;
  }
  
  .info-card {
    flex-direction: column;
    text-align: center;
    gap: 15px;
  }
}
</style>
