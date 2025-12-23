<template>
  <div class="home-view">
    <!-- 英雄区域 -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">发现你的下一部最爱电影</h1>
        <p class="hero-subtitle">基于智能算法的个性化电影推荐系统</p>
        <div class="hero-search">
          <SearchBar />
        </div>
      </div>
      <div class="hero-background">
        <div class="background-overlay"></div>
      </div>
    </section>

    <!-- 电影列表区域 -->
    <div class="content-container">
      <!-- 热门电影 -->
      <MovieList
        title="🔥 热门电影"
        :movies="popularMovies"
        :loading="loadingPopular"
        :error="errorPopular"
        :is-horizontal="true"
        :show-view-more="true"
        @view-more="handleViewMore('popular')"
        @retry="fetchPopularMovies"
      />

      <!-- 高分电影 -->
      <MovieList
        title="⭐ 高分精选"
        :movies="topRatedMovies"
        :loading="loadingTopRated"
        :error="errorTopRated"
        :is-horizontal="true"
        :show-view-more="true"
        @view-more="handleViewMore('top-rated')"
        @retry="fetchTopRatedMovies"
      />

      <!-- 最新电影 -->
      <MovieList
        title="🆕 最新上映"
        :movies="latestMovies"
        :loading="loadingLatest"
        :error="errorLatest"
        :is-horizontal="true"
        :show-view-more="true"
        @view-more="handleViewMore('latest')"
        @retry="fetchLatestMovies"
      />

      <!-- 推荐电影 -->
      <MovieList
        v-if="recommendedMovies.length > 0"
        title="🎯 为你推荐"
        :movies="recommendedMovies"
        :loading="loadingRecommended"
        :error="errorRecommended"
        :is-horizontal="true"
        @retry="fetchRecommendedMovies"
      />
    </div>

    <!-- 统计信息 -->
    <section class="stats-section">
      <div class="stats-container">
        <div class="stat-item">
          <div class="stat-number">{{ totalMovies.toLocaleString() }}</div>
          <div class="stat-label">电影总数</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ totalUsers.toLocaleString() }}</div>
          <div class="stat-label">用户数量</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ totalReviews.toLocaleString() }}</div>
          <div class="stat-label">评价数量</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import MovieList from '@/components/MovieList.vue'
import SearchBar from '@/components/SearchBar.vue'
import movieApi from '@/services/movieApi'

const router = useRouter()

// 响应式数据
const popularMovies = ref([])
const topRatedMovies = ref([])
const latestMovies = ref([])
const recommendedMovies = ref([])

// 加载状态
const loadingPopular = ref(false)
const loadingTopRated = ref(false)
const loadingLatest = ref(false)
const loadingRecommended = ref(false)

// 错误状态
const errorPopular = ref(null)
const errorTopRated = ref(null)
const errorLatest = ref(null)
const errorRecommended = ref(null)

// 统计数据
const totalMovies = ref(50000)
const totalUsers = ref(10000)
const totalReviews = ref(500000)

// 获取热门电影
const fetchPopularMovies = async () => {
  loadingPopular.value = true
  errorPopular.value = null
  
  try {
    const response = await movieApi.getPopularMovies()
    popularMovies.value = response.results || response || []
  } catch (error) {
    console.error('获取热门电影失败:', error)
    // 直接使用模拟数据，不显示错误
    popularMovies.value = generateMockMovies('热门')
  } finally {
    loadingPopular.value = false
  }
}

// 获取高分电影
const fetchTopRatedMovies = async () => {
  loadingTopRated.value = true
  errorTopRated.value = null
  
  try {
    const response = await movieApi.getTopRatedMovies()
    topRatedMovies.value = response.results || response || []
  } catch (error) {
    console.error('获取高分电影失败:', error)
    // 直接使用模拟数据，不显示错误
    topRatedMovies.value = generateMockMovies('高分')
  } finally {
    loadingTopRated.value = false
  }
}

// 获取最新电影
const fetchLatestMovies = async () => {
  loadingLatest.value = true
  errorLatest.value = null
  
  try {
    const response = await movieApi.getLatestMovies()
    latestMovies.value = response.results || response || []
  } catch (error) {
    console.error('获取最新电影失败:', error)
    // 直接使用模拟数据，不显示错误
    latestMovies.value = generateMockMovies('最新')
  } finally {
    loadingLatest.value = false
  }
}

