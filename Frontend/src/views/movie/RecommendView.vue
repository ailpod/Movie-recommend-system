<template>
  <div class="recommend-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">🌟个性化推荐</h1>
      <p class="page-subtitle">依据来源于观影历史、收藏和偏好</p>
    </div>

    <!-- 推荐算法状态 -->
    <div class="recommendation-status">
      <div v-if="!userPreferences" class="no-preferences">
        <div class="empty-state">
          <div class="empty-icon">🎭</div>
          <h3>还没有设置电影偏好</h3>
          <p>请先在个人资料页面设置您喜欢的电影类型</p>
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
    <div class="movies-section">
      <div class="section-header">
        <h2>为您推荐</h2>
        <p>基于智能算法精选的 {{ recommendations.length }} 部电影</p>
        <button @click="refreshRecommendations" class="refresh-btn" :disabled="loading">
          <i class="icon">🔄</i>
          {{ loading ? '刷新中...' : '换一批推荐' }}
        </button>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p class="loading-text">正在为您计算专属推荐...</p>
      </div>

      <!-- 推荐电影网格 -->
      <div v-else-if="recommendations.length > 0" class="movies-grid">
        <MovieCard 
          v-for="movie in recommendations" 
          :key="movie.id" 
          :movie="movie"
        />
      </div>

      <!-- 无推荐结果 -->
      <div v-else class="no-movies">
        <div class="empty-state">
          <div class="no-movies-icon">🔍</div>
          <h3>暂无推荐内容</h3>
          <p>多收藏和浏览一些电影，可以帮助我们更好地了解您的喜好！</p>
          <router-link to="/browse" class="btn btn-primary">
            <i class="icon">🎬</i>
            去浏览电影
          </router-link>
        </div>
      </div>
    </div>
    
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import userApi from '@/services/userApi';
import MovieCard from '@/components/MovieCard.vue';

const authStore = useAuthStore();
const recommendations = ref([]);
const loading = ref(true);

// 用户偏好
const userPreferences = computed(() => {
  return authStore.user?.like_genres
});

const fetchRecommendations = async () => {
  try {
    console.log("开始获取个性化推荐...");
    loading.value = true;
    const response = await userApi.getPersonalizedRecommendations();
    console.log("API响应:", response);
    
    // 处理响应数据
    if (response && response.data) {
      recommendations.value = response.data;
    } else if (Array.isArray(response)) {
      recommendations.value = response;
    } else {
      recommendations.value = [];
    }
    
    console.log("推荐结果:", recommendations.value);
  } catch (error) {
    console.error("获取个性化推荐失败:", error);
    // 显示错误详情
    if (error.response) {
      console.error("错误状态:", error.response.status);
      console.error("错误信息:", error.response.data);
    }
  } finally {
    loading.value = false;
  }
};

// 刷新推荐
const refreshRecommendations = () => {
  fetchRecommendations();
};

onMounted(() => {
  if (authStore.user) {
    fetchRecommendations();
  } else {
    loading.value = false;
  }
});
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
  text-align: center;
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
  justify-content: center;
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

.algorithm-info {
  margin: 30px 20px;
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
  font-size: 1.1rem;
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
  padding: 5px 0;
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

.movies-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
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
  margin-bottom: 20px;
}

.refresh-btn {
  background: linear-gradient(135deg, rgba(0, 255, 255, 0.8), rgba(123, 104, 238, 0.8));
  color: white;
  border: 1px solid rgba(0, 255, 255, 0.3);
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
}

.refresh-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 
    0 6px 20px rgba(0, 255, 255, 0.4),
    0 0 20px rgba(0, 255, 255, 0.2);
  background: linear-gradient(135deg, rgba(0, 255, 255, 0.9), rgba(123, 104, 238, 0.9));
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.refresh-btn .icon {
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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

.loading-text {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
  margin-bottom: 40px;
}

.no-movies {
  padding: 60px 20px;
  text-align: center;
  color: white;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  border: 1px solid rgba(0, 255, 255, 0.2);
}

.no-movies-icon {
  font-size: 3rem;
  margin-bottom: 20px;
  filter: drop-shadow(0 0 10px rgba(0, 255, 255, 0.3));
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .movies-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
  }
}

@media (max-width: 768px) {
  .page-title {
    font-size: 2.2rem;
  }
  
  .page-subtitle {
    font-size: 1rem;
  }
  
  .movies-grid {
    grid-template-columns: repeat(3, 1fr);
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
  
  .movies-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .recommendation-status {
    padding: 20px 10px;
  }
  
  .movies-section {
    padding: 20px 10px;
  }
}

/* 渐入动画效果 */
@media (prefers-reduced-motion: no-preference) {
  .page-header {
    animation: fadeInUp 1s ease-out;
  }

  .recommendation-status {
    animation: fadeInUp 1.2s ease-out;
  }

  .algorithm-info {
    animation: fadeInUp 1.4s ease-out;
  }

  .movies-section {
    animation: fadeInUp 1.6s ease-out;
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
