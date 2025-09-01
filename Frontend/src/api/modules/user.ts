/**
 * 用户相关 API
 */
import { apiClient } from '../client'
import type { Movie } from '@/types/movie'

export interface WatchHistoryItem {
  movie: Movie
  watch_date: string
}

export const userApi = {
  // 获取用户收藏的电影
  getFavorites: (): Promise<Movie[]> => {
    return apiClient.get('/api/v1/users/me/favorites')
  },

  // 添加电影到收藏
  addToFavorites: (movieId: number): Promise<void> => {
    return apiClient.post(`/api/v1/users/me/favorites/${movieId}`)
  },

  // 从收藏中移除电影
  removeFromFavorites: (movieId: number): Promise<void> => {
    return apiClient.delete(`/api/v1/users/me/favorites/${movieId}`)
  },

  // 获取观看历史
  getWatchHistory: (): Promise<WatchHistoryItem[]> => {
    return apiClient.get('/api/v1/users/me/history')
  },

  // 添加观看记录
  addToHistory: (movieId: number): Promise<void> => {
    return apiClient.post(`/api/v1/users/me/history/${movieId}`)
  },

  // 更新用户资料
  updateProfile: (data: any): Promise<any> => {
    return apiClient.put('/api/v1/users/me', data)
  }
}