// 获取推荐电影（基于用户行为）
const fetchRecommendedMovies = async () => {
  loadingRecommended.value = true
  errorRecommended.value = null
  
  try {
    // 这里可以根据用户历史记录获取推荐
    // 暂时使用热门电影作为推荐
    const response = await movieApi.getPopularMovies()
    recommendedMovies.value = (response.results || response || []).slice(5, 15)
  } catch (error) {
    console.error('获取推荐电影失败:', error)
    errorRecommended.value = error.message || '加载失败，请重试'
    recommendedMovies.value = []
  } finally {
    loadingRecommended.value = false
  }
}

// 生成模拟数据
const generateMockMovies = (category) => {
  const mockMovies = []
  const samplePosters = [
    'https://images.unsplash.com/photo-1489599210039-aeb5cf5abd63?w=300&h=450&fit=crop',
    'https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=300&h=450&fit=crop',
    'https://images.unsplash.com/photo-1594909122845-11baa439b7bf?w=300&h=450&fit=crop',
    'https://images.unsplash.com/photo-1518676590629-3dcbd9c5a5c9?w=300&h=450&fit=crop',
    'https://images.unsplash.com/photo-1595769816263-9b910be24d5f?w=300&h=450&fit=crop',
    'https://images.unsplash.com/photo-1505686994434-e3cc5abf1330?w=300&h=450&fit=crop',
    'https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=300&h=450&fit=crop',
    'https://images.unsplash.com/photo-1485846234645-a62644f84728?w=300&h=450&fit=crop'
  ]
  
  for (let i = 1; i <= 10; i++) {
    mockMovies.push({
      id: `${category}-${i}`,
      title: `${category}电影 ${i}`,
      poster_path: samplePosters[i % samplePosters.length], // 循环使用示例海报
      avg_rate: Math.random() * 4 + 6, // 6-10分
      release_date: '2024-01-01',
      genre_ids: [28, 12, 878] // 动作、冒险、科幻
    })
  }
  return mockMovies
}

// 处理查看更多
const handleViewMore = (category) => {
  router.push({
    name: 'Search',
    query: { category }
  })
}

// 组件挂载时获取数据
onMounted(() => {
  fetchPopularMovies()
  fetchTopRatedMovies()
  fetchLatestMovies()
  fetchRecommendedMovies()
})
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

.home-view {
  min-height: 100vh;
  position: relative;
  padding-top: 100px; /* 为固定导航栏留出空间 */
  /* 更炫酷的科技感背景 */
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
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  overflow: hidden;
  margin-bottom: 10vh; 
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
  margin-bottom: 40px;
  font-weight: 300;
  line-height: 1.5;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

.hero-search {
  max-width: 500px;
  margin: 0 auto;
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

/* 统计区域 */
.stats-section {
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(15px);
  padding: 60px 20px;
  margin: 80px 0 40px 0;
  box-shadow: 
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.stats-container {
  max-width: 800px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 40px;
  text-align: center;
}

.stat-item {
  padding: 20px;
}

.stat-number {
  font-size: 3rem;
  font-weight: 800;
  color: white;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #00bfff 0%, #7b68ee 50%, #ff69b4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 20px rgba(0, 191, 255, 0.3);
}

.stat-label {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1.1rem;
  }

  .hero-section {
    height: 60vh;
    min-height: 400px;
  }

  .stats-container {
    grid-template-columns: 1fr;
    gap: 30px;
  }

  .stat-number {
    font-size: 2.5rem;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1rem;
    margin-bottom: 30px;
  }

  .hero-section {
    height: 50vh;
    min-height: 350px;
    margin-bottom: 40px;
  }

  .content-container {
    padding: 0 15px;
  }

  .stats-section {
    padding: 40px 15px;
    margin: 60px 0 30px 0;
  }

  .stat-number {
    font-size: 2rem;
  }

  .stat-label {
    font-size: 1rem;
  }
}

/* 滚动动画 */
@media (prefers-reduced-motion: no-preference) {
  .hero-content {
    animation: fadeInUp 1s ease-out;
  }

  .stat-item {
    animation: fadeInUp 0.8s ease-out;
  }

  .stat-item:nth-child(2) {
    animation-delay: 0.2s;
  }

  .stat-item:nth-child(3) {
    animation-delay: 0.4s;
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
