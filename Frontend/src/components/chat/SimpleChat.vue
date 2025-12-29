<template>
  <div class="chat-container">
    <!-- 返回按钮 -->
    <div class="header">
      <button @click="goBack" class="back-btn">← 返回</button>
      <h2>AI 电影助手</h2>
    </div>

    <!-- 消息列表 -->
    <div ref="messagesContainer" class="messages">
      <div v-if="messages.length === 0" class="welcome">
        <h3>👋 你好！我是电影推荐助手</h3>
        <p>试试问我：</p>
        <button @click="send('推荐一些科幻电影')" class="suggestion">推荐一些科幻电影</button>
        <button @click="send('有哪些高分悬疑片？')" class="suggestion">有哪些高分悬疑片？</button>
      </div>

      <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.role]">
        <div class="message-bubble">
          <div class="message-header">{{ msg.role === 'user' ? 'You' : 'Agent' }}</div>
          <div class="message-content" v-html="renderMarkdown(msg.content)"></div>
        </div>
      </div>

      <!-- 加载指示器 -->
      <div v-if="isLoading" class="message assistant">
        <div class="message-bubble">
          <div class="message-header">Agent</div>
          <div class="loading-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="input-area">
      <input
        v-model="inputText"
        @keyup.enter="sendMessage"
        :disabled="isLoading"
        placeholder="输入消息... (Enter 发送)"
        class="input"
      />
      <button @click="sendMessage" :disabled="isLoading || !inputText.trim()" class="send-btn">
        发送
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import MarkdownIt from 'markdown-it'

const router = useRouter()
const messages = ref([])
const inputText = ref('')
const isLoading = ref(false)
const messagesContainer = ref(null)

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

const send = (text) => {
  inputText.value = text
  sendMessage()
}

const sendMessage = async () => {
  const text = inputText.value.trim()
  if (!text || isLoading.value) return

  // 添加用户消息
  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  scrollToBottom()

  // 创建 AI 消息
  const aiMessage = { role: 'assistant', content: '' }
  messages.value.push(aiMessage)
  scrollToBottom()

  isLoading.value = true

  try {
    const token = localStorage.getItem('access_token')
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    
    console.log('发送请求到:', `${API_BASE_URL}/api/v1/agent/chat/stream`)
    console.log('消息内容:', text)

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

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const jsonStr = line.slice(6).trim()
            if (!jsonStr) continue

            const data = JSON.parse(jsonStr)
            console.log('接收数据:', data)

            if (data.error) {
              throw new Error(data.error)
            }
            
            if (!data.done && data.content) {
              aiMessage.content += data.content
              scrollToBottom()
            }
          } catch (e) {
            console.error('解析错误:', e, '行:', line)
          }
        }
      }
    }

    if (!aiMessage.content) {
      aiMessage.content = '抱歉，我没有收到回复。'
    }

  } catch (error) {
    console.error('聊天错误:', error)
    aiMessage.content = `错误: ${error.message}`
  } finally {
    isLoading.value = false
  }
}

const goBack = () => {
  router.push('/browse')
}
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
}

.header {
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-btn {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.header h2 {
  margin: 0;
  color: white;
  font-size: 1.25rem;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.welcome {
  text-align: center;
  color: white;
  margin: auto;
}

.welcome h3 {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.welcome p {
  margin-bottom: 1.5rem;
  opacity: 0.8;
}

.suggestion {
  display: block;
  margin: 0.5rem auto;
  padding: 0.75rem 1.5rem;
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion:hover {
  background: rgba(59, 130, 246, 0.3);
  transform: translateY(-2px);
}

.message {
  display: flex;
  max-width: 80%;
}

.message.user {
  margin-left: auto;
}

.message.assistant {
  margin-right: auto;
}

.message-bubble {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  padding: 1rem 1.25rem;
  color: white;
}

.message.user .message-bubble {
  background: rgba(59, 130, 246, 0.3);
}

.message-header {
  font-size: 0.75rem;
  opacity: 0.6;
  margin-bottom: 0.5rem;
}

.message-content {
  line-height: 1.6;
}

.message-content :deep(p) {
  margin: 0.5rem 0;
}

.message-content :deep(ul), .message-content :deep(ol) {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.loading-dots {
  display: flex;
  gap: 0.25rem;
  padding: 0.5rem 0;
}

.loading-dots span {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.input-area {
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  gap: 1rem;
}

.input {
  flex: 1;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.75rem;
  color: white;
  font-size: 1rem;
  outline: none;
  transition: all 0.2s;
}

.input:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(59, 130, 246, 0.5);
}

.input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.send-btn {
  padding: 0.75rem 2rem;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
