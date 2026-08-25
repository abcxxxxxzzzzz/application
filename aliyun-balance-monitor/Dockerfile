FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir \
    -i https://mirrors.aliyun.com/pypi/simple \
    -r requirements.txt

COPY . .

ENV TZ=Asia/Shanghai

CMD ["python", "monitor.py"]