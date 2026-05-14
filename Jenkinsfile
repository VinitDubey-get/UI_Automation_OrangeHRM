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
                                    def json = readJSON text: content

                                    def status   = json.status  ?: 'unknown'
                                    def testName = json.name    ?: file
                                    def labels   = json.labels  ?: []

                                    def isSmoke      = labels.any { it.name == 'tag' && it.value?.toLowerCase() == 'smoke' }
                                    def isRegression = labels.any { it.name == 'tag' && it.value?.toLowerCase() == 'regression' }

                                    def countFor = { passVar, failVar, skipVar, failList ->
                                        if (status == 'passed')                     passVar++
                                        else if (status in ['failed', 'broken'])  { failVar++; failList << testName }
                                        else if (status == 'skipped')               skipVar++
                                    }

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

                    env.SMOKE_PASS            = smokePass.toString()
                    env.SMOKE_FAIL            = smokeFail.toString()
                    env.SMOKE_SKIP            = smokeSkip.toString()
                    env.REGRESSION_PASS       = regressionPass.toString()
                    env.REGRESSION_FAIL       = regressionFail.toString()
                    env.REGRESSION_SKIP       = regressionSkip.toString()
                    env.UNTAGGED_PASS         = untaggedPass.toString()
                    env.UNTAGGED_FAIL         = untaggedFail.toString()
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
                if (params.USER_EMAIL?.trim()) {

                    // ── Colour tokens driven by build result ──────────────
                    def statusColor   = currentBuild.currentResult == 'SUCCESS'  ? '#1b8a4e' :
                                        currentBuild.currentResult == 'UNSTABLE' ? '#d97706' : '#c0392b'
                    def statusBg      = currentBuild.currentResult == 'SUCCESS'  ? '#f0fdf4' :
                                        currentBuild.currentResult == 'UNSTABLE' ? '#fffbeb' : '#fef2f2'
                    def statusIcon    = currentBuild.currentResult == 'SUCCESS'  ? '✔' :
                                        currentBuild.currentResult == 'UNSTABLE' ? '⚠' : '✖'
                    def statusLabel   = currentBuild.currentResult == 'SUCCESS'  ? 'Build Passed' :
                                        currentBuild.currentResult == 'UNSTABLE' ? 'Build Unstable' : 'Build Failed'

                    // ── Helper: render one suite results block ────────────
                    def suiteBlock = { suiteName, pass, fail, skip, failedList ->
                        def total  = pass + fail + skip
                        def rate   = total > 0 ? String.format('%.0f', (pass / total) * 100) : '0'
                        def barW   = rate.toInteger()
                        def failHtml = ''
                        if (fail > 0 && failedList) {
                            def rows = failedList.split('\\|\\|').collect { t ->
                                """<tr>
                                     <td style="padding:7px 10px;border-bottom:1px solid #f1f1f1;font-size:13px;color:#374151;">
                                       <span style="display:inline-block;width:7px;height:7px;border-radius:50%;
                                                    background:#e53e3e;margin-right:8px;vertical-align:middle;"></span>${t.trim()}
                                     </td>
                                   </tr>"""
                            }.join('')
                            failHtml = """
                            <div style="margin-top:10px;">
                              <p style="margin:0 0 6px;font-size:12px;font-weight:600;color:#6b7280;
                                        text-transform:uppercase;letter-spacing:.6px;">Failed test cases</p>
                              <table style="width:100%;border-collapse:collapse;border:1px solid #f1f1f1;border-radius:6px;overflow:hidden;">
                                ${rows}
                              </table>
                            </div>"""
                        }
                        return """
                        <div style="margin-bottom:16px;border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;">
                          <div style="display:flex;justify-content:space-between;align-items:center;
                                      padding:10px 14px;background:#f9fafb;border-bottom:1px solid #e5e7eb;">
                            <span style="font-size:13px;font-weight:600;color:#111827;">${suiteName}</span>
                            <span style="font-size:12px;color:#6b7280;">${total} tests &nbsp;|&nbsp; ${rate}% passed</span>
                          </div>
                          <div style="padding:12px 14px;">
                            <div style="display:flex;gap:16px;margin-bottom:10px;">
                              <span style="font-size:13px;color:#1b8a4e;">
                                <b style="font-size:18px;">${pass}</b> passed
                              </span>
                              <span style="font-size:13px;color:#c0392b;">
                                <b style="font-size:18px;">${fail}</b> failed
                              </span>
                              <span style="font-size:13px;color:#6b7280;">
                                <b style="font-size:18px;">${skip}</b> skipped
                              </span>
                            </div>
                            <div style="background:#e5e7eb;border-radius:999px;height:6px;overflow:hidden;">
                              <div style="width:${barW}%;height:100%;background:#1b8a4e;border-radius:999px;"></div>
                            </div>
                            ${failHtml}
                          </div>
                        </div>"""
                    }

                    def smokeSection      = (params.TEST_SUITE == 'all' || params.TEST_SUITE == 'smoke')
                        ? suiteBlock('Smoke Tests',
                            (env.SMOKE_PASS ?: '0').toInteger(),
                            (env.SMOKE_FAIL ?: '0').toInteger(),
                            (env.SMOKE_SKIP ?: '0').toInteger(),
                            env.SMOKE_FAILED_TESTS)
                        : ''

                    def regressionSection = (params.TEST_SUITE == 'all' || params.TEST_SUITE == 'regression')
                        ? suiteBlock('Regression Tests',
                            (env.REGRESSION_PASS ?: '0').toInteger(),
                            (env.REGRESSION_FAIL ?: '0').toInteger(),
                            (env.REGRESSION_SKIP ?: '0').toInteger(),
                            env.REGRESSION_FAILED_TESTS)
                        : ''

                    def overallBar = (env.PASS_RATE ?: '0').toDouble().toInteger()

                    emailext(
                        subject: "[Jenkins] ${statusIcon} ${env.JOB_NAME} › Build #${env.BUILD_NUMBER} — ${currentBuild.currentResult}",
                        mimeType: 'text/html',
                        to: "${params.USER_EMAIL}",
                        body: """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Jenkins Build Report</title>
</head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:'Segoe UI',Arial,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f4f6;padding:32px 0;">
<tr><td align="center">
<table width="640" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%;">

  <!-- ── HEADER ───────────────────────────────────────────────── -->
  <tr>
    <td style="background:#1b1f23;border-radius:10px 10px 0 0;padding:22px 32px;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td>
            <!-- Jenkins wordmark (SVG inline, no external fetch) -->
            <svg width="110" height="28" viewBox="0 0 110 28" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="28" height="28" rx="5" fill="#D33833"/>
              <text x="14" y="20" font-size="14" font-weight="bold" text-anchor="middle" fill="white" font-family="Arial">J</text>
              <text x="38" y="20" font-size="15" font-weight="600" fill="#ffffff" font-family="Arial,sans-serif">Jenkins</text>
            </svg>
          </td>
          <td align="right">
            <span style="font-size:11px;color:#8b949e;letter-spacing:.4px;">CI / CD PIPELINE</span>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- ── STATUS BANNER ─────────────────────────────────────────── -->
  <tr>
    <td style="background:${statusBg};border-left:4px solid ${statusColor};padding:18px 32px;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td>
            <p style="margin:0;font-size:20px;font-weight:700;color:${statusColor};">
              ${statusIcon}&nbsp; ${statusLabel}
            </p>
            <p style="margin:4px 0 0;font-size:13px;color:#6b7280;">
              ${env.JOB_NAME} &nbsp;›&nbsp; Build <b>#${env.BUILD_NUMBER}</b>
              &nbsp;·&nbsp; ${new Date().format('dd MMM yyyy, HH:mm z')}
            </p>
          </td>
          <td align="right" valign="middle">
            <a href="${env.BUILD_URL}" target="_blank"
               style="display:inline-block;padding:9px 18px;background:${statusColor};
                      color:#ffffff;text-decoration:none;font-size:12px;font-weight:600;
                      border-radius:6px;letter-spacing:.3px;">
              View Build
            </a>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- ── BODY ──────────────────────────────────────────────────── -->
  <tr>
    <td style="background:#ffffff;padding:28px 32px;">

      <!-- Build metadata -->
      <p style="margin:0 0 16px;font-size:11px;font-weight:700;color:#9ca3af;
                text-transform:uppercase;letter-spacing:.8px;">Build Details</p>

      <table width="100%" cellpadding="0" cellspacing="0"
             style="border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;margin-bottom:28px;">
        <tr style="background:#f9fafb;">
          <td style="padding:10px 14px;font-size:12px;font-weight:600;color:#6b7280;
                     text-transform:uppercase;letter-spacing:.5px;width:38%;">Field</td>
          <td style="padding:10px 14px;font-size:12px;font-weight:600;color:#6b7280;
                     text-transform:uppercase;letter-spacing:.5px;">Value</td>
        </tr>
        <tr><td style="padding:9px 14px;border-top:1px solid #f1f1f1;font-size:13px;color:#6b7280;">Job Name</td>
            <td style="padding:9px 14px;border-top:1px solid #f1f1f1;font-size:13px;color:#111827;font-weight:500;">${env.JOB_NAME}</td></tr>
        <tr style="background:#fafafa;">
            <td style="padding:9px 14px;border-top:1px solid #f1f1f1;font-size:13px;color:#6b7280;">Build Number</td>
            <td style="padding:9px 14px;border-top:1px solid #f1f1f1;font-size:13px;color:#111827;font-weight:500;">#${env.BUILD_NUMBER}</td></tr>
        <tr><td style="padding:9px 14px;border-top:1px solid #f1f1f1;font-size:13px;color:#6b7280;">Test Suite</td>
            <td style="padding:9px 14px;border-top:1px solid #f1f1f1;font-size:13px;color:#111827;font-weight:500;">${params.TEST_SUITE}</td></tr>
        <tr style="background:#fafafa;">
            <td style="padding:9px 14px;border-top:1px solid #f1f1f1;font-size:13px;color:#6b7280;">Base URL</td>
            <td style="padding:9px 14px;border-top:1px solid #f1f1f1;font-size:13px;color:#111827;font-weight:500;">${params.BASE_URL}</td></tr>
        <tr><td style="padding:9px 14px;border-top:1px solid #f1f1f1;font-size:13px;color:#6b7280;">Duration</td>
            <td style="padding:9px 14px;border-top:1px solid #f1f1f1;font-size:13px;color:#111827;font-weight:500;">${currentBuild.durationString}</td></tr>
        <tr style="background:#fafafa;">
            <td style="padding:9px 14px;border-top:1px solid #f1f1f1;font-size:13px;color:#6b7280;">Status</td>
            <td style="padding:9px 14px;border-top:1px solid #f1f1f1;font-size:13px;">
              <span style="display:inline-block;padding:3px 10px;border-radius:999px;font-size:12px;
                           font-weight:600;background:${statusBg};color:${statusColor};">
                ${currentBuild.currentResult}
              </span>
            </td></tr>
      </table>

      <!-- Overall summary cards -->
      <p style="margin:0 0 12px;font-size:11px;font-weight:700;color:#9ca3af;
                text-transform:uppercase;letter-spacing:.8px;">Overall Summary</p>

      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:10px;">
        <tr>
          <td width="24%" style="padding-right:8px;">
            <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:14px;text-align:center;">
              <p style="margin:0;font-size:24px;font-weight:700;color:#1b8a4e;">${env.TOTAL_PASS ?: '0'}</p>
              <p style="margin:4px 0 0;font-size:11px;color:#1b8a4e;font-weight:600;text-transform:uppercase;letter-spacing:.5px;">Passed</p>
            </div>
          </td>
          <td width="24%" style="padding-right:8px;">
            <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:14px;text-align:center;">
              <p style="margin:0;font-size:24px;font-weight:700;color:#c0392b;">${env.TOTAL_FAIL ?: '0'}</p>
              <p style="margin:4px 0 0;font-size:11px;color:#c0392b;font-weight:600;text-transform:uppercase;letter-spacing:.5px;">Failed</p>
            </div>
          </td>
          <td width="24%" style="padding-right:8px;">
            <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:14px;text-align:center;">
              <p style="margin:0;font-size:24px;font-weight:700;color:#d97706;">${env.TOTAL_SKIP ?: '0'}</p>
              <p style="margin:4px 0 0;font-size:11px;color:#d97706;font-weight:600;text-transform:uppercase;letter-spacing:.5px;">Skipped</p>
            </div>
          </td>
          <td width="24%">
            <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:14px;text-align:center;">
              <p style="margin:0;font-size:24px;font-weight:700;color:#1d4ed8;">${env.TOTAL_TESTS ?: '0'}</p>
              <p style="margin:4px 0 0;font-size:11px;color:#1d4ed8;font-weight:600;text-transform:uppercase;letter-spacing:.5px;">Total</p>
            </div>
          </td>
        </tr>
      </table>

      <!-- Pass-rate bar -->
      <div style="margin:14px 0 28px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
          <span style="font-size:12px;color:#6b7280;">Pass rate</span>
          <span style="font-size:12px;font-weight:600;color:#111827;">${env.PASS_RATE ?: '0'}%</span>
        </div>
        <div style="background:#e5e7eb;border-radius:999px;height:8px;overflow:hidden;">
          <div style="width:${overallBar}%;height:100%;background:#1b8a4e;border-radius:999px;"></div>
        </div>
      </div>

      <!-- Per-suite results -->
      <p style="margin:0 0 12px;font-size:11px;font-weight:700;color:#9ca3af;
                text-transform:uppercase;letter-spacing:.8px;">Results by Suite</p>

      ${smokeSection}
      ${regressionSection}

      <!-- CTA buttons -->
      <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:28px;">
        <tr>
          <td align="center">
            <a href="${env.BUILD_URL}" target="_blank"
               style="display:inline-block;padding:11px 24px;background:#1b1f23;color:#ffffff;
                      text-decoration:none;font-size:13px;font-weight:600;border-radius:7px;
                      margin-right:10px;">
              🔍 View Console Log
            </a>
            <a href="${env.BUILD_URL}allure" target="_blank"
               style="display:inline-block;padding:11px 24px;background:#6366f1;color:#ffffff;
                      text-decoration:none;font-size:13px;font-weight:600;border-radius:7px;">
              📊 Open Allure Report
            </a>
          </td>
        </tr>
      </table>

    </td>
  </tr>

  <!-- ── FOOTER ─────────────────────────────────────────────────── -->
  <tr>
    <td style="background:#1b1f23;border-radius:0 0 10px 10px;padding:16px 32px;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td>
            <p style="margin:0;font-size:11px;color:#8b949e;">
              Generated by <b style="color:#d1d5db;">Jenkins CI</b>
              &nbsp;·&nbsp; ${env.JOB_NAME} #${env.BUILD_NUMBER}
            </p>
          </td>
          <td align="right">
            <p style="margin:0;font-size:11px;color:#8b949e;">
              <a href="${env.BUILD_URL}" style="color:#8b949e;">Unsubscribe</a>
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