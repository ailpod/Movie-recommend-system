<template>
  <div class="not-found-view">
    <div class="not-found-container">
      <!-- 404动画图标 -->
      <div class="animation-container">
        <div class="film-reel">
          <div class="reel reel-1">
            <div class="center-hole"></div>
            <div class="film-holes">
              <div v-for="i in 8" :key="i" class="hole" :style="{ transform: `rotate(${i * 45}deg)` }"></div>
            </div>
          </div>
          <div class="reel reel-2">
            <div class="center-hole"></div>
            <div class="film-holes">
              <div v-for="i in 8" :key="i" class="hole" :style="{ transform: `rotate(${i * 45}deg)` }"></div>
            </div>
          </div>
        </div>
        <div class="film-strip">
          <div class="film-frame" v-for="i in 5" :key="i">
            <div class="frame-holes">
              <div class="frame-hole"></div>
              <div class="frame-hole"></div>
              <div class="frame-hole"></div>
              <div class="frame-hole"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 错误信息 -->
      <div class="error-content">
        <h1 class="error-code">404</h1>
        <h2 class="error-title">页面走丢了</h2>
        <p class="error-message">
          抱歉，您访问的页面不存在或已被移动。<br>
          可能是因为URL输入错误，或者页面已被删除。
        </p>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <router-link to="/" class="btn btn-primary">
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              <polyline points="9,22 9,12 15,12 15,22"/>
            </svg>
            回到首页
          </router-link>
          
          <button @click="goBack" class="btn btn-secondary">
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="m12 19-7-7 7-7"/>
              <path d="M19 12H5"/>
            </svg>
            返回上页
          </button>
        </div>

        <!-- 搜索建议 -->
        <div class="search-suggestion">
          <p class="suggestion-text">或者试试搜索您想要的内容：</p>
          <div class="search-container">
            <SearchBar />
          </div>
        </div>

        <!-- 热门推荐 -->
        <div class="popular-suggestions">
          <h3 class="suggestions-title">热门推荐</h3>
          <div class="suggestion-links">
            <router-link to="/search?category=popular" class="suggestion-link">
              🔥 热门电影
            </router-link>
            <router-link to="/search?category=top-rated" class="suggestion-link">
              ⭐ 高分电影
            </router-link>
            <router-link to="/search?category=latest" class="suggestion-link">
              🆕 最新上映
            </router-link>
            <router-link to="/genre/28" class="suggestion-link">
              🎬 动作电影
            </router-link>
            <router-link to="/genre/35" class="suggestion-link">
              😄 喜剧电影
            </router-link>
            <router-link to="/genre/878" class="suggestion-link">
              🚀 科幻电影
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="floating-element" v-for="i in 6" :key="i" :style="getFloatingStyle(i)">
        {{ getRandomEmoji() }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import SearchBar from '@/components/SearchBar.vue'

const router = useRouter()

// 返回上一页
const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}

// 获取随机浮动样式
const getFloatingStyle = (index) => {
  const animations = [
    'float-1 8s ease-in-out infinite',
    'float-2 10s ease-in-out infinite',
    'float-3 12s ease-in-out infinite',
    'float-4 9s ease-in-out infinite',
    'float-5 11s ease-in-out infinite',
    'float-6 7s ease-in-out infinite'
  ]
  
  const positions = [
    { top: '10%', left: '10%' },
    { top: '20%', right: '15%' },
    { top: '60%', left: '5%' },
    { top: '70%', right: '10%' },
    { top: '30%', left: '80%' },
    { top: '80%', left: '70%' }
  ]
  
  return {
    ...positions[index % positions.length],
    animation: animations[index % animations.length],
    animationDelay: `${index * 0.5}s`
  }
}

// 获取随机表情
const getRandomEmoji = () => {
  const emojis = ['🎬', '🎭', '🎪', '🎨', '🎯', '🎲', '🎸', '🎺', '🎻', '🎤']
  return emojis[Math.floor(Math.random() * emojis.length)]
}
</script>

<style scoped>
.not-found-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f1419 0%, #1a2332 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.not-found-container {
  max-width: 800px;
  text-align: center;
  position: relative;
  z-index: 2;
}

/* 动画容器 */
.animation-container {
  margin-bottom: 40px;
  position: relative;
}

.film-reel {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 20px;
}

.reel {
  width: 100px;
  height: 100px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  position: relative;
  background: rgba(255, 255, 255, 0.05);
  animation: rotate 4s linear infinite;
}

.reel-1 {
  animation-direction: normal;
}

.reel-2 {
  animation-direction: reverse;
  animation-duration: 3s;
}

