FROM dockerproxy.net/library/python:3.11-slim
# FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y curl ffmpeg git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制requirements.txt和pyproject.toml
COPY requirements.txt pyproject.toml ./

# 安装依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 复制项目文件
COPY . .

EXPOSE 8001

CMD ["./start.sh", "--prod"]

