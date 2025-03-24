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
                echo "Перевірка Python:"
                which python3  # Виведе шлях до Python у віртуальному середовищі
                echo "Перевірка pip:"
                which pip  # Виведе шлях до pip у віртуальному середовищ
                pip install -r ${REQUIREMENTS_FILE}
                """
            }
        }
    /*
        stage('Install Dependencies') {
            steps {
                sh """
               . venv/bin/activate
                pip install --upgrade pip
                pip install -r ${REQUIREMENTS_FILE}
                """
            }
        }

        stage('Code Linting and Security Check') {
            parallel {
                stage('Code Linting') {
                    steps {
                        sh 'flake8'
                        sh 'black --check .'
                    }
                }

                stage('Security Check') {
                    steps {
                        sh 'bandit WISHI.py'
                    }
                }
            }
        } */
    }

    post {
        always {
            cleanWs()
        }
    }
}
