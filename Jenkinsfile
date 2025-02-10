def getNextEcrTag(String repositoryName, String region) {
    def latestTag = sh(
        script: """
            aws ecr describe-images \
                --repository-name ${repositoryName} \
                --region ${region} \
                --query 'sort_by(imageDetails,& imagePushedAt)[-1].imageTags[0]' \
                --output text
        """,
        returnStdout: true
    ).trim()
    
    // v{major}.{minor} 형식인지 확인
    def matcher = latestTag =~ /^v(\d+)\.(\d+)$/
    if (matcher.matches()) {
        def major = matcher[0][1].toInteger()
        def minor = matcher[0][2].toInteger()
        
        // minor 버전을 1 증가
        minor += 1
        
        // 새 태그 생성
        def nextTag = "v${major}.${minor}"
        return nextTag
    } else {
        // 형식이 맞지 않는 경우 에러 처리 또는 기본값 반환
        echo "Warning: Latest tag is not in v{major}.{minor} format. Returning default value."
        return "v1.0"
    }
}


pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "390844761387"
        AWS_DEFAULT_REGION = "ap-northeast-2"
        IMAGE_REPO_NAME = "transform"
        REPOSITORY_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${IMAGE_REPO_NAME}"
        CREDENTIAL_ID = "ecr-credential"
        ARGO_GITHUB_REPO = "aws-argocd"
    }
    stages {
        stage('ECR Login') {
            steps {
                script {
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: "${CREDENTIAL_ID}"]]) {
                        sh "aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com"
                    }
                }
            }
        }
        stage('Set Latest Tag') {
            steps {
                script {
                    echo '도커 태그 마지막을 불러온 후 마이너 버전을 증가시킵니다.'
                    env.IMAGE_TAG = getNextEcrTag(IMAGE_REPO_NAME, AWS_DEFAULT_REGION)
                }
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    echo '도커 이미지 빌드를 시작합니다.'
                    sh "docker image build --platform linux/amd64 -t ${IMAGE_REPO_NAME}:${IMAGE_TAG} ."
                    echo '도커 이미지 빌드가 완료되었습니다.'
                }
            }
        }

        stage('Tag Docker Image') {
            steps {
                script {
                    echo '도커 이미지에 태그를 추가합니다.'
                    sh "docker tag ${IMAGE_REPO_NAME}:${IMAGE_TAG} ${REPOSITORY_URI}:${IMAGE_TAG}"
                    echo '도커 이미지 태그 추가가 완료되었습니다.'
                }
            }
        }

        stage('Push to ECR') {
            steps {
                script {
                    echo 'ECR에 도커 이미지를 업로드합니다.'
                    sh "docker push ${REPOSITORY_URI}:${IMAGE_TAG}"
                    echo 'ECR에 도커 이미지 업로드가 완료되었습니다.'
                }
            }
        }

        stage('Update ArgoCD YAML') { 
            steps {
                sh "rm -rf ${ARGO_GITHUB_REPO}"
                script {
                    // GITHUB_TOKEN을 사용하여 인증
                    withCredentials([string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')]) {
                        sh """
                        git config --global credential.helper store
                        echo "https://$GITHUB_TOKEN:@github.com" > ~/.git-credentials
                        git clone https://github.com/sesac-awscloud2-final-project-team2/${ARGO_GITHUB_REPO}.git
                        """
                    }
                }
                sh """
                sed -i 's|image: ${REPOSITORY_URI}:.*|image: ${REPOSITORY_URI}:${IMAGE_TAG}|' ${ARGO_GITHUB_REPO}/collector/collector-deployment.yaml
                """
                echo 'ArgoCD repo에 있는 YAML 파일 태그가 수정되었습니다.'
            }
        }

        stage('Commit and Push Changes') {
            steps {
                sh """
                cd ${ARGO_GITHUB_REPO}
                git config user.email "jenkins@example.com"
                git config user.name "Jenkins"
                git remote add argo_repo https://github.com/sesac-awscloud2-final-project-team2/${ARGO_GITHUB_REPO}.git
                git add .
                git commit -m "Update ${IMAGE_REPO_NAME} image tag to ${IMAGE_TAG}"
                git push argo_repo main
                """
                echo '수정된 ArgoCD repo main 브랜치로 push 되었습니다.'
            }
        }

    }
}
