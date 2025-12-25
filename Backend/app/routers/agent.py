"""
AI Agent 路由控制器
提供智能对话和推荐接口
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import json

from ..core.database import get_db
from ..core.dependencies import get_current_active_user
from ..models.models import User
from ..services.agent_service import get_agent_service


router = APIRouter(prefix="/agent", tags=["AI助手"])


# ==================== 请求/响应模型 ====================

class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息", min_length=1, max_length=1000)
    context: Optional[Dict[str, Any]] = Field(None, description="页面上下文信息")
    conversation_history: Optional[List[Dict[str, str]]] = Field(None, description="对话历史")
    stream: bool = Field(False, description="是否使用流式输出")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "推荐一些科幻电影",
                "context": {
                    "page": "browse",
                    "filters": {"genre": "Science Fiction"}
                },
                "stream": False
            }
        }


class ChatResponse(BaseModel):
    """聊天响应"""
    content: str = Field(..., description="AI回复内容")
    success: bool = Field(True, description="是否成功")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "根据您的喜好，我为您推荐以下科幻电影...",
                "success": True
            }
        }


class ContextRequest(BaseModel):
    """上下文请求"""
    page: str = Field(..., description="当前页面")
    current_movie: Optional[Dict[str, Any]] = Field(None, description="当前电影信息")
    filters: Optional[Dict[str, Any]] = Field(None, description="当前筛选条件")


# ==================== 路由端点 ====================

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    与 AI 助手对话（非流式）
    
    - **message**: 用户消息
    - **context**: 页面上下文（可选）
    - **conversation_history**: 对话历史（可选）
    - **stream**: 是否流式输出（此接口固定为False）
    
    支持的上下文类型：
    - movie_detail: 电影详情页
    - browse: 浏览页
    - recommend: 推荐页
    """
    try:
        # 获取 Agent 服务
        agent_service = get_agent_service()
        
        # 调用聊天接口
        response_content = await agent_service.chat(
            user_message=request.message,
            user_id=current_user.id,
            db=db,
            context=request.context,
            conversation_history=request.conversation_history
        )
        
        return ChatResponse(
            content=response_content,
            success=True
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI助手出错: {str(e)}"
        )


@router.post("/chat/stream")
async def chat_with_agent_stream(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    与 AI 助手对话（流式输出）
    
    返回 Server-Sent Events (SSE) 流
    
    - **message**: 用户消息
    - **context**: 页面上下文（可选）
    - **conversation_history**: 对话历史（可选）
    """
    async def generate():
        try:
            agent_service = get_agent_service()
            
            # 使用流式聊天
            async for chunk in agent_service.chat_stream(
                user_message=request.message,
                user_id=current_user.id,
                db=db,
                context=request.context,
                conversation_history=request.conversation_history
            ):
                # 发送 SSE 格式数据
                yield f"data: {json.dumps({'content': chunk, 'done': False}, ensure_ascii=False)}\n\n"
            
            # 发送结束标记
            yield f"data: {json.dumps({'content': '', 'done': True}, ensure_ascii=False)}\n\n"
        
        except Exception as e:
            # 发送错误信息
            yield f"data: {json.dumps({'error': str(e), 'done': True}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/context")
async def update_context(
    request: ContextRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    更新页面上下文
    
    前端可以调用此接口告知后端当前页面状态，
    以便 AI 助手提供更精准的建议
    
    - **page**: 当前页面类型
    - **current_movie**: 当前正在查看的电影（如果在详情页）
    - **filters**: 当前的筛选条件（如果在浏览页）
    """
    return {
        "success": True,
        "message": "上下文已更新",
        "context": request.dict()
    }


@router.get("/health")
async def agent_health_check():
    """
    健康检查
    
    检查 AI Agent 服务是否正常运行
    """
    try:
        agent_service = get_agent_service()
        return {
            "status": "healthy",
            "model": agent_service.model,
            "stream_enabled": agent_service.stream_enabled
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI助手服务不可用: {str(e)}"
        )


# ==================== 快捷接口 ====================

@router.get("/quick/recommend")
async def quick_recommend(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    快捷推荐接口
    
    基于用户历史快速生成推荐，无需对话
    """
    try:
        from ..services.agent_tools import get_recommendations_for_user
        
        recommendations = await get_recommendations_for_user(
            db=db,
            user_id=current_user.id,
            limit=limit
        )
        
        return {
            "success": True,
            "recommendations": recommendations
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成推荐失败: {str(e)}"
        )


@router.get("/quick/similar/{movie_id}")
async def quick_similar(
    movie_id: int,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    快捷相似电影接口
    
    获取与指定电影相似的其他电影
    """
    try:
        from ..services.agent_tools import get_similar_movies
        
        similar_movies = await get_similar_movies(
            db=db,
            movie_id=movie_id,
            limit=limit
        )
        
        return {
            "success": True,
            "similar_movies": similar_movies
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取相似电影失败: {str(e)}"
        )
