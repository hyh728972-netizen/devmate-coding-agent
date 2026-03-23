FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

# ⭐ 先复制依赖文件（利用缓存）
COPY pyproject.toml .
RUN uv pip install --system .

# ⭐ 再复制源码
COPY . .

# ⭐⭐⭐⭐⭐ 关键：src layout 必须设置
ENV PYTHONPATH=/app/src

CMD ["python", "main.py"]