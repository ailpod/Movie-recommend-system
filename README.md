# 🎬 电影推荐系统

一个基于 **Vue 3 + TypeScript** 和 **FastAPI** 的现代化智能电影推荐平台，采用前后端分离架构，实现个性化推荐、用户管理、收藏评分等完整功能。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.4-brightgreen.svg)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 主要功能

### 核心功能
- 🔐 **用户认证系统** - JWT Token 认证，安全的注册登录机制
- 🎭 **电影浏览** - 1000+ 电影数据库，精美卡片展示，分类筛选
- ❤️ **收藏功能** - 个性化收藏管理，快速收藏/取消
- 📈 **浏览历史** - 自动记录浏览轨迹，智能历史管理
- ⭐ **评分系统** - 5星评分机制，支持用户评价
- 🎯 **智能推荐** - 基于协同过滤和内容推荐的混合推荐算法
- 🔍 **搜索功能** - 支持电影名称、类型、年份等多维度搜索
- 📱 **响应式设计** - 完美适配桌面端、平板、移动端

### 技术亮点
- 🚀 **高性能** - 异步 FastAPI 后端，Vite 快速构建
- 🎨 **现代 UI** - TailwindCSS 美化，流畅动画效果
- 🔒 **安全可靠** - 密码加密存储，Token 验证机制
- 📊 **数据分析** - 基于 scikit-learn 的推荐算法
- 🛠️ **类型安全** - TypeScript + Pydantic 双重类型检查

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

### 📋 环境要求

| 软件 | 版本要求 | 说明 |
|------|---------|------|
| Python | 3.8+ | 后端运行环境 |
| Node.js | 18.0+ | 前端运行环境 |
| npm | 8.0+ | 包管理工具 |
| pip | 最新版 | Python 包管理 |

### 📥 安装步骤

#### 1️⃣ 克隆项目
```bash
git clone https://github.com/ailpod/Movie-recommend-system.git
cd Movie-recommend-system
```

#### 2️⃣ 后端配置与启动

```bash
# 进入后端目录
cd Backend

# 安装 Python 依赖
pip install -r requirements.txt

# 初始化数据库（首次运行）
python DataBase/import_data.py

# 启动后端服务
python start.py
# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**后端运行在：**
- 🌐 API 服务：http://localhost:8000
- 📖 API 文档：http://localhost:8000/docs
- 📘 ReDoc 文档：http://localhost:8000/redoc

#### 3️⃣ 前端配置与启动

```bash
# 进入前端目录（新开一个终端）
cd Frontend

# 安装 npm 依赖
npm install

# 启动开发服务器
npm run dev
```

**前端运行在：**
- 🎨 前端应用：http://localhost:5173

#### 4️⃣ 首次使用

1. 访问 http://localhost:5173
2. 点击"注册"创建新账户
3. 登录后即可开始探索电影推荐功能

### 🔧 环境配置（可选）

创建 `Backend/.env` 文件配置环境变量：

```env
# 数据库配置
DATABASE_URL=sqlite:///./Recommend.db

# JWT 密钥配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API 配置
API_V1_STR=/api/v1
PROJECT_NAME=Movie Recommendation System

# CORS 配置
BACKEND_CORS_ORIGINS=["http://localhost:5173"]
```

## 🎯 核心功能详解

### 🤖 智能推荐算法
采用混合推荐策略，结合多种推荐技术：

- **协同过滤推荐**
  - 基于用户偏好权重（60%）的个性化推荐
  - 基于收藏历史（30%）的协同推荐
  - 基于浏览历史（10%）的行为推荐
  
- **内容推荐**
  - 使用余弦相似度矩阵计算电影相似性
  - 基于电影类型、导演、演员等特征的内容匹配
  - 支持动态类型偏好自动学习

- **推荐优化**
  - 去重过滤已收藏/已浏览电影
  - 多样性保证，避免推荐结果单一
  - 实时更新用户画像
�️ 技术栈

### 后端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | 0.104.1 | 现代高性能 Web 框架 |
| SQLAlchemy | 2.0.23 | ORM 数据库操作 |
| Pydantic | 2.5.1 | 数据验证和设置管理 |
| Python-JOSE | 3.3.0 | JWT Token 认证 |
| Passlib | 1.7.4 | 密码加密 |
| Scikit-learn | 1.3.2 | 机器学习和推荐算法 |
| Pandas | 2.1.4 | 数据处理和分析 |
| NumPy | 1.26.3 | 科学计算 |
| Uvicorn | 0.24.0 | ASGI 服务器 |
| Alembic | 1.13.1 | 数据库迁移工具 |

### 前端技术
| 技术� 项目截图

> 待添加：首页、电影详情、推荐页面、个人中心等截图

## 🚢 部署说明

### Docker 部署（推荐）

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

### 生产环境部署

**后端部署：**
```bash
# 使用 Gunicorn + Uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

