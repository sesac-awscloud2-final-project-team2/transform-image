# docker build --build-arg BATCH=10 -t {tag_name} .

# 베이스 이미지
FROM python:3.9-slim

ARG BATCH=10

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 복사
COPY . .

# Flask 실행 포트
EXPOSE 30002

# Flask 서버 실행
CMD ["python", "app.py", BATCH]
