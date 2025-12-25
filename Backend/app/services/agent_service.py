"""
AI Agent 核心服务
基于 DeepSeek API 实现智能电影助手
支持 Tool Calling 和流式输出
"""
from typing import List, Dict, Any, Optional, AsyncGenerator
from openai import OpenAI
import json
from sqlalchemy.orm import Session

from ..core.config import get_settings
from . import agent_tools


class AgentService:
    """AI Agent 服务类"""
    
    def __init__(self):
        """初始化 DeepSeek 客户端"""
        settings = get_settings()
        self.client = OpenAI(
            api_key=settings.ai.deepseek_api_key,
            base_url=settings.ai.deepseek_base_url
        )
        self.model = settings.ai.deepseek_model
        self.max_tokens = settings.ai.max_tokens
        self.temperature = settings.ai.temperature
        self.stream_enabled = settings.ai.stream
        
        # 定义可用工具
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_movies",
                    "description": "根据关键词、类型或年份搜索电影库。用于回答'有哪些科幻电影'、'诺兰的作品'、'2020年的动作片'等问题",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索关键词，如：诺兰、盗梦空间、科幻、太空"
                            },
                            "genre": {
                                "type": "string",
                                "description": "电影类型，如：Science Fiction, Action, Drama, Comedy"
                            },
                            "year_start": {
                                "type": "integer",
                                "description": "起始年份，如：2020"
                            },
                            "year_end": {
                                "type": "integer",
                                "description": "结束年份，如：2024"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "返回数量限制，默认10"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_user_favorites",
                    "description": "获取用户收藏的电影列表以分析口味偏好。用于了解用户喜欢什么类型的电影",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer",
                                "description": "用户ID"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "返回数量限制，默认20"
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_user_ratings",
                    "description": "获取用户的评分历史记录。用于了解用户对哪些电影评分高，哪些评分低",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer",
                                "description": "用户ID"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "返回数量限制，默认20"
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_recommendations_for_user",
                    "description": "基于用户的观看历史和评分生成个性化推荐。用于回答'给我推荐一些电影'类问题",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer",
                                "description": "用户ID"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "推荐数量，默认10"
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_similar_movies",
                    "description": "获取与指定电影相似的其他电影。用于回答'有什么类似的电影'类问题",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "movie_id": {
                                "type": "integer",
                                "description": "电影ID"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "返回数量，默认10"
                            }
                        },
                        "required": ["movie_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_movie_details",
                    "description": "获取电影的详细信息，包括简介、评分、类型等",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "movie_id": {
                                "type": "integer",
                                "description": "电影ID"
                            }
                        },
                        "required": ["movie_id"]
                    }
                }
            }
        ]
    
    def _build_system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        构建系统提示词，注入上下文
        
        Args:
            context: 页面上下文信息
        
        Returns:
            系统提示词
        """
        base_prompt = """你是一个专业的电影推荐助手，名字叫"小影"。你的特点：
1. 你可以访问完整的电影数据库，提供精准的电影信息和推荐
2. 你能分析用户的观影喜好，提供个性化建议
3. 你的回答应该专业、友好且带有一点幽默感
4. 当推荐电影时，要说明推荐理由
5. 如果用户问的问题不在你的能力范围内，诚实告知并建议其他方式

