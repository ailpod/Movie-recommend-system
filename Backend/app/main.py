
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import time
import uuid
import json
import os
import pickle
import pandas as pd
from contextlib import asynccontextmanager

from .core.config import get_settings
from .core.database import engine, Base
from .routers import auth_router, users_router, movies_router, api_router
from .routers.user_actions import router as user_actions_router
from .routers.ratings import router as ratings_router


settings = get_settings()

# --- 用于存放加载好的模型 ---
recommendation_models = {}
models = recommendation_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("应用启动中...")
    
    # 安全的数据库初始化
    init_database()
    
    # 加载推荐模型
    load_recommendation_models()
    
    yield
    
    # 关闭时执行
    recommendation_models.clear()
    print("应用关闭，模型卸载")


def load_recommendation_models():
    """加载推荐模型"""
    print("正在加载推荐模型...")
    
    # 构建模型文件的绝对路径 (相对于 main.py)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    similarity_model_path = os.path.join(base_dir, "..", "algorithm", "movie_similarity.pkl")
    indices_path = os.path.join(base_dir, "..", "algorithm", "movie_indices.pkl")
    
    try:
        # 检查文件是否存在
        if not os.path.exists(similarity_model_path):
            print(f"相似度模型文件未找到: {similarity_model_path}")
            return
            
        if not os.path.exists(indices_path):
            print(f"索引文件未找到: {indices_path}")
            return
        
        # 加载相似度矩阵
        with open(similarity_model_path, 'rb') as f:
            recommendation_models['cosine_sim'] = pickle.load(f)
        print(f"✅ 相似度矩阵加载成功 (shape: {recommendation_models['cosine_sim'].shape})")
        
        # 加载电影索引
        with open(indices_path, 'rb') as f:
            recommendation_models['indices'] = pickle.load(f)
        print(f"✅ 电影索引加载成功 (索引数量: {len(recommendation_models['indices'])})")
            
        print("推荐模型加载成功！")
        
        # 设置推荐工具的模型引用
        from .services.recommendation_utils import set_recommendation_models
        set_recommendation_models(recommendation_models)
        
        # --- 👇 在加载pkl文件后，新增这部分代码 👇 ---
        print("正在加载全量电影数据用于类型匹配...")
        # 我们需要加载那个原始的JSON数据文件
        json_file_path = os.path.join(base_dir, "..", "static", "tmdb_1000_movies.json")
        try:
            # 将JSON加载为Pandas DataFrame并存入models字典
            df_raw = pd.read_json(json_file_path)
            # 只保留模型中存在的电影数据，确保一致性
            movie_titles_in_model = recommendation_models['indices'].index
            recommendation_models['all_movies_df'] = df_raw[df_raw['title'].isin(movie_titles_in_model)].copy()
            print("✅ 全量电影数据加载成功！")
        except Exception as e:
            print(f"🚨 错误：加载全量电影数据时发生错误: {e}")
        
    except FileNotFoundError as e:
        print(f"警告：推荐模型文件未找到 - {e}")
        print("推荐功能将不可用，请确保模型文件存在于 Backend/algorithm/ 目录下")
    except Exception as e:
        print(f"❌ 加载模型时发生错误: {e}")
        print("推荐功能将不可用")


def get_recommendation_models():
    """获取加载的推荐模型"""
    return recommendation_models


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
            
            # 检查是否缺少 ratings 表
            if 'ratings' not in existing_tables:
                print("检测到缺少 ratings 表，正在创建...")
                Base.metadata.create_all(bind=engine, tables=[Base.metadata.tables.get('ratings')])
                print("✅ ratings 表创建成功")
            
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
    app.include_router(ratings_router, prefix=settings.api_v1_str)
    
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


@app.get("/models/info", tags=["推荐"])
async def get_model_info():
    """获取推荐模型信息"""
    from .services.recommendation_utils import get_model_info
    return get_model_info()


@app.get("/models/recommend/{movie_title}", tags=["推荐"])
async def get_recommendations(movie_title: str, num_recommendations: int = 10):
    """基于电影标题获取推荐"""
    from .services.recommendation_utils import get_movie_recommendations
    
    recommendations = get_movie_recommendations(movie_title, num_recommendations)
    
    return {
        "movie_title": movie_title,
        "num_recommendations": len(recommendations),
        "recommendations": [
            {
                "title": title,
                "similarity_score": score
            }
            for title, score in recommendations
        ]
    }
