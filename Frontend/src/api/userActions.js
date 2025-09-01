// Frontend/src/api/userActions.js - 用户操作API
import apiClient from './client'

// 记录浏览历史
export const recordHistory = (movieId) => {
  return apiClient.post(`/users/me/history/${movieId}`)
}

// 获取浏览历史
export const fetchHistory = () => {
  return apiClient.get('/users/me/history')
}

// 删除特定浏览记录
export const deleteHistoryRecord = (movieId) => {
  return apiClient.delete(`/users/me/history/${movieId}`)
}

// 清空所有浏览历史
export const clearAllHistory = () => {
  return apiClient.delete('/users/me/history')
}

// 添加收藏
export const addFavorite = (movieId) => {
  return apiClient.post(`/users/me/favorites/${movieId}`)
}

// 移除收藏
export const removeFavorite = (movieId) => {
  return apiClient.delete(`/users/me/favorites/${movieId}`)
}

// 获取收藏列表
export const fetchFavorites = () => {
  return apiClient.get('/users/me/favorites')
}

// 检查收藏状态
export const checkFavoriteStatus = (movieId) => {
  return apiClient.get(`/users/me/favorites/${movieId}/status`)
}
