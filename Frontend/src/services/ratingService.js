/**
 * 评分相关 API
 */
import axios from 'axios'

// 创建专门用于评分的axios实例
const ratingApiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// 请求拦截器 - 自动添加token
ratingApiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
ratingApiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('评分API请求错误:', error)
    
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
      window.location.href = '/login'
    }
    
    return Promise.reject(error.response?.data || error)
  }
)

/**
 * 创建电影评分
 * @param {number} movieId - 电影ID
 * @param {number} rating - 评分（1.0-10.0）
 */
export const createRating = async (movieId, rating) => {
  const response = await ratingApiClient.post('/ratings/', {
    movie_id: movieId,
    rating: rating
  })
  return response
}

/**
 * 更新电影评分
 * @param {number} movieId - 电影ID
 * @param {number} rating - 新的评分（1.0-10.0）
 */
export const updateRating = async (movieId, rating) => {
  const response = await ratingApiClient.put(`/ratings/${movieId}`, {
    rating: rating
  })
  return response
}

/**
 * 删除电影评分
 * @param {number} movieId - 电影ID
 */
export const deleteRating = async (movieId) => {
  await ratingApiClient.delete(`/ratings/${movieId}`)
}

/**
 * 获取当前用户对某电影的评分
 * @param {number} movieId - 电影ID
 */
export const getUserMovieRating = async (movieId) => {
  try {
    const response = await ratingApiClient.get(`/ratings/movie/${movieId}`)
    return response
  } catch (error) {
    if (error.status === 404) {
      return null // 用户尚未评分
    }
    throw error
  }
}

/**
 * 获取当前用户的所有评分记录
 * @param {number} skip - 跳过的记录数
 * @param {number} limit - 返回的最大记录数
 */
export const getMyRatings = async (skip = 0, limit = 100) => {
  const response = await ratingApiClient.get('/ratings/my-ratings', {
    params: { skip, limit }
  })
  return response
}

/**
 * 提交或更新评分（智能判断是创建还是更新）
 * @param {number} movieId - 电影ID
 * @param {number} rating - 评分（1.0-10.0）
 */
export const submitRating = async (movieId, rating) => {
  try {
    // 先尝试获取现有评分
    const existingRating = await getUserMovieRating(movieId)
    
    if (existingRating) {
      // 如果已有评分，更新它
      return await updateRating(movieId, rating)
    } else {
      // 如果没有评分，创建新的
      return await createRating(movieId, rating)
    }
  } catch (error) {
    // 如果获取失败，尝试直接创建
    try {
      return await createRating(movieId, rating)
    } catch (createError) {
      // 如果创建失败且提示已存在，则更新
      if (createError.status === 400) {
        return await updateRating(movieId, rating)
      }
      throw createError
    }
  }
}
