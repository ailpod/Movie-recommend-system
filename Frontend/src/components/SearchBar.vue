<template>
  <form @submit.prevent="handleSearch" class="search-form">
    <div class="search-container">
      <input
        v-model="searchText"
        type="text"
        placeholder="搜索电影..."
        class="search-input"
        @focus="showSuggestions = true"
        @blur="hideSuggestions"
      />
      <button type="submit" class="search-button" :disabled="!searchText.trim()">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>

    <!-- 搜索建议下拉框 -->
    <div v-if="showSuggestions && suggestions.length > 0" class="suggestions-dropdown">
      <div
        v-for="suggestion in suggestions"
        :key="suggestion.id"
        class="suggestion-item"
        @mousedown="selectSuggestion(suggestion)"
      >
        <img 
          v-if="suggestion.poster_path" 
          :src="getImageUrl(suggestion.poster_path, 'w92')" 
          :alt="suggestion.title"
          class="suggestion-poster"
        />
        <div class="suggestion-info">
          <div class="suggestion-title">{{ suggestion.title }}</div>
          <div class="suggestion-year">{{ formatYear(suggestion.release_date) }}</div>
        </div>
      </div>
    </div>
  </form>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import movieApi, { getImageUrl } from '@/services/movieApi'

const router = useRouter()
const searchText = ref('')
const showSuggestions = ref(false)
const suggestions = ref([])
const searchTimeout = ref(null)

// 处理搜索提交
const handleSearch = () => {
  if (!searchText.value.trim()) return
  
  hideSuggestions()
  router.push({
    name: 'Search',
    query: { q: searchText.value.trim() }
  })
}

// 选择搜索建议
const selectSuggestion = (movie) => {
  searchText.value = movie.title
  hideSuggestions()
  router.push({
    name: 'MovieDetail',
    params: { id: movie.id }
  })
}

// 隐藏搜索建议
const hideSuggestions = () => {
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
}

// 获取搜索建议
const fetchSuggestions = async (query) => {
  if (!query.trim() || query.length < 2) {
    suggestions.value = []
    return
  }

  try {
    const response = await movieApi.searchMovies(query)
    suggestions.value = (response.results || []).slice(0, 5) // 只显示前5个建议
  } catch (error) {
    console.error('获取搜索建议失败:', error)
    suggestions.value = []
  }
}

// 格式化年份
const formatYear = (dateString) => {
  if (!dateString) return '未知年份'
  return new Date(dateString).getFullYear()
}

// 监听搜索文本变化，实现防抖搜索建议
watch(searchText, (newValue) => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }

  searchTimeout.value = setTimeout(() => {
    if (showSuggestions.value) {
      fetchSuggestions(newValue)
    }
  }, 300)
})
</script>

<style scoped>
.search-form {
  position: relative;
  width: 100%;
}

.search-container {
  display: flex;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 25px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.search-container:focus-within {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3);
}

.search-input {
  flex: 1;
  padding: 12px 20px;
  background: transparent;
  border: none;
  color: white;
  font-size: 16px;
  outline: none;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.search-button {
  padding: 12px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
}

.search-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.search-icon {
  width: 20px;
  height: 20px;
  color: white;
}

/* 搜索建议下拉框 */
.suggestions-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  margin-top: 5px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  max-height: 300px;
  overflow-y: auto;
}

.suggestion-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  gap: 12px;
}

.suggestion-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.suggestion-item:not(:last-child) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.suggestion-poster {
  width: 40px;
  height: 60px;
  object-fit: cover;
  border-radius: 6px;
  flex-shrink: 0;
}

.suggestion-info {
  flex: 1;
  min-width: 0;
}

.suggestion-title {
  color: white;
  font-weight: 500;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.suggestion-year {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .search-input {
    font-size: 16px; /* 防止iOS设备缩放 */
    padding: 10px 15px;
  }
  
  .search-button {
    padding: 10px 15px;
  }
  
  .search-icon {
    width: 18px;
    height: 18px;
  }
}
</style>
