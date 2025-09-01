<template>
  <div class="genre-view">
    <!-- 类型头部 -->
    <div class="genre-header">
      <div class="header-content">
        <div class="breadcrumb">
          <router-link to="/" class="breadcrumb-link">首页</router-link>
          <span class="breadcrumb-separator">></span>
          <span class="breadcrumb-current">{{ genreName || '类型浏览' }}</span>
        </div>
        
        <h1 class="genre-title">
          <span class="genre-icon">{{ genreIcon }}</span>
          {{ genreName || '加载中...' }}
        </h1>
        
        <p class="genre-description">{{ genreDescription }}</p>
      </div>
    </div>

    <!-- 电影列表 -->
    <div class="content-container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>正在加载{{ genreName }}电影...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container">
        <div class="error-icon">😕</div>
        <h2>加载失败</h2>
        <p class="error-message">{{ error }}</p>
        <button @click="fetchMovies" class="retry-btn">重新加载</button>
      </div>

      <!-- 无结果 -->
      <div v-else-if="movies.length === 0" class="no-results-container">
        <div class="no-results-icon">🎬</div>
        <h2>暂无电影</h2>
        <p class="no-results-message">当前分类下暂时没有电影数据</p>
      </div>

      <!-- 电影网格 -->
      <div v-else>
        <!-- 排序和过滤 -->
        <div class="controls-section">
          <div class="controls-container">
            <div class="sort-group">
              <label class="control-label">排序：</label>
              <select v-model="sortBy" @change="applySorting" class="control-select">
                <option value="popularity.desc">热门度</option>
                <option value="avg_rate.desc">评分</option>
                <option value="release_date.desc">最新</option>
                <option value="title.asc">标题</option>
              </select>
            </div>

            <div class="view-toggle">
              <button 
                @click="viewMode = 'grid'" 
                :class="['view-btn', { active: viewMode === 'grid' }]"
                title="网格视图"
              >
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M3 3h8v8H3V3zm10 0h8v8h-8V3zM3 13h8v8H3v-8zm10 0h8v8h-8v-8z"/>
                </svg>
              </button>
              <button 
                @click="viewMode = 'list'" 
                :class="['view-btn', { active: viewMode === 'list' }]"
                title="列表视图"
              >
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M3 4h18v2H3V4zm0 7h18v2H3v-2zm0 7h18v2H3v-2z"/>
                </svg>
              </button>
            </div>

            <div class="results-info">
              共 {{ totalResults.toLocaleString() }} 部电影
            </div>
          </div>
        </div>

        <!-- 电影展示区域 -->
        <div :class="['movies-display', viewMode]">
          <MovieCard 
            v-for="movie in displayMovies" 
            :key="movie.id" 
            :movie="movie"
            :class="['movie-item', { 'list-item': viewMode === 'list' }]"
          />
        </div>

        <!-- 加载更多 -->
        <div v-if="hasMore" class="load-more-container">
          <button 
            @click="loadMore" 
            :disabled="loadingMore"
            class="load-more-btn"
          >
            <span v-if="loadingMore" class="loading-text">
              <div class="mini-spinner"></div>
              加载中...
            </span>
            <span v-else>加载更多</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import MovieCard from '@/components/MovieCard.vue'
import movieApi from '@/services/movieApi'

const route = useRoute()

// 响应式数据
const movies = ref([])
const loading = ref(false)
const loadingMore = ref(false)
const error = ref(null)
const currentPage = ref(1)
const totalResults = ref(0)
const totalPages = ref(0)
const sortBy = ref('popularity.desc')
const viewMode = ref('grid')

// 类型信息映射
const genreInfo = {
  28: { name: '动作片', icon: '🎬', description: '充满刺激与冒险的动作电影' },
  12: { name: '冒险片', icon: '🗺️', description: '探索未知世界的冒险故事' },
  16: { name: '动画片', icon: '🎨', description: '精彩纷呈的动画世界' },
  35: { name: '喜剧片', icon: '😄', description: '轻松幽默的喜剧电影' },
  80: { name: '犯罪片', icon: '🔍', description: '扣人心弦的犯罪悬疑' },
  99: { name: '纪录片', icon: '📹', description: '真实记录生活的纪录电影' },
  18: { name: '剧情片', icon: '🎭', description: '深度刻画人性的剧情电影' },
  10751: { name: '家庭片', icon: '👨‍👩‍👧‍👦', description: '适合全家观看的温馨电影' },
  14: { name: '奇幻片', icon: '🦄', description: '充满魔法与想象的奇幻世界' },
  36: { name: '历史片', icon: '📚', description: '重现历史的史诗电影' },
  27: { name: '恐怖片', icon: '👻', description: '惊悚刺激的恐怖电影' },
  10402: { name: '音乐片', icon: '🎵', description: '美妙动听的音乐电影' },
  9648: { name: '悬疑片', icon: '🔮', description: '扑朔迷离的悬疑故事' },
  10749: { name: '爱情片', icon: '💕', description: '浪漫温馨的爱情故事' },
  878: { name: '科幻片', icon: '🚀', description: '探索未来的科幻电影' },
  10770: { name: '电视电影', icon: '📺', description: '电视制作的精彩电影' },
  53: { name: '惊悚片', icon: '😱', description: '紧张刺激的惊悚电影' },
  10752: { name: '战争片', icon: '⚔️', description: '展现战争题材的史诗电影' },
  37: { name: '西部片', icon: '🤠', description: '经典的西部牛仔电影' }
}

