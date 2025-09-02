<template>
  <header class="app-header">
    <div class="header-container">
      <!-- Logo和网站标题 -->
      <div class="logo-section">
        <router-link to="/" class="logo-link">
          <div class="logo">
            <span class="logo-icon"></span>
            <span class="logo-text">MovieSystem</span>
          </div>
        </router-link>
      </div>

      <!-- 导航菜单 -->
      <nav class="navigation">
        <router-link to="/" class="nav-link" :class="{ active: $route.name === 'Home' }">
          首页
        </router-link>
        <router-link to="/browse" class="nav-link" :class="{ active: $route.name === 'Browse' }">
          浏览
        </router-link>
        <router-link to="/recommend" class="nav-link" :class="{ active: $route.name === 'Recommend' }">
          推荐
        </router-link>
      </nav>

      <!-- 搜索框 -->
      <div class="search-section">
        <SearchBar />
      </div>

      <!-- 用户区域 -->
      <div class="user-section">
        <!-- 未登录状态 -->
        <div v-if="!authStore.isAuthenticated" class="auth-buttons">
          <router-link to="/login" class="login-btn">登录</router-link>
        </div>

        <!-- 已登录状态 -->
        <div v-else class="user-menu" @click="toggleUserMenu" ref="userMenuRef">
          <div class="user-avatar">
            <img 
              :src="getUserAvatar()" 
              :alt="authStore.userInfo?.username"
              @error="onAvatarError"
            >
            <span class="username">{{ authStore.userInfo?.username }}</span>
            <svg class="dropdown-arrow" :class="{ open: showUserMenu }" viewBox="0 0 24 24" fill="currentColor">
              <path d="m7 10 5 5 5-5H7Z"/>
            </svg>
          </div>
          
          <!-- 用户下拉菜单 -->
          <div class="user-dropdown" v-show="showUserMenu">
            <div class="user-info">
              <div class="user-details">
                <p class="user-name">{{ authStore.userInfo?.username }}</p>
                <p class="user-email">{{ authStore.userInfo?.email }}</p>
              </div>
            </div>
            <div class="menu-divider"></div>
            <div class="menu-items">
              <router-link to="/profile" class="menu-item">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
                个人资料
              </router-link>
              <router-link to="/favorites" class="menu-item">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                </svg>
                我的收藏
              </router-link>
              <router-link to="/history" class="menu-item">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M13,3A9,9 0 0,0 4,12H1L4.89,15.89L4.96,16.03L9,12H6A7,7 0 0,1 13,5A7,7 0 0,1 20,12A7,7 0 0,1 13,19C11.07,19 9.32,18.21 8.06,16.94L6.64,18.36C8.27,20 10.5,21 13,21A9,9 0 0,0 22,12A9,9 0 0,0 13,3Z"/>
                </svg>
                观看记录
              </router-link>
            </div>
            <div class="menu-divider"></div>
            <button @click="handleLogout" class="menu-item logout-btn">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.59L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
              </svg>
              退出登录
            </button>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import SearchBar from './SearchBar.vue'
import movieApi from '@/services/movieApi'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const showGenres = ref(false)
const showUserMenu = ref(false)
const genres = ref([])
const userMenuRef = ref(null)

// 获取电影类型列表
const fetchGenres = async () => {
  try {
    const response = await movieApi.getGenres()
    genres.value = response.genres || []
  } catch (error) {
    console.error('获取电影类型失败:', error)
    // 设置默认类型
    genres.value = [
      { id: 28, name: '动作' },
      { id: 35, name: '喜剧' },
      { id: 18, name: '剧情' },
      { id: 27, name: '恐怖' },
      { id: 10749, name: '爱情' },
      { id: 878, name: '科幻' }
    ]
  }
}

// 切换用户菜单显示
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

// 处理登出
const handleLogout = async () => {
  try {
    await authStore.logout()
  } catch (error) {
    console.error('登出失败:', error)
  }
  showUserMenu.value = false
  router.push('/')
}

// 头像加载错误处理
const onAvatarError = (event) => {
  // 如果加载失败，也使用指定的默认头像
  event.target.src = 'http://localhost:8000/static/identify.jpg'
}

