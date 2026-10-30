
pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    environment {
        IMAGE_NAME = "24mis0392/social-app:v1"

        PYTHON_EXE = "C:\\Users\\siddh\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe"

        DOCKER_EXE = "C:\\Users\\siddh\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/prvligagithub/social-app.git'
            }
        }

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

        stage('Docker Hub Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'social-dockerhub-new',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    bat '''
                        echo %DOCKER_PASS% | "%DOCKER_EXE%" login -u %DOCKER_USER% --password-stdin
                        if errorlevel 1 exit /b 1
                    '''
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                bat '"%DOCKER_EXE%" push %IMAGE_NAME%'
            }
        }
    }

    post {
        success {
            echo 'Social App V1 successfully built and pushed!'
        }

        failure {
            echo 'Pipeline failed. Check Console Output.'
        }
    }
}