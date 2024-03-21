FROM python:3.10-slim

WORKDIR /app

# git 설치
RUN apt-get update && apt-get install -y git

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8002

CMD ["python", "main.py"]