**前端部署：**
```bash
# 构建生产版本
cd Frontend
npm run build

# 部署 dist 目录到 Nginx/Apache
```

## 📊 API 文档

启动后端服务后，访问以下地址查看自动生成的 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

主要 API 端点：
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/movies` - 获取电影列表
- `GET /api/movies/{id}` - 获取电影详情
- `POST /api/movies/{id}/favorite` - 收藏电影
- `GET /api/recommendations` - 获取个性化推荐

## 🐛 常见问题

<details>
<summary><b>Q: 后端启动失败，提示数据库错误？</b></summary>

**A:** 确保 `Backend/Recommend.db` 数据库文件存在，如不存在运行：
```bash
cd Backend
python -c "from app.core.database import engine, Base; Base.metadata.create_all(bind=engine)"
```
</details>

<details>
<summary><b>Q: 前端请求后端失败，CORS 错误？</b></summary>

**A:** 检查 `Backend/app/core/config.py` 中的 CORS 配置，确保包含前端地址：
```python
BACKEND_CORS_ORIGINS = ["http://localhost:5173"]
```
</details>

<details>
<summary><b>Q: 推荐结果为空？</b></summary>

**A:** 需要先导入电影数据和生成相似度矩阵：
```bash
cd Backend
python DataBase/import_data.py
python algorithm/Similarity_matrix.py
```
</details>

<details>
<summary><b>Q: npm install 很慢或失败？</b></summary>

**A:** 使用国内镜像源：
```bash
npm config set registry https://registry.npmmirror.com
npm install
```
</details>

## 🗺️ 开发路线图

- [x] 基础用户认证系统
- [x] 电影浏览和搜索
- [x] 收藏和历史功能
- [x] 协同过滤推荐算法
- [ ] 社交功能（关注、评论）
- [ ] 电影评论系统
- [ ] 用户画像可视化
- [ ] 推荐算法优化（深度学习）
- [ ] 移动端 App
- [ ] 实时推荐

## 🤝 贡献指南

欢迎各种形式的贡献！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

## 👨‍💻 作者

- GitHub: [@ailpod](https://github.com/ailpod)

## 🙏 致谢

- [TMDB](https://www.themoviedb.org/) - 电影数据来源
- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [Vue.js](https://vuejs.org/) - 前端框架
- 所有贡献者和支持者

---

⭐ 如果这个项目对你有帮助，请给一个 Star具 |
| Axios | 1.6.7 | HTTP 请求库 |
| TailwindCSS | 3.4.1 | 实用优先的 CSS 框架 |
| VueUse | 10.7.2 | Vue 组合式 API 工具集 |
| DayJS | 1.11.10 | 轻量级日期处理 |
| Vue I18n | 9.9.1 | 国际化支持 |

### 数据库
- **SQLite** - 开发环境默认数据库，轻量级、零配置
- 支持迁移至 PostgreSQL/MySQL 生产环境B 电影数据库
  - 电影海报、简介、评分等详细信息
  - 分类标签系统（动作、喜剧、科幻等）
  
- **浏览功能**
  - 多维度分类筛选
  - 关键词搜索
  - 评分排序
  - 上映年份筛选
  
- **交互功能**
  - 电影详情页
  - 相似电影推荐
  - 快速收藏
  - 评分功能

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
