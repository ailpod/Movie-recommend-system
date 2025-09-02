<template>
  <div class="history-view">
    <!-- 英雄区域 -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-icon">🕒</div>
        <h1 class="hero-title">最近浏览</h1>
        <p class="hero-subtitle">{{ watchHistory.length }} 条观看记录</p>
      </div>
      <div class="hero-background">
        <div class="background-overlay"></div>
      </div>
    </section>

    <!-- 历史记录列表 -->
    <div class="content-container">
      <!-- 空状态 -->
      <div v-if="watchHistory.length === 0" class="empty-state">
        <div class="empty-icon">📺</div>
        <h3>还没有观看记录</h3>
        <p>开始观看一些电影吧</p>
        <router-link to="/" class="explore-btn">
          <span class="btn-icon">🎬</span>
          开始观看
        </router-link>
      </div>

      <!-- 历史记录轮播 -->
      <div v-else class="movies-carousel-container">
        <div class="carousel-header">
          <h3 class="carousel-title">历史浏览电影</h3>
          <div class="carousel-controls">
            <button 
              @click="prevSlide" 
              :disabled="currentSlide === 0"
              class="carousel-btn prev-btn"
            >
              ‹
            </button>
            <span class="slide-indicator">{{ currentSlide + 1 }} / {{ totalSlides }}</span>
            <button 
              @click="nextSlide" 
              :disabled="currentSlide >= totalSlides - 1"
              class="carousel-btn next-btn"
            >
              ›
            </button>
          </div>
        </div>
        
        <div class="movies-carousel" ref="carouselRef">
          <div 
            class="movies-slide" 
            :style="{ transform: `translateX(-${currentSlide * 100}%)` }"
          >
            <!-- 分页显示电影 -->
            <div 
              v-for="(pageMovies, pageIndex) in paginatedHistory" 
              :key="`page-${pageIndex}`"
              class="movies-page"
            >
              <div 
                v-for="item in pageMovies" 
                :key="item.id"
                class="movie-card"
              >
                <!-- 删除按钮 -->
                <button 
                  @click.stop="deleteHistoryItem(item.movie.id)"
                  class="delete-btn"
                  title="删除这条记录"
                >
                  ✕
                </button>
                
                <div class="movie-poster" @click="goToDetail(item.movie.id)">
                  <img 
                    :src="getMoviePoster(item.movie)" 
                    :alt="item.movie.title"
                  >
                  <div class="poster-overlay">
                    <div class="play-btn">▶</div>
                  </div>
                  <div class="watch-time-badge">
                    {{ formatDate(item.visited_at) }}
                  </div>
                </div>
                <div class="movie-info" @click="goToDetail(item.movie.id)">
                  <h3 class="movie-title">{{ item.movie.title }}</h3>
                  <div class="movie-meta">
                    <span v-if="getMovieGenres(item.movie).length > 0" class="genre">
                      {{ getMovieGenres(item.movie).slice(0, 2).join('·') }}
                    </span>
                    <span v-else class="genre">剧情</span>
                    <span class="rating">⭐ {{ formatRating(item.movie.avg_rate) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { fetchHistory, deleteHistoryRecord } from '@/api/userActions.js'

const router = useRouter()
const watchHistory = ref([])
const loading = ref(true)

// 轮播相关
const currentSlide = ref(0)
const carouselRef = ref(null)
const itemsPerSlide = ref(4) // 每页显示4个电影

// 计算分页后的历史记录
const paginatedHistory = computed(() => {
  const pages = []
  for (let i = 0; i < watchHistory.value.length; i += itemsPerSlide.value) {
    pages.push(watchHistory.value.slice(i, i + itemsPerSlide.value))
  }
  return pages
})

// 计算总页数
const totalSlides = computed(() => {
  return paginatedHistory.value.length
})

// 轮播控制函数
const nextSlide = () => {
  if (currentSlide.value < totalSlides.value - 1) {
    currentSlide.value++
  }
}

const prevSlide = () => {
  if (currentSlide.value > 0) {
    currentSlide.value--
  }
}

// 获取浏览历史
const loadHistory = async () => {
  try {
    loading.value = true
    const response = await fetchHistory()
    console.log('历史记录 API 响应:', response)
    
    // 去重处理：保留每个电影的最新访问记录
    const historyData = response.data || response || []
    const uniqueHistory = []
    const movieIds = new Set()
    
    // 按访问时间倒序排序，确保最新的在前面
    historyData.sort((a, b) => new Date(b.visited_at) - new Date(a.visited_at))
    
    // 去重，只保留每部电影的最新记录
    historyData.forEach(item => {
      if (!movieIds.has(item.movie.id)) {
        movieIds.add(item.movie.id)
        uniqueHistory.push(item)
      }
    })
    
    watchHistory.value = uniqueHistory
  } catch (error) {
    console.error('Failed to fetch history:', error)
    watchHistory.value = []
  } finally {
    loading.value = false
  }
}

// 删除单个历史记录
const deleteHistoryItem = async (movieId) => {
  try {
    await deleteHistoryRecord(movieId)
    // 从本地数组中移除该记录
    watchHistory.value = watchHistory.value.filter(item => item.movie.id !== movieId)
    
    // 如果当前页面没有记录了，调整到前一页
    if (currentSlide.value >= totalSlides.value && currentSlide.value > 0) {
      currentSlide.value--
    }
  } catch (error) {
    console.error('删除历史记录失败:', error)
    alert('删除失败，请重试')
  }
}

const getMoviePoster = (movie) => {
  if (movie.poster_path && movie.poster_path.startsWith('http')) {
    return movie.poster_path
  }
  return movie.poster_path ? 
    `https://image.tmdb.org/t/p/w500${movie.poster_path}` : 
    'https://images.unsplash.com/photo-1489599210039-aeb5cf5abd63?w=300&h=450&fit=crop'
}

// 获取电影类型，最多返回两个
const getMovieGenres = (movie) => {
  let genres = []
  
  // 检查各种可能的类型字段
  if (movie.genres) {
    try {
      if (typeof movie.genres === 'string') {
        // 先尝试 JSON 解析
        try {
          const parsed = JSON.parse(movie.genres)
          genres = Array.isArray(parsed) ? parsed : [parsed]
        } catch {
          // 如果不是 JSON，按逗号分割
          genres = movie.genres.split(',').map(g => g.trim()).filter(g => g)
        }
      } else if (Array.isArray(movie.genres)) {
        genres = movie.genres
      } else {
        genres = [movie.genres]
      }
    } catch (e) {
      console.warn('解析电影类型失败:', e)
      return []
    }
  } else if (movie.genre) {
    if (typeof movie.genre === 'string') {
      genres = movie.genre.split(',').map(g => g.trim()).filter(g => g)
    } else if (Array.isArray(movie.genre)) {
      genres = movie.genre
    } else {
      genres = [movie.genre]
    }
  } else if (movie.genre_ids && Array.isArray(movie.genre_ids)) {
    genres = movie.genre_ids
  }
  
  // 限制最多返回两个类型
  return genres.slice(0, 2)
}

const formatDate = (dateString) => {
  try {
    // 创建日期对象并转换为北京时间
    const date = new Date(dateString)
    const now = new Date()
    
    // 如果日期字符串没有时区信息，假设它是北京时间
    const offsetDate = dateString.includes('T') && !dateString.includes('+') && !dateString.includes('Z') 
      ? new Date(dateString + '+08:00') 
      : date
    
    const diff = now - offsetDate
    const minutes = Math.floor(diff / (1000 * 60))
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    
    if (minutes < 60) return `${minutes}分钟前`
    if (hours < 24) return `${hours}小时前`
    if (days < 7) return `${days}天前`
    
    // 超过一周显示具体日期
    return offsetDate.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      timeZone: 'Asia/Shanghai'
    })
  } catch (e) {
    console.warn('时间格式化失败:', e, dateString)
    return '刚刚'
  }
}

