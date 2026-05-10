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
        
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
        
                    bat '''
                        pytest -m smoke ^
                        --alluredir=allure-results ^
                        --clean-alluredir ^
                        -v --tb=short
                    '''
                }
            }
        }

        stage('Publish Allure Report') {
            steps {
        
                echo 'Generating Allure HTML report...'
        
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
    
            emailext(
                subject: "Jenkins Build: ${currentBuild.currentResult} - ${env.JOB_NAME}",
                
                body: """
                    <h2>UI Automation Pipeline Result</h2>
    
                    <p><b>Project:</b> ${env.JOB_NAME}</p>
                    <p><b>Build Number:</b> ${env.BUILD_NUMBER}</p>
                    <p><b>Status:</b> ${currentBuild.currentResult}</p>
    
                    <p>
                        <a href="${env.BUILD_URL}allure">
                            Open Allure Report
                        </a>
                    </p>
    
                    <p>
                        <a href="${env.BUILD_URL}">
                            Open Jenkins Build
                        </a>
                    </p>
                """,
    
                mimeType: 'text/html',
    
                to: "${params.USER_EMAIL}"
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
