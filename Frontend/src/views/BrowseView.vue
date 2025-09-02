<template>
  <div class="browse-view">
    <!-- 英雄区域 -->
    <section class="hero-section">
      <div class="hero-content">
        <h3 class="hero-title">电影浏览</h3>
        <p class="hero-subtitle">发现更多精彩电影，享受观影乐趣</p>
      </div>
      <div class="hero-background">
        <div class="background-overlay"></div>
      </div>
    </section>

    <!-- 内容容器 -->
    <div class="content-container">
      <!-- 筛选选项模块 -->
      <div class="filter-card">
        <div class="card-header">
          <h2 class="card-title">
            <span class="title-icon">🔍</span>
            筛选选项
          </h2>
          <p class="card-subtitle">根据您的偏好筛选电影</p>
        </div>
        
        <div class="filter-content">
          <div class="filter-grid">
            <!-- 排序方式 -->
            <div class="filter-group">
              <label class="filter-label">排序方式</label>
              <select v-model="filters.sort_by" @change="applyFilters" class="filter-select">
                <option value="popular">热门电影</option>
                <option value="top_rated">高分电影</option>
                <option value="latest">最新上映</option>
                <option value="vote">投票数</option>
                <option value="rating">评分</option>
                <option value="year">年份</option>
              </select>
            </div>
            
            <!-- 电影类型 -->
            <div class="filter-group">
              <label class="filter-label">电影类型</label>
              <select v-model="filters.genre" @change="applyFilters" class="filter-select">
                <option value="">全部类型</option>
                <option v-for="genre in genres" :key="genre" :value="genre">
                  {{ genre }}
                </option>
              </select>
            </div>
            
            <!-- 年份范围 -->
            <div class="filter-group">
              <label class="filter-label">年份范围</label>
              <div class="range-inputs">
                <input 
                  type="number" 
                  v-model="filters.year_start" 
                  placeholder="起始" 
                  min="1900" 
                  :max="currentYear"
                  @change="applyFilters"
                  class="range-input"
                >
                <span class="range-separator">-</span>
                <input 
                  type="number" 
                  v-model="filters.year_end" 
                  placeholder="结束" 
                  min="1900" 
                  :max="currentYear"
                  @change="applyFilters"
                  class="range-input"
                >
              </div>
            </div>
          </div>
          
          <div class="filter-actions">
            <button @click="resetFilters" class="reset-btn">重置筛选</button>
            <div class="results-count">找到 {{ totalResults }} 部电影</div>
          </div>
        </div>
      </div>

      <!-- 电影网格 -->
      <div v-if="loading" class="loading-section">
        <div class="loading-spinner"></div>
        <p class="loading-text">正在加载电影...</p>
      </div>
      
      <div v-else-if="movies.length > 0" class="movies-grid-section">
        <div class="movies-grid">
          <MovieCard 
            v-for="movie in movies" 
            :key="movie.id" 
            :movie="movie"
            class="movie-grid-item"
          />
        </div>
        
        <!-- 分页控制 -->
        <div class="pagination-section" v-if="totalPages > 1">
          <div class="pagination-container">
            <button 
              @click="goToPage(currentPage - 1)" 
              :disabled="currentPage <= 1"
              class="pagination-btn pagination-prev"
            >
              <span>‹</span> 上一页
            </button>
            
            <div class="page-numbers">
              <button 
                v-for="page in visiblePages" 
                :key="page"
                @click="goToPage(page)"
                :class="['page-btn', { 'active': page === currentPage }]"
                :disabled="page === '...'"
              >
                {{ page }}
              </button>
            </div>
            
            <button 
              @click="goToPage(currentPage + 1)" 
              :disabled="currentPage >= totalPages"
              class="pagination-btn pagination-next"
            >
              下一页 <span>›</span>
            </button>
          </div>
          
          <div class="pagination-info">
            第 {{ currentPage }} 页，共 {{ totalPages }} 页
          </div>
        </div>
      </div>
      
      <!-- 无结果 -->
      <div v-else class="no-results-section">
        <div class="no-results-card">
          <div class="no-results-icon">🎭</div>
          <h3 class="no-results-title">未找到符合条件的电影</h3>
          <p class="no-results-subtitle">请尝试调整筛选条件或搜索其他内容</p>
          <button @click="resetFilters" class="retry-btn">重置筛选条件</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import MovieCard from '@/components/MovieCard.vue'
