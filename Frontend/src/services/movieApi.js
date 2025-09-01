import axios from 'axios';

// 创建axios实例
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1', // 后端API地址
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10秒超时
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    console.log('发送请求:', config.url);
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
      // 服务器返回错误状态码
      const { status, data } = error.response;
      return Promise.reject({
        status,
        message: data.message || '服务器错误',
        data: data
      });
    } else if (error.request) {
      // 请求发送但没有收到响应
      return Promise.reject({
        status: 0,
        message: '网络连接失败，请检查网络设置'
      });
    } else {
      // 其他错误
      return Promise.reject({
        status: -1,
        message: error.message || '未知错误'
      });
    }
  }
);

// API方法集合
export default {
  // 获取热门电影
  getPopularMovies(page = 1) {
    return apiClient.get(`/movies/popular?page=${page}`);
  },

  // 获取高分电影
  getTopRatedMovies(page = 1) {
    return apiClient.get(`/movies/top-rated?page=${page}`);
  },

  // 获取最新电影
  getLatestMovies(page = 1) {
    return apiClient.get(`/movies/latest?page=${page}`);
  },

  // 根据ID获取电影详情
  getMovieById(id) {
    return apiClient.get(`/movie/${id}`);
  },

  // 获取电影推荐
  getRecommendations(id, limit = 10) {
    return apiClient.get(`/movie/${id}/recommendations?limit=${limit}`);
  },

  // 搜索电影
  searchMovies(query, page = 1) {
    return apiClient.get(`/search?q=${encodeURIComponent(query)}&page=${page}`);
  },

  // 获取电影类型列表
  getGenres() {
    return apiClient.get('/genres');
  },

  // 根据类型获取电影
  getMoviesByGenre(genreId, page = 1) {
    return apiClient.get(`/movies/genre/${genreId}?page=${page}`);
  },

  // 获取推荐电影（基于搜索关键词）
  getRecommendations(query) {
    return apiClient.get(`/movies/recommendations?q=${encodeURIComponent(query)}`);
  },

  // 获取演员信息
  getActorInfo(actorId) {
    return apiClient.get(`/actor/${actorId}`);
  },

  // 获取导演信息
  getDirectorInfo(directorId) {
    return apiClient.get(`/director/${directorId}`);
  }
};

// 工具函数：获取完整的图片URL
export const getImageUrl = (path, size = 'w500') => {
  if (!path) {
    // 返回一些示例电影海报图片
    const samplePosters = [
      'https://images.unsplash.com/photo-1489599210039-aeb5cf5abd63?w=300&h=450&fit=crop&crop=faces',
      'https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=300&h=450&fit=crop&crop=faces',
      'https://images.unsplash.com/photo-1594909122845-11baa439b7bf?w=300&h=450&fit=crop&crop=faces',
      'https://images.unsplash.com/photo-1518676590629-3dcbd9c5a5c9?w=300&h=450&fit=crop&crop=faces',
      'https://images.unsplash.com/photo-1595769816263-9b910be24d5f?w=300&h=450&fit=crop&crop=faces',
      'https://images.unsplash.com/photo-1505686994434-e3cc5abf1330?w=300&h=450&fit=crop&crop=faces'
    ];
    // 根据某种规则返回不同的示例海报
    const randomIndex = Math.floor(Math.random() * samplePosters.length);
    return samplePosters[randomIndex];
  }
  
  // 如果是完整URL，直接返回（某些情况下可能会有完整URL）
  if (path.startsWith('http')) {
    return path;
  }
  
  // 如果是相对路径，转换为TMDB完整URL
  if (path.startsWith('/')) {
    return `https://image.tmdb.org/t/p/${size}${path}`;
  }
  
  // 其他情况，假设是TMDB路径
  return `https://image.tmdb.org/t/p/${size}/${path}`;
};

// 工具函数：格式化评分（保留一位小数）
export const formatRating = (rating) => {
  if (!rating) return 'N/A';
  return Number(rating).toFixed(1);
};

// 工具函数：格式化发布日期
export const formatDate = (dateString) => {
  if (!dateString) return '未知';
  
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

// 工具函数：格式化电影时长
export const formatRuntime = (minutes) => {
  if (!minutes) return '未知';
  
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  
  if (hours > 0) {
    return `${hours}小时${mins}分钟`;
  }
  return `${mins}分钟`;
};
