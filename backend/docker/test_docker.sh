#!/bin/bash

echo "🚀 开始测试Docker配置..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装"
    exit 1
fi

# 构建镜像
echo "🏗️ 构建Django镜像..."
cd docker && docker-compose build

# 检查构建结果
if [ $? -eq 0 ]; then
    echo "✅ 镜像构建成功"
else
    echo "❌ 镜像构建失败"
    exit 1
fi

# 启动服务
echo "🚀 启动服务..."
cd docker && docker-compose up -d

# 检查服务状态
sleep 10
if cd docker && docker-compose ps | grep -q "Up"; then
    echo "✅ 服务启动成功"
    echo "🌐 Django服务地址: http://localhost:8001"
    echo "🌐 Ollama服务地址: http://localhost:11434"
else
    echo "❌ 服务启动失败"
    cd docker && docker-compose logs
    exit 1
fi

echo "🎉 测试完成！"