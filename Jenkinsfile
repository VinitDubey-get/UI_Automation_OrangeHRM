pipeline {

    agent any

    environment {
        GHCR_REGISTRY      = 'ghcr.io'
        GHCR_IMAGE         = 'ghcr.io/vinitdubey-get/ui_automation_orangehrm'
        IMAGE_TAG          = 'latest'
        NOTIFICATION_EMAIL = 'vinitwork9958@gmail.com'
    }

    options {
        skipDefaultCheckout(true)
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
            description: 'Email address to receive build notification (leave blank to use default)'
        )
    }

    stages {

        // ─────────────────────────────────────────────────────────────
        // CHECKOUT SCM
        // ─────────────────────────────────────────────────────────────
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        // ─────────────────────────────────────────────────────────────
        // CLEAN OLD ALLURE RESULTS
        // ─────────────────────────────────────────────────────────────
        stage('Clean Allure Results') {
            steps {
                echo 'Cleaning old Allure results...'
                bat """
                    if exist allure-results (
                        rmdir /s /q allure-results
                    )
                    mkdir allure-results
                """
            }
        }

        // ─────────────────────────────────────────────────────────────
        // PULL IMAGE FROM GHCR
        // ─────────────────────────────────────────────────────────────
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

        // ─────────────────────────────────────────────────────────────
        // SMOKE TESTS
        // ─────────────────────────────────────────────────────────────
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
                            --entrypoint sh ^
                            --shm-size=2gb ^
                            -e BASE_URL=%BASE_URL% ^
                            -e HEADLESS=true ^
                            -v %WORKSPACE%/allure-results:/results ^
                            %GHCR_IMAGE%:%IMAGE_TAG% ^
                            -c "pytest tests/ -m smoke -p no:cacheprovider --alluredir=/tmp/allure-results -v --tb=short ; cp -r /tmp/allure-results/* /results/ || true"
                    """
                }
            }
        }

        // ─────────────────────────────────────────────────────────────
        // REGRESSION TESTS
        // ─────────────────────────────────────────────────────────────
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
                            --entrypoint sh ^
                            --shm-size=2gb ^
                            -e BASE_URL=%BASE_URL% ^
                            -e HEADLESS=true ^
                            -v %WORKSPACE%/allure-results:/results ^
                            %GHCR_IMAGE%:%IMAGE_TAG% ^
                            -c "pytest tests/ -m regression -p no:cacheprovider --alluredir=/tmp/allure-results -v --tb=short ; cp -r /tmp/allure-results/* /results/ || true"
                    """
                }
            }
        }

        // ─────────────────────────────────────────────────────────────
        // PARSE TEST RESULTS
        // ─────────────────────────────────────────────────────────────
        stage('Parse Test Results') {
            steps {
                script {
                    def smokePass = 0
                    def smokeFail = 0
                    def smokeSkip = 0
                    def smokeFailedTests = []

                    def regressionPass = 0
                    def regressionFail = 0
                    def regressionSkip = 0
                    def regressionFailedTests = []

                    def untaggedPass = 0
                    def untaggedFail = 0
                    def untaggedFailedTests = []

                    if (fileExists('allure-results')) {
                        def rawFiles = bat(
                            script: 'dir /b allure-results\\*-result.json 2>nul',
                            returnStdout: true
                        ).trim()

                        if (rawFiles) {
                            def files = rawFiles.split('\n')
                            files.each { file ->
                                file = file.trim()
                                if (!file || file.startsWith('Volume') || file.startsWith('Directory') || file.isEmpty()) return

                                try {
                                    def content = readFile("allure-results\\${file}")
                                    def json = new groovy.json.JsonSlurper().parseText(content)

                                    def status   = json.status  ?: 'unknown'
                                    def testName = json.name    ?: file
                                    def labels   = json.labels  ?: []

                                    def isSmoke      = labels.any { it.name == 'tag' && it.value?.toLowerCase() == 'smoke' }
                                    def isRegression = labels.any { it.name == 'tag' && it.value?.toLowerCase() == 'regression' }

                                    if (isSmoke) {
                                        if (status == 'passed')                    smokePass++
                                        else if (status in ['failed','broken'])  { smokeFail++; smokeFailedTests << testName }
                                        else if (status == 'skipped')              smokeSkip++
                                    } else if (isRegression) {
                                        if (status == 'passed')                    regressionPass++
                                        else if (status in ['failed','broken'])  { regressionFail++; regressionFailedTests << testName }
                                        else if (status == 'skipped')              regressionSkip++
                                    } else {
                                        if (status == 'passed')                    untaggedPass++
                                        else if (status in ['failed','broken'])  { untaggedFail++; untaggedFailedTests << testName }
                                    }
                                } catch (e) {
                                    echo "Skipping file ${file}: ${e.message}"
                                }
                            }
                        }
                    }

                    env.SMOKE_PASS              = smokePass.toString()
                    env.SMOKE_FAIL              = smokeFail.toString()
                    env.SMOKE_SKIP              = smokeSkip.toString()
                    env.REGRESSION_PASS         = regressionPass.toString()
                    env.REGRESSION_FAIL         = regressionFail.toString()
                    env.REGRESSION_SKIP         = regressionSkip.toString()
                    env.UNTAGGED_PASS           = untaggedPass.toString()
                    env.UNTAGGED_FAIL           = untaggedFail.toString()
                    env.SMOKE_FAILED_TESTS      = smokeFailedTests.join('||')
                    env.REGRESSION_FAILED_TESTS = regressionFailedTests.join('||')
                    env.UNTAGGED_FAILED_TESTS   = untaggedFailedTests.join('||')

                    def totalPass = smokePass + regressionPass + untaggedPass
                    def totalFail = smokeFail + regressionFail + untaggedFail
                    def totalSkip = smokeSkip + regressionSkip
                    def total     = totalPass + totalFail + totalSkip
                    env.TOTAL_PASS  = totalPass.toString()
                    env.TOTAL_FAIL  = totalFail.toString()
                    env.TOTAL_SKIP  = totalSkip.toString()
                    env.TOTAL_TESTS = total.toString()
                    env.PASS_RATE   = total > 0 ? String.format('%.1f', (totalPass / total) * 100) : '0.0'

                    echo "=== Test Summary ==="
                    echo "Smoke     : ${smokePass} passed / ${smokeFail} failed / ${smokeSkip} skipped"
                    echo "Regression: ${regressionPass} passed / ${regressionFail} failed / ${regressionSkip} skipped"
                    echo "Total     : ${totalPass}/${total} (${env.PASS_RATE}%)"
                }
            }
        }

        // ─────────────────────────────────────────────────────────────
        // PUBLISH ALLURE REPORT
        // ─────────────────────────────────────────────────────────────
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

    // ─────────────────────────────────────────────────────────────
    // POST ACTIONS
    // ─────────────────────────────────────────────────────────────
    post {

        always {

            archiveArtifacts(
                artifacts: 'allure-results/**',
                allowEmptyArchive: true
            )

            bat "docker logout %GHCR_REGISTRY%"
            bat "docker rmi %GHCR_IMAGE%:%IMAGE_TAG% || exit 0"

            script {

                // ── Resolve recipient ─────────────────────────────────
                def recipient  = (params.USER_EMAIL?.trim()) ? params.USER_EMAIL.trim() : env.NOTIFICATION_EMAIL
                def isSuccess  = currentBuild.currentResult == 'SUCCESS'
                def isUnstable = currentBuild.currentResult == 'UNSTABLE'

                def statusColor  = isSuccess ? '#16a34a' : isUnstable ? '#d97706' : '#dc2626'
                def statusBg     = isSuccess ? '#f0fdf4' : isUnstable ? '#fffbeb' : '#fef2f2'
                def statusBorder = isSuccess ? '#bbf7d0' : isUnstable ? '#fde68a' : '#fecaca'
                def statusLabel  = isSuccess ? 'Passed'  : isUnstable ? 'Unstable' : 'Failed'
                def statusEmoji  = isSuccess ? '&#x2714;' : isUnstable ? '&#x26A0;' : '&#x2718;'
                def subjectEmoji = isSuccess ? '✅' : isUnstable ? '⚠️' : '❌'

                // ── Suite block renderer ──────────────────────────────
                def suiteBlock = { suiteName, suiteTag, pass, fail, skip, failedList ->
                    def total = pass + fail + skip
                    def rate  = total > 0 ? String.format('%.0f', (pass / total) * 100) : '0'
                    def barW  = rate.toInteger()

                    def tagColor  = suiteTag == 'SMOKE' ? '#0369a1' : '#6d28d9'
                    def tagBg     = suiteTag == 'SMOKE' ? '#e0f2fe'  : '#ede9fe'
                    def rateColor = barW >= 80 ? '#16a34a' : barW >= 50 ? '#d97706' : '#dc2626'
                    def barColor  = barW >= 80 ? '#16a34a' : barW >= 50 ? '#d97706' : '#dc2626'

                    def failRows = ''
                    if (fail > 0 && failedList) {
                        failRows = failedList.split('\\|\\|').collect { t ->
                            """<tr>
                              <td style="padding:8px 16px;border-bottom:1px solid #f3f4f6;
                                         font-size:12px;color:#374151;font-family:'Courier New',Courier,monospace;">
                                <span style="display:inline-block;width:6px;height:6px;background:#dc2626;
                                             border-radius:50%;margin-right:8px;vertical-align:middle;"></span>${t.trim()}
                              </td>
                            </tr>"""
                        }.join('')
                    }

                    def failSection = fail > 0 ? """
                    <tr>
                      <td style="padding:0 20px 16px;">
                        <p style="margin:0 0 8px;font-size:11px;font-weight:600;color:#6b7280;
                                  text-transform:uppercase;letter-spacing:0.8px;">Failed Tests</p>
                        <table width="100%" cellpadding="0" cellspacing="0"
                               style="background:#fafafa;border:1px solid #e5e7eb;border-radius:6px;overflow:hidden;">
                          ${failRows}
                        </table>
                      </td>
                    </tr>""" : ''

                    return """
                    <table width="100%" cellpadding="0" cellspacing="0"
                           style="background:#ffffff;border:1px solid #e5e7eb;
                                  border-radius:8px;overflow:hidden;margin-bottom:12px;">
                      <tr>
                        <td style="padding:14px 20px;border-bottom:1px solid #f3f4f6;">
                          <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                              <td valign="middle">
                                <span style="display:inline-block;padding:2px 10px;border-radius:4px;
                                             font-size:10px;font-weight:700;letter-spacing:0.8px;
                                             color:${tagColor};background:${tagBg};
                                             margin-right:8px;text-transform:uppercase;">${suiteTag}</span>
                                <span style="font-size:13px;font-weight:600;color:#111827;">${suiteName}</span>
                              </td>
                              <td align="right" valign="middle">
                                <span style="font-size:11px;color:#9ca3af;margin-right:6px;">${total} tests</span>
                                <span style="font-size:14px;font-weight:700;color:${rateColor};">${rate}%</span>
                              </td>
                            </tr>
                          </table>
                        </td>
                      </tr>
                      <tr>
                        <td style="padding:16px 20px;">
                          <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:14px;">
                            <tr>
                              <td width="33%" align="center">
                                <p style="margin:0;font-size:22px;font-weight:700;color:#16a34a;">${pass}</p>
                                <p style="margin:3px 0 0;font-size:11px;color:#6b7280;">Passed</p>
                              </td>
                              <td width="33%" align="center"
                                  style="border-left:1px solid #f3f4f6;border-right:1px solid #f3f4f6;">
                                <p style="margin:0;font-size:22px;font-weight:700;color:#dc2626;">${fail}</p>
                                <p style="margin:3px 0 0;font-size:11px;color:#6b7280;">Failed</p>
                              </td>
                              <td width="33%" align="center">
                                <p style="margin:0;font-size:22px;font-weight:700;color:#d97706;">${skip}</p>
                                <p style="margin:3px 0 0;font-size:11px;color:#6b7280;">Skipped</p>
                              </td>
                            </tr>
                          </table>
                          <div style="background:#f3f4f6;border-radius:999px;height:4px;overflow:hidden;">
                            <div style="width:${barW}%;height:100%;border-radius:999px;background:${barColor};"></div>
                          </div>
                        </td>
                      </tr>
                      ${failSection}
                    </table>"""
                }

                def smokeSection = (params.TEST_SUITE == 'all' || params.TEST_SUITE == 'smoke')
                    ? suiteBlock('Smoke Tests', 'SMOKE',
                        (env.SMOKE_PASS ?: '0').toInteger(),
                        (env.SMOKE_FAIL ?: '0').toInteger(),
                        (env.SMOKE_SKIP ?: '0').toInteger(),
                        env.SMOKE_FAILED_TESTS) : ''

                def regressionSection = (params.TEST_SUITE == 'all' || params.TEST_SUITE == 'regression')
                    ? suiteBlock('Regression Tests', 'REGRESSION',
                        (env.REGRESSION_PASS ?: '0').toInteger(),
                        (env.REGRESSION_FAIL ?: '0').toInteger(),
                        (env.REGRESSION_SKIP ?: '0').toInteger(),
                        env.REGRESSION_FAILED_TESTS) : ''

                def overallBar   = (env.PASS_RATE ?: '0').toDouble().toInteger()
                def overallColor = overallBar >= 80 ? '#16a34a' : overallBar >= 50 ? '#d97706' : '#dc2626'
                def barColor     = overallBar >= 80 ? '#16a34a' : overallBar >= 50 ? '#d97706' : '#dc2626'

                emailext(
                    subject: "[CI/CD] ${subjectEmoji} ${env.JOB_NAME} #${env.BUILD_NUMBER} — ${statusLabel}",
                    mimeType: 'text/html',
                    to: "${recipient}",
                    body: """<!DOCTYPE html>
                    <html lang="en">
                    <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width,initial-scale=1">
                    <title>Pipeline Report</title>
                    </head>
                    <body style="margin:0;padding:0;background:#f3f4f6;
                                font-family:'Segoe UI',Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased;">

                    <table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f4f6;padding:32px 16px 48px;">
                    <tr><td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

                      <!-- ══════════════════════════════════════
                          HEADER
                      ══════════════════════════════════════ -->
                      <tr>
                        <td style="background:#111827;border-radius:10px 10px 0 0;padding:24px 32px;">
                          <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                              <td valign="middle">
                                <p style="margin:0;font-size:11px;font-weight:600;color:#6b7280;
                                          text-transform:uppercase;letter-spacing:1.2px;">CI / CD Pipeline</p>
                                <p style="margin:4px 0 0;font-size:20px;font-weight:700;color:#f9fafb;
                                          letter-spacing:-0.3px;">${env.JOB_NAME}</p>
                              </td>
                              <td align="right" valign="middle">
                                <span style="display:inline-block;padding:5px 14px;border-radius:20px;
                                            font-size:12px;font-weight:700;letter-spacing:0.4px;
                                            background:${statusBg};color:${statusColor};
                                            border:1px solid ${statusBorder};">
                                  ${statusEmoji}&nbsp;&nbsp;${statusLabel}
                                </span>
                              </td>
                            </tr>
                          </table>
                        </td>
                      </tr>

                      <!-- ══════════════════════════════════════
                          BUILD SUMMARY
                      ══════════════════════════════════════ -->
                      <tr>
                        <td style="background:#ffffff;padding:28px 32px 24px;border-left:1px solid #e5e7eb;
                                  border-right:1px solid #e5e7eb;">

                          <p style="margin:0 0 16px;font-size:11px;font-weight:600;color:#9ca3af;
                                    text-transform:uppercase;letter-spacing:1px;">Build Details</p>

                          <table width="100%" cellpadding="0" cellspacing="0"
                                style="border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;">
                            <tr style="background:#f9fafb;">
                              <td style="padding:10px 16px;font-size:12px;color:#6b7280;font-weight:500;
                                        width:38%;border-bottom:1px solid #e5e7eb;">Build Number</td>
                              <td style="padding:10px 16px;font-size:12px;color:#111827;font-weight:600;
                                        border-bottom:1px solid #e5e7eb;">#${env.BUILD_NUMBER}</td>
                            </tr>
                            <tr>
                              <td style="padding:10px 16px;font-size:12px;color:#6b7280;font-weight:500;
                                        border-bottom:1px solid #e5e7eb;">Test Suite</td>
                              <td style="padding:10px 16px;font-size:12px;border-bottom:1px solid #e5e7eb;">
                                <span style="display:inline-block;padding:2px 10px;border-radius:4px;
                                            background:#ede9fe;color:#6d28d9;font-size:11px;
                                            font-weight:700;text-transform:uppercase;
                                            letter-spacing:0.6px;">${params.TEST_SUITE}</span>
                              </td>
                            </tr>
                            <tr style="background:#f9fafb;">
                              <td style="padding:10px 16px;font-size:12px;color:#6b7280;font-weight:500;
                                        border-bottom:1px solid #e5e7eb;">Base URL</td>
                              <td style="padding:10px 16px;font-size:12px;border-bottom:1px solid #e5e7eb;">
                                <a href="${params.BASE_URL}"
                                  style="color:#2563eb;text-decoration:none;">${params.BASE_URL}</a>
                              </td>
                            </tr>
                            <tr>
                              <td style="padding:10px 16px;font-size:12px;color:#6b7280;font-weight:500;">Duration</td>
                              <td style="padding:10px 16px;font-size:12px;color:#111827;">${currentBuild.durationString}</td>
                            </tr>
                          </table>
                        </td>
                      </tr>

                      <!-- ══════════════════════════════════════
                          STAT CARDS
                      ══════════════════════════════════════ -->
                      <tr>
                        <td style="background:#ffffff;padding:0 32px 28px;
                                  border-left:1px solid #e5e7eb;border-right:1px solid #e5e7eb;
                                  border-top:1px solid #f3f4f6;">

                          <p style="margin:0 0 14px;font-size:11px;font-weight:600;color:#9ca3af;
                                    text-transform:uppercase;letter-spacing:1px;">Test Summary</p>

                          <!-- 4 stat cards -->
                          <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:20px;">
                            <tr>
                              <td width="25%" style="padding-right:8px;">
                                <table width="100%" cellpadding="0" cellspacing="0"
                                      style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;">
                                  <tr><td style="padding:16px 8px;text-align:center;">
                                    <p style="margin:0;font-size:26px;font-weight:700;color:#16a34a;line-height:1;">
                                      ${env.TOTAL_PASS ?: '0'}
                                    </p>
                                    <p style="margin:6px 0 0;font-size:11px;color:#6b7280;font-weight:500;">Passed</p>
                                  </td></tr>
                                </table>
                              </td>
                              <td width="25%" style="padding-right:8px;">
                                <table width="100%" cellpadding="0" cellspacing="0"
                                      style="background:#fef2f2;border:1px solid #fecaca;border-radius:8px;">
                                  <tr><td style="padding:16px 8px;text-align:center;">
                                    <p style="margin:0;font-size:26px;font-weight:700;color:#dc2626;line-height:1;">
                                      ${env.TOTAL_FAIL ?: '0'}
                                    </p>
                                    <p style="margin:6px 0 0;font-size:11px;color:#6b7280;font-weight:500;">Failed</p>
                                  </td></tr>
                                </table>
                              </td>
                              <td width="25%" style="padding-right:8px;">
                                <table width="100%" cellpadding="0" cellspacing="0"
                                      style="background:#fffbeb;border:1px solid #fde68a;border-radius:8px;">
                                  <tr><td style="padding:16px 8px;text-align:center;">
                                    <p style="margin:0;font-size:26px;font-weight:700;color:#d97706;line-height:1;">
                                      ${env.TOTAL_SKIP ?: '0'}
                                    </p>
                                    <p style="margin:6px 0 0;font-size:11px;color:#6b7280;font-weight:500;">Skipped</p>
                                  </td></tr>
                                </table>
                              </td>
                              <td width="25%">
                                <table width="100%" cellpadding="0" cellspacing="0"
                                      style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;">
                                  <tr><td style="padding:16px 8px;text-align:center;">
                                    <p style="margin:0;font-size:26px;font-weight:700;color:#2563eb;line-height:1;">
                                      ${env.TOTAL_TESTS ?: '0'}
                                    </p>
                                    <p style="margin:6px 0 0;font-size:11px;color:#6b7280;font-weight:500;">Total</p>
                                  </td></tr>
                                </table>
                              </td>
                            </tr>
                          </table>

                          <!-- Pass rate bar -->
                          <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:8px;">
                            <tr>
                              <td style="font-size:12px;font-weight:500;color:#6b7280;">Pass Rate</td>
                              <td align="right" style="font-size:14px;font-weight:700;color:${overallColor};">
                                ${env.PASS_RATE ?: '0'}%
                              </td>
                            </tr>
                          </table>
                          <div style="background:#e5e7eb;border-radius:999px;height:6px;overflow:hidden;">
                            <div style="width:${overallBar}%;height:100%;border-radius:999px;background:${barColor};"></div>
                          </div>
                        </td>
                      </tr>

                      <!-- ══════════════════════════════════════
                          SUITE RESULTS
                      ══════════════════════════════════════ -->
                      <tr>
                        <td style="background:#f9fafb;padding:24px 32px;
                                  border-left:1px solid #e5e7eb;border-right:1px solid #e5e7eb;
                                  border-top:1px solid #e5e7eb;">

                          <p style="margin:0 0 14px;font-size:11px;font-weight:600;color:#9ca3af;
                                    text-transform:uppercase;letter-spacing:1px;">Results by Suite</p>

                          ${smokeSection}
                          ${regressionSection}
                        </td>
                      </tr>

                      <!-- ══════════════════════════════════════
                          ACTION BUTTONS
                      ══════════════════════════════════════ -->
                      <tr>
                        <td style="background:#ffffff;padding:24px 32px;
                                  border-left:1px solid #e5e7eb;border-right:1px solid #e5e7eb;
                                  border-top:1px solid #e5e7eb;">
                          <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                              <td align="center">
                                <a href="${env.BUILD_URL}" target="_blank"
                                  style="display:inline-block;padding:11px 24px;
                                          background:#111827;color:#f9fafb;
                                          text-decoration:none;font-size:13px;font-weight:600;
                                          border-radius:7px;margin-right:10px;letter-spacing:0.2px;">
                                  View Build
                                </a>
                                <a href="${env.BUILD_URL}allure" target="_blank"
                                  style="display:inline-block;padding:11px 24px;
                                          background:#ffffff;color:#2563eb;
                                          text-decoration:none;font-size:13px;font-weight:600;
                                          border-radius:7px;border:1px solid #2563eb;
                                          letter-spacing:0.2px;">
                                  Allure Report
                                </a>
                              </td>
                            </tr>
                          </table>
                        </td>
                      </tr>

                      <!-- ══════════════════════════════════════
                          FOOTER
                      ══════════════════════════════════════ -->
                      <tr>
                        <td style="background:#f9fafb;border:1px solid #e5e7eb;border-top:none;
                                  border-radius:0 0 10px 10px;padding:16px 32px;">
                          <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                              <td>
                                <p style="margin:0;font-size:11px;color:#9ca3af;">
                                  This is an automated notification from your Jenkins CI pipeline.
                                </p>
                              </td>
                              <td align="right">
                                <p style="margin:0;font-size:11px;color:#9ca3af;">
                                  ${new Date().format('dd MMM yyyy, HH:mm z')}
                                </p>
                              </td>
                            </tr>
                          </table>
                        </td>
                      </tr>

                    </table>
                    </td></tr>
                    </table>
                    </body>
                    </html>"""
                )
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