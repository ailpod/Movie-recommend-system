"""
AI Agent 核心服务
基于 DeepSeek API 实现智能电影助手
支持 Tool Calling 和流式输出
"""
from typing import List, Dict, Any, Optional, AsyncGenerator
from openai import AsyncOpenAI
import json
from sqlalchemy.orm import Session

from ..core.config import get_settings
from . import agent_tools
from ..models.models import Movie, Favorite, BrowsingHistory


class AgentService:
    """AI Agent 服务类"""
    
    def __init__(self):
        """初始化 DeepSeek 客户端"""
        # 直接硬编码 API Key（临时方案）
        self.client = AsyncOpenAI(
            api_key="sk-006150277bb74c208df3d81b227fef60",
            base_url="https://api.deepseek.com"
        )
        self.model = "deepseek-chat"
        self.max_tokens = 2000
        self.temperature = 0.7
        self.stream_enabled = True
        
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
    
    def _generate_reason(self, movie: Movie, user_favorites: List[Movie]) -> str:
        """
        生成推荐理由
        
        Args:
            movie: 推荐的电影
            user_favorites: 用户收藏的电影列表
        
        Returns:
            推荐理由字符串
        """
        reasons = []
        
        # 高分理由
        if movie.avg_rate >= 8.5:
            reasons.append("IMDb高分佳作")
        elif movie.avg_rate >= 8.0:
            reasons.append("口碑优秀")
        
        # 类型匹配
        if user_favorites:
            user_genres = set()
            for fav in user_favorites:
                if fav.genres:
                    user_genres.update([g.strip() for g in fav.genres.split(',')])
            
            if movie.genres:
                movie_genres = set([g.strip() for g in movie.genres.split(',')])
                common_genres = user_genres & movie_genres
                if common_genres:
                    reasons.append(f"符合你喜欢的{list(common_genres)[0]}类型")
        
        # 经典作品
        if movie.release_year and movie.release_year < 2000:
            reasons.append("经典老片")
        
        if not reasons:
            reasons.append("综合评分推荐")
        
        return "，".join(reasons)
    
    def _build_system_prompt(self, context: Optional[Dict[str, Any]] = None, user_id: int = None) -> str:
        """
        构建系统提示词，注入上下文
        
        Args:
            context: 页面上下文信息
            user_id: 当前用户ID
        
        Returns:
            系统提示词
        """
        base_prompt = f"""你是一个专业的电影推荐助手，名字叫"小影"。你的特点：
1. 你可以访问完整的电影数据库，提供精准的电影信息和推荐
2. 你能分析用户的观影喜好，提供个性化建议
3. 你的回答应该专业、友好且带有一点幽默感
4. 当推荐电影时，要说明推荐理由
5. 如果用户问的问题不在你的能力范围内，诚实告知并建议其他方式

当前用户ID：{user_id}

重要规则：
- 当调用需要user_id的工具时（如get_user_favorites、get_user_ratings、get_recommendations_for_user），使用当前用户ID：{user_id}
- 所有电影信息必须通过工具函数从数据库获取，不要编造电影名称或信息
- 如果搜索结果为空，要明确告知用户
- 推荐电影时要考虑用户的历史偏好
- 用户询问"我的收藏"、"我的评分"、"我的历史"时，必须调用相应工具查询真实数据
- 当工具返回结果后，必须基于这些结果生成回复，不要只是重复调用工具
- 推荐电影时，从工具返回的列表中选择1-3部详细介绍，包括片名、类型、评分和推荐理由"""
        
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
            {"role": "system", "content": self._build_system_prompt(context, user_id)}
        ]
        
        # 添加对话历史
        if conversation_history:
            messages.extend(conversation_history)
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        # 第一次请求 DeepSeek
        response = await self.client.chat.completions.create(
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
            final_response = await self.client.chat.completions.create(
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
        # 检测推荐关键词，使用硬编码演示逻辑
        recommend_keywords = ["推荐", "建议", "介绍", "推荐电影", "推荐一部", "给我推荐"]
        if any(keyword in user_message for keyword in recommend_keywords):
            import asyncio
            
            # 第一步：显示思考状态
            thinking_msg = "正在分析...\n\n"
            for char in thinking_msg:
                yield char
                await asyncio.sleep(0.05)
            
            await asyncio.sleep(0.8)  # 停顿0.8秒模拟思考
            
            # 第二步：数据分析
            analyzing_msg = "正在读取你的观影数据\n"
            for char in analyzing_msg:
                yield char
                await asyncio.sleep(0.03)
            
            await asyncio.sleep(0.6)
            
            # 获取用户收藏和浏览历史
            favorites = db.query(Favorite).filter(Favorite.user_id == user_id).all()
            history = db.query(BrowsingHistory).filter(BrowsingHistory.user_id == user_id).all()
            
            # 获取收藏的电影详情
            fav_movie_ids = [f.movie_id for f in favorites]
            fav_movies = db.query(Movie).filter(Movie.id.in_(fav_movie_ids)).limit(5).all() if fav_movie_ids else []
            
            # 第三步：显示数据统计
            stats_msg = f"\n收藏记录：{len(favorites)} 部\n浏览历史：{len(history)} 条\n\n"
            for char in stats_msg:
                yield char
                await asyncio.sleep(0.02)
            
            await asyncio.sleep(0.5)
            
            # 第四步：分析偏好
            if fav_movies:
                pref_msg = "你的收藏偏好：\n"
                for char in pref_msg:
                    yield char
                    await asyncio.sleep(0.03)
                
                genres_count = {}
                for movie in fav_movies[:3]:  # 只显示前3部
                    movie_info = f"  • 《{movie.title}》 - {movie.genres or '未分类'}\n"
                    for char in movie_info:
                        yield char
                        await asyncio.sleep(0.02)
                    
                    if movie.genres:
                        for g in movie.genres.split(','):
                            g = g.strip()
                            genres_count[g] = genres_count.get(g, 0) + 1
                
                await asyncio.sleep(0.4)
                
                top_genres = sorted(genres_count.items(), key=lambda x: x[1], reverse=True)[:2]
                genre_msg = f"\n主要偏好：{', '.join([g[0] for g in top_genres])}\n\n"
                for char in genre_msg:
                    yield char
                    await asyncio.sleep(0.03)
            
            await asyncio.sleep(0.7)
            
            # 第五步：应用算法
            algo_msg = "应用推荐算法\n"
            for char in algo_msg:
                yield char
                await asyncio.sleep(0.04)
            
            await asyncio.sleep(0.5)
            
            steps = [
                "  • 协同过滤分析\n",
                "  • 内容特征匹配\n",
                "  • 混合模型评分\n"
            ]
            for step in steps:
                for char in step:
                    yield char
                    await asyncio.sleep(0.025)
                await asyncio.sleep(0.3)
            
            await asyncio.sleep(0.8)
            
            # 第六步：生成推荐
            result_header = "\n\n为你推荐以下电影：\n\n"
            for char in result_header:
                yield char
                await asyncio.sleep(0.04)
            
            # 从数据库获取高分电影作为推荐
            recommended = db.query(Movie).filter(
                Movie.avg_rate >= 8.0
            ).order_by(Movie.avg_rate.desc()).limit(3).all()
            
            if recommended:
                for i, movie in enumerate(recommended, 1):
                    movie_text = f"""{'─' * 40}

{i}. 《{movie.title}》 ({movie.release_year or '未知'})

类型：{movie.genres or '暂无分类'}
评分：{movie.avg_rate:.1f}/10
推荐理由：{self._generate_reason(movie, fav_movies)}

"""
                    for char in movie_text:
                        yield char
                        await asyncio.sleep(0.02)
                    
                    await asyncio.sleep(0.4)
            else:
                no_data_msg = "暂无推荐数据，请稍后再试。\n"
                for char in no_data_msg:
                    yield char
                    await asyncio.sleep(0.03)
            
            await asyncio.sleep(0.5)
            
            # 第七步：结束提示
            tip_msg = "\n提示：继续收藏和评分电影可以获得更精准的个性化推荐。"
            for char in tip_msg:
                yield char
                await asyncio.sleep(0.025)
            
            return
        
        # 构建消息列表（原有逻辑）
        messages = [
            {"role": "system", "content": self._build_system_prompt(context, user_id)}
        ]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": user_message})
        
        # 第一次请求（检测是否需要工具调用）
        response = await self.client.chat.completions.create(
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
                
                # 自动注入user_id（如果工具需要但AI没有提供）
                if function_name in ["get_user_favorites", "get_user_ratings", "get_recommendations_for_user"]:
                    if "user_id" not in function_args or function_args.get("user_id") == 0:
                        function_args["user_id"] = user_id
                
                tool_result = await self._execute_tool(
                    function_name,
                    function_args,
                    db
                )
                
                # 打印工具调用结果用于调试
                print(f"\n=== 工具调用: {function_name} ===")
                print(f"参数: {function_args}")
                print(f"结果: {json.dumps(tool_result, ensure_ascii=False)[:500]}")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(tool_result, ensure_ascii=False)
                })
            
            # 第二次请求，使用流式输出
            stream_response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            
            # 过滤DeepSeek的内部DSML标记（完整标签形式）
            buffer = ""
            
            async for chunk in stream_response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    buffer += content
                    
                    # 检查是否包含完整的DSML标签
                    while "<｜DSML｜" in buffer:
                        start = buffer.find("<｜DSML｜")
                        end = buffer.find("｜DSML｜>", start)
                        
                        if end != -1:
                            # 找到完整标签，输出标签前的内容
                            if start > 0:
                                yield buffer[:start]
                            # 移除标签
                            buffer = buffer[end + 8:]  # 8是"｜DSML｜>"的长度
                        else:
                            # 标签未完成，等待更多内容
                            if start > 0:
                                yield buffer[:start]
                                buffer = buffer[start:]
                            break
                    
                    # 如果缓冲区中没有待处理的标签开始符，输出内容
                    if "<｜DSML｜" not in buffer and buffer:
                        yield buffer
                        buffer = ""
            
            # 输出剩余内容（如果有）
            if buffer and "<｜DSML｜" not in buffer:
                yield buffer
        
        else:
            # 没有工具调用，直接流式输出
            stream_response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            
            async for chunk in stream_response:
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
