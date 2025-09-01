# 🎬 电影推荐系统

一个基于Vue.js + FastAPI的现代化电影推荐平台，提供个性化的电影推荐、用户收藏、浏览历史等功能。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.0-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-red.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)

## ✨ 特性

- 🔐 **用户认证系统** - JWT Token认证，安全可靠
- 🎭 **电影浏览** - 丰富的电影信息展示，支持分类浏览
- ❤️ **收藏功能** - 个性化收藏列表，轮播展示
- 📈 **浏览历史** - 智能去重，时间轴展示
- ⭐ **评分系统** - 用户评分，平均分计算
- 🎯 **推荐算法** - （待实现）基于用户行为的个性化推荐
- 📱 **响应式设计** - 完美适配桌面端、平板、手机
- 🌟 **现代化UI** - 炫酷的科技感界面，流畅的交互体验

## 🚀 快速开始

### 环境要求

- **前端**: Node.js 16+ 
- **后端**: Python 3.8+
- **数据库**: SQLite (开发) / PostgreSQL (生产)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/ailpod/Movie-recommend-system.git
   cd Movie-recommend-system
   ```

2. **后端设置**
   ```bash
   cd Backend
   
   # 创建虚拟环境
   python -m venv venv
   
   # 激活虚拟环境
   # Windows
   venv\\Scripts\\activate
   # macOS/Linux
   source venv/bin/activate
   
   # 安装依赖
   pip install -r ../requirements.txt
   
   # 导入数据库数据
   python import_data.py
   pip install -r requirements.txt
   
   # 启动后端服务
   python start.py
   ```
   
   后端服务将在 `http://localhost:8000` 启动

3. **前端设置**
   ```bash
   cd Frontend
   
   # 安装依赖
   npm install
   
   # 启动开发服务器
   npm run dev
   ```
   
   前端服务将在 `http://localhost:5173` 启动

4. **访问应用**
   
   打开浏览器访问 `http://localhost:5173` 即可体验系统

## 📁 项目结构

```
Movie-recommend-system/
├── Backend/                 # 后端代码
│   ├── app/                # FastAPI应用
│   │   ├── core/          # 核心配置
│   │   ├── crud/          # 数据库操作
│   │   ├── models/        # 数据模型
│   │   ├── routers/       # API路由
│   │   ├── schemas/       # Pydantic模式
│   │   └── services/      # 业务逻辑
│   ├── static/            # 静态文件
│   ├── movie_system.db    # SQLite数据库
│   ├── requirements.txt   # Python依赖
│   └── start.py          # 启动文件
├── Frontend/               # 前端代码
│   ├── src/
│   │   ├── api/          # API接口
│   │   ├── components/   # Vue组件
│   │   ├── router/       # 路由配置
│   │   ├── services/     # 服务层
│   │   ├── stores/       # 状态管理
│   │   ├── types/        # TypeScript类型
│   │   └── views/        # 页面组件
│   ├── package.json      # 依赖配置
│   └── vite.config.js    # Vite配置
├── docs/                  # 项目文档
│   ├── requirements.md   # 需求文档
│   └── README.md         # 说明文档
└── README.md             # 项目说明
```

## 🛠️ 技术栈

### 前端

- **Vue.js 3** - 渐进式JavaScript框架
- **Vite** - 下一代前端构建工具
- **Vue Router** - 官方路由管理器
- **Pinia** - Vue状态管理库
- **Axios** - HTTP客户端
- **Font Awesome** - 图标库

### 后端

- **FastAPI** - 现代化Python Web框架
- **SQLAlchemy** - Python SQL工具包和ORM
- **SQLite** - 轻量级数据库
- **JWT** - JSON Web Token认证
- **Uvicorn** - ASGI服务器

## 📖 API文档

启动后端服务后，可访问以下地址查看API文档：

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 主要API端点

```
# 用户认证
POST /api/v1/auth/register     # 用户注册
POST /api/v1/auth/login        # 用户登录

# 电影相关
GET  /api/v1/movies           # 获取电影列表
GET  /api/v1/movies/{id}      # 获取电影详情
GET  /api/v1/movies/popular   # 热门电影
GET  /api/v1/movies/search    # 搜索电影

# 用户操作
POST /api/v1/users/me/favorites/{movie_id}  # 添加收藏
GET  /api/v1/users/me/favorites             # 获取收藏列表
POST /api/v1/users/me/history/{movie_id}    # 记录浏览历史
GET  /api/v1/users/me/history               # 获取浏览历史
```

## 🎨 功能特色

### 用户体验

- **固定导航栏** - 滚动时始终可见，提升导航体验
- **轮播展示** - 收藏和历史页面支持轮播浏览，每页4部电影
- **响应式布局** - 完美适配各种屏幕尺寸
- **Toast通知** - 操作反馈及时清晰
- **加载动画** - 优雅的加载状态提示

### 数据处理

- **时区处理** - 正确显示北京时间
- **去重逻辑** - 浏览历史智能去重，保留最新记录
- **评分格式** - 统一保留一位小数显示
- **标题溢出** - 长标题自动省略，保持布局整洁

### 视觉设计

- **科技感UI** - 深色主题，炫酷渐变背景
- **流畅动画** - 悬停效果、转场动画
- **统一配色** - 紫色系主色调，视觉统一
- **图标系统** - Font Awesome图标，含义清晰

## 🔧 开发指南

### 前端开发

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

### 后端开发

```bash
# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# venv\\Scripts\\activate  # Windows

# 安装开发依赖
pip install -r requirements.txt

# 运行服务器
python start.py

# 运行测试
pytest
```

### 数据库操作

```bash
# 生成迁移文件
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 🚀 部署

### Docker部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 手动部署

1. **后端部署**
   ```bash
   # 安装依赖
   pip install -r requirements.txt
   
   # 配置环境变量
   export DATABASE_URL="postgresql://..."
   export SECRET_KEY="your-secret-key"
   
   # 启动服务
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **前端部署**
   ```bash
   # 构建项目
   npm run build
   
   # 部署到Nginx
   cp -r dist/* /var/www/html/
   ```

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 代码规范

- **前端**: 使用ESLint + Prettier
- **后端**: 遵循PEP 8规范
- **提交信息**: 使用Conventional Commits规范

## 📝 更新日志

### v1.0.0 (2025-01-01)

#### 新增功能
- ✨ 用户注册登录系统
- 🎭 电影浏览和详情展示
- ❤️ 收藏功能
- 📈 浏览历史记录
- ⭐ 用户评分系统
- 📱 响应式设计

#### 技术优化
- 🔧 JWT Token认证
- 🎨 现代化UI设计
- ⚡ 性能优化
- 🛡️ 安全性增强

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👥 团队

- **开发者**: [Ailpod]
- **设计师**: [Ailpod]


## 🙏 致谢

感谢以下开源项目的支持：

- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化Python Web框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL工具包
- [Vite](https://vitejs.dev/) - 下一代前端构建工具

## 📞 联系我们

- 邮箱: 396914396@qq.com
- 项目地址: https://github.com/ailpod/Movie-recommend-system
- 问题反馈: https://github.com/ailpod/Movie-recommend-system/issues

---

⭐ 如果这个项目对你有帮助，请给个Star支持一下！
