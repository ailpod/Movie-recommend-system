<template>
  <div class="recommend-container">
    <!-- 顶部工具栏 -->
    <div class="top-toolbar">
      <button @click="goBack" class="back-button">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        返回
      </button>
      <div class="page-title">
        <span>AI 电影助手</span>
      </div>
      <div class="spacer"></div>
    </div>

    <!-- 消息区域 -->
    <div ref="messagesContainer" class="messages-area">
      <!-- 欢迎界面 -->
      <div v-if="messages.length === 0" class="welcome-screen">
        <div class="welcome-content">
          <h2>欢迎使用电影助手</h2>
          <p>我可以帮你推荐电影、搜索影片、分析你的观影偏好</p>
          <div class="suggestions">
            <button @click="sendSuggestion('推荐一些科幻电影')" class="suggestion-chip">推荐一些科幻电影</button>
            <button @click="sendSuggestion('有哪些高分悬疑片？')" class="suggestion-chip">有哪些高分悬疑片？</button>
            <button @click="sendSuggestion('给我推荐电影')" class="suggestion-chip">根据我的口味推荐</button>
          </div>
        </div>
      </div>

      <!-- 消息列表 -->
      <div v-else class="messages-list">
        <!-- 消息项 -->
        <div v-for="(msg, index) in messages" :key="index" class="message-wrapper">
          <!-- 用户消息 -->
          <div v-if="msg.role === 'user'" class="user-message-container">
            <div class="message-avatar">
              <img src="http://localhost:8000/static/identify.jpg" alt="avatar" />
            </div>
            <div class="message-content-wrapper">
              <div class="message-header">
                <span class="message-author">{{ currentUser?.username || 'You' }}</span>
              </div>
              <div class="message-bubble user-bubble">
                <div class="message-text">{{ msg.content }}</div>
              </div>
              <div class="message-actions">
                <button @click="copyMessage(msg.content)" class="action-btn" title="复制">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                  </svg>
                </button>
                <button @click="editMessage(index)" class="action-btn" title="编辑">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- AI 消息 -->
          <div v-else class="assistant-message-container">
            <div class="message-avatar ai-avatar">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                <path d="M2 17l10 5 10-5"></path>
                <path d="M2 12l10 5 10-5"></path>
              </svg>
            </div>
            <div class="message-content-wrapper">
              <div class="message-header">
                <span class="message-author">Agent</span>
                <span v-if="msg.isStreaming" class="streaming-badge">生成中</span>
              </div>
              <div class="message-bubble assistant-bubble">
                <div class="message-text" v-html="renderMarkdown(msg.content)"></div>
                <span v-if="msg.isStreaming" class="typing-cursor"></span>
              </div>
              <div class="message-actions">
                <button @click="copyMessage(msg.content)" class="action-btn" title="复制">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 加载指示器 -->
        <div v-if="isLoading && messages.length > 0 && !messages[messages.length - 1].isStreaming" class="loading-message">
          <div class="loading-content">
            <div class="loading-name">Agent</div>
            <div class="loading-bubble">
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="error-message">
        <span class="error-icon">⚠️</span>
        <span>{{ error }}</span>
        <button @click="error = null" class="close-error">✕</button>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-container">
      <div class="input-wrapper">
        <input
          v-model="inputText"
          @keyup.enter="sendMessage"
          :disabled="isLoading"
          placeholder="输入你的问题... (Enter 发送, Shift+Enter 换行)"
          class="message-input"
        />
        <button 
          @click="sendMessage" 
          :disabled="isLoading || !inputText.trim()" 
          class="send-button"
        >
          <svg v-if="!isLoading" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
          <div v-else class="button-spinner"></div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import MarkdownIt from 'markdown-it'

const router = useRouter()
const authStore = useAuthStore()
const messages = ref([])
const inputText = ref('')
const isLoading = ref(false)
const error = ref(null)
const messagesContainer = ref(null)

// 获取当前用户信息
const currentUser = ref(authStore.user)

