#!/usr/bin/env python3
"""
数据库数据导出脚本
将SQLite数据库中的数据导出为JSON格式，便于版本控制
"""
import sqlite3
import json
import os
from datetime import datetime

def export_database_to_json():
    """导出数据库数据到JSON文件"""
    db_path = "Recommend.db"
    export_path = "data_export.json"
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        export_data = {
            "export_time": datetime.now().isoformat(),
            "tables": {}
        }
        
        # 导出用户表
        cursor.execute("SELECT * FROM users")
        users = [dict(row) for row in cursor.fetchall()]
        export_data["tables"]["users"] = users
        print(f"导出 {len(users)} 个用户")
        
        # 导出电影表
        cursor.execute("SELECT * FROM movies")
        movies = [dict(row) for row in cursor.fetchall()]
        export_data["tables"]["movies"] = movies
        print(f"导出 {len(movies)} 部电影")
        
        # 如果存在其他表，也可以导出
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT IN ('users', 'movies')")
        other_tables = cursor.fetchall()
        
        for table in other_tables:
            table_name = table[0]
            if table_name.startswith('sqlite_'):
                continue
            
            cursor.execute(f"SELECT * FROM {table_name}")
            table_data = [dict(row) for row in cursor.fetchall()]
            export_data["tables"][table_name] = table_data
            print(f"导出表 {table_name}: {len(table_data)} 条记录")
        
        # 保存到JSON文件
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"数据导出成功: {export_path}")
        return True
        
    except Exception as e:
        print(f"导出失败: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    export_database_to_json()
