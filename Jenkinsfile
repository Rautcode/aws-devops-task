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
                git 'https://github.com/Rautcode/aws-data-pipeline.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${ECR_REPO} ."
            }
        }

        stage('Login to AWS ECR') {
            steps {
                sh "aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
            }
        }

        stage('Push Docker Image to ECR') {
            steps {
                sh '''
                docker tag ${ECR_REPO}:latest ${ECR_URI}:latest
                docker push ${ECR_URI}:latest
                '''
            }
        }

        stage('Deploy Terraform') {
            steps {
                sh '''
                cd terraform
                terraform init
                terraform apply -auto-approve
                '''
            }
        }

        stage('Update AWS Lambda') {
            steps {
                sh "aws lambda update-function-code --function-name ${LAMBDA_FUNCTION} --image-uri ${ECR_URI}:latest"
            }
        }
    }
}
