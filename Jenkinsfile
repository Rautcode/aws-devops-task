pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = '982534379850'       
        AWS_REGION = 'ap-south-1'             
        ECR_REPO = 'my-python-app-lambda'     
        LAMBDA_FUNCTION = 'my-python-app'     
        ECR_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}"
    }

    stages {
        stage('Clone Repo') {
            steps {
                script {
                    echo "Cloning repository..."
                    git 'https://github.com/Rautcode/aws-devops-task.git'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image..."
                    sh "docker build -t ${ECR_REPO} ."
                }
            }
        }

        stage('Login to AWS ECR') {
            steps {
                script {
                    echo "Logging into AWS ECR..."
                    sh '''
                    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
                    '''
                }
            }
        }

        stage('Ensure ECR Repository Exists') {
            steps {
                script {
                    echo "Checking if ECR repository exists..."
                    def ecrExists = sh(script: "aws ecr describe-repositories --repository-names $ECR_REPO --region $AWS_REGION", returnStatus: true)
                    
                    if (ecrExists != 0) {
                        echo "ECR repository does not exist. Creating..."
                        sh "aws ecr create-repository --repository-name $ECR_REPO --region $AWS_REGION"
                    } else {
                        echo "ECR repository already exists."
                    }
                }
            }
        }

        stage('Tag and Push Docker Image') {
            steps {
                script {
                    echo "Tagging Docker image..."
                    sh "docker tag ${ECR_REPO}:latest ${ECR_URI}:latest"

                    echo "Pushing Docker image to ECR..."
                    sh "docker push ${ECR_URI}:latest"
                }
            }
        }

        stage('Deploy to AWS Lambda') {
            steps {
                script {
                    echo "Updating AWS Lambda function..."
                    sh "aws lambda update-function-code --function-name ${LAMBDA_FUNCTION} --image-uri ${ECR_URI}:latest"
                }
            }
        }
    }
}
