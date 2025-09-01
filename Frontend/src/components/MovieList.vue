<template>
  <section class="movie-list-section">
    <!-- 列表标题 -->
    <div class="section-header">
      <h2 class="section-title">{{ title }}</h2>
      <button 
        v-if="showViewMore" 
        @click="$emit('view-more')"
        class="view-more-btn"
      >
        查看更多
        <svg class="arrow-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="m9 18 6-6-6-6"/>
        </svg>
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载电影...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <p class="error-message">{{ error }}</p>
      <button @click="$emit('retry')" class="retry-btn">重试</button>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!movies || movies.length === 0" class="empty-container">
      <div class="empty-icon">🎬</div>
      <p class="empty-message">暂无电影数据</p>
    </div>

    <!-- 电影列表 -->
    <div v-else class="movies-container">
      <div 
        class="movies-grid" 
        :class="{ 'horizontal-scroll': isHorizontal, 'grid-layout': !isHorizontal }"
      >
        <MovieCard 
          v-for="movie in displayMovies" 
          :key="movie.id" 
          :movie="movie"
          class="movie-item"
        />
      </div>

      <!-- 滚动控制按钮（仅水平滚动时显示） -->
      <div v-if="isHorizontal && movies.length > visibleCount" class="scroll-controls">
        <button 
          @click="scrollLeft" 
          class="scroll-btn scroll-left"
          :disabled="scrollPosition <= 0"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="m15 18-6-6 6-6"/>
          </svg>
        </button>
        <button 
          @click="scrollRight" 
          class="scroll-btn scroll-right"
          :disabled="scrollPosition >= maxScrollPosition"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="m9 18 6-6-6-6"/>
          </svg>
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import MovieCard from './MovieCard.vue'

// 定义props
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  movies: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  },
  isHorizontal: {
    type: Boolean,
    default: true
  },
  showViewMore: {
    type: Boolean,
    default: false
  },
  maxDisplay: {
    type: Number,
    default: null
  }
})

// 定义事件
const emit = defineEmits(['view-more', 'retry'])

// 响应式数据
const scrollPosition = ref(0)
const containerWidth = ref(0)
const itemWidth = ref(220) // 单个卡片宽度 - 调整为中等大小

// 计算属性
const displayMovies = computed(() => {
  if (!props.movies) return []
  return props.maxDisplay ? props.movies.slice(0, props.maxDisplay) : props.movies
})

const visibleCount = computed(() => {
  return Math.floor(containerWidth.value / itemWidth.value) || 5
})

const maxScrollPosition = computed(() => {
  return Math.max(0, displayMovies.value.length - visibleCount.value)
})

// 滚动方法
const scrollLeft = () => {
  scrollPosition.value = Math.max(0, scrollPosition.value - 1)
}

const scrollRight = () => {
  scrollPosition.value = Math.min(maxScrollPosition.value, scrollPosition.value + 1)
}

// 处理窗口大小变化
const handleResize = () => {
  // 这里可以根据需要更新containerWidth
  containerWidth.value = window.innerWidth - 80 // 减去padding
}

onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.movie-list-section {
  margin-bottom: 40px;
}

/* 章节头部 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 10px;
}

.section-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: white;
  margin: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.view-more-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.view-more-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.arrow-icon {
  width: 16px;
  height: 16px;
}

/* 状态容器 */
.loading-container,
.error-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-left: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

.error-icon,
.empty-icon {
  font-size: 3rem;
  margin-bottom: 15px;
}

.error-message,
.empty-message {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
  margin-bottom: 20px;
}

.retry-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* 电影容器 */
.movies-container {
  position: relative;
}

/* 水平滚动布局 */
.horizontal-scroll {
  display: flex;
  gap: 15px;
  overflow-x: auto;
  scroll-behavior: smooth;
  padding: 10px 0 20px 0;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
}

.horizontal-scroll .movie-item {
  flex-shrink: 0;
  width: 220px; /* 确保水平滚动时每个卡片宽度固定 */
}

.horizontal-scroll::-webkit-scrollbar {
  height: 6px;
}

.horizontal-scroll::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.horizontal-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.horizontal-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* 网格布局 */
.grid-layout {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 15px;
  padding: 10px 0;
}

/* 滚动控制按钮 */
.scroll-controls {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  transform: translateY(-50%);
  pointer-events: none;
  z-index: 10;
}

.scroll-btn {
  position: absolute;
  width: 40px;
  height: 40px;
  background: rgba(0, 0, 0, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  pointer-events: auto;
  backdrop-filter: blur(10px);
}

.scroll-btn:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.9);
  transform: scale(1.1);
}

.scroll-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.scroll-left {
  left: -20px;
}

.scroll-right {
  right: -20px;
}

.scroll-btn svg {
  width: 20px;
  height: 20px;
}

/* 动画 */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .section-title {
    font-size: 1.5rem;
  }

  .view-more-btn {
    font-size: 0.8rem;
    padding: 6px 12px;
  }

  .grid-layout {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
  }

  .horizontal-scroll {
    gap: 12px;
  }

  .scroll-controls {
    display: none; /* 在移动设备上隐藏滚动按钮 */
  }
}

@media (max-width: 480px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .section-title {
    font-size: 1.3rem;
  }

  .grid-layout {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 12px;
  }

  .horizontal-scroll {
    gap: 10px;
  }
}
</style>
