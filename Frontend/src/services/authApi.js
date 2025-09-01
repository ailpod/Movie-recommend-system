import axios from 'axios';

// 创建专门用于认证的axios实例
const authApiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1', // 后端API地址
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10秒超时
});

// 请求拦截器 - 自动添加token
authApiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log('发送认证请求:', config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理认证错误
authApiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('认证API请求错误:', error);
    
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

// 认证相关API
export default {
  // 用户注册
  register(userData) {
    return authApiClient.post('/auth/register', userData);
  },

  // 用户登录
  login(credentials) {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    return authApiClient.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },

  // 获取当前用户信息
  getCurrentUser() {
    return authApiClient.get('/users/me');
  },

  // 更新用户信息
  updateProfile(userData) {
    return authApiClient.put('/users/me', userData);
  },

  // 获取用户收藏列表
  getFavorites() {
    return authApiClient.get('/users/me/favorites');
  },

  // 添加电影到收藏
  addToFavorites(movieId) {
    return authApiClient.post(`/users/me/favorites/${movieId}`);
  },

  // 从收藏中移除电影
  removeFromFavorites(movieId) {
    return authApiClient.delete(`/users/me/favorites/${movieId}`);
  },

  // 检查电影是否已收藏
  async isFavorited(movieId) {
    try {
      const favorites = await this.getFavorites();
      return favorites.some(movie => movie.id === movieId);
    } catch (error) {
      console.error('检查收藏状态失败:', error);
      return false;
    }
  },

  // 退出登录
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
    window.location.href = '/login';
  },

  // 检查是否已登录
  isAuthenticated() {
    const token = localStorage.getItem('access_token');
    return !!token;
  },

  // 获取存储的token
  getToken() {
    return localStorage.getItem('access_token');
  },

  // 设置token
  setToken(token) {
    localStorage.setItem('access_token', token);
  },

  // 获取存储的用户信息
  getUserInfo() {
    const userInfo = localStorage.getItem('user_info');
    return userInfo ? JSON.parse(userInfo) : null;
  },

  // 设置用户信息
  setUserInfo(userInfo) {
    localStorage.setItem('user_info', JSON.stringify(userInfo));
  }
};