onMounted(async () => {
  // 确保用户信息已加载
  if (!currentUser.value) {
    await authStore.fetchUserProfile()
    currentUser.value = authStore.user
  }
})

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true
})

const renderMarkdown = (text) => {
  return md.render(text || '')
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const goBack = () => {
  router.back()
}

const sendSuggestion = (text) => {
  inputText.value = text
  sendMessage()
}

// 复制消息内容
const copyMessage = async (content) => {
  try {
    await navigator.clipboard.writeText(content)
    // 可以添加提示
  } catch (err) {
    console.error('复制失败:', err)
  }
}

// 编辑用户消息
const editMessage = (index) => {
  const message = messages.value[index]
  if (message.role === 'user') {
    inputText.value = message.content
    // 删除该消息及之后的所有消息
    messages.value = messages.value.slice(0, index)
  }
}

const sendMessage = async () => {
  const text = inputText.value.trim()
  if (!text || isLoading.value) return

  // 添加用户消息
  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  scrollToBottom()

  // 创建 AI 消息
  const aiMessage = { role: 'assistant', content: '', isStreaming: true }
  messages.value.push(aiMessage)
  scrollToBottom()

  isLoading.value = true
  error.value = null

  try {
    const token = localStorage.getItem('access_token')
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

    const response = await fetch(`${API_BASE_URL}/api/v1/agent/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        message: text,
        context: { page: 'recommend' },
        conversation_history: null
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let receivedData = false

    console.log('🔄 开始接收流式数据...')

    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        console.log('✅ 流结束')
        break
      }

      buffer += decoder.decode(value, { stream: true })
      console.log('📦 收到数据块:', buffer.substring(0, 100))
      
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const jsonStr = line.slice(6).trim()
            if (!jsonStr) continue

            console.log('📨 解析 JSON:', jsonStr.substring(0, 100))
            const data = JSON.parse(jsonStr)
            
            if (data.error) {
              throw new Error(data.error)
            }
            
            if (!data.done && data.content) {
              receivedData = true
              aiMessage.content += data.content
              // console.log('✍️ 添加内容:', data.content.substring(0, 50))
              
              // 强制触发 Vue 响应式更新
              messages.value = [...messages.value]
              scrollToBottom()
            } else if (data.done) {
              console.log('🏁 收到结束标记')
            }
          } catch (e) {
            console.error('❌ 解析错误:', e, '原始行:', line)
          }
        }
      }
    }

    console.log('📊 接收统计 - 收到数据:', receivedData, '内容长度:', aiMessage.content.length)

    aiMessage.isStreaming = false
    messages.value = [...messages.value] // 强制更新

    if (!aiMessage.content) {
      aiMessage.content = '抱歉，我没有收到回复。'
    }

  } catch (err) {
    console.error('聊天错误:', err)
    error.value = `发送失败: ${err.message}`
    messages.value.pop() // 移除失败的 AI 消息
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.recommend-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
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
  z-index: 1;
}

/* 顶部工具栏 */
.top-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(-2px);
}

.page-title {
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
}

.spacer {
  width: 100px;
}

/* 消息区域 */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  scroll-behavior: smooth;
}

.messages-area::-webkit-scrollbar {
  width: 8px;
}

.messages-area::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

.messages-area::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 10px;
}

/* 欢迎界面 */
.welcome-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.welcome-content {
  text-align: center;
  color: white;
  max-width: 600px;
}

.welcome-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.welcome-content h2 {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.welcome-content p {
  font-size: 1.1rem;
  opacity: 0.8;
  margin-bottom: 2rem;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: center;
}

.suggestion-chip {
  padding: 0.75rem 1.5rem;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 20px;
  color: #60a5fa;
  cursor: pointer;
  transition: all 0.3s;
}

.suggestion-chip:hover {
  background: rgba(59, 130, 246, 0.3);
  transform: translateY(-2px);
}

/* 消息列表 */
.messages-list {
  max-width: 900px;
  margin: 0 auto;
}

.message-wrapper {
  margin-bottom: 2rem;
}

/* 用户消息 */
.user-message-container,
.assistant-message-container {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.user-message-container {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.message-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: #e5e5e5;
  color: #666;
  font-weight: 600;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-avatar {
  background: #f5f5f5;
  color: #666;
}

.message-content-wrapper {
  flex: 1;
  min-width: 0;
  max-width: 70%;
}

.user-message-container .message-content-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
}

.message-author {
  font-weight: 500;
}

.streaming-badge {
  background: rgba(0, 0, 0, 0.1);
  color: rgba(255, 255, 255, 0.7);
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
  font-size: 0.65rem;
}

/* 消息气泡 */
.message-bubble {
  padding: 0.875rem 1rem;
  border-radius: 12px;
  word-break: break-word;
  line-height: 1.6;
}

.user-bubble {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border-bottom-right-radius: 4px;
}

.assistant-bubble {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border-bottom-left-radius: 4px;
}

.message-text {
  font-size: 0.95rem;
}

.message-text :deep(p) {
  margin: 0.5rem 0;
}

.message-text :deep(p:first-child) {
  margin-top: 0;
}

.message-text :deep(p:last-child) {
  margin-bottom: 0;
}

.message-text :deep(ul),
.message-text :deep(ol) {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.message-text :deep(code) {
  background: rgba(0, 0, 0, 0.05);
  padding: 0.15rem 0.3rem;
  border-radius: 3px;
  font-size: 0.9em;
  color: #333;
}

.message-text :deep(pre) {
  background: rgba(0, 0, 0, 0.05);
  padding: 0.75rem;
  border-radius: 6px;
  overflow-x: auto;
  margin: 0.5rem 0;
}

.typing-cursor {
  display: inline-block;
  width: 2px;
  height: 1.2em;
  margin-left: 0.25rem;
  background: #666;
  vertical-align: text-bottom;
  animation: blink 0.7s step-end infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* 消息操作按钮 */
.message-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.message-wrapper:hover .message-actions {
  opacity: 1;
}

.action-btn {
  padding: 0.25rem;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  color: rgba(255, 255, 255, 0.9);
  transform: scale(1.1);
}

/* 加载指示器 */
.loading-message {
  display: flex;
  margin-bottom: 1.5rem;
}

.loading-content {
  max-width: 90%;
}

.loading-name {
  margin-bottom: 0.5rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
}

.loading-bubble {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border-radius: 0.75rem;
  padding: 0.875rem 1rem;
}

.typing-indicator {
  display: flex;
  gap: 0.4rem;
  padding: 0.5rem 0;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.4);
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { 
    transform: translateY(0);
    opacity: 0.3;
  }
  30% {
    transform: translateY(-8px);
    opacity: 1;
  }
}

/* 错误消息 */
.error-message {
  max-width: 900px;
  margin: 1rem auto;
  background: #fed7d7;
  color: #c53030;
  padding: 1rem;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.close-error {
  margin-left: auto;
  background: none;
  border: none;
  color: #c53030;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
}

/* 输入区域 */
.input-container {
  padding: 1.5rem 2rem;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.input-wrapper {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.message-input {
  flex: 1;
  padding: 0.875rem 1.25rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: white;
  font-size: 0.95rem;
  outline: none;
  transition: all 0.3s;
}

.message-input:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(59, 130, 246, 0.5);
}

.message-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.send-button {
  padding: 0.875rem 1.5rem;
  background: #f5f5f5;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  color: #333;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-button:hover:not(:disabled) {
  background: #e8e8e8;
  border-color: #d4d4d4;
}

.send-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.send-button svg {
  stroke: #333;
  width: 1.25rem;
  height: 1.25rem;
}

.send-button {
  padding: 0.875rem 1.5rem;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  border-radius: 12px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.button-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .messages-area {
    padding: 1rem;
  }
  
  .input-container {
    padding: 1rem;
  }
  
  .top-toolbar {
    padding: 1rem;
  }
}
</style>
