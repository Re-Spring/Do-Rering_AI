FROM python:3.10

WORKDIR /app

# 필요한 패키지 설치 (libgl1-mesa-glx와 git을 한 번에 설치)
RUN apt-get update && \
    apt-get install -y \
    libgl1-mesa-glx \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]