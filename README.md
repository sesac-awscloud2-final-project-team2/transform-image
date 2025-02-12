# transform-image

## 실행 방법
- run 파일 실행
- argument : dynamodb, 배치 사이즈 (기본 1)
- 예) `python run.py 10`

## ECR 업로드
```shell
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin 390844761387.dkr.ecr.ap-northeast-2.amazonaws.com
# docker image build -t transform .
docker image build --platform linux/amd64 -t transform .
docker tag transform 390844761387.dkr.ecr.ap-northeast-2.amazonaws.com/transform:test
docker push 390844761387.dkr.ecr.ap-northeast-2.amazonaws.com/transform:test
```