import { movieApi } from '@/services/movieApi'

export default {
  name: 'BrowseView',
  components: {
    MovieCard
  },
  data() {
    return {
      movies: [],
      genres: [],
      loading: false,
      currentPage: 1,
      totalResults: 0,
      totalPages: 0,
      itemsPerPage: 15, // 3行5列
      currentYear: new Date().getFullYear(),
      filters: {
        sort_by: 'popular',
        genre: '',
        year_start: null,
        year_end: null
      }
    }
  },
  computed: {
    visiblePages() {
      const delta = 2
      const range = []
      const rangeWithDots = []
      
      for (let i = Math.max(2, this.currentPage - delta);
           i <= Math.min(this.totalPages - 1, this.currentPage + delta);
           i++) {
        range.push(i)
      }
      
      if (this.currentPage - delta > 2) {
        rangeWithDots.push(1, '...')
      } else {
        rangeWithDots.push(1)
      }
      
      rangeWithDots.push(...range)
      
      if (this.currentPage + delta < this.totalPages - 1) {
        rangeWithDots.push('...', this.totalPages)
      } else if (this.totalPages > 1) {
        rangeWithDots.push(this.totalPages)
      }
      
      return rangeWithDots.filter((item, index, array) => array.indexOf(item) === index)
    }
  },
  async mounted() {
    await this.loadGenres()
    await this.loadMovies()
  },
  methods: {
    async loadGenres() {
      try {
        this.genres = await movieApi.getGenres()
      } catch (error) {
        console.error('加载电影类型失败:', error)
      }
    },
    
    async loadMovies() {
      this.loading = true
      try {
        const params = {
          skip: (this.currentPage - 1) * this.itemsPerPage,
          limit: this.itemsPerPage,
          ...this.filters
        }
        
        // 移除空值
        Object.keys(params).forEach(key => {
          if (params[key] === null || params[key] === '') {
            delete params[key]
          }
        })
        
        const response = await movieApi.getMoviesWithFilters(params)
        this.movies = response.data || response
        
        // 计算总页数（暂时使用简单估算）
        this.totalResults = this.movies.length > 0 ? Math.max(this.movies.length, 100) : 0
        this.totalPages = Math.ceil(this.totalResults / this.itemsPerPage)
        
      } catch (error) {
        console.error('加载电影失败:', error)
        this.movies = []
      } finally {
        this.loading = false
      }
    },
    
    async applyFilters() {
      this.currentPage = 1
      await this.loadMovies()
    },
    
    resetFilters() {
      this.filters = {
        sort_by: 'popular',
        genre: '',
        year_start: null,
        year_end: null
      }
      this.applyFilters()
    },
    
    async goToPage(page) {
      if (page >= 1 && page <= this.totalPages && page !== this.currentPage && page !== '...') {
        this.currentPage = page
        await this.loadMovies()
        // 滚动到顶部
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    }
  }
}
</script>

<style>
/* 全局样式确保完整覆盖 */
body, html {
  margin: 0 !important;
  padding: 0 !important;
  width: 100vw !important;
  overflow-x: hidden !important;
}
</style>

<style scoped>
/* 全局重置确保无边距 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* 主容器 */
.browse-view {
  min-height: 100vh;
  position: relative;
  padding-top: 100px; /* 为固定导航栏留出空间 */
  /* 更炫酷的科技感背景 - 与HomeView一致 */
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
  background-attachment: fixed; /* 关键：背景固定不滚动 */
  background-repeat: no-repeat;
  /* 确保背景完全覆盖整个页面 */
  background-size: cover;
  width: 100vw;
  margin: 0 !important;
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
  height: 45vh;
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  overflow: hidden;
  margin-bottom: 8vh; 
}

.hero-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: transparent; /* 移除局部背景，让整体背景显示 */
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
  max-width: 800px;
  padding: 0 20px;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  color: white;
  margin-bottom: 20px;
  text-shadow: 
    0 0 10px rgba(0, 255, 255, 0.5),
    0 0 20px rgba(0, 255, 255, 0.3),
    0 0 40px rgba(0, 255, 255, 0.1),
    0 2px 20px rgba(0, 0, 0, 0.8);
  line-height: 1.2;
  background: linear-gradient(
    45deg, 
    #ffffff 0%, 
    #00ffff 50%, 
    #ffffff 100%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: glow 3s ease-in-out infinite alternate;
}

@keyframes glow {
  from {
    filter: drop-shadow(0 0 5px rgba(0, 255, 255, 0.3));
  }
  to {
    filter: drop-shadow(0 0 15px rgba(0, 255, 255, 0.6));
  }
}

.hero-subtitle {
  font-size: 1.3rem;
  color: rgba(0, 255, 255, 0.8);
  margin-bottom: 0;
  font-weight: 300;
  line-height: 1.5;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

/* 内容容器 */
.content-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  background: rgba(0, 0, 0, 0.6); /* 增强背景透明度 */
  backdrop-filter: blur(15px); /* 增强毛玻璃效果 */
  border-radius: 20px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

/* 筛选卡片 */
.filter-card {
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 30px;
  border: 1px solid rgba(0, 255, 255, 0.2);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.card-header {
  text-align: center;
  margin-bottom: 25px;
}

.card-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 10px;
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

.title-icon {
  font-size: 2.2rem;
}

.card-subtitle {
  font-size: 1rem;
  color: rgba(0, 255, 255, 0.8);
  font-weight: 300;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

.filter-content {
  max-width: 800px;
  margin: 0 auto;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 15px;
  margin-bottom: 25px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-label {
  font-weight: 600;
  color: white;
  font-size: 0.95rem;
  margin-bottom: 3px;
}

.filter-select,
.range-input {
  padding: 15px 18px;
  border: 2px solid rgba(0, 255, 255, 0.3);
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.filter-select:focus,
.range-input:focus {
  outline: none;
  border-color: rgba(0, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 3px rgba(0, 255, 255, 0.1);
}

.filter-select option {
  background: rgba(30, 30, 60, 0.95);
  color: white;
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.range-separator {
  color: rgba(0, 255, 255, 0.7);
  font-weight: 500;
  font-size: 1.1rem;
}

.filter-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 25px;
  border-top: 1px solid rgba(0, 255, 255, 0.2);
}

.reset-btn {
  padding: 15px 30px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
  border: 2px solid rgba(0, 255, 255, 0.3);
  border-radius: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.reset-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(0, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
}

.results-count {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  font-size: 1rem;
}

/* 加载状态 */
.loading-section {
  text-align: center;
  padding: 80px 20px;
  color: white;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-top: 4px solid rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

.loading-text {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 电影网格区域 */
.movies-grid-section {
  margin-top: 40px;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
  margin-bottom: 40px;
}

.movie-grid-item {
  transition: transform 0.3s ease;
}

.movie-grid-item:hover {
  transform: translateY(-5px);
}

/* 分页区域 */
.pagination-section {
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 30px;
  border: 1px solid rgba(0, 255, 255, 0.2);
  text-align: center;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.pagination-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.pagination-btn {
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
  border: 2px solid rgba(0, 255, 255, 0.3);
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(0, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.page-numbers {
  display: flex;
  gap: 8px;
}

.page-btn {
  width: 45px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(0, 255, 255, 0.3);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.page-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(0, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
}

.page-btn.active {
  background: rgba(0, 255, 255, 0.2);
  border-color: rgba(0, 255, 255, 0.6);
  box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.pagination-info {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.95rem;
}

/* 无结果状态 */
.no-results-section {
  margin-top: 40px;
}

.no-results-card {
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 60px 40px;
  border: 1px solid rgba(0, 255, 255, 0.2);
  text-align: center;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.no-results-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.no-results-title {
  font-size: 1.8rem;
  color: white;
  margin-bottom: 10px;
  font-weight: 600;
}

.no-results-subtitle {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 30px;
}

.retry-btn {
  padding: 15px 30px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
  border: 2px solid rgba(0, 255, 255, 0.3);
  border-radius: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.retry-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(0, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .movies-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1.1rem;
  }
  
  .filter-card {
    padding: 30px 25px;
  }
  
  .filter-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .filter-actions {
    flex-direction: column;
    gap: 15px;
  }
  
  .movies-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
  }
  
  .pagination-container {
    flex-direction: column;
    gap: 20px;
  }
  
  .page-numbers {
    flex-wrap: wrap;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .movies-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .content-container {
    margin: -40px auto 0;
    padding: 30px 15px;
  }
  
  .filter-card {
    padding: 25px 20px;
  }
  
  .card-title {
    font-size: 1.6rem;
  }
}
</style>
