# 베이스 이미지
FROM python:3.9-slim

ARG BATCH=10
ARG TABLE_NAME=user

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 복사
COPY . .

CMD ["python", "run.py", "${BATCH}", "${TABLE_NAME}"]
