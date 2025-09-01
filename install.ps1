# 电影推荐系统 - 一键安装脚本
# Movie Recommendation System - One-click Installation

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🎬 电影推荐系统 - 环境配置" -ForegroundColor Yellow
Write-Host "Movie Recommendation System Setup" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Cyan

# 检查Python版本
Write-Host "`n🐍 检查Python环境..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python版本: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 未安装Python或Python未添加到PATH" -ForegroundColor Red
    Write-Host "请先安装Python 3.8+: https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# 检查Node.js版本
Write-Host "`n📦 检查Node.js环境..." -ForegroundColor Green
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js版本: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 未安装Node.js或Node.js未添加到PATH" -ForegroundColor Red
    Write-Host "请先安装Node.js 16+: https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# 安装后端依赖
Write-Host "`n🔧 安装后端依赖..." -ForegroundColor Green
Set-Location Backend

# 创建虚拟环境
if (!(Test-Path "venv")) {
    Write-Host "创建Python虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
}

# 激活虚拟环境并安装依赖
Write-Host "激活虚拟环境并安装依赖..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
pip install -r ..\requirements.txt

# 导入数据
if (Test-Path "import_data.py") {
    Write-Host "导入数据库数据..." -ForegroundColor Yellow
    python import_data.py
} else {
    Write-Host "⚠️  数据导入脚本不存在，跳过数据导入" -ForegroundColor Yellow
}

Set-Location ..

# 安装前端依赖
Write-Host "`n🎨 安装前端依赖..." -ForegroundColor Green
Set-Location Frontend
npm install
Set-Location ..

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "🎉 安装完成！" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan

Write-Host "`n🚀 启动说明:" -ForegroundColor Yellow
Write-Host "1. 启动后端 (新终端):" -ForegroundColor White
Write-Host "   cd Backend" -ForegroundColor Gray
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Gray

Write-Host "`n2. 启动前端 (新终端):" -ForegroundColor White
Write-Host "   cd Frontend" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray

Write-Host "`n3. 访问应用:" -ForegroundColor White
Write-Host "   前端: http://localhost:5173" -ForegroundColor Gray
Write-Host "   后端API: http://localhost:8000/docs" -ForegroundColor Gray

Write-Host "`n📝 注意事项:" -ForegroundColor Yellow
Write-Host "• 确保8000和5173端口未被占用" -ForegroundColor Gray
Write-Host "• 如遇到依赖冲突，可尝试删除node_modules后重新安装" -ForegroundColor Gray
Write-Host "• 数据库文件位于Backend/Recommend.db" -ForegroundColor Gray
