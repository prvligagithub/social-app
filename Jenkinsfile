
pipeline {
    agent any

    environment {
        IMAGE_NAME = "24mis0392/social-app:v1"

        PYTHON_EXE = "C:\\Users\\siddh\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe"

        DOCKER_EXE = "C:\\Users\\siddh\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"
    }

    stages {

        stage('Install Dependencies') {
            steps {
                bat '"%PYTHON_EXE%" -m pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat '"%PYTHON_EXE%" -m pytest -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '"%DOCKER_EXE%" build -t %IMAGE_NAME% .'
            }
        }

        stage('Docker Hub Login and Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'social-dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    bat '''
                        echo %DOCKER_PASS% | "%DOCKER_EXE%" login -u %DOCKER_USER% --password-stdin
                        "%DOCKER_EXE%" push %IMAGE_NAME%
                        "%DOCKER_EXE%" logout
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Social App V1 pipeline completed successfully!'
        }

        failure {
            echo 'Social App V1 pipeline failed. Check the console output.'
        }
    }
}
