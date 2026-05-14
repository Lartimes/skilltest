# syntax=docker/dockerfile:1

# ==================== 后端构建阶段 ====================
FROM python:3.11-slim AS builder

WORKDIR /app

# 设置国内 pip 镜像源（阿里云）
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.aliyun.com

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt ./

# 预下载依赖（用于缓存）
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt || \
    pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY src/ ./src/
COPY config.yaml ./

# ==================== 生产阶段 ====================
FROM python:3.11-slim AS production

WORKDIR /app

# 设置国内 pip 镜像源
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.aliyun.com

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN useradd -m -u 1001 appuser

# 从 builder 复制依赖和代码
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app/src ./src
COPY --from=builder /app/config.yaml ./

# 设置权限
RUN chown -R appuser:appuser /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    NODE_ENV=production

# 切换到非 root 用户
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查（使用 uvicorn 内置）
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.connect(('localhost',8000)); s.close()" || exit 1

# 启动应用（使用 uvicorn）
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
