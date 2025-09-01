#!/usr/bin/env python3
"""
电影推荐系统后端启动脚本
"""
import uvicorn
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    """启动FastAPI应用"""
    print("🎬 启动电影推荐系统后端服务...")
    print("📍 项目路径:", project_root)
    
    # 启动服务器
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
