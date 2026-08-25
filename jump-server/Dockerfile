FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=2
ENV PIP_NO_CACHE_DIR=1

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app ./app
COPY templates ./templates
COPY static ./static

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "18667", "--workers", "8", "--loop", "uvloop", "--http", "httptools", "--no-server-header", "--timeout-keep-alive", "5", "--backlog", "8192"]