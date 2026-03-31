#!/bin/bash

echo "🚀 开始测试Docker构建..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装"
    exit 1
fi

# 构建镜像
echo "🏗️ 构建Django镜像..."
docker build -f dev.Dockerfile -t nezha-django .

# 检查构建结果
if [ $? -eq 0 ]; then
    echo "✅ 镜像构建成功"
    echo "📦 镜像名称: nezha-django"
else
    echo "❌ 镜像构建失败"
    exit 1
fi