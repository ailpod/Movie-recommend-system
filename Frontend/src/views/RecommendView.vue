<template>
  <div class="recommend-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">🎯 个性化推荐</h1>
      <p class="page-subtitle">基于您的喜好为您精心推荐的电影</p>
    </div>

    <!-- 推荐算法状态 -->
    <div class="recommendation-status">
      <div v-if="!userPreferences" class="no-preferences">
        <div class="empty-state">
          <div class="empty-icon">🎭</div>
          <h3>还没有设置电影偏好</h3>
          <p>请先在个人资料页面设置您喜欢的电影类型，我们将为您提供个性化推荐</p>
          <router-link to="/profile" class="btn btn-primary">
            <i class="icon">⚙️</i>
            去设置偏好
          </router-link>
        </div>
      </div>
      
      <div v-else class="preferences-display">
        <h3>您的电影偏好</h3>
        <div class="genre-tags">
          <span v-for="genre in userPreferences.split(',')" :key="genre" class="genre-tag">
            {{ genre.trim() }}
          </span>
        </div>
      </div>
    </div>

    <!-- 推荐电影列表 -->
    <div v-if="userPreferences" class="recommendation-section">
      <div class="section-header">
        <h2>🌟 为您推荐</h2>
        <p>根据您的喜好精选的{{ recommendedMovies.length }}部电影</p>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>正在为您生成个性化推荐...</p>
      </div>

      <!-- 推荐电影网格 -->
      <div v-else-if="recommendedMovies.length > 0" class="movies-grid">
        <MovieCard 
          v-for="movie in recommendedMovies" 
          :key="movie.id" 
          :movie="movie"
          :show-match-score="true"
        />
      </div>

      <!-- 无推荐结果 -->
      <div v-else class="no-results">
        <div class="empty-state">
          <div class="empty-icon">🔍</div>
          <h3>暂无推荐内容</h3>
          <p>我们正在完善推荐算法，稍后再来看看吧！</p>
        </div>
      </div>
    </div>

    <!-- 推荐算法说明 -->
    <div class="algorithm-info">
      <details class="info-details">
        <summary>🧠 推荐算法说明</summary>
        <div class="info-content">
          <h4>我们的推荐基于以下因素：</h4>
          <ul>
            <li>🎭 您设置的电影类型偏好</li>
            <li>⭐ 电影的平均评分</li>
            <li>👥 您的最近浏览</li>
            <li>🔥 电影的热门程度</li>
          </ul>
          <p class="note">
            推荐算法会持续学习和优化，为您提供更精准的个性化推荐。
          </p>
        </div>
      </details>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import MovieCard from '@/components/MovieCard.vue'
import movieApi from '@/services/movieApi'

export default {
  name: 'RecommendView',
  components: {
    MovieCard
  },
  setup() {
    const authStore = useAuthStore()
    const loading = ref(false)
    const recommendedMovies = ref([])
    const allMovies = ref([])

    // 用户偏好
    const userPreferences = computed(() => {
      return authStore.user?.like_genres
    })

    // 获取所有电影
    const fetchAllMovies = async () => {
      try {
        const response = await movieApi.getMovies()
        allMovies.value = response.data
      } catch (error) {
        console.error('获取电影列表失败:', error)
      }
    }

    // 生成推荐
    const generateRecommendations = () => {
      if (!userPreferences.value || allMovies.value.length === 0) {
        return
      }

      loading.value = true

      try {
        // 用户喜欢的类型
        const likedGenres = userPreferences.value.split(',').map(g => g.trim())
        
        // 计算电影匹配分数
        const moviesWithScore = allMovies.value.map(movie => {
          let score = 0
          const movieGenres = movie.genres ? movie.genres.split(',').map(g => g.trim()) : []
          
          // 类型匹配分数 (40%)
          const genreMatches = likedGenres.filter(liked => 
            movieGenres.some(movieGenre => movieGenre.includes(liked) || liked.includes(movieGenre))
          ).length
          score += (genreMatches / likedGenres.length) * 40

          // 评分分数 (30%)
          score += (movie.avg_rate / 10) * 30

          // 热门度分数 (20%)
          const maxVotes = Math.max(...allMovies.value.map(m => m.vote))
          score += (movie.vote / maxVotes) * 20

          // 随机因子 (10%) - 增加推荐多样性
          score += Math.random() * 10

          return {
            ...movie,
            matchScore: Math.round(score)
          }
        })

        // 排序并获取推荐
        recommendedMovies.value = moviesWithScore
          .filter(movie => movie.matchScore > 20) // 过滤低分电影
          .sort((a, b) => b.matchScore - a.matchScore)
          .slice(0, 12) // 取前12部电影

      } catch (error) {
        console.error('生成推荐失败:', error)
      } finally {
        loading.value = false
      }
    }

    // 页面加载时执行
    onMounted(async () => {
      if (authStore.user) {
        await fetchAllMovies()
        generateRecommendations()
      }
    })

    return {
      loading,
      recommendedMovies,
      userPreferences,
      generateRecommendations
    }
  }
}
</script>

