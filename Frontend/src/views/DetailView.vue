<template>
  <div class="detail-view">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载电影详情...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <div class="error-content">
        <h2>😕 加载失败</h2>
        <p>{{ error }}</p>
        <button @click="loadMovieDetail" class="retry-btn">重试</button>
        <button @click="$router.back()" class="back-btn">返回</button>
      </div>
    </div>

    <!-- 电影详情内容 -->
    <div v-else-if="movie" class="movie-detail">
      <!-- 全屏背景 -->
      <div class="movie-backdrop">
        <div class="backdrop-image" :style="{ backgroundImage: `url(${getImageUrl(movie.poster_path)})` }"></div>
        <div class="backdrop-overlay">
          <div class="gradient-overlay"></div>
        </div>
      </div>

      <!-- 主要内容区域 -->
      <div class="detail-content">
        <div class="container">
          <!-- 电影主要信息 -->
          <div class="movie-header">
            <div class="poster-section">
              <img 
                :src="getImageUrl(movie.poster_path)" 
                :alt="movie.title"
                class="movie-poster"
                @error="handleImageError"
              />
            </div>
            
            <div class="info-section">
              <h1 class="movie-title">{{ movie.title }}</h1>
              
              <div class="movie-meta">
                <span class="year">{{ movie.release_year || 'N/A' }}</span>
                <span class="genre">{{ getMovieGenres(movie) }}</span>
                <span class="rating">⭐ {{ formatRating(movie.avg_rate) }}</span>
              </div>
              
              <div class="movie-description">
                <p>{{ movie.description || '暂无简介' }}</p>
              </div>
              
              <div class="movie-details">
                <div class="detail-item" v-if="movie.director">
                  <strong>导演：</strong>{{ movie.director }}
                </div>
                <div class="detail-item" v-if="movie.actors">
                  <strong>主演：</strong>{{ movie.actors }}
                </div>
                <div class="detail-item" v-if="movie.vote">
                  <strong>投票数：</strong>{{ movie.vote }}
                </div>
              </div>
              
              <div class="action-buttons">
                <button 
                  :class="['btn-primary', { 'favorited': isFavorited, 'loading': favoriteLoading }]"
                  @click="toggleFavorite"
                  :disabled="favoriteLoading"
                >
                  <i v-if="favoriteLoading" class="fas fa-spinner fa-spin"></i>
                  <i v-else-if="isFavorited" class="fas fa-heart"></i>
                  <i v-else class="far fa-heart"></i>
                  {{ favoriteLoading ? '处理中...' : (isFavorited ? '已收藏' : '收藏') }}
                </button>
                <button class="btn-secondary" @click="$router.back()">返回</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 猜你喜欢推荐区域 -->
      <div v-if="movie" class="recommendations-section">
        <div class="container">
          <div class="section-header">
            <h2 class="section-title">
              <span class="icon">🎬</span>
              猜你喜欢
            </h2>
            <p class="section-subtitle">基于这部电影为你推荐</p>
          </div>

          <!-- 加载状态 -->
          <div v-if="recommendationsLoading" class="recommendations-loading">
            <div class="loading-spinner small"></div>
            <span>正在为您推荐...</span>
          </div>

          <!-- 推荐电影列表 -->
          <div v-else-if="recommendedMovies.length > 0" class="recommendations-grid">
            <div 
              v-for="movie in recommendedMovies" 
              :key="'rec-' + movie.id" 
              class="recommendation-card"
              @click="goToMovie(movie.id)"
            >
              <div class="rec-poster">
                <img 
                  :src="getImageUrl(movie.poster_path)" 
                  :alt="movie.title"
                  @error="handleImageError"
                />
                <div class="rec-rating">
                  <span>{{ formatRating(movie.avg_rate) }}</span>
                </div>
                <div class="rec-overlay">
                  <div class="play-btn">▶</div>
                </div>
              </div>
              
              <div class="rec-info">
                <h4 class="rec-title">{{ movie.title }}</h4>
                <div class="rec-meta">
                  <span class="rec-year">{{ movie.release_year }}</span>
                  <span class="rec-genre">{{ getMovieGenres(movie) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 无推荐时的提示 -->
          <div v-else class="no-recommendations">
            <p>暂无相关推荐</p>
          </div>
        </div>
      </div>
    </div>
    </div>
    
    <!-- Toast 提示 -->
    <div class="toast-container">
      <div 
        v-for="toast in toasts" 
        :key="toast.id"
        :class="['toast', `toast-${toast.type}`]"
        @click="removeToast(toast.id)"
      >
        <span>{{ toast.message }}</span>
        <button class="toast-close">&times;</button>
      </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import movieApi, { getImageUrl, formatRating } from '@/services/movieApi'
import { recordHistory, addFavorite, removeFavorite, checkFavoriteStatus } from '@/api/userActions.js'
import { useAuthStore } from '@/stores/auth'
import ratingApi from '@/services/ratingApi'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const movie = ref(null)
const recommendedMovies = ref([])
const loading = ref(false)
const recommendationsLoading = ref(false)
const error = ref(null)
const isFavorited = ref(false)

// 收藏切换函数
const toggleFavorite = async () => {
  if (!authStore.isAuthenticated) {
    alert('请先登录')
    return
  }
  
  try {
    favoriteLoading.value = true
    if (isFavorited.value) {
      await removeFavorite(movieId.value)
      isFavorited.value = false
      // 显示取消收藏提示
      showToast('已取消收藏', 'info')
    } else {
      await addFavorite(movieId.value)
      isFavorited.value = true
      // 显示收藏成功提示
      showToast('收藏成功 ❤️', 'success')
    }
  } catch (error) {
    console.error('收藏操作失败:', error)
    showToast('操作失败，请稍后重试', 'error')
  } finally {
    favoriteLoading.value = false
  }
}
const favoriteLoading = ref(false)

// Toast 提示功能
const toasts = ref([])
const showToast = (message, type = 'info') => {
  const id = Date.now()
  toasts.value.push({ id, message, type })
  
  // 3秒后自动移除
  setTimeout(() => {
    const index = toasts.value.findIndex(toast => toast.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }, 3000)
}

const removeToast = (id) => {
  const index = toasts.value.findIndex(toast => toast.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

// 获取电影ID
const movieId = computed(() => route.params.id)

// 加载电影详情
const loadMovieDetail = async () => {
  if (!movieId.value) {
    error.value = '无效的电影ID'
    return
  }

  loading.value = true
  error.value = null
  
  try {
    const response = await movieApi.getMovieById(movieId.value)
    movie.value = response.data || response
    
    // 获取收藏状态
    if (movie.value.is_favorited !== undefined) {
      isFavorited.value = movie.value.is_favorited
    }
    
    // 调试：输出电影数据和海报URL
    console.log('电影数据:', movie.value)
    if (movie.value?.poster_path) {
      console.log('海报路径:', movie.value.poster_path)
      console.log('处理后的URL:', getImageUrl(movie.value.poster_path))
    }
    
    // 记录浏览历史（如果用户已登录）
    if (authStore.isAuthenticated) {
      try {
        await recordHistory(movieId.value)
        
        // 检查收藏状态
        const response = await checkFavoriteStatus(movieId.value)
        isFavorited.value = response?.is_favorited || false
      } catch (error) {
        console.error('记录浏览历史或检查收藏状态失败:', error)
      }
    }
    
    // 加载完电影详情后获取推荐
    await getRecommendations()
  } catch (err) {
    console.error('获取电影详情失败:', err)
    error.value = err.message || '获取电影详情失败'
  } finally {
    loading.value = false
  }
}

// 处理图片加载错误
const handleImageError = (event) => {
  event.target.src = '/default-poster.jpg'
}

// 解析电影类型
const getMovieGenres = (movie) => {
  if (!movie) return ''
  
  // 优先使用 genres 字段（JSON 格式）
  if (movie.genres) {
    try {
      const genresArray = typeof movie.genres === 'string' 
        ? JSON.parse(movie.genres) 
        : movie.genres
      return Array.isArray(genresArray) ? genresArray.join(' • ') : movie.genres
    } catch (e) {
      console.warn('解析电影类型失败:', e)
      return movie.genres
    }
  }
  
  // 备用字段
  if (movie.genre) return movie.genre
  if (movie.genre_ids && Array.isArray(movie.genre_ids)) return movie.genre_ids.join(' • ')
  
  return ''
}

// 跳转到其他电影详情页
const goToMovie = (movieId) => {
  console.log('跳转到电影:', movieId)
  router.push(`/movie/${movieId}`)
}

// 获取推荐电影
const getRecommendations = async () => {
  recommendationsLoading.value = true
  
  try {
    // 基于当前电影获取推荐
    let response
    
    if (movie.value?.genre) {
      // 如果有电影类型，获取同类型推荐
      response = await movieApi.getPopularMovies(1, 20)
    } else {
      // 否则获取热门推荐
      response = await movieApi.getPopularMovies(1, 20)
    }
    
    // 处理推荐数据，排除当前电影
    let recommendations = Array.isArray(response) ? response : (response.results || response.data || [])
    
    // 过滤掉当前电影，取前5个
    recommendations = recommendations
      .filter(recMovie => recMovie.id !== movie.value?.id)
      .slice(0, 5)
    
    recommendedMovies.value = recommendations
    
  } catch (err) {
    console.error('获取推荐失败:', err)
    recommendedMovies.value = []
  } finally {
    recommendationsLoading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadMovieDetail()
})

// 监听路由变化，重新加载数据
watch(() => route.params.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    loadMovieDetail()
  }
})
</script>

<style scoped>
.detail-view {
  min-height: 100vh;
  position: relative;
  width: 100vw;
  margin: 0 !important;
  padding: 0 !important;
  padding-top: 80px; /* 为固定导航栏留出空间 */
  overflow-x: hidden;
  left: 50%;
  right: 50%;
  margin-left: -50vw !important;
  margin-right: -50vw !important;
  background: #0f1419;
  color: white;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  gap: 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-left: 4px solid #00d4ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
}

.error-content {
  text-align: center;
  max-width: 500px;
}

.error-content h2 {
  font-size: 2rem;
  margin-bottom: 1rem;
  color: #ff6b6b;
}

.error-content p {
  margin-bottom: 2rem;
  color: #ccc;
}

.retry-btn, .back-btn {
  padding: 10px 20px;
  margin: 0 10px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.retry-btn {
  background: #00d4ff;
  color: white;
}

.retry-btn:hover {
  background: #00b8e6;
}

.back-btn {
  background: #666;
  color: white;
}

.back-btn:hover {
  background: #777;
}

/* 电影海报背景 - 类似HomeView的风格 */
.movie-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
}

.backdrop-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  filter: blur(2px) brightness(0.7);
  transform: scale(1.05);
}

.backdrop-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    linear-gradient(
      135deg,
      rgba(0, 0, 0, 0.4) 0%,
      rgba(13, 25, 43, 0.5) 25%,
      rgba(27, 38, 59, 0.5) 50%,
      rgba(65, 84, 118, 0.5) 75%,
      rgba(0, 0, 0, 0.6) 100%
    );
}

.gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(
      ellipse at center,
      rgba(0, 0, 0, 0.1) 0%,
      rgba(0, 0, 0, 0.4) 100%
    );
}

