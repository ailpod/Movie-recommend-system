#!/usr/bin/env python3
"""
数据库数据导入脚本
从JSON文件导入数据到SQLite数据库
"""
import sqlite3
import json
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.models import Base
from app.core.database import engine

def import_data_from_json():
    """从JSON文件导入数据到数据库"""
    export_path = "data_export.json"
    
    if not os.path.exists(export_path):
        print(f"数据文件不存在: {export_path}")
        return False
    
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("数据库表创建完成")
        
        # 读取JSON数据
        with open(export_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conn = sqlite3.connect("Recommend.db")
        cursor = conn.cursor()
        
        # 清空现有数据（可选）
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM movies")
        print("清空现有数据")
        
        # 导入用户数据
        if "users" in data["tables"]:
            users = data["tables"]["users"]
            for user in users:
                columns = ', '.join(user.keys())
                placeholders = ', '.join(['?' for _ in user.values()])
                query = f"INSERT INTO users ({columns}) VALUES ({placeholders})"
                cursor.execute(query, list(user.values()))
            print(f"导入 {len(users)} 个用户")
        
        # 导入电影数据
        if "movies" in data["tables"]:
            movies = data["tables"]["movies"]
            for movie in movies:
                columns = ', '.join(movie.keys())
                placeholders = ', '.join(['?' for _ in movie.values()])
                query = f"INSERT INTO movies ({columns}) VALUES ({placeholders})"
                cursor.execute(query, list(movie.values()))
            print(f"导入 {len(movies)} 部电影")
        
        # 导入其他表数据
        for table_name, table_data in data["tables"].items():
            if table_name in ["users", "movies"]:
                continue
            
            if table_data:
                for row in table_data:
                    columns = ', '.join(row.keys())
                    placeholders = ', '.join(['?' for _ in row.values()])
                    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    cursor.execute(query, list(row.values()))
                print(f"导入表 {table_name}: {len(table_data)} 条记录")
        
        conn.commit()
        print("数据导入成功")
        return True
        
    except Exception as e:
        print(f"导入失败: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    import_data_from_json()