.center-hole {
  width: 20px;
  height: 20px;
  background: #0f1419;
  border-radius: 50%;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.film-holes {
  position: absolute;
  width: 100%;
  height: 100%;
}

.hole {
  width: 8px;
  height: 8px;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  position: absolute;
  top: 10px;
  left: 50%;
  transform-origin: 50% 40px;
  margin-left: -4px;
}

.film-strip {
  display: flex;
  justify-content: center;
  gap: 5px;
  opacity: 0.6;
}

.film-frame {
  width: 40px;
  height: 30px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  position: relative;
  animation: flicker 2s ease-in-out infinite;
  animation-delay: calc(var(--i) * 0.2s);
}

.frame-holes {
  display: flex;
  flex-direction: column;
  gap: 2px;
  position: absolute;
  left: -3px;
  top: 50%;
  transform: translateY(-50%);
}

.frame-hole {
  width: 2px;
  height: 4px;
  background: #0f1419;
}

/* 错误内容 */
.error-content {
  margin-bottom: 40px;
}

.error-code {
  font-size: 6rem;
  font-weight: 900;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
}

.error-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 20px;
  color: white;
}

.error-message {
  font-size: 1.2rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 40px;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 50px;
}

.btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px 25px;
  border-radius: 25px;
  text-decoration: none;
  font-weight: 500;
  font-size: 1rem;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-3px);
}

.btn-icon {
  width: 20px;
  height: 20px;
}

/* 搜索建议 */
.search-suggestion {
  margin-bottom: 40px;
}

.suggestion-text {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 20px;
}

.search-container {
  max-width: 400px;
  margin: 0 auto;
}

/* 热门推荐 */
.popular-suggestions {
  margin-bottom: 20px;
}

.suggestions-title {
  font-size: 1.5rem;
  margin-bottom: 20px;
  color: white;
}

.suggestion-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  max-width: 600px;
  margin: 0 auto;
}

.suggestion-link {
  display: block;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.suggestion-link:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  transform: translateY(-2px);
}

/* 背景装饰 */
.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.floating-element {
  position: absolute;
  font-size: 2rem;
  opacity: 0.1;
  user-select: none;
}

/* 动画 */
@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes flicker {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 0.3; }
}

@keyframes float-1 {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

@keyframes float-2 {
  0%, 100% { transform: translateX(0px) rotate(0deg); }
  50% { transform: translateX(20px) rotate(-180deg); }
}

@keyframes float-3 {
  0%, 100% { transform: translateY(0px) translateX(0px) rotate(0deg); }
  50% { transform: translateY(-15px) translateX(15px) rotate(90deg); }
}

@keyframes float-4 {
  0%, 100% { transform: translateY(0px) scale(1) rotate(0deg); }
  50% { transform: translateY(-25px) scale(1.1) rotate(-90deg); }
}

@keyframes float-5 {
  0%, 100% { transform: translateX(0px) rotate(0deg); }
  50% { transform: translateX(-20px) rotate(180deg); }
}

@keyframes float-6 {
  0%, 100% { transform: translateY(0px) translateX(0px) rotate(0deg); }
  50% { transform: translateY(20px) translateX(-10px) rotate(-180deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .error-code {
    font-size: 4rem;
  }

  .error-title {
    font-size: 2rem;
  }

  .error-message {
    font-size: 1rem;
  }

  .action-buttons {
    flex-direction: column;
    align-items: center;
    gap: 15px;
  }

  .btn {
    width: 100%;
    max-width: 250px;
    justify-content: center;
  }

  .film-reel {
    gap: 20px;
  }

  .reel {
    width: 80px;
    height: 80px;
  }

  .suggestion-links {
    grid-template-columns: 1fr;
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .not-found-view {
    padding: 15px;
  }

  .error-code {
    font-size: 3rem;
  }

  .error-title {
    font-size: 1.5rem;
  }

  .film-reel {
    gap: 15px;
  }

  .reel {
    width: 60px;
    height: 60px;
  }

  .center-hole {
    width: 15px;
    height: 15px;
  }

  .hole {
    width: 6px;
    height: 6px;
    top: 8px;
    transform-origin: 50% 22px;
  }

  .floating-element {
    font-size: 1.5rem;
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .not-found-view {
    background: #000;
  }
  
  .error-code {
    background: white;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .btn-primary {
    background: #0066cc;
  }
  
  .btn-secondary {
    background: #333;
    border-color: #666;
  }
}

/* 减少动画模式 */
@media (prefers-reduced-motion: reduce) {
  .reel {
    animation: none;
  }
  
  .film-frame {
    animation: none;
  }
  
  .floating-element {
    animation: none;
  }
}
</style>
