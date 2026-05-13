pipeline {

    agent any

    environment {
        GHCR_REGISTRY = 'ghcr.io'
        GHCR_IMAGE    = 'ghcr.io/vinitdubey-get/ui_automation_orangehrm'
        IMAGE_TAG     = 'latest'
    }

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
    }

    triggers {
        cron('0 2 * * *')
    }

    parameters {
        choice(
            name: 'TEST_SUITE',
            choices: ['all', 'smoke', 'regression'],
            description: 'Select which suite to run'
        )
        string(
            name: 'BASE_URL',
            defaultValue: 'https://practice.expandtesting.com',
            description: 'Target application URL'
        )
        string(
            name: 'USER_EMAIL',
            defaultValue: '',
            description: 'Email address to receive build notification'
        )
    }

    stages {

        // ── 1. PULL IMAGE FROM GHCR ───────────────────────────────────────────
        stage('Pull Image') {
            steps {
                echo "Pulling image: ${env.GHCR_IMAGE}:${env.IMAGE_TAG}"
                withCredentials([
                    usernamePassword(
                        credentialsId: 'ghcr-credentials',
                        usernameVariable: 'GH_USER',
                        passwordVariable: 'GH_TOKEN'
                    )
                ]) {
                    bat """
                        echo %GH_TOKEN% | docker login %GHCR_REGISTRY% --username %GH_USER% --password-stdin
                        docker pull %GHCR_IMAGE%:%IMAGE_TAG%
                    """
                }
            }
        }

        // ── 2. SMOKE TESTS ────────────────────────────────────────────────────
        stage('Smoke Tests') {
            when {
                anyOf {
                    expression { params.TEST_SUITE == 'all' }
                    expression { params.TEST_SUITE == 'smoke' }
                }
            }
            steps {
                echo 'Running smoke tests...'
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                    bat """
                        docker run --rm ^
                            --shm-size=2gb ^
                            -e BASE_URL=%BASE_URL% ^
                            -e HEADLESS=true ^
                            -v %WORKSPACE%/allure-results:/app/allure-results ^
                            %GHCR_IMAGE%:%IMAGE_TAG% ^
                            tests/ -m smoke --alluredir=allure-results -v --tb=short
                    """
                }
            }
        }

        // ── 3. REGRESSION TESTS ───────────────────────────────────────────────
        stage('Regression Tests') {
            when {
                anyOf {
                    expression { params.TEST_SUITE == 'all' }
                    expression { params.TEST_SUITE == 'regression' }
                }
            }
            steps {
                echo 'Running regression tests...'
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                    bat """
                        docker run --rm ^
                            --shm-size=2gb ^
                            -e BASE_URL=%BASE_URL% ^
                            -e HEADLESS=true ^
                            -v %WORKSPACE%/allure-results:/app/allure-results ^
                            %GHCR_IMAGE%:%IMAGE_TAG% ^
                            tests/ -m regression --alluredir=allure-results -v --tb=short
                    """
                }
            }
        }

        // ── 4. PUBLISH ALLURE REPORT ──────────────────────────────────────────
        stage('Publish Allure Report') {
            steps {
                echo 'Generating Allure HTML report...'
                allure([
                    includeProperties: false,
                    jdk              : '',
                    results          : [[path: 'allure-results']]
                ])
            }
        }

    }

    // ── POST ──────────────────────────────────────────────────────────────────
    post {

        always {
            archiveArtifacts(
                artifacts: 'allure-results/**',
                allowEmptyArchive: true
            )

            bat "docker rmi %GHCR_IMAGE%:%IMAGE_TAG% || exit 0"

            script {
                if (params.USER_EMAIL?.trim()) {
                    emailext(
                        subject: "🚀 ${env.JOB_NAME} | Build #${env.BUILD_NUMBER} | ${currentBuild.currentResult}",
                        mimeType: 'text/html',
                        to: "${params.USER_EMAIL}",
                        body: """
                        <html>
                        <body style="font-family: Arial, sans-serif; background-color:#f4f4f4; padding:20px;">
                            <div style="max-width:700px; margin:auto; background:white; border-radius:10px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                                <div style="background-color:${currentBuild.currentResult == 'SUCCESS' ? '#28a745' : currentBuild.currentResult == 'UNSTABLE' ? '#ffc107' : '#dc3545'}; color:white; padding:20px; text-align:center;">
                                    <h1 style="margin:0;">${currentBuild.currentResult}</h1>
                                    <p style="margin-top:10px;">Jenkins Automation Pipeline Notification</p>
                                </div>
                                <div style="padding:30px;">
                                    <h2>📌 Build Details</h2>
                                    <table style="width:100%; border-collapse:collapse;">
                                        <tr>
                                            <td style="padding:10px; border-bottom:1px solid #ddd;"><b>Project</b></td>
                                            <td style="padding:10px; border-bottom:1px solid #ddd;">${env.JOB_NAME}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding:10px; border-bottom:1px solid #ddd;"><b>Build Number</b></td>
                                            <td style="padding:10px; border-bottom:1px solid #ddd;">#${env.BUILD_NUMBER}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding:10px; border-bottom:1px solid #ddd;"><b>Test Suite</b></td>
                                            <td style="padding:10px; border-bottom:1px solid #ddd;">${params.TEST_SUITE}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding:10px; border-bottom:1px solid #ddd;"><b>Status</b></td>
                                            <td style="padding:10px; border-bottom:1px solid #ddd;">${currentBuild.currentResult}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding:10px; border-bottom:1px solid #ddd;"><b>Duration</b></td>
                                            <td style="padding:10px; border-bottom:1px solid #ddd;">${currentBuild.durationString}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding:10px; border-bottom:1px solid #ddd;"><b>Build URL</b></td>
                                            <td style="padding:10px; border-bottom:1px solid #ddd;"><a href="${env.BUILD_URL}">Open Jenkins Build</a></td>
                                        </tr>
                                    </table>
                                    <div style="margin-top:30px; text-align:center;">
                                        <a href="${env.BUILD_URL}" style="background:#007bff; color:white; padding:12px 20px; text-decoration:none; border-radius:6px; margin-right:10px; display:inline-block;">🔍 View Build</a>
                                        <a href="${env.BUILD_URL}allure" style="background:#6f42c1; color:white; padding:12px 20px; text-decoration:none; border-radius:6px; display:inline-block;">📊 Open Allure Report</a>
                                    </div>
                                </div>
                                <div style="background:#f0f0f0; padding:15px; text-align:center; font-size:12px; color:#666;">
                                    Generated automatically by Jenkins CI Pipeline
                                </div>
                            </div>
                        </body>
                        </html>
                        """
                    )
                }
            }
        }

        success {
            echo '✅ Pipeline passed successfully.'
        }

        unstable {
            echo '⚠️ Pipeline completed with test failures — check Allure report.'
        }

        failure {
            echo '❌ Pipeline failed — check console output.'
        }

    }
}