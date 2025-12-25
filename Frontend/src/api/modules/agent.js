/**
 * AI Agent API Client
 * 与后端 AI Agent 服务通信
 */
import apiClient from '../client'

/**
 * 与 AI 助手对话（非流式）
 * @param {Object} data - 请求数据
 * @param {string} data.message - 用户消息
 * @param {Object} data.context - 页面上下文
 * @param {Array} data.conversation_history - 对话历史
 * @returns {Promise<Object>} AI 回复
 */
export const chatWithAgent = async (data) => {
  const response = await apiClient.post('/agent/chat', {
    message: data.message,
    context: data.context || null,
    conversation_history: data.conversation_history || null,
    stream: false
  })
  return response.data
}

/**
 * 与 AI 助手对话（流式输出）
 * @param {Object} data - 请求数据
 * @param {Function} onChunk - 接收数据块的回调
 * @returns {Promise<void>}
 */
export const chatWithAgentStream = async (data, onChunk) => {
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  
  const response = await fetch(`${API_BASE_URL}/api/v1/agent/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    },
    body: JSON.stringify({
      message: data.message,
      context: data.context || null,
      conversation_history: data.conversation_history || null
    })
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    const text = decoder.decode(value)
    const lines = text.split('\n')

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6))
          if (data.error) {
            throw new Error(data.error)
          }
          if (!data.done && data.content) {
            onChunk(data.content)
          }
        } catch (e) {
          console.error('Parse error:', e)
        }
      }
    }
  }
}

/**
 * 更新页面上下文
 * @param {Object} context - 上下文信息
 * @returns {Promise<Object>}
 */
export const updateContext = async (context) => {
  const response = await apiClient.post('/agent/context', context)
  return response.data
}

/**
 * 快捷推荐接口
 * @param {number} limit - 推荐数量
 * @returns {Promise<Array>} 推荐电影列表
 */
export const getQuickRecommendations = async (limit = 5) => {
  const response = await apiClient.get('/agent/quick/recommend', {
    params: { limit }
  })
  return response.data
}

/**
 * 快捷相似电影接口
 * @param {number} movieId - 电影ID
 * @param {number} limit - 返回数量
 * @returns {Promise<Array>} 相似电影列表
 */
export const getQuickSimilarMovies = async (movieId, limit = 5) => {
  const response = await apiClient.get(`/agent/quick/similar/${movieId}`, {
    params: { limit }
  })
  return response.data
}

/**
 * 健康检查
 * @returns {Promise<Object>} 服务状态
 */
export const checkAgentHealth = async () => {
  const response = await apiClient.get('/agent/health')
  return response.data
}
