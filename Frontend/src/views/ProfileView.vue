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

      <!-- 电影偏好设置 -->
      <div class="preferences-section">
        <div class="section-header">
          <h2>🎭 电影偏好设置</h2>
          <p>选择您喜欢的电影类型，我们将为您提供个性化推荐</p>
        </div>
        
        <div class="preferences-card">
          <div class="current-preferences" v-if="userInfo?.like_genres">
            <h3>当前偏好</h3>
            <div class="genre-tags">
              <span v-for="genre in userInfo.like_genres.split(',')" :key="genre" class="genre-tag current">
                {{ genre.trim() }}
              </span>
            </div>
          </div>
          
          <div class="genre-selector">
            <h3>选择电影类型 (可多选)</h3>
            <div class="genre-grid">
              <label 
                v-for="genre in availableGenres" 
                :key="genre" 
                class="genre-option"
                :class="{ selected: selectedGenres.includes(genre) }"
              >
                <input 
                  type="checkbox" 
                  :value="genre" 
                  v-model="selectedGenres"
                >
                <span class="genre-name">{{ genre }}</span>
              </label>
            </div>
          </div>
          
          <div class="preferences-actions">
            <button 
              @click="updatePreferences" 
              class="save-btn"
              :disabled="saving || selectedGenres.length === 0"
            >
              <span v-if="saving">保存中...</span>
              <span v-else>💾 保存偏好</span>
            </button>
            <button 
              @click="resetPreferences" 
              class="reset-btn"
              :disabled="saving"
            >
              🔄 重置
            </button>
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
import userApi from '@/services/userApi.js'

const router = useRouter()
const authStore = useAuthStore()

// 用户信息
const userInfo = ref(null)
// 收藏电影数
const favoriteCount = ref(0)

// 电影偏好相关
const selectedGenres = ref([])
const saving = ref(false)

// 可选的电影类型
const availableGenres = ref([
  '动作', '冒险', '喜剧', '剧情', '家庭', '奇幻', 
  '恐怖', '悬疑', '爱情', '科幻', '惊悚', '战争',
  '西部', '动画', '犯罪', '纪录片', '历史', '音乐',
  '运动', '传记', '儿童', '短片'
])

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
    // 同时更新选中的电影类型
    if (newUserInfo.like_genres) {
      selectedGenres.value = newUserInfo.like_genres.split(',').map(g => g.trim())
    }
  }
}, { immediate: true, deep: true })

// 初始化用户偏好
watch(() => userInfo.value?.like_genres, (newGenres) => {
  if (newGenres) {
    selectedGenres.value = newGenres.split(',').map(g => g.trim())
  } else {
    selectedGenres.value = []
  }
}, { immediate: true })

// 更新用户电影偏好
const updatePreferences = async () => {
  if (selectedGenres.value.length === 0) {
    alert('请至少选择一个电影类型！')
    return
  }

  saving.value = true
  try {
    const genres = selectedGenres.value.join(',')
    
    // 调用API更新用户信息
    const updateData = {
      like_genres: genres
    }
    
    const response = await userApi.updateUser(updateData)
    
    // 更新本地用户信息
    userInfo.value = { ...userInfo.value, like_genres: genres }
    authStore.updateUserInfo({ ...authStore.userInfo, like_genres: genres })
    
    alert('电影偏好更新成功！')
  } catch (error) {
    console.error('更新电影偏好失败:', error)
    alert('更新失败，请稍后重试')
  } finally {
    saving.value = false
  }
}

// 重置偏好
const resetPreferences = () => {
  selectedGenres.value = []
}
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

  .preferences-card {
    padding: 20px;
  }

  .genre-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .genre-option {
    padding: 15px;
    justify-content: center;
  }

  .preferences-actions {
    flex-direction: column;
  }

  .save-btn,
  .reset-btn {
    width: 100%;
  }
}

/* 电影偏好设置样式 */
.preferences-section {
  margin-top: 40px;
}

.section-header {
  text-align: center;
  margin-bottom: 30px;
}

.section-header h2 {
  font-size: 2rem;
  color: white;
  margin-bottom: 10px;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

.section-header p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
}

.preferences-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 255, 255, 0.2);
  border-radius: 20px;
  padding: 30px;
  backdrop-filter: blur(10px);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.current-preferences {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(0, 255, 255, 0.2);
}

.current-preferences h3 {
  color: white;
  margin-bottom: 15px;
  font-size: 1.2rem;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

.genre-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.genre-tag {
  padding: 8px 16px;
  border-radius: 25px;
  font-size: 0.9rem;
  font-weight: 500;
}

.genre-tag.current {
  background: linear-gradient(135deg, rgba(0, 255, 255, 0.8), rgba(123, 104, 238, 0.8));
  color: white;
  border: 1px solid rgba(0, 255, 255, 0.3);
  text-shadow: 0 0 5px rgba(0, 255, 255, 0.3);
}

.genre-selector h3 {
  color: white;
  margin-bottom: 20px;
  font-size: 1.2rem;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

.genre-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.genre-option {
  display: flex;
  align-items: center;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 255, 255, 0.2);
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  gap: 15px;
  position: relative;
  color: white;
}

.genre-option:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(0, 255, 255, 0.4);
  transform: translateY(-5px);
  box-shadow: 
    0 10px 30px rgba(0, 255, 255, 0.1),
    0 0 20px rgba(0, 255, 255, 0.1);
}

.genre-option.selected {
  background: rgba(0, 255, 255, 0.1);
  border-color: rgba(0, 255, 255, 0.5);
  transform: translateY(-5px);
  box-shadow: 
    0 10px 30px rgba(0, 255, 255, 0.2),
    0 0 20px rgba(0, 255, 255, 0.2);
}

.genre-option::before {
  content: '🎬';
  font-size: 1.5rem;
  flex-shrink: 0;
}

.genre-option input {
  display: none;
}

.genre-name {
  font-weight: 500;
  font-size: 1rem;
  text-shadow: 0 0 5px rgba(0, 255, 255, 0.3);
}

.preferences-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.save-btn,
.reset-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.save-btn {
  background: linear-gradient(135deg, rgba(0, 255, 255, 0.8), rgba(123, 104, 238, 0.8));
  color: white;
  border: 1px solid rgba(0, 255, 255, 0.3);
}

.save-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 
    0 6px 20px rgba(0, 255, 255, 0.4),
    0 0 20px rgba(0, 255, 255, 0.2);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.reset-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.reset-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 255, 255, 0.1);
}

.reset-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
