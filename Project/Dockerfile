FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    curl \
    git \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# Fonts for PaddleOCR
RUN mkdir -p ~/.paddleocr/fonts && \
    curl -L -o ~/.paddleocr/fonts/PingFang-SC-Regular.ttf https://paddle-model-ecology.bj.bcebos.com/paddlex/PaddleX3.0/fonts/PingFang-SC-Regular.ttf && \
    curl -L -o ~/.paddleocr/fonts/simfang.ttf https://paddle-model-ecology.bj.bcebos.com/paddlex/PaddleX3.0/fonts/simfang.ttf

# Requirements
COPY requirements.txt .
RUN pip install --upgrade pip && \
    for i in 1 2 3 4 5; do pip install --no-cache-dir -r requirements.txt && break || sleep 5; done


COPY . .

# Disattiva usage tracking di Streamlit
ENV STREAMLIT_BROWSER_GATHERUSAGESTATS=false

EXPOSE 8501

RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
