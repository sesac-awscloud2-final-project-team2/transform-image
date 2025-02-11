# transform-image

## 실행 방법
- run 파일 실행
- argument : dynamodb, 배치 사이즈 (기본 1)
- 예) `python run.py 10`

## ECR 업로드
```shell
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin 390844761387.dkr.ecr.ap-northeast-2.amazonaws.com
# docker image build -t transform .
docker image build --platform linux/arm64 -t transform .
docker tag transform 390844761387.dkr.ecr.ap-northeast-2.amazonaws.com/transform:v1.1
docker push 390844761387.dkr.ecr.ap-northeast-2.amazonaws.com/transform:v1.1
```

docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 -t 390844761387.dkr.ecr.ap-northeast-2.amazonaws.com/transform:v1.1 --push .
