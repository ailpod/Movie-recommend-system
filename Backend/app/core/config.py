"""
优化后的应用配置模块
支持环境变量、类型验证和配置分组
"""
from pydantic_settings import BaseSettings
from pydantic import validator
from typing import List, Optional
import os
from functools import lru_cache


class DatabaseSettings(BaseSettings):
    """数据库配置"""
    url: str = "sqlite:///./Recommend.db"
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    recreate_on_startup: bool = False  # 是否在启动时重新创建表
    
    class Config:
        env_prefix = "DATABASE_"


class RedisSettings(BaseSettings):
    """Redis 配置"""
    url: str = "redis://localhost:6379/0"
    max_connections: int = 20
    
    class Config:
        env_prefix = "REDIS_"


class SecuritySettings(BaseSettings):
    """安全配置"""
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    bcrypt_rounds: int = 12
    
    class Config:
        env_prefix = "SECURITY_"


class CORSSettings(BaseSettings):
    """CORS 配置"""
    allowed_origins: List[str] = [
        "http://localhost:8080",
        "http://localhost:8081",  # 添加 8081 端口支持
        "http://localhost:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8081"   # 添加 127.0.0.1:8081 支持
    ]
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]
    
    @validator('allowed_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_prefix = "CORS_"


class EmailSettings(BaseSettings):
    """邮件配置"""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: Optional[str] = None
    use_tls: bool = True
    
    class Config:
        env_prefix = "EMAIL_"


class LoggingSettings(BaseSettings):
    """日志配置"""
    level: str = "INFO"
    file: str = "logs/app.log"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    
    class Config:
        env_prefix = "LOG_"


class RecommendationSettings(BaseSettings):
    """推荐算法配置"""
    batch_size: int = 100
    max_recommendations: int = 20
    min_rating_count: int = 5
    similarity_threshold: float = 0.1
    
    class Config:
        env_prefix = "RECOMMENDATION_"


class Settings(BaseSettings):
    """主配置类"""
    # 应用基本信息
    app_name: str = "电影推荐系统"
    app_version: str = "1.0.0"
    debug: bool = True  # 启用调试模式以显示文档
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # API 配置
    api_v1_str: str = "/api/v1"
    
    # 文件上传配置
    max_file_size: int = 10485760  # 10MB
    upload_path: str = "uploads/"
    
    # 分组配置
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    security: SecuritySettings = SecuritySettings()
    cors: CORSSettings = CORSSettings()
    email: EmailSettings = EmailSettings()
    logging: LoggingSettings = LoggingSettings()
    recommendation: RecommendationSettings = RecommendationSettings()
    
    @validator('upload_path')
    def create_upload_directory(cls, v):
        os.makedirs(v, exist_ok=True)
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取应用配置（缓存）"""
    return Settings()