<style scoped>
/* 全局重置确保无边距 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.recommend-container {
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

.page-header {
  text-align: center;
  padding: 60px 20px;
  background: transparent;
  border-radius: 20px;
  margin: 20px;
  border: 1px solid rgba(0, 255, 255, 0.2);
}

.page-title {
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

.page-subtitle {
  font-size: 1.2rem;
  color: rgba(0, 255, 255, 0.8);
  font-weight: 300;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

.recommendation-status {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
}

.no-preferences {
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(0, 255, 255, 0.2);
}

.preferences-display {
  background: transparent;
  border-radius: 20px;
  padding: 30px;
  border: 1px solid rgba(0, 255, 255, 0.2);
}

.empty-state {
  color: white;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  filter: drop-shadow(0 0 10px rgba(0, 255, 255, 0.3));
}

.empty-state h3 {
  font-size: 1.8rem;
  margin-bottom: 15px;
  color: white;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

.empty-state p {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 30px;
  line-height: 1.6;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.btn-primary {
  background: linear-gradient(135deg, rgba(0, 255, 255, 0.8), rgba(123, 104, 238, 0.8));
  color: white;
  border: 1px solid rgba(0, 255, 255, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 6px 20px rgba(0, 255, 255, 0.4),
    0 0 20px rgba(0, 255, 255, 0.2);
  background: linear-gradient(135deg, rgba(0, 255, 255, 0.9), rgba(123, 104, 238, 0.9));
}

.preferences-display h3 {
  color: white;
  margin-bottom: 20px;
  font-size: 1.4rem;
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
  background: linear-gradient(135deg, rgba(0, 255, 255, 0.2), rgba(123, 104, 238, 0.2));
  color: rgba(0, 255, 255, 0.9);
  border: 1px solid rgba(0, 255, 255, 0.3);
  text-shadow: 0 0 5px rgba(0, 255, 255, 0.3);
}

.section-header {
  margin-bottom: 30px;
  text-align: center;
}

.section-header h2 {
  font-size: 1.8rem;
  color: white;
  margin-bottom: 10px;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

.section-header p {
  color: rgba(255, 255, 255, 0.8);
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: white;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top: 4px solid rgba(0, 255, 255, 0.8);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

.movies-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.no-results {
  padding: 60px 20px;
}

.algorithm-info {
  margin-top: 60px;
  background: #f9fafb;
  border-radius: 16px;
  overflow: hidden;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.no-results {
  padding: 60px 20px;
  text-align: center;
  color: white;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  border: 1px solid rgba(0, 255, 255, 0.2);
}

.algorithm-info {
  margin-top: 60px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(15px);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(0, 255, 255, 0.2);
}

.info-details {
  padding: 20px;
}

.info-details summary {
  font-weight: 600;
  color: white;
  cursor: pointer;
  user-select: none;
  outline: none;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

.info-details summary:hover {
  color: rgba(0, 255, 255, 0.8);
}

.info-content {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(0, 255, 255, 0.2);
}

.info-content h4 {
  margin-bottom: 15px;
  color: white;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

.info-content ul {
  list-style: none;
  padding: 0;
  margin-bottom: 15px;
}

.info-content li {
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.8);
}

.note {
  background: rgba(255, 193, 7, 0.1);
  border: 1px solid rgba(255, 193, 7, 0.3);
  border-radius: 8px;
  padding: 12px;
  color: rgba(255, 193, 7, 0.9);
  font-size: 0.9rem;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-title {
    font-size: 2.2rem;
  }
  
  .page-subtitle {
    font-size: 1rem;
  }
  
  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 16px;
  }
  
  .no-preferences,
  .preferences-display {
    padding: 20px;
  }
  
  .page-header {
    padding: 40px 20px;
    margin: 10px;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.8rem;
  }
  
  .recommendation-status {
    padding: 20px 10px;
  }
  
  .movies-section {
    padding: 20px 10px;
  }
}
</style>
