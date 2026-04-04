# Sử dụng base image Python 3.12
FROM python:3.10-slim

WORKDIR /app

# Cài đặt các gói hệ thống cần thiết
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port cho FastAPI
EXPOSE 8000

CMD ["python", "src/app.py"]