pipeline {
    agent any

    triggers{
        githubPush()
    }
    environment {
        PYTHON_ENV = 'python3'
        REQUIREMENTS_FILE = 'requirements.txt'
        API_TOKEN = credentials('my_telegram_bot_token')
        MONGODB_URI = 'mongodb://localhost:27017/'
    }

    stages {
        stage('Install Dependencies') {
            steps {
                sh """
                ${PYTHON_ENV} -m venv venv
                . venv/bin/activate
                pip install -r ${REQUIREMENTS_FILE}
                pip install flake8 bandit black
                """
            }
        }

        stage('Code Linting and Security Check') {
            parallel {
                stage('Code Linting') {
                    steps {
                        sh 'python3 flake8'
                        sh 'python3 black --check .'
                    }
                }

                stage('Security Check') {
                    steps {
                        sh 'python3 bandit WISHI.py'
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
