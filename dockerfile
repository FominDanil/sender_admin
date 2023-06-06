FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

ADD requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

ADD . /app
