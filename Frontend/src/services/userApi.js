import axios from 'axios';

// 创建axios实例
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// 请求拦截器 - 添加认证token
apiClient.interceptors.request.use(
  (config) => {
    // 先尝试获取access_token，如果没有再尝试token
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API请求错误:', error);
    if (error.response) {
      const { status, data } = error.response;
      return Promise.reject({
        status,
        message: data.message || '服务器错误',
        data: data
      });
    } else if (error.request) {
      return Promise.reject({
        status: 0,
        message: '网络连接失败，请检查网络设置'
      });
    } else {
      return Promise.reject({
        status: -1,
        message: error.message || '未知错误'
      });
    }
  }
);

// 用户API方法集合
export default {
  // 获取当前用户信息
  getCurrentUser() {
    return apiClient.get('/users/me');
  },

  // 获取用户收藏的电影
  getUserFavorites() {
    return apiClient.get('/users/me/favorites');
  },

  // 添加电影到收藏
  addToFavorites(movieId) {
    return apiClient.post(`/users/me/favorites/${movieId}`);
  },

  // 从收藏中移除电影
  removeFromFavorites(movieId) {
    return apiClient.delete(`/users/me/favorites/${movieId}`);
  },

  // 获取用户观看历史
  getWatchHistory() {
    return apiClient.get('/users/me/history');
  },

  // 添加电影到观看历史
  addToHistory(movieId) {
    return apiClient.post(`/users/me/history/${movieId}`);
  },

  // 清空观看历史
  clearHistory() {
    return apiClient.delete('/users/me/history');
  },

  // 获取用户偏好设置
  getUserPreferences() {
    return apiClient.get('/users/me/preferences');
  },

  // 更新用户偏好设置
  updatePreferences(preferences) {
    return apiClient.put('/users/me/preferences', preferences);
  },

  // 更新用户信息
  updateProfile(profileData) {
    return apiClient.put('/users/me', profileData);
  },

  // 更改密码
  changePassword(passwordData) {
    return apiClient.post('/users/me/change-password', passwordData);
  }
};
