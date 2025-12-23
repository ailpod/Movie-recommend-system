<template>
  <div class="favorites-view">
    <!-- 英雄区域 -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-icon">💖</div>
        <h1 class="hero-title">我的收藏</h1>
        <p class="hero-subtitle">{{ favorites.length }} 部精选电影</p>
      </div>
      <div class="hero-background">
        <div class="background-overlay"></div>
      </div>
    </section>

    <!-- 收藏电影网格 -->
    <div class="content-container">
      <!-- 空状态 -->
      <div v-if="favorites.length === 0" class="empty-state">
        <div class="empty-icon">🎬</div>
        <h3>还没有收藏任何电影</h3>
        <p>去首页发现更多精彩电影吧</p>
        <router-link to="/" class="explore-btn">
          <span class="btn-icon">✨</span>
          开始探索
        </router-link>
      </div>

      <!-- 收藏电影轮播 -->
      <div v-else class="movies-carousel-container">
        <div class="carousel-header">
          <h3 class="carousel-title">我的收藏电影</h3>
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
              v-for="(pageMovies, pageIndex) in paginatedFavorites" 
              :key="`page-${pageIndex}`"
              class="movies-page"
            >
              <div 
                v-for="item in pageMovies" 
                :key="item.movie.id"
                class="movie-card"
              >
                <div class="movie-poster" @click="goToDetail(item.movie.id)">
                  <img 
                    :src="getMoviePoster(item.movie)" 
                    :alt="item.movie.title"
                  >
                  <div class="poster-overlay">
                    <div class="play-btn">▶</div>
                  </div>
                  <div class="favorite-badge">
                    ❤️
                  </div>
                  <button 
                    @click.stop="handleRemoveFavorite(item.movie.id)" 
                    class="delete-btn"
                    title="删除收藏"
                  >
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"/>
                    </svg>
                  </button>
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

    <!-- 确认对话框 -->
    <ConfirmDialog
      v-model:visible="showConfirmDialog"
      :title="confirmDialogTitle"
      :message="confirmDialogMessage"
      @confirm="handleConfirmRemove"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { fetchFavorites, removeFavorite } from '@/api/userActions.js'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const router = useRouter()
const favorites = ref([])
const loading = ref(true)

// 确认对话框
const showConfirmDialog = ref(false)
const confirmDialogTitle = ref('')
const confirmDialogMessage = ref('')
const pendingRemoveMovieId = ref(null)

// 轮播相关
const currentSlide = ref(0)
const carouselRef = ref(null)
const itemsPerSlide = ref(4) // 每页显示4个电影

// 计算分页后的收藏记录
const paginatedFavorites = computed(() => {
  const pages = []
  for (let i = 0; i < favorites.value.length; i += itemsPerSlide.value) {
    pages.push(favorites.value.slice(i, i + itemsPerSlide.value))
  }
  return pages
})

