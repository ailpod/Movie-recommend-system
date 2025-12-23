<template>
  <div class="rating-history-view">
    <!-- 英雄区域 -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-icon">⭐</div>
        <h1 class="hero-title">我的评分</h1>
        <p class="hero-subtitle">{{ totalRatings }} 部电影已评分</p>
      </div>
      <div class="hero-background">
        <div class="background-overlay"></div>
      </div>
    </section>

    <!-- 评分记录列表 -->
    <div class="content-container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>正在加载评分记录...</p>
      </div>

      <!-- 空状态 -->
      <div v-else-if="ratings.length === 0" class="empty-state">
        <div class="empty-icon">🌟</div>
        <h3>还没有评分记录</h3>
        <p>为你喜欢的电影打分吧</p>
        <router-link to="/" class="explore-btn">
          <span class="btn-icon">🎬</span>
          探索电影
        </router-link>
      </div>

      <!-- 评分记录轮播 -->
      <div v-else class="movies-carousel-container">
        <div class="carousel-header">
          <h3 class="carousel-title">我的评分记录</h3>
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
            <!-- 分页显示评分 -->
            <div 
              v-for="(pageRatings, pageIndex) in paginatedRatings" 
              :key="`page-${pageIndex}`"
              class="movies-page"
            >
              <div 
                v-for="item in pageRatings" 
                :key="item.id || item.movie.id"
                class="movie-card"
              >
                <div class="movie-poster" @click="goToDetail(item.movie.id)">
                  <img 
                    :src="getMoviePoster(item.movie)" 
                    :alt="item.movie?.title"
                  />
                  <div class="poster-overlay">
                    <div class="play-btn">▶</div>
                  </div>
                  <div class="rating-badge">
                    <span class="rating-score">{{ formatRating(item.rating) }}</span>
                    <span class="rating-max">/10</span>
                  </div>
                  <button 
                    @click.stop="deleteRating(item.movie.id)" 
                    class="delete-btn"
                    title="删除评分"
                  >
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"/>
                    </svg>
                  </button>
                </div>
                <div class="movie-info" @click="goToDetail(item.movie.id)">
                  <h3 class="movie-title">{{ item.movie?.title || '未知电影' }}</h3>
                  <div class="movie-meta">
                    <span v-if="getMovieGenres(item.movie).length > 0" class="genre">
                      {{ getMovieGenres(item.movie).slice(0, 2).join('·') }}
                    </span>
                    <span v-else class="genre">剧情</span>
                    <span class="rating-time">{{ formatTime(item.created_at) }}</span>
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
      @confirm="handleConfirmDelete"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ratingApi from '@/services/ratingApi'
import { getImageUrl, formatRating as fmtRating } from '@/services/movieApi'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const router = useRouter()
const ratings = ref([])
const loading = ref(true)

// 确认对话框
const showConfirmDialog = ref(false)
const confirmDialogTitle = ref('')
const confirmDialogMessage = ref('')
const pendingDeleteMovieId = ref(null)

// 轮播相关
const currentSlide = ref(0)
const carouselRef = ref(null)
const itemsPerSlide = ref(4) // 每页显示4个电影

const totalRatings = computed(() => ratings.value.length)

// 计算分页后的评分记录
const paginatedRatings = computed(() => {
  const pages = []
  for (let i = 0; i < ratings.value.length; i += itemsPerSlide.value) {
    pages.push(ratings.value.slice(i, i + itemsPerSlide.value))
  }
  return pages
})

