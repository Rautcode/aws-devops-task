pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = '939533572395'
        AWS_DEFAULT_REGION = 'ap-south-1'
        ECR_REPOSITORY = 'aws-data-pipeline-repo'
        IMAGE_TAG = 'latest'
        GIT_REPOSITORY = 'https://github.com/Its-Lord-Stark/aws-data-pipeline'
        GIT_BRANCH = 'main'
        DOCKER_IMAGE = "${ECR_REPOSITORY}:${IMAGE_TAG}"
        ECR_REGISTRY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com"
        LAMBDA_FUNCTION = 'my-python-app'
    }

    stages {
        stage('Checkout Code') {
            steps {
                script {
                    checkout([$class: 'GitSCM', branches: [[name: "${GIT_BRANCH}"]],
                        userRemoteConfigs: [[url: "${GIT_REPOSITORY}"]]])
                }
            }
        }
        
        stage('Ensure ECR Repository Exists') {
            steps {
                withCredentials([string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'), 
                                 string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')]) {
                    script {
                        bat '''
                        set AWS_ACCESS_KEY_ID=%AWS_ACCESS_KEY_ID%
                        set AWS_SECRET_ACCESS_KEY=%AWS_SECRET_ACCESS_KEY%
                        aws ecr describe-repositories --repository-names %ECR_REPOSITORY% || aws ecr create-repository --repository-name %ECR_REPOSITORY%
                        '''
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    def dockerImage = docker.build("${DOCKER_IMAGE}")
                }
            }
        }

        stage('Push Docker Image to ECR') {
            steps {
                withCredentials([string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'), 
                                 string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')]) {
                    script {
                        bat '''
                        FOR /F "tokens=*" %%i IN ('aws ecr get-login-password --region %AWS_DEFAULT_REGION%') DO docker login --username AWS --password %%i %ECR_REGISTRY%
                        docker tag %DOCKER_IMAGE% %ECR_REGISTRY%/%ECR_REPOSITORY%:%IMAGE_TAG%
                        docker push %ECR_REGISTRY%/%ECR_REPOSITORY%:%IMAGE_TAG%
                        '''
                    }
                }
            }
        }

        stage('Update Lambda Function') {
            steps {
                script {
                    // Updating the Lambda function with the new Docker image from ECR
                    bat '''
                    set AWS_ACCESS_KEY_ID=%AWS_ACCESS_KEY_ID%
                    set AWS_SECRET_ACCESS_KEY=%AWS_SECRET_ACCESS_KEY%
                    aws lambda update-function-code --function-name %LAMBDA_FUNCTION% --image-uri %ECR_REGISTRY%/%ECR_REPOSITORY%:%IMAGE_TAG% --region %AWS_DEFAULT_REGION%
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Lambda function updated successfully with the new Docker image.'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