// 计算总页数
const totalSlides = computed(() => {
  return paginatedFavorites.value.length
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

// 获取收藏列表
const loadFavorites = async () => {
  try {
    loading.value = true
    const response = await fetchFavorites()
    console.log('收藏 API 响应:', response)
    favorites.value = response || []
  } catch (error) {
    console.error('Failed to fetch favorites:', error)
    // 如果请求失败，使用默认数据
    favorites.value = []
  } finally {
    loading.value = false
  }
}

// 移除收藏
const handleRemoveFavorite = (movieId) => {
  pendingRemoveMovieId.value = movieId
  confirmDialogTitle.value = '取消收藏'
  confirmDialogMessage.value = '确定要取消收藏这部电影吗？'
  showConfirmDialog.value = true
}

// 确认移除
const handleConfirmRemove = async () => {
  if (!pendingRemoveMovieId.value) return
  
  try {
    await removeFavorite(pendingRemoveMovieId.value)
    // 从本地数组中移除该记录
    favorites.value = favorites.value.filter(item => item.movie.id !== pendingRemoveMovieId.value)
    
    // 如果当前页面没有记录了，调整到前一页
    if (currentSlide.value >= totalSlides.value && currentSlide.value > 0) {
      currentSlide.value--
    }
  } catch (error) {
    console.error('Failed to remove favorite:', error)
    alert('取消收藏失败，请重试')
  } finally {
    pendingRemoveMovieId.value = null
  }
}

// 获取电影类型
const getMovieGenres = (movie) => {
  // 检查各种可能的类型字段
  if (movie.genres) {
    try {
      if (typeof movie.genres === 'string') {
        const parsed = JSON.parse(movie.genres)
        return Array.isArray(parsed) ? parsed : [parsed]
      }
      if (Array.isArray(movie.genres)) {
        return movie.genres
      }
    } catch (e) {
      console.warn('解析电影类型失败:', e)
    }
  }
  
  if (movie.genre) {
    if (typeof movie.genre === 'string') {
      return movie.genre.split(',').map(g => g.trim()).filter(g => g)
    }
    return [movie.genre]
  }
  
  // 根据电影标题推测类型
  const title = movie.title || ''
  if (title.includes('复仇者') || title.includes('蜘蛛侠') || title.includes('蝙蝠侠')) {
    return ['动作', '科幻']
  }
  if (title.includes('哈利·波特')) {
    return ['奇幻', '冒险']
  }
  if (title.includes('盗梦空间')) {
    return ['科幻', '悬疑']
  }
  if (title.includes('你的名字')) {
    return ['动画', '爱情']
  }
  
  return ['剧情']
}

const getMoviePoster = (movie) => {
  if (movie.poster_path && movie.poster_path.startsWith('http')) {
    return movie.poster_path
  }
  return movie.poster_path ? 
    `https://image.tmdb.org/t/p/w500${movie.poster_path}` : 
    'https://images.unsplash.com/photo-1489599210039-aeb5cf5abd63?w=300&h=450&fit=crop'
}

const goToDetail = (movieId) => router.push(`/movie/${movieId}`)

// 格式化评分，保留一位小数
const formatRating = (rating) => {
  if (!rating) return '8.5'
  const num = parseFloat(rating)
  return isNaN(num) ? '8.5' : num.toFixed(1)
}

onMounted(() => {
  loadFavorites()
})
</script>

<style scoped>
.favorites-view {
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
  filter: drop-shadow(0 0 20px rgba(255, 105, 180, 0.6));
  animation: heartbeat 2s ease-in-out infinite;
}

@keyframes heartbeat {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  color: white;
  margin-bottom: 15px;
  background: linear-gradient(45deg, #ffffff 0%, #ff69b4 50%, #ffffff 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 1.2rem;
  color: rgba(255, 105, 180, 0.8);
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
  background: linear-gradient(135deg, #ff69b4, #ff1493);
  color: white;
  padding: 15px 30px;
  border-radius: 50px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.explore-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(255, 105, 180, 0.4);
}

.movies-carousel-container {
  padding: 20px 0;
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
  background: rgba(255, 105, 180, 0.8);
  color: white;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.carousel-btn:hover:not(:disabled) {
  background: rgba(255, 105, 180, 1);
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
  border: 1px solid rgba(255, 105, 180, 0.2);
  border-radius: 15px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  flex: 1;
  max-width: calc(25% - 19px); /* 每行4个 */
  min-width: 200px;
}

.movie-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(255, 105, 180, 0.2);
  border-color: rgba(255, 105, 180, 0.4);
}

.movie-poster {
  position: relative;
  height: 350px;
  overflow: hidden;
}

.movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.movie-card:hover .movie-poster img {
  transform: scale(1.1);
}

.poster-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.3s ease;
}

.movie-card:hover .poster-overlay {
  opacity: 1;
}

.play-btn {
  width: 60px;
  height: 60px;
  background: rgba(255, 105, 180, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  transform: scale(0.8);
  transition: all 0.3s ease;
}

.movie-card:hover .play-btn {
  transform: scale(1);
}

.favorite-badge {
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

.delete-btn {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(231, 76, 60, 0.9);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.3s ease;
  opacity: 0;
  transform: translateY(10px);
}

.delete-btn svg {
  width: 16px;
  height: 16px;
}

.movie-card:hover .delete-btn {
  opacity: 1;
  transform: translateY(0);
}

.delete-btn:hover {
  background: rgba(192, 57, 43, 1);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.4);
}

.movie-info {
  padding: 20px;
  cursor: pointer;
}

.movie-title {
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.movie-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.genre {
  background: rgba(255, 105, 180, 0.2);
  padding: 4px 12px;
  border-radius: 15px;
  border: 1px solid rgba(255, 105, 180, 0.3);
}

.rating {
  font-weight: 500;
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

/* 渐入动画效果 */
@media (prefers-reduced-motion: no-preference) {
  .hero-content {
    animation: fadeInUp 1s ease-out;
  }

  .content-container {
    animation: fadeInUp 1.2s ease-out;
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