const goToDetail = (movieId) => router.push(`/movie/${movieId}`)

// 格式化评分，保留一位小数
const formatRating = (rating) => {
  if (!rating) return '8.5'
  const num = parseFloat(rating)
  return isNaN(num) ? '8.5' : num.toFixed(1)
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.history-view {
  min-height: 100vh;
  background: 
    linear-gradient(135deg, rgba(0, 0, 0, 0.85) 0%, rgba(13, 25, 43, 0.9) 25%, rgba(27, 38, 59, 0.9) 50%, rgba(65, 84, 118, 0.9) 75%, rgba(0, 0, 0, 0.95) 100%),
    url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920&h=1080&fit=crop&crop=center') center/cover;
  background-attachment: fixed;
  width: 100vw;
  margin-left: -50vw !important;
  margin-right: -50vw !important;
  left: 50%;
  right: 50%;
  position: relative;
  padding-top: 80px; /* 为固定导航栏留出空间 */
}

.hero-section {
  height: 40vh;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  margin-bottom: 5vh;
}

.hero-content {
  z-index: 1;
  padding: 0 20px;
}

.hero-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  filter: drop-shadow(0 0 20px rgba(186, 85, 211, 0.6));
  animation: tick 2s ease-in-out infinite;
}

@keyframes tick {
  0%, 100% { transform: rotate(-5deg); }
  50% { transform: rotate(5deg); }
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  color: white;
  margin-bottom: 15px;
  background: linear-gradient(45deg, #ffffff 0%, #8a2be2 50%, #ffffff 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 1.2rem;
  color: rgba(138, 43, 226, 0.8);
  font-weight: 300;
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: white;
}

.empty-icon {
  font-size: 5rem;
  margin-bottom: 20px;
  opacity: 0.7;
}

.empty-state h3 {
  font-size: 1.8rem;
  margin-bottom: 10px;
}

.empty-state p {
  font-size: 1.1rem;
  margin-bottom: 30px;
  opacity: 0.7;
}

.explore-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, #8a2be2, #9370db);
  color: white;
  padding: 15px 30px;
  border-radius: 50px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.explore-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(138, 43, 226, 0.4);
}

