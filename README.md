# 🎬 电影推荐系统

一个基于Vue.js + FastAPI的现代化电影推荐平台，实现个性化电影推荐、用户管理、收藏评分等完整功能。

## ✨ 主要功能

- 🔐 **用户认证系统** - JWT Token认证，注册登录
- 🎭 **电影浏览** - 电影信息展示，分类搜索
- ❤️ **收藏功能** - 个性化收藏管理
- 📈 **浏览历史** - 智能历史记录
- ⭐ **评分系统** - 用户评分功能
- 🎯 **智能推荐** - 基于用户偏好和行为的个性化推荐算法
- 📱 **响应式设计** - 适配多种设备

## 🏗️ 项目结构

```
Movie-recommend-system/
├── Backend/                    # 后端 FastAPI 应用
│   ├── app/
│   │   ├── main.py            # FastAPI 主应用入口
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 应用配置
│   │   │   ├── database.py    # 数据库连接
│   │   │   ├── security.py    # 安全认证
│   │   │   └── dependencies.py # 依赖注入
│   │   ├── models/            # 数据模型
│   │   │   └── models.py      # SQLAlchemy 模型
│   │   ├── schemas/           # Pydantic 模式
│   │   │   └── schemas.py     # API 数据模式
│   │   ├── crud/              # 数据库操作
│   │   │   ├── crud.py        # 基础 CRUD
│   │   │   └── crud_user_actions.py # 用户行为 CRUD
│   │   ├── routers/           # API 路由
│   │   │   ├── auth.py        # 认证路由
│   │   │   ├── users.py       # 用户管理
│   │   │   ├── movies.py      # 电影相关
│   │   │   └── api.py         # API 路由汇总
│   │   └── services/          # 业务逻辑
│   │       ├── recommendation.py     # 推荐服务
│   │       └── recommendation_utils.py # 推荐算法实现
│   ├── algorithm/             # 推荐算法
│   │   ├── movie_indices.pkl  # 电影索引
│   │   ├── movie_similarity.pkl # 相似度矩阵
│   │   └── Similarity_matrix.py # 相似度计算
│   ├── static/               # 静态资源
│   │   └── tmdb_1000_movies.json # 电影数据
│   ├── DataBase/             # 数据库工具
│   │   ├── import_data.py    # 数据导入
│   │   └── export_data.py    # 数据导出
│   └── Recommend.db          # SQLite 数据库
├── Frontend/                 # 前端 Vue.js 应用
│   ├── src/
│   │   ├── main.js          # Vue 应用入口
│   │   ├── App.vue          # 根组件
│   │   ├── components/      # 可复用组件
│   │   │   ├── AppHeader.vue    # 应用头部
│   │   │   ├── MovieCard.vue    # 电影卡片
│   │   │   ├── MovieList.vue    # 电影列表
│   │   │   └── SearchBar.vue    # 搜索栏
│   │   ├── views/           # 页面组件
│   │   │   ├── HomeView.vue     # 首页
│   │   │   ├── LoginView.vue    # 登录页
│   │   │   ├── RegisterView.vue # 注册页
│   │   │   ├── ProfileView.vue  # 个人资料
│   │   │   ├── BrowseView.vue   # 浏览页面
│   │   │   ├── SearchView.vue   # 搜索页面
│   │   │   ├── DetailView.vue   # 电影详情
│   │   │   ├── FavoritesView.vue # 收藏页面
│   │   │   ├── HistoryView.vue  # 历史记录
│   │   │   └── RecommendView.vue # 推荐页面
│   │   ├── services/        # API 服务
│   │   │   ├── authApi.js       # 认证 API
│   │   │   ├── movieApi.js      # 电影 API
│   │   │   ├── userApi.js       # 用户 API
│   │   │   └── ratingApi.js     # 评分 API
│   │   ├── stores/          # 状态管理
│   │   │   ├── auth.ts          # 认证状态
│   │   │   └── userStore.js     # 用户状态
│   │   └── router/          # 路由配置
│   │       └── index.js         # 路由定义
│   ├── package.json         # 前端依赖配置
│   └── vite.config.js       # Vite 构建配置
├── requirements.txt         # Python 依赖
└── README.md               # 项目说明
```

## 🚀 快速开始

### 环境要求

- **Python** 3.8+
- **Node.js** 16+
- **npm** 8+

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/ailpod/Movie-recommend-system.git
   cd Movie-recommend-system
   ```

2. **后端设置**
   ```bash
   # 安装 Python 依赖
   pip install -r requirements.txt
   
   # 进入后端目录
   cd Backend
   
   # 初始化数据库（首次运行）
   python DataBase/import_data.py
   
   # 启动后端服务
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **前端设置**（新开一个终端）
   ```bash
   cd Frontend
   
   # 安装依赖
   npm install
   
   # 启动开发服务器
   npm run dev
   ```

4. **访问应用**
   - 前端：http://localhost:5173
   - 后端API：http://localhost:8000
   - API文档：http://localhost:8000/docs

## 🎯 核心功能说明

### 推荐算法
- 基于用户偏好权重（60%）、收藏历史（30%）、浏览历史（10%）的加权推荐
- 使用余弦相似度矩阵计算电影相似性
- 支持动态类型偏好匹配

### 用户系统
- JWT Token认证
- 用户注册登录
- 个人偏好设置
- 收藏和历史管理

### 电影系统
- 1000+电影数据库
- 多维度分类浏览
- 搜索和过滤功能
- 电影详情和相似推荐

## 📱 技术栈

**后端**
- FastAPI - 现代Python Web框架
- SQLAlchemy - ORM数据库操作
- Pydantic - 数据验证
- JWT - 用户认证
- Scikit-learn - 机器学习
- Pandas/Numpy - 数据处理

**前端**
- Vue.js 3 - 响应式框架
- Vue Router - 路由管理
- Vite - 构建工具
- TypeScript - 类型安全
- CSS3 - 现代样式

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
