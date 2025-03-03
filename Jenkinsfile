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
                    checkout([
                        $class: 'GitSCM',
                        branches: [[name: 'refs/heads/main']],
                        userRemoteConfigs: [[url: 'https://github.com/Rautcode/aws-devops-task.git']]
                    ])
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image..."
                    sh "docker build -t ${ECR_REPO}:latest ."
                }
            }
        }

        stage('Login to AWS ECR') {
            steps {
                script {
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-credentials']]) {
                        echo "Logging into AWS ECR..."
                        sh """
                        PASSWORD=\$(aws ecr get-login-password --region ${AWS_REGION})
                        echo \$PASSWORD | docker login --username AWS --password-stdin ${ECR_URI}
                        """
                    }
                }
            }
        }

        stage('Ensure ECR Repository Exists') {
            steps {
                script {
                    echo "Checking if ECR repository exists..."
                    def ecrExists = sh(returnStatus: true, script: """
                        aws ecr describe-repositories --repository-names ${ECR_REPO} --region ${AWS_REGION} || exit 1
                    """)

                    if (ecrExists != 0) {
                        echo "ECR repository does not exist. Creating..."
                        sh "aws ecr create-repository --repository-name ${ECR_REPO} --region ${AWS_REGION}"
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
                    sh "aws lambda update-function-code --function-name ${LAMBDA_FUNCTION} --image-uri ${ECR_URI}:latest --region ${AWS_REGION}"
                }
            }
        }
    }
}