.movies-carousel-container {
  padding: 20px 0;
  position: relative;
}

.carousel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 0 20px;
}

.carousel-title {
  color: white;
  font-size: 1.8rem;
  font-weight: 600;
}

.carousel-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.carousel-btn {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: rgba(186, 85, 211, 0.8);
  color: white;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.carousel-btn:hover:not(:disabled) {
  background: rgba(186, 85, 211, 1);
  transform: scale(1.1);
}

.carousel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.slide-indicator {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  min-width: 60px;
  text-align: center;
}

.movies-carousel {
  overflow: hidden;
  border-radius: 15px;
}

.movies-slide {
  display: flex;
  width: 100%;
  transition: transform 0.5s ease;
}

.movies-page {
  display: flex;
  gap: 25px;
  padding: 0 20px;
  width: 100%;
  flex-shrink: 0;
}

.movie-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(186, 85, 211, 0.2);
  border-radius: 15px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  flex: 1;
  max-width: calc(25% - 19px); /* 每行4个 */
  min-width: 200px;
}

/* 删除按钮样式 */
.delete-btn {
  position: absolute;
  top: 8px;
  left: 8px;
  width: 28px;
  height: 28px;
  background: rgba(255, 71, 87, 0.9);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.3s ease;
  z-index: 10;
}

.movie-card:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: rgba(255, 71, 87, 1);
  transform: scale(1.1);
}