// 计算总页数
const totalSlides = computed(() => {
  return paginatedRatings.value.length
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

const loadRatings = async () => {
  try {
    loading.value = true
    const response = await ratingApi.getMyRatings()
    console.log('评分历史 API 响应:', response)
    ratings.value = (response?.data || response || [])
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  } catch (error) {
    console.error('获取评分历史失败:', error)
    ratings.value = []
  } finally {
    loading.value = false
  }
}

const deleteRating = (movieId) => {
  pendingDeleteMovieId.value = movieId
  confirmDialogTitle.value = '删除评分'
  confirmDialogMessage.value = '确定要删除这条评分记录吗？'
  showConfirmDialog.value = true
}

// 确认删除
const handleConfirmDelete = async () => {
  if (!pendingDeleteMovieId.value) return
  
  try {
    await ratingApi.deleteRating(pendingDeleteMovieId.value)
    ratings.value = ratings.value.filter((r) => r.movie.id !== pendingDeleteMovieId.value)
    
    // 如果当前页面没有记录了，调整到前一页
    if (currentSlide.value >= totalSlides.value && currentSlide.value > 0) {
      currentSlide.value--
    }
  } catch (error) {
    console.error('删除评分失败:', error)
    alert('删除失败，请重试')
  } finally {
    pendingDeleteMovieId.value = null
  }
}

const goToDetail = (movieId) => {
  if (movieId) router.push(`/movie/${movieId}`)
}

const getMoviePoster = (movie) => {
  if (!movie) return ''
  return getImageUrl(movie.poster_path)
}

const getMovieGenres = (movie) => {
  if (!movie) return []
  let genres = []
  if (movie.genres) {
    try {
      if (typeof movie.genres === 'string') {
        try {
          const parsed = JSON.parse(movie.genres)
          genres = Array.isArray(parsed) ? parsed : [parsed]
        } catch {
          genres = movie.genres.split(',').map((g) => g.trim()).filter((g) => g)
        }
      } else if (Array.isArray(movie.genres)) {
        genres = movie.genres
      } else {
        genres = [movie.genres]
      }
    } catch (e) {
      return []
    }
  }
  return genres
}

const formatRating = (rating) => {
  const num = parseFloat(rating)
  return isNaN(num) ? 'N/A' : num.toFixed(1)
}

const formatTime = (dateStr) => {
  try {
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now - date
    const minutes = Math.floor(diff / (1000 * 60))
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (minutes < 60) return `${minutes} 分钟前`
    if (hours < 24) return `${hours} 小时前`
    if (days < 7) return `${days} 天前`
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch (e) {
    return '刚刚'
  }
}

onMounted(() => {
  loadRatings()
})
</script>

<style scoped>
.rating-history-view {
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
  padding-top: 80px;
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
  filter: drop-shadow(0 0 20px rgba(255, 215, 0, 0.6));
  animation: twinkle 2s ease-in-out infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.8; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  color: white;
  margin-bottom: 15px;
  background: linear-gradient(45deg, #ffffff 0%, #ffd700 50%, #ffffff 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 1.2rem;
  color: rgba(255, 215, 0, 0.8);
  font-weight: 300;
}

.content-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 20px 100px;
  position: relative;
  z-index: 1;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: white;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-left: 3px solid #ffd700;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #333;
  padding: 15px 30px;
  border-radius: 50px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.explore-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(255, 215, 0, 0.4);
}

/* 轮播样式 */
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
  font-size: 1.8rem;
  font-weight: 700;
  color: white;
  margin: 0;
}

.carousel-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.carousel-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid rgba(255, 215, 0, 0.5);
  background: rgba(0, 0, 0, 0.5);
  color: #ffd700;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.carousel-btn:hover:not(:disabled) {
  background: rgba(255, 215, 0, 0.2);
  border-color: #ffd700;
  transform: scale(1.1);
}

.carousel-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.slide-indicator {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95rem;
  font-weight: 500;
}

.movies-carousel {
  position: relative;
  overflow: hidden;
  border-radius: 20px;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  padding: 30px;
}

.movies-slide {
  display: flex;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.movies-page {
  min-width: 100%;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 25px;
}

.movie-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(255, 215, 0, 0.2);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.movie-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 40px rgba(255, 215, 0, 0.2);
  border-color: rgba(255, 215, 0, 0.6);
  z-index: 10;
}

.movie-poster {
  position: relative;
  width: 100%;
  aspect-ratio: 2/3;
  overflow: hidden;
  cursor: pointer;
}

.movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.movie-card:hover .movie-poster img {
  transform: scale(1.15);
}

.poster-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.9) 0%,
    rgba(0, 0, 0, 0.4) 50%,
    transparent 100%
  );
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.4s ease;
}

.movie-card:hover .poster-overlay {
  opacity: 1;
}

.play-btn {
  width: 70px;
  height: 70px;
  background: rgba(255, 215, 0, 0.95);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  font-size: 28px;
  padding-left: 4px;
  box-shadow: 0 8px 25px rgba(255, 215, 0, 0.4);
  transform: scale(0.8);
  transition: all 0.3s ease;
}

.movie-card:hover .play-btn {
  transform: scale(1);
}

.rating-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(255, 215, 0, 0.95);
  color: #333;
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 2px;
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
}

.rating-score {
  font-size: 1rem;
}

.rating-max {
  font-size: 0.8rem;
  opacity: 0.8;
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
  transition: color 0.2s ease;
}

.movie-card:hover .movie-title {
  color: #ffd700;
}

.movie-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
}

.genre {
  color: rgba(255, 215, 0, 0.8);
}

.rating-time {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.85rem;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .movies-page {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 1024px) {
  .movies-page {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .carousel-title {
    font-size: 1.4rem;
  }

  .movies-page {
    grid-template-columns: 1fr;
  }

  .content-container {
    padding: 20px 10px 60px;
  }
}
</style>
