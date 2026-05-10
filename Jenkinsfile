pipeline {

    agent any

    environment {
        BASE_URL = 'https://opensource-demo.orangehrmlive.com/web/index.php'
        PYTHONPATH = "${WORKSPACE}"
    }

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Cloning repository...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {

                echo 'Installing dependencies...'

                bat 'pip install -r requirements.txt'

                bat 'playwright install chromium'
            }
        }

        stage('Smoke Tests') {
            steps {

                echo 'Running smoke tests...'

                bat '''
                    pytest -m smoke --alluredir=allure-results --clean-alluredir -v --tb=short
                '''
            }
        }

        stage('Publish Allure Report') {
            steps {

                echo 'Publishing Allure report...'

                allure([
                    includeProperties: false,
                    jdk: '',
                    results: [[path: 'allure-results']]
                ])
            }
        }
    }

    post {

        always {

            archiveArtifacts(
                artifacts: 'allure-results/**',
                allowEmptyArchive: true
            )
        }

        success {
            echo 'Smoke tests passed!'
        }

        unstable {
            echo 'Some tests failed.'
        }

        failure {
            echo 'Pipeline failed.'
        }
    }
}
