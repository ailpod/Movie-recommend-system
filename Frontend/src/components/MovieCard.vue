<template>
  <router-link :to="`/movie/${movie.id}`" class="movie-card">
    <div class="card-container">
      <!-- 电影海报 -->
      <div class="poster-container">
        <img 
          :src="getImageUrl(movie.poster_path)" 
          :alt="movie.title"
          class="movie-poster"
          @error="handleImageError"
          loading="lazy"
        />
        <div class="overlay">
          <div class="play-button">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </div>
        </div>
        
        <!-- 评分标签 -->
        <div v-if="movie.avg_rate" class="rating-badge">
          <span class="rating-score">{{ formatRating(movie.avg_rate) }}</span>
        </div>

        <!-- 匹配分数标签 -->
        <div v-if="showMatchScore && movie.matchScore" class="match-badge">
          <span class="match-score">{{ movie.matchScore }}%</span>
        </div>
      </div>

      <!-- 电影信息 -->
      <div class="movie-info">
        <h3 class="movie-title" :title="movie.title">{{ movie.title }}</h3>
        <p v-if="movie.release_year || movie.release_date" class="movie-year">
          {{ movie.release_year || formatYear(movie.release_date) }}
        </p>
        <div v-if="movieGenres && movieGenres.length > 0" class="movie-genres">
          <span 
            v-for="genre in movieGenres.slice(0, 2)" 
            :key="genre" 
            class="genre-tag"
          >
            {{ genre }}
          </span>
        </div>
      </div>
    </div>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'
import { getImageUrl, formatRating } from '@/services/movieApi'

// 定义props
const props = defineProps({
  movie: {
    type: Object,
    required: true,
    validator: (movie) => {
      return movie && movie.id && movie.title
    }
  },
  showMatchScore: {
    type: Boolean,
    default: false
  }
})

// 电影类型映射表
const genreMap = {
  28: '动作',
  12: '冒险',
  16: '动画',
  35: '喜剧',
  80: '犯罪',
  99: '纪录',
  18: '剧情',
  10751: '家庭',
  14: '奇幻',
  36: '历史',
  27: '恐怖',
  10402: '音乐',
  9648: '悬疑',
  10749: '爱情',
  878: '科幻',
  10770: '电视电影',
  53: '惊悚',
  10752: '战争',
  37: '西部'
}

// 格式化年份
const formatYear = (dateString) => {
  if (!dateString) return '未知年份'
  return new Date(dateString).getFullYear()
}

// 解析电影类型
const movieGenres = computed(() => {
  // 检查各种可能的类型字段
  if (props.movie.genres) {
    try {
      // 如果是字符串，先尝试按逗号分割（后端返回的格式）
      if (typeof props.movie.genres === 'string') {
        // 检查是否是逗号分隔的字符串
        if (props.movie.genres.includes(',')) {
          return props.movie.genres.split(',').map(g => g.trim()).filter(g => g)
        }
        // 如果不包含逗号，尝试 JSON 解析
        try {
          const parsed = JSON.parse(props.movie.genres)
          return Array.isArray(parsed) ? parsed : [parsed]
        } catch (jsonError) {
          // JSON 解析失败，直接返回单个类型
          return [props.movie.genres.trim()]
        }
      }
      // 如果已经是数组，直接返回
      if (Array.isArray(props.movie.genres)) {
        return props.movie.genres
      }
    } catch (e) {
      console.warn('解析电影类型失败:', e)
    }
  }
  
  // 检查 genre 字段（单个类型字符串）
  if (props.movie.genre) {
    if (typeof props.movie.genre === 'string') {
      return props.movie.genre.split(',').map(g => g.trim()).filter(g => g)
    }
    return [props.movie.genre]
  }
  
  // 检查 genre_ids 字段（TMDB 风格的 ID 数组）
  if (props.movie.genre_ids && Array.isArray(props.movie.genre_ids) && props.movie.genre_ids.length > 0) {
    return props.movie.genre_ids.map(id => getGenreName(id))
  }
  
})

// 获取类型名称
const getGenreName = (genreId) => {
  return genreMap[genreId] || '其他'
}

// 处理图片加载错误
const handleImageError = (event) => {
  event.target.src = '/placeholder-movie.jpg'
}
</script>

<style scoped>
.movie-card {
  display: block;
  text-decoration: none;
  color: inherit;
  width: 220px; /* 调整为中等大小 */
  min-width: 220px;
  flex-shrink: 0;
}

.card-container {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-container:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
  border-color: rgba(102, 126, 234, 0.5);
}

.poster-container {
  position: relative;
  width: 100%;
  aspect-ratio: 2/3;
  overflow: hidden;
}

.movie-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.card-container:hover .movie-poster {
  transform: scale(1.1);
}

/* 悬停遮罩层 */
.overlay {
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

.card-container:hover .overlay {
  opacity: 1;
}

.play-button {
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  transform: scale(0.8);
  transition: transform 0.3s ease;
}

.card-container:hover .play-button {
  transform: scale(1);
}

.play-button svg {
  width: 24px;
  height: 24px;
  margin-left: 3px; /* 调整播放图标位置 */
}

/* 评分标签 */
.rating-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.8);
  border-radius: 6px;
  padding: 4px 8px;
  backdrop-filter: blur(10px);
}

.rating-score {
  color: #ffd700;
  font-weight: bold;
  font-size: 0.9rem;
}

.match-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 6px;
  padding: 4px 8px;
  backdrop-filter: blur(10px);
}

.match-score {
  color: white;
  font-weight: bold;
  font-size: 0.8rem;
}

/* 电影信息区域 */
.movie-info {
  padding: 15px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.my-rating {
  margin-top: 8px;
}

.movie-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: white;
  margin: 0;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: 2.6em;
}

.movie-year {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  margin: 0;
}

.movie-genres {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: auto;
}

.genre-tag {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .movie-card {
    min-width: 130px;
  }
  
  .movie-title {
    font-size: 1rem;
  }
  
  .play-button {
    width: 50px;
    height: 50px;
  }
  
  .play-button svg {
    width: 20px;
    height: 20px;
  }
}

@media (max-width: 480px) {
  .movie-card {
    width: 160px; /* 手机端固定宽度 */
    min-width: 160px;
  }
  
  .movie-info {
    padding: 12px;
  }
  
  .movie-title {
    font-size: 0.95rem;
  }
  
  .rating-badge {
    top: 8px;
    right: 8px;
    padding: 3px 6px;
  }
  
  .rating-score {
    font-size: 0.8rem;
  }
}

/* 加载状态 */
.movie-poster[src=""] {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.1) 0%,
    rgba(255, 255, 255, 0.2) 50%,
    rgba(255, 255, 255, 0.1) 100%
  );
  background-size: 200px 100%;
  background-repeat: no-repeat;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% {
    background-position: -200px 0;
  }
  100% {
    background-position: calc(200px + 100%) 0;
  }
}
</style>
