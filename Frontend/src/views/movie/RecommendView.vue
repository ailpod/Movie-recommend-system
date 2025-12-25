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
      <!-- 欢迎屏幕 -->
      <Welcome 
        v-if="messages.length === 0" 
        @select="sendSuggestion"
      />

      <!-- 消息列表 -->
      <div v-else class="messages-list">
        <MessageList
          v-for="(message, index) in messages"
          :key="index"
          :message="message"
          :message-index="index"
          @edit-user-message="handleEditUserMessage"
          @regenerate-response="handleRegenerateResponse"
          @like="handleLike"
          @dislike="handleDislike"
        />

        <!-- 加载指示器 -->
        <div v-if="isLoading" class="loading-message">
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
    <InputArea
      :is-generating="isLoading"
      :disabled="false"
      @send="handleSend"
      @stop="handleStop"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { chatWithAgent, chatWithAgentStream } from '@/api/modules/agent'
import Welcome from '@/components/chat/Welcome.vue'
import MessageList from '@/components/chat/MessageList.vue'
import InputArea from '@/components/chat/InputArea.vue'

const router = useRouter()

// State
const messages = ref([])
const isLoading = ref(false)
const error = ref(null)
const messagesContainer = ref(null)

// 返回上一页
const goBack = () => {
  router.back()
}

// 发送消息
const handleSend = async ({ text }) => {
  if (!text.trim() || isLoading.value) return

  const userMessage = {
    role: 'user',
    content: text,
    timestamp: new Date()
  }

  messages.value.push(userMessage)

  await nextTick()
  scrollToBottom()

  // 创建助手消息（流式输出）
  const assistantMessage = {
    role: 'assistant',
    content: '',
    timestamp: new Date(),
    isStreaming: true
  }
  
  messages.value.push(assistantMessage)
  await nextTick()
  scrollToBottom()

  isLoading.value = true
  error.value = null

  try {
    // 准备对话历史
    const conversationHistory = messages.value
      .slice(0, -1) // 排除刚添加的空助手消息
      .map(msg => ({
        role: msg.role,
        content: msg.content
      }))

    // 使用流式 API
    await chatWithAgentStream(
      {
        message: text,
        context: {
          page: 'recommend'
        },
        conversation_history: conversationHistory.length > 0 ? conversationHistory : null
      },
      (chunk) => {
        // 更新消息内容
        const lastMessage = messages.value[messages.value.length - 1]
        lastMessage.content += chunk
        scrollToBottom()
      }
    )

    // 流式传输完成
    const lastMessage = messages.value[messages.value.length - 1]
    lastMessage.isStreaming = false

  } catch (err) {
    console.error('Chat error:', err)
    error.value = err.message || '抱歉，我遇到了一些问题，请稍后再试'
    
    // 移除失败的消息
    messages.value.pop()
  } finally {
    isLoading.value = false
  }
}

// 停止生成
const handleStop = () => {
  isLoading.value = false
  const lastMessage = messages.value[messages.value.length - 1]
  if (lastMessage && lastMessage.isStreaming) {
    lastMessage.isStreaming = false
  }
}

// 发送建议
const sendSuggestion = (suggestion) => {
  handleSend({ text: suggestion })
}

// 编辑用户消息
const handleEditUserMessage = async (index, newContent) => {
  // 删除该消息之后的所有消息
  messages.value = messages.value.slice(0, index)
  
  // 发送新消息
  await handleSend({ text: newContent })
}

// 重新生成回复
const handleRegenerateResponse = async (index) => {
  // 找到对应的用户消息
  const userMessageIndex = index - 1
  if (userMessageIndex < 0) return
  
  const userMessage = messages.value[userMessageIndex]
  
  // 删除该回复及之后的消息
  messages.value = messages.value.slice(0, index)
  
  // 重新发送
  await handleSend({ text: userMessage.content })
}

// 点赞
const handleLike = (index) => {
  console.log('Like message at index:', index)
  // TODO: 实现点赞逻辑
}

// 踩
const handleDislike = (index) => {
  console.log('Dislike message at index:', index)
  // TODO: 实现踩逻辑
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 监听消息变化，自动滚动
watch(messages, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })

onMounted(() => {
  scrollToBottom()
})
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
  background-repeat: no-repeat;
  background-size: cover;
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
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(-2px);
}

.page-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
}

.title-icon {
  font-size: 1.5rem;
}

.spacer {
  width: 100px; /* 与返回按钮宽度相当，保持居中 */
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  scroll-behavior: smooth;
}

.messages-list {
  max-width: 900px;
  margin: 0 auto;
}

/* 加载指示器 */
.loading-message {
  display: flex;
  margin-bottom: 1.5rem;
  width: 100%;
}

.loading-content {
  flex: 1;
  max-width: 90%;
}

.loading-name {
  margin-bottom: 0.5rem;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

.loading-bubble {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border-radius: 0.75rem;
  padding: 0.875rem 1rem;
}

/* 打字指示器 */
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

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

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
  box-shadow: 0 2px 8px rgba(197, 48, 48, 0.1);
}

.error-icon {
  font-size: 1.2rem;
}

.close-error {
  margin-left: auto;
  background: none;
  border: none;
  color: #c53030;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-error:hover {
  background: rgba(197, 48, 48, 0.1);
}

/* 滚动条样式 */
.messages-area::-webkit-scrollbar {
  width: 8px;
}

.messages-area::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.messages-area::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 10px;
}

.messages-area::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .messages-area {
    padding: 1rem;
  }
}
</style>
