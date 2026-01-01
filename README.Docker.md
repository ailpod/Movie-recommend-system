# Docker 部署指南

本文档介绍如何使用 Docker 一键部署电影推荐系统。

## 📋 前置要求

- Docker 20.10+
- Docker Compose 2.0+

检查安装：
```bash
docker --version
docker-compose --version
```

## 🚀 快速开始

### 1. 克隆项目（如果还没有）

```bash
git clone <repository-url>
cd Movie-recommend-system
```

### 2. 配置环境变量（可选）

复制环境变量示例文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，至少修改以下内容：
- `SECRET_KEY`: 设置一个强随机字符串
- `OPENAI_API_KEY`: 如果需要 AI 功能，填入你的 OpenAI API 密钥

### 3. 一键启动所有服务

```bash
docker-compose up -d
```

这将启动以下服务：
- **PostgreSQL** (端口 5432): 数据库
- **Redis** (端口 6379): 缓存
- **Backend** (端口 8000): FastAPI 后端服务
- **Frontend** (端口 80): Vue.js 前端
- **Celery Worker**: 异步任务处理

### 4. 访问应用

- 前端界面: http://localhost
- 后端 API 文档: http://localhost:8000/docs
- 后端健康检查: http://localhost:8000/api/health

## 📦 服务说明

### 架构组件

```
┌─────────────┐
│   Frontend  │ :80
│  (Nginx)    │
└─────┬───────┘
      │
      ▼
┌─────────────┐     ┌──────────┐
│   Backend   │────▶│PostgreSQL│ :5432
│  (FastAPI)  │ :8000│          │
└─────┬───────┘     └──────────┘
      │
      ▼
┌─────────────┐     ┌──────────┐
│   Celery    │────▶│  Redis   │ :6379
│   Worker    │     │          │
└─────────────┘     └──────────┘
```

### 数据持久化

使用 Docker volumes 持久化数据：
- `postgres_data`: PostgreSQL 数据库数据
- `redis_data`: Redis 缓存数据
- `./Backend/uploads`: 上传的文件
- `./Backend/static`: 静态文件

## 🛠️ 常用命令

### 查看服务状态
```bash
docker-compose ps
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend

# 实时查看日志
docker-compose logs -f backend
```

### 停止服务
```bash
docker-compose stop
```

### 停止并删除容器
```bash
docker-compose down
```

### 停止并删除容器及数据卷
```bash
docker-compose down -v
```

### 重启服务
```bash
docker-compose restart
```

### 重新构建并启动
```bash
docker-compose up -d --build
```

### 进入容器
```bash
# 进入后端容器
docker-compose exec backend bash

# 进入数据库容器
docker-compose exec postgres psql -U movieuser -d moviedb
```

### 数据库迁移
```bash
# 运行数据库迁移
docker-compose exec backend alembic upgrade head

# 创建新的迁移
docker-compose exec backend alembic revision --autogenerate -m "description"
```

## 🔧 配置说明

### 环境变量

主要环境变量（在 `docker-compose.yml` 或 `.env` 中配置）：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | JWT 密钥 | your-super-secret-key-change-in-production |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - |
| `DATABASE_URL` | 数据库连接 | postgresql://movieuser:moviepass@postgres:5432/moviedb |
| `REDIS_URL` | Redis 连接 | redis://redis:6379/0 |
| `APP_DEBUG` | 调试模式 | false |

### 端口映射

修改端口映射（在 `docker-compose.yml` 中）：

```yaml
services:
  frontend:
    ports:
      - "8080:80"  # 将前端映射到 8080 端口
  backend:
    ports:
      - "8001:8000"  # 将后端映射到 8001 端口
```

### Nginx 配置

前端 Nginx 配置文件位于 `Frontend/nginx.conf`，可以修改：
- 反向代理规则
- 缓存策略
- Gzip 压缩
- 安全头

## 🐛 故障排查

### 1. 容器启动失败

查看日志定位问题：
```bash
docker-compose logs backend
```

### 2. 数据库连接失败

确保 PostgreSQL 容器健康：
```bash
docker-compose ps postgres
docker-compose logs postgres
```

### 3. 前端无法连接后端

检查网络配置：
```bash
docker network ls
docker network inspect movie-recommend-system_movie-network
```

### 4. 端口被占用

修改 `docker-compose.yml` 中的端口映射，使用其他端口。

### 5. 磁盘空间不足

清理未使用的 Docker 资源：
```bash
docker system prune -a --volumes
```

## 🔄 更新应用

### 更新代码后重新部署

```bash
# 1. 停止服务
docker-compose down

# 2. 拉取最新代码
git pull

# 3. 重新构建并启动
docker-compose up -d --build
```

### 仅更新特定服务

```bash
# 只重新构建并重启后端
docker-compose up -d --build backend

# 只重新构建并重启前端
docker-compose up -d --build frontend
```

## 📊 监控和维护

### 资源使用情况
```bash
docker stats
```

### 容器健康检查
```bash
docker-compose ps
```

### 备份数据库
```bash
docker-compose exec postgres pg_dump -U movieuser moviedb > backup.sql
```

### 恢复数据库
```bash
docker-compose exec -T postgres psql -U movieuser moviedb < backup.sql
```

## 🚀 生产环境部署

在生产环境部署时，请注意：

1. **修改密钥**：在 `.env` 中设置强随机的 `SECRET_KEY`
2. **配置 HTTPS**：使用 Let's Encrypt 或其他证书
3. **设置防火墙**：只开放必要的端口（80, 443）
4. **配置备份**：定期备份数据库和上传文件
5. **监控日志**：使用日志聚合工具
6. **资源限制**：在 `docker-compose.yml` 中配置 CPU 和内存限制

### 添加资源限制示例

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## 📚 更多信息

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [FastAPI 部署指南](https://fastapi.tiangolo.com/deployment/)
- [Vue.js 生产环境部署](https://vuejs.org/guide/best-practices/production-deployment.html)

## 🆘 获取帮助

如果遇到问题：
1. 查看日志：`docker-compose logs`
2. 检查服务状态：`docker-compose ps`
3. 查阅故障排查章节
4. 提交 Issue 到项目仓库