重要规则：
- 所有电影信息必须通过工具函数从数据库获取，不要编造电影名称或信息
- 如果搜索结果为空，要明确告知用户
- 推荐电影时要考虑用户的历史偏好"""
        
        # 注入页面上下文
        if context:
            context_info = "\n\n当前上下文：\n"
            
            if context.get("page") == "movie_detail":
                movie = context.get("current_movie", {})
                context_info += f"- 用户正在查看电影：《{movie.get('title')}》\n"
                context_info += f"- 电影类型：{movie.get('genres')}\n"
                context_info += "- 当用户问'这个'、'它'等指代词时，指的是这部电影\n"
            
            elif context.get("page") == "browse":
                filters = context.get("filters", {})
                if filters.get("genre"):
                    context_info += f"- 用户正在浏览：{filters['genre']} 类型的电影\n"
                if filters.get("year_range"):
                    context_info += f"- 年份范围：{filters['year_range']}\n"
            
            elif context.get("page") == "recommend":
                context_info += "- 用户在推荐页面，可能想要个性化推荐\n"
            
            base_prompt += context_info
        
        return base_prompt
    
    async def _execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        db: Session
    ) -> Any:
        """
        执行工具函数
        
        Args:
            tool_name: 工具函数名称
            arguments: 函数参数
            db: 数据库会话
        
        Returns:
            工具执行结果
        """
        try:
            if tool_name == "search_movies":
                return await agent_tools.search_movies(db, **arguments)
            
            elif tool_name == "get_user_favorites":
                return await agent_tools.get_user_favorites(db, **arguments)
            
            elif tool_name == "get_user_ratings":
                return await agent_tools.get_user_ratings(db, **arguments)
            
            elif tool_name == "get_recommendations_for_user":
                return await agent_tools.get_recommendations_for_user(db, **arguments)
            
            elif tool_name == "get_similar_movies":
                return await agent_tools.get_similar_movies(db, **arguments)
            
            elif tool_name == "get_movie_details":
                return await agent_tools.get_movie_details(db, **arguments)
            
            else:
                return {"error": f"未知的工具函数: {tool_name}"}
        
        except Exception as e:
            return {"error": f"执行工具出错: {str(e)}"}
    
    async def chat(
        self,
        user_message: str,
        user_id: int,
        db: Session,
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        非流式聊天（适合 MVP 版本）
        
        Args:
            user_message: 用户消息
            user_id: 用户ID
            db: 数据库会话
            context: 页面上下文
            conversation_history: 对话历史
        
        Returns:
            AI 回复内容
        """
        # 构建消息列表
        messages = [
            {"role": "system", "content": self._build_system_prompt(context)}
        ]
        
        # 添加对话历史
        if conversation_history:
            messages.extend(conversation_history)
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        # 第一次请求 DeepSeek
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto",
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        # 如果 AI 决定调用工具
        if tool_calls:
            # 将 AI 的响应添加到消息历史
            messages.append(response_message)
            
            # 执行所有工具调用
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # 自动注入 user_id（如果工具需要）
                if "user_id" in function_args and function_args["user_id"] == 0:
                    function_args["user_id"] = user_id
                
                # 执行工具
                tool_result = await self._execute_tool(
                    function_name,
                    function_args,
                    db
                )
                
                # 添加工具结果到消息
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(tool_result, ensure_ascii=False)
                })
            
            # 第二次请求，让 AI 结合工具结果生成最终回答
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return final_response.choices[0].message.content
        
        # 如果没有工具调用，直接返回 AI 回复
        return response_message.content
    
    async def chat_stream(
        self,
        user_message: str,
        user_id: int,
        db: Session,
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天（Phase 2 优化版本）
        
        Args:
            user_message: 用户消息
            user_id: 用户ID
            db: 数据库会话
            context: 页面上下文
            conversation_history: 对话历史
        
        Yields:
            流式输出的文本片段
        """
        # 构建消息列表
        messages = [
            {"role": "system", "content": self._build_system_prompt(context)}
        ]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": user_message})
        
        # 第一次请求（检测是否需要工具调用）
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto",
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=False  # 工具调用阶段不使用流式
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        # 如果需要工具调用
        if tool_calls:
            messages.append(response_message)
            
            # 执行工具
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if "user_id" in function_args and function_args["user_id"] == 0:
                    function_args["user_id"] = user_id
                
                tool_result = await self._execute_tool(
                    function_name,
                    function_args,
                    db
                )
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(tool_result, ensure_ascii=False)
                })
            
            # 第二次请求，使用流式输出
            stream_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            
            for chunk in stream_response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        else:
            # 没有工具调用，直接流式输出
            stream_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            
            for chunk in stream_response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content


# 全局单例
_agent_service: Optional[AgentService] = None


def get_agent_service() -> AgentService:
    """获取 Agent 服务单例"""
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service
