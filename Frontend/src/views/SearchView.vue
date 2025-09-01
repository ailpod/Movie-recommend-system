<template>
  <div class="search-view">
    <!-- 搜索头部 -->
    <div class="search-header">
      <div class="container">
        <div class="search-info">
          <h1 v-if="searchQuery" class="search-title">
            搜索 "{{ searchQuery }}" 的结果
          </h1>
          <h1 v-else class="search-title">搜索结果</h1>
          
          <p v-if="totalResults > 0" class="search-stats">
            共找到 {{ totalResults }} 个结果
          </p>
        </div>
      </div>
    </div>

    <!-- 搜索结果 -->
    <div class="results-section">
      <div class="container">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>正在搜索...</p>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="error-container">
          <div class="error-icon">⚠️</div>
          <h3>搜索失败</h3>
          <p class="error-message">{{ error }}</p>
          <button @click="() => performSearch(1)" class="retry-btn">重试</button>
        </div>

        <!-- 无结果 -->
        <div v-else-if="movies.length === 0 && !loading" class="no-results-container">
          <div class="no-results-icon">🔍</div>
          <h3>未找到相关内容</h3>
          <p class="no-results-message">
            试试其他关键词或调整筛选条件
          </p>
        </div>

        <!-- 搜索结果列表 -->
        <div v-else class="results-list">
          <div 
            v-for="movie in movies" 
            :key="movie.id" 
            class="movie-item"
            @click="goToMovie(movie.id)"
          >
            <div class="movie-poster">
              <img 
                :src="getImageUrl(movie.poster_path)" 
                :alt="movie.title"
                @error="handleImageError"
              />
              <div class="movie-rating">
                <span class="rating-score">{{ formatRating(movie.avg_rate) }}</span>
              </div>
            </div>
            
            <div class="movie-info">
              <h3 class="movie-title">{{ movie.title }}</h3>
              
              <div class="movie-meta">
                <span class="movie-year">{{ movie.release_year || getYear(movie.release_date) }}</span>
                <span class="movie-genre">{{ getMovieGenres(movie) }}</span>
                <span class="movie-director" v-if="movie.director">{{ movie.director }}</span>
              </div>
              
              <p class="movie-description">
                {{ truncateText(movie.description || movie.overview, 150) }}
              </p>
              
              <div class="movie-stats">
                <span class="stat-item">
                  ⭐ {{ formatRating(movie.avg_rate) }}
                </span>
                <span class="stat-item">
                  👥 {{ formatVotes(movie.vote) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="totalPages > 1" class="pagination-container">
          <div class="pagination">
            <button 
              @click="goToPage(1)"
              :disabled="currentPage <= 1"
              class="page-btn"
            >
              首页
            </button>
            
            <button 
              @click="goToPage(currentPage - 1)"
              :disabled="currentPage <= 1"
              class="page-btn"
            >
              上一页
            </button>

            <div class="page-numbers">
              <button
                v-for="page in visiblePages"
                :key="page"
                @click="goToPage(page)"
                :class="['page-btn', { active: page === currentPage }]"
              >
                {{ page }}
              </button>
            </div>

            <button 
              @click="goToPage(currentPage + 1)"
              :disabled="currentPage >= totalPages"
              class="page-btn"
            >
              下一页
            </button>
            
            <button 
              @click="goToPage(totalPages)"
              :disabled="currentPage >= totalPages"
              class="page-btn"
            >
              末页
            </button>
          </div>

          <div class="pagination-info">
            第 {{ currentPage }} 页 / 共 {{ totalPages }} 页
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import movieApi, { getImageUrl, formatRating } from '@/services/movieApi'

const route = useRoute()
const router = useRouter()

// 响应式数据
const movies = ref([])
const loading = ref(false)
const error = ref(null)
const currentPage = ref(1)
const totalPages = ref(0)
const totalResults = ref(0)

// 计算属性
const searchQuery = computed(() => route.query.q || '')

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// 工具函数
const truncateText = (text, maxLength) => {
  if (!text) return ''
  return text.length > maxLength ? text.slice(0, maxLength) + '...' : text
}

const getYear = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).getFullYear()
}

