import axios from 'axios';

// 创建专门用于评分的axios实例
const ratingApiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1', // 后端API地址
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10秒超时
});

// 请求拦截器 - 自动添加token
ratingApiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log('发送评分请求:', config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
ratingApiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('评分API请求错误:', error);
    
    if (error.response?.status === 401) {
      // Token过期或无效，清除本地存储并跳转到登录页
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
      window.location.href = '/login';
    }
    
    if (error.response) {
      const { status, data } = error.response;
      return Promise.reject({
        status,
        message: data.detail || data.message || '服务器错误',
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

// 评分相关API
export default {
  // 创建或更新评分
  rateMovie(movieId, rating) {
    return ratingApiClient.post('/ratings/', {
      movie_id: movieId,
      rate: rating
    });
  },

  // 更新评分
  updateRating(movieId, rating) {
    return ratingApiClient.put(`/ratings/${movieId}`, {
      rate: rating
    });
  },

  // 删除评分
  deleteRating(movieId) {
    return ratingApiClient.delete(`/ratings/${movieId}`);
  },

  // 获取我的所有评分
  getMyRatings() {
    return ratingApiClient.get('/ratings/my-ratings');
  },

  // 获取电影的所有评分
  getMovieRatings(movieId, page = 1) {
    const skip = (page - 1) * 20;
    return ratingApiClient.get(`/ratings/movie/${movieId}?skip=${skip}&limit=20`);
  },

  // 获取我对特定电影的评分
  getMyRating(movieId) {
    return ratingApiClient.get(`/ratings/${movieId}/my-rating`);
  },

  // 检查是否已评分
  async hasRated(movieId) {
    try {
      await this.getMyRating(movieId);
      return true;
    } catch (error) {
      if (error.status === 404) {
        return false;
      }
      throw error;
    }
  }
};