// 计算属性
const genreId = computed(() => parseInt(route.params.id))
const genreName = computed(() => genreInfo[genreId.value]?.name || '未知类型')
const genreIcon = computed(() => genreInfo[genreId.value]?.icon || '🎬')
const genreDescription = computed(() => genreInfo[genreId.value]?.description || '探索精彩的电影世界')

const displayMovies = computed(() => {
  let sortedMovies = [...movies.value]
  
  switch (sortBy.value) {
    case 'avg_rate.desc':
      sortedMovies.sort((a, b) => (b.avg_rate || 0) - (a.avg_rate || 0))
      break
    case 'release_date.desc':
      sortedMovies.sort((a, b) => new Date(b.release_date || 0) - new Date(a.release_date || 0))
      break
    case 'title.asc':
      sortedMovies.sort((a, b) => (a.title || '').localeCompare(b.title || ''))
      break
    default:
      // 保持原有顺序（热门度）
      break
  }
  
  return sortedMovies
})

const hasMore = computed(() => currentPage.value < totalPages.value)

// 获取电影数据
const fetchMovies = async (reset = true) => {
  if (reset) {
    loading.value = true
    currentPage.value = 1
    movies.value = []
  } else {
    loadingMore.value = true
  }
  
  error.value = null

  try {
    const response = await movieApi.getMoviesByGenre(genreId.value, currentPage.value)
    const newMovies = response.results || response || []
    
    if (reset) {
      movies.value = newMovies
    } else {
      movies.value = [...movies.value, ...newMovies]
    }
    
    totalResults.value = response.total_results || movies.value.length
    totalPages.value = response.total_pages || 1
    
  } catch (err) {
    console.error('获取类型电影失败:', err)
    error.value = err.message || '加载失败，请重试'
    
    // 设置模拟数据作为后备
    if (reset) {
      movies.value = generateMockMovies()
      totalResults.value = movies.value.length
      totalPages.value = 1
    }
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

// 生成模拟数据
const generateMockMovies = () => {
  const mockMovies = []
  for (let i = 1; i <= 20; i++) {
    mockMovies.push({
      id: `genre-${genreId.value}-${i}`,
      title: `${genreName.value} ${i}`,
      poster_path: null,
      avg_rate: Math.random() * 4 + 6,
      release_date: '2024-01-01',
      genre_ids: [genreId.value]
    })
  }
  return mockMovies
}

// 应用排序
const applySorting = () => {
  // 排序逻辑在computed属性中处理
}

// 加载更多
const loadMore = () => {
  if (hasMore.value && !loadingMore.value) {
    currentPage.value++
    fetchMovies(false)
  }
}

// 监听路由变化
watch(() => route.params.id, () => {
  if (route.name === 'Genre') {
    fetchMovies(true)
  }
})

// 组件挂载
onMounted(() => {
  fetchMovies(true)
})
</script>

<style scoped>
.genre-view {
  min-height: 100vh;
  background: #0f1419;
  color: white;
}

/* 类型头部 */
.genre-header {
  background: linear-gradient(
    135deg,
    rgba(102, 126, 234, 0.8) 0%,
    rgba(118, 75, 162, 0.8) 100%
  );
  padding: 60px 20px;
  text-align: center;
}

.header-content {
  max-width: 800px;
  margin: 0 auto;
}

.breadcrumb {
  margin-bottom: 20px;
  font-size: 0.9rem;
}

.breadcrumb-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: color 0.3s ease;
}

.breadcrumb-link:hover {
  color: white;
}

.breadcrumb-separator {
  margin: 0 10px;
  color: rgba(255, 255, 255, 0.6);
}

.breadcrumb-current {
  color: white;
  font-weight: 500;
}

.genre-title {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.genre-icon {
  font-size: 3.5rem;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.3));
}

.genre-description {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  line-height: 1.6;
}

/* 内容容器 */
.content-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
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
  padding: 40px 20px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-left: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

.error-icon,
.no-results-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.error-message,
.no-results-message {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
  margin-bottom: 30px;
}

.retry-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

/* 控制区域 */
.controls-section {
  margin-bottom: 30px;
}

.controls-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 20px;
  background: rgba(255, 255, 255, 0.05);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.sort-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.control-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
}

.control-select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
}

.control-select option {
  background: #1a2332;
  color: white;
}

.view-toggle {
  display: flex;
  gap: 5px;
}

.view-btn {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.7);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.view-btn svg {
  width: 20px;
  height: 20px;
}

.view-btn:hover,
.view-btn.active {
  background: rgba(102, 126, 234, 0.3);
  border-color: #667eea;
  color: white;
}

.results-info {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

/* 电影展示 */
.movies-display.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 25px;
  margin-bottom: 40px;
}

.movies-display.list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 40px;
}

.movie-item.list-item {
  width: 100%;
}

/* 加载更多 */
.load-more-container {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}

.load-more-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
}

.load-more-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.load-more-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.loading-text {
  display: flex;
  align-items: center;
  gap: 10px;
}

.mini-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-left: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .genre-title {
    font-size: 2rem;
    flex-direction: column;
    gap: 10px;
  }

  .genre-icon {
    font-size: 2.5rem;
  }

  .controls-container {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }

  .sort-group {
    justify-content: space-between;
  }

  .view-toggle {
    justify-content: center;
  }

  .results-info {
    text-align: center;
  }

  .movies-display.grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 20px;
  }
}

@media (max-width: 480px) {
  .genre-header {
    padding: 40px 15px;
  }

  .genre-title {
    font-size: 1.5rem;
  }

  .content-container {
    padding: 30px 15px;
  }

  .movies-display.grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 15px;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