// 获取用户头像
const getUserAvatar = () => {
  // 直接使用指定的头像路径
  return 'http://localhost:8000/static/identify.jpg'
}

// 点击外部关闭用户菜单
const handleClickOutside = (event) => {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target)) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  fetchGenres()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.app-header {
  background: rgba(0, 0, 0, 0.95);
  backdrop-filter: blur(15px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  width: 100%;
  z-index: 1000;
  padding: 0;
  transition: background-color 0.3s ease;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  gap: 20px;
}

/* Logo部分 */
.logo-section {
  flex-shrink: 0;
}

.logo-link {
  text-decoration: none;
  color: inherit;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
}

.logo-icon {
  font-size: 2rem;
  filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.5));
}

.logo-text {
  font-size: 1.5rem;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 导航部分 */
.navigation {
  display: flex;
  align-items: center;
  gap: 30px;
  flex-shrink: 0;
}

.nav-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
  position: relative;
  cursor: pointer;
}

.nav-link:hover,
.nav-link.active {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}
/* 
.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: -39px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 3px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
} */

/* 下拉菜单 */
.nav-dropdown {
  position: relative;
  cursor: pointer;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background: rgba(0, 0, 0, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 10px 0;
  min-width: 200px;
  margin-top: 10px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  z-index: 100;
}

.dropdown-item {
  display: block;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  padding: 12px 20px;
  transition: all 0.3s ease;
}

.dropdown-item:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

/* 搜索部分 */
.search-section {
  flex: 1;
  max-width: 400px;
  margin: 0 20px;
}

/* 用户区域 */
.user-section {
  flex-shrink: 0;
  position: relative;
}

.auth-buttons {
  display: flex;
  gap: 12px;
  align-items: center;
}

.login-btn {
  padding: 8px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

/* 用户菜单 */
.user-menu {
  position: relative;
  cursor: pointer;
}

.user-avatar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px;
  border-radius: 50px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.user-avatar:hover {
  background: rgba(255, 255, 255, 0.1);
}

.user-avatar img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.username {
  color: white;
  font-weight: 500;
  font-size: 0.9rem;
}

.dropdown-arrow {
  width: 16px;
  height: 16px;
  fill: rgba(255, 255, 255, 0.6);
  transition: transform 0.3s ease;
}

.dropdown-arrow.open {
  transform: rotate(180deg);
}

/* 用户下拉菜单 */
.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: rgba(0, 0, 0, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 0;
  min-width: 280px;
  margin-top: 10px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  z-index: 100;
  overflow: hidden;
}

.user-info {
  padding: 20px;
  background: rgba(255, 255, 255, 0.02);
}

.user-details .user-name {
  color: white;
  font-weight: 600;
  font-size: 1rem;
  margin: 0 0 4px 0;
}

.user-details .user-email {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
  margin: 0;
}

.menu-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 0;
}

.menu-items {
  padding: 8px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  padding: 12px 20px;
  transition: all 0.3s ease;
  border: none;
  background: none;
  width: 100%;
  cursor: pointer;
  font-size: 0.9rem;
}

.menu-item:hover {
  color: white;
  background: rgba(255, 255, 255, 0.05);
}

.menu-item svg {
  width: 18px;
  height: 18px;
  fill: currentColor;
  flex-shrink: 0;
}

.logout-btn {
  color: #ff6b6b;
}

.logout-btn:hover {
  background: rgba(255, 107, 107, 0.1);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .header-container {
    padding: 15px 15px;
    gap: 15px;
  }

  .search-section {
    max-width: 300px;
  }

  .navigation {
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .header-container {
    flex-wrap: wrap;
    gap: 10px;
  }

  .logo-text {
    display: none;
  }

  .navigation {
    display: none;
  }

  .search-section {
    flex: 1;
    order: 3;
    max-width: none;
    margin: 0;
    width: 100%;
  }

  .user-section {
    order: 2;
  }

  .username {
    display: none;
  }
}

@media (max-width: 480px) {
  .header-container {
    padding: 10px 15px;
  }

  .logo-icon {
    font-size: 1.5rem;
  }

  .user-dropdown {
    right: -10px;
    min-width: 260px;
  }
}
</style>
