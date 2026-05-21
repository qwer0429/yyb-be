# ==========================================
# Django 后端 Dockerfile
# 基于 Python 3.9 + Gunicorn + Gevent
# ==========================================

FROM python:3.9-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=simpleserver.settings \
    TZ=Asia/Shanghai \
    DEBIAN_FRONTEND=noninteractive

# 设置工作目录
WORKDIR /app

# 安装系统依赖
# - default-libmysqlclient-dev / pkg-config / gcc: 编译 mysqlclient
# - libffi-dev / libssl-dev: 部分 Python 包的依赖
# - libpng-dev / libjpeg-dev / zlib1g-dev: Pillow 图像处理库依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    python3-dev \
    libffi-dev \
    libssl-dev \
    libpng-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 先复制 requirements.txt 并安装依赖（利用 Docker 缓存层）
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建日志和 media 目录（确保容器内有写权限）
RUN mkdir -p log media whoosh_index && chmod -R 755 log media whoosh_index

# 暴露 Gunicorn 端口（与 gunicorn.conf.py 中的 bind 保持一致）
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

# 启动命令
CMD ["gunicorn", "-c", "gunicorn.conf.py", "simpleserver.wsgi:application"]