.detail-content {
  position: relative;
  z-index: 10;
  min-height: 100vh;
  padding-top: 150px;
  display: flex;
  align-items: center;
  color: white;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.movie-header {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 40px;
  align-items: start;
}

.movie-poster {
  width: 100%;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.movie-title {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: white;
  font-weight: 800;
  text-shadow: 
    0 0 10px rgba(0, 255, 255, 0.5),
    0 0 20px rgba(0, 255, 255, 0.3),
    0 0 30px rgba(0, 255, 255, 0.2),
    2px 2px 4px rgba(0, 0, 0, 0.8);
  line-height: 1.2;
}

.movie-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.movie-meta span {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  font-size: 14px;
  color: #ccc;
}

.rating {
  background: rgba(255, 193, 7, 0.2) !important;
  color: #ffc107 !important;
}

.movie-description {
  margin-bottom: 2rem;
  line-height: 1.6;
  color: #ddd;
}

.movie-details {
  margin-bottom: 2rem;
}

.detail-item {
  margin-bottom: 10px;
  color: #ccc;
}

.detail-item strong {
  color: white;
  margin-right: 8px;
}

.action-buttons {
  display: flex;
  gap: 15px;
}

.btn-primary, .btn-secondary {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #00d4ff;
  color: white;
}

.btn-primary:hover {
  background: #00b8e6;
  transform: translateY(-2px);
}

.btn-secondary {
  background: transparent;
  color: white;
  border: 2px solid #666;
}

.btn-secondary:hover {
  border-color: #999;
  background: rgba(255, 255, 255, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .movie-header {
    grid-template-columns: 1fr;
    gap: 20px;
    text-align: center;
  }
  
  .poster-section {
    display: flex;
    justify-content: center;
  }
  
  .movie-poster {
    max-width: 250px;
  }
  
  .movie-title {
    font-size: 2rem;
  }
  
  .detail-content {
    padding-top: 150px;
  }
}

/* 推荐组件样式 */
.recommendations-section {
  background: 
    linear-gradient(
      180deg,
      rgba(15, 20, 25, 0.95) 0%,
      rgba(15, 20, 25, 0.98) 100%
    );
  backdrop-filter: blur(15px);
  padding: 60px 0;
  margin-top: 0;
  border-top: 1px solid rgba(0, 255, 255, 0.2);
  position: relative;
  z-index: 15;
}

.section-header {
  text-align: center;
  margin-bottom: 40px;
}

.section-title {
  font-size: 2.2rem;
  margin-bottom: 10px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  text-shadow: 
    0 0 10px rgba(0, 255, 255, 0.4),
    0 0 20px rgba(0, 255, 255, 0.2),
    2px 2px 4px rgba(0, 0, 0, 0.6);
  gap: 10px;
}

.icon {
  font-size: 1.5rem;
}

.section-subtitle {
  color: #999;
  font-size: 1rem;
}

.recommendations-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  padding: 40px;
  color: #ccc;
}

.loading-spinner.small {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-left: 2px solid #00d4ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
  margin-bottom: 40px;
}

.recommendation-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.recommendation-card:hover {
  transform: translateY(-8px);
  border-color: #00d4ff;
  box-shadow: 0 8px 32px rgba(0, 212, 255, 0.3);
}

.rec-poster {
  position: relative;
  width: 100%;
  aspect-ratio: 2/3;
  overflow: hidden;
}

.rec-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.recommendation-card:hover .rec-poster img {
  transform: scale(1.05);
}

.rec-rating {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.8);
  color: #ffc107;
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
}

.rec-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.recommendation-card:hover .rec-overlay {
  opacity: 1;
}

.play-btn {
  width: 50px;
  height: 50px;
  background: #00d4ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  transform: scale(0.8);
  transition: transform 0.3s ease;
}

.recommendation-card:hover .play-btn {
  transform: scale(1);
}

.rec-info {
  padding: 15px;
}

.rec-title {
  color: white;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-clamp: 2;
  overflow: hidden;
}

.rec-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #999;
}

.rec-year {
  color: #00d4ff;
}

.no-recommendations {
  text-align: center;
  padding: 40px;
  color: #666;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Toast 提示样式 */
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.toast {
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 12px 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-width: 250px;
  max-width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  animation: slideIn 0.3s ease-out;
  cursor: pointer;
}

.toast-success {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.9) 0%, rgba(21, 128, 61, 0.9) 100%);
  border-color: rgba(34, 197, 94, 0.3);
}

.toast-error {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.9) 0%, rgba(185, 28, 28, 0.9) 100%);
  border-color: rgba(239, 68, 68, 0.3);
}

.toast-info {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.9) 0%, rgba(29, 78, 216, 0.9) 100%);
  border-color: rgba(59, 130, 246, 0.3);
}

.toast-close {
  background: none;
  border: none;
  color: currentColor;
  font-size: 18px;
  cursor: pointer;
  margin-left: 12px;
  padding: 0;
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.toast-close:hover {
  opacity: 1;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .recommendations-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 900px) {
  .recommendations-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 600px) {
  .recommendations-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
