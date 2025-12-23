import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/common/HomeView.vue'
import DetailView from '../views/movie/DetailView.vue'
import SearchView from '../views/movie/SearchView.vue'
import LoginView from '../views/auth/LoginView.vue'
import RegisterView from '../views/auth/RegisterView.vue'
import ProfileView from '../views/user/ProfileView.vue'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: {
      title: '首页 - 电影推荐系统'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: {
      title: '用户登录 - 电影推荐系统'
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: {
      title: '用户注册 - 电影推荐系统'
    }
  },
  {
    path: '/movie/:id',
    name: 'MovieDetail',
    component: DetailView,
    props: true,
    meta: {
      title: '电影详情 - 电影推荐系统'
    }
  },
  {
    path: '/search',
    name: 'Search',
    component: SearchView,
    meta: {
      title: '搜索结果 - 电影推荐系统'
    }
  },
  {
    path: '/browse',
    name: 'Browse',
    component: () => import('../views/movie/BrowseView.vue'),
    meta: {
      title: '电影浏览 - 电影推荐系统'
    }
  },
  {
    path: '/recommend',
    name: 'Recommend',
    component: () => import('../views/movie/RecommendView.vue'),
    meta: {
      title: '个性化推荐 - 电影推荐系统',
      requiresAuth: true
    }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: {
      title: '个人资料 - 电影推荐系统',
      requiresAuth: true
    }
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('../views/user/FavoritesView.vue'),
    meta: {
      title: '我的收藏 - 电影推荐系统',
      requiresAuth: true
    }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/user/HistoryView.vue'),
    meta: {
      title: '观看记录 - 电影推荐系统',
      requiresAuth: true
    }
  },
  {
    path: '/ratings',
    name: 'RatingHistory',
    component: () => import('../views/user/RatingHistoryView.vue'),
    meta: {
      title: '评分历史 - 电影推荐系统',
      requiresAuth: true
    }
  },
  {
    // 404页面
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/common/NotFoundView.vue'),
    meta: {
      title: '页面未找到 - 电影推荐系统'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // 如果有保存的滚动位置，恢复它
    if (savedPosition) {
      return savedPosition
    }
    // 否则滚动到顶部
    return { top: 0 }
  }
})

// 路由守卫：设置页面标题和认证检查
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title
  }
  
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    const authStore = useAuthStore()
    
    // 初始化认证状态（如果还未初始化）
    if (!authStore.initialized) {
      await authStore.initialize()
    }
    
    // 如果用户未登录，重定向到登录页面
    if (!authStore.isAuthenticated) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }
  }
  
  next()
})

// 路由错误处理
router.onError((error) => {
  console.error('路由错误:', error)
})

export default router