.movie-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(186, 85, 211, 0.4);
  transform: translateY(-8px);
  box-shadow: 0 15px 40px rgba(186, 85, 211, 0.2);
}

.movie-poster {
  position: relative;
  width: 100%;
  aspect-ratio: 2/3;
  overflow: hidden;
}

.movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.movie-card:hover .movie-poster img {
  transform: scale(1.05);
}

.poster-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.movie-card:hover .poster-overlay {
  opacity: 1;
}

.play-btn {
  width: 60px;
  height: 60px;
  background: rgba(186, 85, 211, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  transform: scale(0.8);
  transition: transform 0.3s ease;
}

.movie-card:hover .play-btn {
  transform: scale(1);
}

.watch-time-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.movie-info {
  padding: 15px;
}

.movie-title {
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.3;
}

.movie-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.genre {
  background: rgba(255, 105, 180, 0.2);
  padding: 4px 12px;
  border-radius: 15px;
  border: 1px solid rgba(255, 105, 180, 0.3);
}

.rating {
  color: #ffd700;
  font-weight: 600;
}

@media (max-width: 1200px) {
  .movie-card {
    max-width: calc(33.333% - 17px); /* 每行3个 */
  }
}

@media (max-width: 900px) {
  .movie-card {
    max-width: calc(50% - 12px); /* 每行2个 */
  }
  
  .carousel-title {
    font-size: 1.5rem;
  }
}

@media (max-width: 768px) {
  .hero-title { 
    font-size: 2.2rem; 
  }
  
  .movie-card {
    max-width: 100%; /* 每行1个 */
  }
  
  .carousel-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .movies-page {
    flex-direction: column;
    align-items: center;
  }
}

/* 对话框样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.dialog {
  background: linear-gradient(135deg, rgba(20, 20, 20, 0.95), rgba(40, 40, 40, 0.95));
  border: 1px solid rgba(186, 85, 211, 0.3);
  border-radius: 20px;
  min-width: 400px;
  max-width: 500px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
  overflow: hidden;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 30px;
  border-bottom: 1px solid rgba(186, 85, 211, 0.2);
}

.dialog-header h3 {
  color: white;
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
}

.dialog-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 24px;
  cursor: pointer;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.dialog-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.dialog-body {
  padding: 30px;
  text-align: center;
}

.dialog-body p {
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  font-size: 1.1rem;
  line-height: 1.6;
}

.dialog-footer {
  padding: 24px 30px;
  border-top: 1px solid rgba(186, 85, 211, 0.2);
  display: flex;
  gap: 15px;
  justify-content: flex-end;
}

.dialog-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  min-width: 80px;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.confirm-btn {
  background: linear-gradient(135deg, #ff4757, #ff3838);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 71, 87, 0.3);
}

.confirm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 71, 87, 0.4);
}

@media (max-width: 480px) {
  .dialog {
    min-width: 320px;
    margin: 20px;
  }
  
  .dialog-footer {
    flex-direction: column;
  }
  
  .dialog-btn {
    width: 100%;
  }
  
  .clear-all-btn-fixed {
    bottom: 20px;
    right: 20px;
    padding: 10px 18px;
    font-size: 14px;
  }
}

/* 渐入动画效果 */
@media (prefers-reduced-motion: no-preference) {
  .hero-content {
    animation: fadeInUp 1s ease-out;
  }

  .content-container {
    animation: fadeInUp 1.2s ease-out;
  }

  .movies-carousel-container {
    animation: fadeInUp 1.4s ease-out;
  }

  .movie-card {
    animation: fadeInUp 0.8s ease-out;
  }

  .movie-card:nth-child(2) {
    animation-delay: 0.1s;
  }

  .movie-card:nth-child(3) {
    animation-delay: 0.2s;
  }

  .movie-card:nth-child(4) {
    animation-delay: 0.3s;
  }

  .clear-all-btn-fixed {
    animation: fadeInUp 1.8s ease-out;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>