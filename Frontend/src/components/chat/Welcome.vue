<script setup>
import { computed } from 'vue';

const emit = defineEmits(['select']);

const suggestions = computed(() => [
  {
    title: '🎬 推荐电影',
    desc: '根据你的喜好推荐电影',
    prompt: '推荐一些科幻电影'
  },
  {
    title: '🔍 相似电影',
    desc: '找到类似风格的电影',
    prompt: '有什么类似《盗梦空间》的电影？'
  },
  {
    title: '⭐ 高分电影',
    desc: '查找高评分的优质电影',
    prompt: '2020年后的高分动作片'
  },
  {
    title: '🎯 个性化推荐',
    desc: '基于你的观影历史推荐',
    prompt: '根据我的观影记录推荐电影'
  }
]);
</script>

<template>
  <div class="welcome-container">
    <!-- 顶部欢迎语 -->
    <div class="welcome-header">
      <div class="welcome-icon">🎬</div>
      <h1 class="welcome-title">
        你好！我是你的电影助手
      </h1>
      <p class="welcome-subtitle">
        我可以帮你搜索电影、推荐好片、分析观影偏好
      </p>
    </div>

    <!-- 建议卡片 -->
    <div class="suggestions-grid">
      <button 
        v-for="(item, index) in suggestions" 
        :key="index"
        @click="$emit('select', item.prompt)"
        class="suggestion-card"
      >
        <div class="card-content">
          <div class="card-title">
            {{ item.title }}
          </div>
          <div class="card-desc">
            {{ item.desc }}
          </div>
        </div>
      </button>
    </div>
  </div>
</template>

<style scoped>
.welcome-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 2rem 1rem;
  animation: fadeIn 0.5s ease-out forwards;
}

.welcome-header {
  text-align: center;
  margin-bottom: 3rem;
}

.welcome-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.welcome-title {
  font-size: 2rem;
  font-weight: 600;
  color: white;
  margin-bottom: 1rem;
}

.welcome-subtitle {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
}

.suggestions-grid {
  width: 100%;
  max-width: 800px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.suggestion-card {
  display: flex;
  align-items: flex-start;
  text-align: left;
  padding: 1.5rem;
  border-radius: 12px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  cursor: pointer;
  transition: all 0.3s;
}

.suggestion-card:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.card-content {
  flex: 1;
}

.card-title {
  font-weight: 600;
  color: white;
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.card-desc {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.7);
}

@keyframes fadeIn {
  from { 
    opacity: 0; 
    transform: translateY(20px); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0); 
  }
}

@media (max-width: 768px) {
  .suggestions-grid {
    grid-template-columns: 1fr;
  }
  
  .welcome-title {
    font-size: 1.5rem;
  }
}
</style>
