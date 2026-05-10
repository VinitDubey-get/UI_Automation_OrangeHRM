pipeline {

    agent any

    environment {

        // Application URL
        BASE_URL = 'https://opensource-demo.orangehrmlive.com/web/index.php'

        // Project root for imports
        PYTHONPATH = "${WORKSPACE}"
    }

    options {

        // Show timestamps in console logs
        timestamps()

        // Stop build if hanging too long
        timeout(time: 30, unit: 'MINUTES')

        // Keep only last 10 builds
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

                echo 'Installing Python dependencies...'

                sh '''
                    pip install -r requirements.txt
                '''

                sh '''
                    pip show playwright pytest allure-pytest
                '''
            }
        }

        stage('Smoke Tests') {
            steps {

                echo 'Running smoke test suite...'

                sh '''
                    pytest -m smoke \
                    --alluredir=allure-results \
                    --clean-alluredir \
                    -v --tb=short
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

            echo 'Archiving artifacts...'

            archiveArtifacts(
                artifacts: 'allure-results/**',
                allowEmptyArchive: true
            )
        }

        success {
            echo 'Smoke suite passed successfully!'
        }

        unstable {
            echo 'Some smoke tests failed. Check Allure report.'
        }

        failure {
            echo 'Pipeline execution failed. Check Jenkins logs.'
        }
    }
}
