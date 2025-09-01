#!/bin/bash

# 电影推荐系统 - 一键安装脚本
# Movie Recommendation System - One-click Installation

echo "========================================="
echo "🎬 电影推荐系统 - 环境配置"
echo "Movie Recommendation System Setup"
echo "========================================="

# 检查Python版本
echo ""
echo "🐍 检查Python环境..."
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    echo "✅ Python版本: $python_version"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    python_version=$(python --version)
    echo "✅ Python版本: $python_version"
    PYTHON_CMD="python"
else
    echo "❌ 未安装Python或Python未添加到PATH"
    echo "请先安装Python 3.8+: https://www.python.org/downloads/"
    exit 1
fi

# 检查Node.js版本
echo ""
echo "📦 检查Node.js环境..."
if command -v node &> /dev/null; then
    node_version=$(node --version)
    echo "✅ Node.js版本: $node_version"
else
    echo "❌ 未安装Node.js或Node.js未添加到PATH"
    echo "请先安装Node.js 16+: https://nodejs.org/"
    exit 1
fi

# 安装后端依赖
echo ""
echo "🔧 安装后端依赖..."
cd Backend

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    $PYTHON_CMD -m venv venv
fi

# 激活虚拟环境并安装依赖
echo "激活虚拟环境并安装依赖..."
source venv/bin/activate
pip install -r ../requirements.txt

# 导入数据
if [ -f "import_data.py" ]; then
    echo "导入数据库数据..."
    python import_data.py
else
    echo "⚠️  数据导入脚本不存在，跳过数据导入"
fi

cd ..

# 安装前端依赖
echo ""
echo "🎨 安装前端依赖..."
cd Frontend
npm install
cd ..

echo ""
echo "========================================="
echo "🎉 安装完成！"
echo "========================================="

echo ""
echo "🚀 启动说明:"
echo "1. 启动后端 (新终端):"
echo "   cd Backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo ""
echo "2. 启动前端 (新终端):"
echo "   cd Frontend"
echo "   npm run dev"

echo ""
echo "3. 访问应用:"
echo "   前端: http://localhost:5173"
echo "   后端API: http://localhost:8000/docs"

echo ""
echo "📝 注意事项:"
echo "• 确保8000和5173端口未被占用"
echo "• 如遇到依赖冲突，可尝试删除node_modules后重新安装"
echo "• 数据库文件位于Backend/Recommend.db"
