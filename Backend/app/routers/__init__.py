# 路由模块包
from .api import router as api_router
from .auth import router as auth_router
from .movies import router as movies_router
from .users import router as users_router

__all__ = ["api_router", "auth_router", "movies_router", "users_router"]
