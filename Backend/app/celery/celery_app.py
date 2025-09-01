# Celery app 初始化
from celery import Celery

celery_app = Celery(
    "movie_system",
    broker="redis://localhost:6379/0",  # Redis 作为消息代理
    backend="redis://localhost:6379/0", # Redis 作为结果后端
    include=["app.tasks"]
)

# Celery 配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    
    # 任务路由配置
    task_routes={
        "app.tasks.update_movie_recommendations": {"queue": "recommendations"},
        "app.tasks.crawl_movie_data": {"queue": "data_crawl"},
        "app.tasks.send_recommendation_email": {"queue": "emails"},
    },
    
    # 定时任务配置
    beat_schedule={
        "update-recommendations-daily": {
            "task": "app.tasks.update_movie_recommendations",
            "schedule": 86400.0,  # 每天执行一次
        },
        "crawl-movie-data-weekly": {
            "task": "app.tasks.crawl_movie_data",
            "schedule": 604800.0,  # 每周执行一次
        },
    },
)

if __name__ == "__main__":
    celery_app.start()