const formatVotes = (votes) => {
  if (!votes) return '0'
  if (votes >= 1000000) {
    return (votes / 1000000).toFixed(1) + 'M'
  } else if (votes >= 1000) {
    return (votes / 1000).toFixed(1) + 'K'
  }
  return votes.toString()
}

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

const handleImageError = (event) => {
  event.target.src = '/default-poster.jpg'
}

const goToMovie = (movieId) => {
  router.push(`/movie/${movieId}`)
}

// 执行搜索
const performSearch = async (page = 1) => {
  loading.value = true
  error.value = null
  
  try {
    const query = searchQuery.value
    let response

    if (query) {
      response = await movieApi.searchMovies(query, page)
    } else {
      response = await movieApi.getPopularMovies(page)
    }

    // 处理响应数据
    if (Array.isArray(response)) {
      movies.value = response
      totalResults.value = response.length
      totalPages.value = Math.ceil(totalResults.value / 20)
    } else {
      movies.value = response.results || response.data || []
      totalResults.value = response.total_results || movies.value.length
      totalPages.value = response.total_pages || Math.ceil(totalResults.value / 20)
    }
    
    currentPage.value = page
    
  } catch (err) {
    console.error('搜索失败:', err)
    error.value = err.message || '搜索失败，请稍后重试'
    movies.value = []
    totalResults.value = 0
    totalPages.value = 0
  } finally {
    loading.value = false
  }
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    performSearch(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// 监听路由变化
watch(() => route.query.q, () => {
  currentPage.value = 1
  performSearch(1)
}, { immediate: false })

// 组件挂载
onMounted(() => {
  performSearch(1)
})
</script>

<style scoped>
.search-view {
  min-height: 100vh;
  background: #0f1419;
  color: white;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 搜索头部 */
.search-header {
  background: rgba(15, 20, 25, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 30px 0;
}

.search-info {
  text-align: center;
}

.search-title {
  font-size: 2.2rem;
  font-weight: 600;
  margin-bottom: 10px;
  color: #fff;
}

.search-stats {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

/* 结果区域 */
.results-section {
  padding: 30px 0;
}

/* 状态容器 */
.loading-container,
.error-container,
.no-results-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-left: 3px solid #4a9eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon,
.no-results-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.error-message,
.no-results-message {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
  margin-bottom: 20px;
}

.retry-btn {
  background: #4a9eff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: #3a8eef;
}

/* 电影列表 */
.results-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.movie-item {
  display: flex;
  gap: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.movie-item:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.movie-poster {
  flex-shrink: 0;
  width: 120px;
  height: 180px;
  position: relative;
  border-radius: 6px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.1);
}

.movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.movie-rating {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.8);
  color: #ffd700;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.movie-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.movie-title {
  font-size: 1.4rem;
  font-weight: 600;
  color: white;
  margin: 0;
  line-height: 1.3;
}

.movie-meta {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.movie-meta span:not(:last-child)::after {
  content: '•';
  margin-left: 10px;
  color: rgba(255, 255, 255, 0.4);
}

.movie-description {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.95rem;
  line-height: 1.5;
  margin: 0;
  flex: 1;
}

.movie-stats {
  display: flex;
  gap: 20px;
  margin-top: auto;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

/* 分页 */
.pagination-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 40px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: 40px;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  min-width: 40px;
  text-align: center;
}

.page-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn.active {
  background: #4a9eff;
  border-color: #4a9eff;
}

.page-numbers {
  display: flex;
  gap: 5px;
}

.pagination-info {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-title {
    font-size: 1.8rem;
  }

  .movie-item {
    flex-direction: column;
    gap: 15px;
  }

  .movie-poster {
    width: 100%;
    height: 200px;
  }

  .pagination {
    flex-wrap: wrap;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 0 15px;
  }

  .search-header {
    padding: 20px 0;
  }

  .search-title {
    font-size: 1.6rem;
  }

  .movie-meta {
    flex-direction: column;
    gap: 8px;
  }

  .movie-meta span::after {
    display: none;
  }
}
</style>
