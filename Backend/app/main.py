
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import time
import uuid
import json
from contextlib import asynccontextmanager

from .core.config import get_settings
from .core.database import engine, Base
from .routers import auth_router, users_router, movies_router, api_router
from .routers.user_actions import router as user_actions_router


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    # 安全的数据库初始化
    init_database()
    yield
    # 关闭时执行


def init_database():
    """数据库初始化检查"""
    try:
        from sqlalchemy import inspect
        
        # 检查数据库是否存在表
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if not existing_tables:
            print("数据库为空")
            print("请使用DataBase下的脚本来做数据库迁移:")
        else:
            print(f"数据库已存在 {len(existing_tables)} 个表: {', '.join(existing_tables)}")
            print("数据库连接正常")
                
    except Exception as e:
        print(f"数据库连接检查失败: {e}")
 

def create_application() -> FastAPI:
    """创建 FastAPI 应用实例"""
    
    app = FastAPI(
        title=settings.app_name,
        description="基于 FastAPI 的现代化电影推荐系统",
        version=settings.app_version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan
    )
    
    # 添加中间件
    add_middleware(app)
    
    # 添加异常处理器
    add_exception_handlers(app)
    
    # 注册路由
    app.include_router(auth_router, prefix=settings.api_v1_str)
    app.include_router(users_router, prefix=settings.api_v1_str)
    app.include_router(movies_router, prefix=settings.api_v1_str)
    app.include_router(api_router, prefix=settings.api_v1_str)
    app.include_router(user_actions_router, prefix=settings.api_v1_str)
    
    # 挂载静态文件目录
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    return app


class UTF8JSONResponse(JSONResponse):
    """确保UTF-8编码的JSON响应"""
    media_type = "application/json; charset=utf-8"
    
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


def add_middleware(app: FastAPI) -> None:
    """添加中间件"""
    
    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allowed_origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )
    
    # 请求追踪中间件
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        response = await call_next(request)
        process_time = time.time() - start_time
        
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        return response


def add_exception_handlers(app: FastAPI) -> None:
    """添加异常处理器"""
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "请求参数验证失败",
                "errors": exc.errors(),
                "body": exc.body
            }
        )


# 创建应用实例
app = create_application()


@app.get("/", tags=["基础"])
async def root():
    """根路径"""
    return {
        "message": f"欢迎使用{settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health", tags=["基础"])
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.app_version
    }
