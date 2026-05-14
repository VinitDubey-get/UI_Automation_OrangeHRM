pipeline {

    agent any

    environment {
        GHCR_REGISTRY = 'ghcr.io'
        GHCR_IMAGE    = 'ghcr.io/vinitdubey-get/ui_automation_orangehrm'
        IMAGE_TAG     = 'latest'
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
                if (params.USER_EMAIL?.trim()) {

                    // ── Status theming ────────────────────────────────────
                    def isSuccess  = currentBuild.currentResult == 'SUCCESS'
                    def isUnstable = currentBuild.currentResult == 'UNSTABLE'

                    def statusColor  = isSuccess  ? '#22c55e' : isUnstable ? '#f59e0b' : '#ef4444'
                    def statusDark   = isSuccess  ? '#16a34a' : isUnstable ? '#d97706' : '#dc2626'
                    def statusBg     = isSuccess  ? '#052e16' : isUnstable ? '#1c1007' : '#1a0505'
                    def statusBorder = isSuccess  ? '#166534' : isUnstable ? '#92400e' : '#7f1d1d'
                    def statusGlow   = isSuccess  ? 'rgba(34,197,94,0.20)'  : isUnstable ? 'rgba(245,158,11,0.20)'  : 'rgba(239,68,68,0.20)'
                    def statusIcon   = isSuccess  ? '&#10003;' : isUnstable ? '&#9888;' : '&#10005;'
                    def statusLabel  = isSuccess  ? 'BUILD PASSED' : isUnstable ? 'BUILD UNSTABLE' : 'BUILD FAILED'
                    def statusEmoji  = isSuccess  ? '🟢' : isUnstable ? '🟡' : '🔴'

                    // ── Suite block renderer ──────────────────────────────
                    def suiteBlock = { suiteName, suiteTag, pass, fail, skip, failedList ->
                        def total = pass + fail + skip
                        def rate  = total > 0 ? String.format('%.0f', (pass / total) * 100) : '0'
                        def barW  = rate.toInteger()
                        def tagColor = suiteTag == 'SMOKE' ? '#38bdf8' : '#a78bfa'
                        def tagBg    = suiteTag == 'SMOKE' ? 'rgba(56,189,248,0.10)' : 'rgba(167,139,250,0.10)'
                        def tagBorder= suiteTag == 'SMOKE' ? '#0e7490' : '#6d28d9'
                        def barColor = barW >= 80 ? '#16a34a,#22c55e' : barW >= 50 ? '#d97706,#f59e0b' : '#dc2626,#ef4444'
                        def rateColor= barW >= 80 ? '#22c55e' : barW >= 50 ? '#f59e0b' : '#ef4444'

                        def failRows = ''
                        if (fail > 0 && failedList) {
                            failRows = failedList.split('\\|\\|').collect { t ->
                                """<tr>
                                  <td style="padding:9px 14px 9px 34px;border-bottom:1px solid #0f172a;
                                             font-size:12px;color:#94a3b8;font-family:'Courier New',Courier,monospace;
                                             position:relative;">
                                    <span style="position:absolute;left:14px;top:12px;
                                                 width:6px;height:6px;background:#ef4444;
                                                 border-radius:50%;display:inline-block;"></span>
                                    ${t.trim()}
                                  </td>
                                </tr>"""
                            }.join('')
                        }

                        def failSection = fail > 0 ? """
                        <tr>
                          <td style="padding:0 14px 14px;">
                            <p style="margin:0 0 7px;font-size:10px;font-weight:700;color:#475569;
                                      text-transform:uppercase;letter-spacing:1px;">Failed Test Cases</p>
                            <table width="100%" cellpadding="0" cellspacing="0"
                                   style="background:#060a10;border:1px solid #1e293b;
                                          border-radius:6px;overflow:hidden;">
                              ${failRows}
                            </table>
                          </td>
                        </tr>""" : ''

                        return """
                        <table width="100%" cellpadding="0" cellspacing="0"
                               style="background:#0d1117;border:1px solid #1e293b;
                                      border-radius:10px;overflow:hidden;margin-bottom:12px;">
                          <tr>
                            <td style="padding:12px 14px;border-bottom:1px solid #1e293b;
                                       background:linear-gradient(135deg,#0d1117 0%,#111827 100%);">
                              <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                  <td valign="middle">
                                    <span style="display:inline-block;padding:2px 9px;border-radius:4px;
                                                 font-size:10px;font-weight:700;letter-spacing:1px;
                                                 color:${tagColor};background:${tagBg};
                                                 border:1px solid ${tagBorder};margin-right:8px;">${suiteTag}</span>
                                    <span style="font-size:13px;font-weight:600;color:#e2e8f0;">${suiteName}</span>
                                  </td>
                                  <td align="right" valign="middle">
                                    <span style="font-size:11px;color:#475569;margin-right:8px;">${total} tests</span>
                                    <span style="font-size:15px;font-weight:800;color:${rateColor};">${rate}%</span>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                          <tr>
                            <td style="padding:14px;">
                              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:12px;">
                                <tr>
                                  <td width="33%" align="center" style="border-right:1px solid #1e293b;padding:6px 0;">
                                    <p style="margin:0;font-size:24px;font-weight:800;color:#22c55e;">${pass}</p>
                                    <p style="margin:3px 0 0;font-size:10px;color:#16a34a;text-transform:uppercase;letter-spacing:.8px;">Passed</p>
                                  </td>
                                  <td width="33%" align="center" style="border-right:1px solid #1e293b;padding:6px 0;">
                                    <p style="margin:0;font-size:24px;font-weight:800;color:#ef4444;">${fail}</p>
                                    <p style="margin:3px 0 0;font-size:10px;color:#dc2626;text-transform:uppercase;letter-spacing:.8px;">Failed</p>
                                  </td>
                                  <td width="33%" align="center" style="padding:6px 0;">
                                    <p style="margin:0;font-size:24px;font-weight:800;color:#f59e0b;">${skip}</p>
                                    <p style="margin:3px 0 0;font-size:10px;color:#d97706;text-transform:uppercase;letter-spacing:.8px;">Skipped</p>
                                  </td>
                                </tr>
                              </table>
                              <div style="background:#0f172a;border-radius:999px;height:5px;
                                          overflow:hidden;border:1px solid #1e293b;">
                                <div style="width:${barW}%;height:100%;border-radius:999px;
                                            background:linear-gradient(90deg,${barColor});"></div>
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

                    def overallBar     = (env.PASS_RATE ?: '0').toDouble().toInteger()
                    def overallColor   = overallBar >= 80 ? '#22c55e' : overallBar >= 50 ? '#f59e0b' : '#ef4444'
                    def barGradient    = overallBar >= 80 ? '#16a34a,#22c55e' : overallBar >= 50 ? '#d97706,#f59e0b' : '#dc2626,#ef4444'

                    emailext(
                        subject: "[Jenkins] ${statusEmoji} ${env.JOB_NAME} #${env.BUILD_NUMBER} — ${currentBuild.currentResult}",
                        mimeType: 'text/html',
                        to: "${params.USER_EMAIL}",
                        body: """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Jenkins Build Report</title>
</head>
<body style="margin:0;padding:0;background:#060a10;font-family:'Segoe UI',system-ui,Arial,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0"
       style="background:#060a10;min-height:100vh;padding:28px 0 40px;">
<tr><td align="center">
<table width="620" cellpadding="0" cellspacing="0" style="max-width:620px;width:100%;">

  <!-- ═══════════ HEADER ═══════════ -->
  <tr>
    <td style="background:linear-gradient(160deg,#0d1117 0%,#161b22 100%);
               border-radius:14px 14px 0 0;
               border:1px solid #21262d;border-bottom:none;
               padding:20px 28px;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td valign="middle">
            <table cellpadding="0" cellspacing="0">
              <tr>
                <td valign="middle" style="padding-right:12px;">
                  <!-- Jenkins Butler SVG — inline, no external request -->
                  <svg width="44" height="50" viewBox="0 0 44 50" xmlns="http://www.w3.org/2000/svg">
                    <!-- Outer head shape -->
                    <ellipse cx="22" cy="20" rx="17" ry="18" fill="#f0d9b5"/>
                    <ellipse cx="22" cy="20" rx="17" ry="18" fill="none" stroke="#c9a96a" stroke-width="1"/>
                    <!-- Hair mass -->
                    <ellipse cx="22" cy="5"  rx="12" ry="6"  fill="#2d1a0e"/>
                    <ellipse cx="6"  cy="17" rx="4"  rx2="4" ry="8" fill="#2d1a0e"/>
                    <ellipse cx="6"  cy="17" rx="4"  ry="8"  fill="#2d1a0e"/>
                    <ellipse cx="38" cy="17" rx="4"  ry="8"  fill="#2d1a0e"/>
                    <!-- Ears -->
                    <ellipse cx="5"  cy="20" rx="3" ry="4" fill="#e8c99a"/>
                    <ellipse cx="39" cy="20" rx="3" ry="4" fill="#e8c99a"/>
                    <!-- Eyes -->
                    <circle cx="15" cy="18" r="2.8" fill="#1a0f00"/>
                    <circle cx="29" cy="18" r="2.8" fill="#1a0f00"/>
                    <circle cx="16" cy="17" r="0.9" fill="white"/>
                    <circle cx="30" cy="17" r="0.9" fill="white"/>
                    <!-- Nose -->
                    <ellipse cx="22" cy="23" rx="2.2" ry="1.4" fill="#c8a060"/>
                    <!-- Moustache -->
                    <path d="M15 25.5 Q19 28 22 25.5 Q25 28 29 25.5"
                          fill="none" stroke="#2d1a0e" stroke-width="2" stroke-linecap="round"/>
                    <!-- Smile -->
                    <path d="M16 28 Q22 33 28 28"
                          fill="none" stroke="#9b6b3a" stroke-width="1.5" stroke-linecap="round"/>
                    <!-- Jacket body -->
                    <rect x="8" y="35" width="28" height="14" rx="5" fill="#cc3d2a"/>
                    <!-- Lapels -->
                    <polygon points="14,35 22,35 17,43" fill="white"/>
                    <polygon points="30,35 22,35 27,43" fill="white"/>
                    <!-- Tie -->
                    <polygon points="22,35 20,40 22,49 24,40" fill="#111827"/>
                    <!-- Buttons -->
                    <circle cx="22" cy="37" r="1.1" fill="#f0f0f0"/>
                    <circle cx="22" cy="40" r="1.1" fill="#f0f0f0"/>
                  </svg>
                </td>
                <td valign="middle">
                  <p style="margin:0;font-size:22px;font-weight:800;color:#f0f6fc;
                             letter-spacing:-.4px;">Jenkins</p>
                  <p style="margin:2px 0 0;font-size:10px;color:#3d5a6e;
                             text-transform:uppercase;letter-spacing:1.8px;">CI / CD Pipeline</p>
                </td>
              </tr>
            </table>
          </td>
          <td align="right" valign="middle">
            <p style="margin:0;font-size:12px;color:#3d5a6e;line-height:1.8;">
              ${new Date().format('dd MMM yyyy')}<br>
              <span style="color:#2a3f50;">${new Date().format('HH:mm z')}</span>
            </p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- ═══════════ STATUS BANNER ═══════════ -->
  <tr>
    <td style="background:${statusBg};
               border-left:1px solid ${statusBorder};
               border-right:1px solid ${statusBorder};
               padding:20px 28px;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td valign="middle">
            <table cellpadding="0" cellspacing="0">
              <tr>
                <td style="padding-right:14px;">
                  <div style="width:48px;height:48px;border-radius:50%;
                              background:${statusGlow};
                              border:2px solid ${statusColor};
                              text-align:center;line-height:44px;
                              font-size:22px;font-weight:900;color:${statusColor};">
                    ${statusIcon}
                  </div>
                </td>
                <td>
                  <p style="margin:0;font-size:17px;font-weight:800;
                             color:${statusColor};letter-spacing:.8px;
                             text-transform:uppercase;">${statusLabel}</p>
                  <p style="margin:4px 0 0;font-size:12px;color:#4a6178;">
                    <span style="color:#7a9ab5;">${env.JOB_NAME}</span>
                    &nbsp;<span style="color:#2a3f50;">&#8250;</span>&nbsp;
                    <span style="color:#c9d7e2;font-weight:700;">Build #${env.BUILD_NUMBER}</span>
                  </p>
                </td>
              </tr>
            </table>
          </td>
          <td align="right" valign="middle">
            <a href="${env.BUILD_URL}" target="_blank"
               style="display:inline-block;padding:11px 22px;
                      background:${statusColor};color:#000;
                      text-decoration:none;font-size:12px;font-weight:800;
                      border-radius:8px;letter-spacing:.5px;white-space:nowrap;">
              View Build &#8594;
            </a>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- ═══════════ BODY ═══════════ -->
  <tr>
    <td style="background:#0d1117;
               border:1px solid #21262d;
               border-top:none;border-bottom:none;
               padding:24px 28px;">

      <!-- Build Details label -->
      <p style="margin:0 0 10px;font-size:10px;font-weight:700;color:#3d5a6e;
                text-transform:uppercase;letter-spacing:1.5px;">Build Details</p>

      <!-- Metadata table -->
      <table width="100%" cellpadding="0" cellspacing="0"
             style="background:#080c12;border:1px solid #1e293b;
                    border-radius:10px;overflow:hidden;margin-bottom:24px;">
        <tr style="background:#0a0f18;">
          <td style="padding:9px 16px;font-size:10px;font-weight:700;color:#3d5a6e;
                     text-transform:uppercase;letter-spacing:1px;width:36%;
                     border-bottom:1px solid #1a2332;">Field</td>
          <td style="padding:9px 16px;font-size:10px;font-weight:700;color:#3d5a6e;
                     text-transform:uppercase;letter-spacing:1px;
                     border-bottom:1px solid #1a2332;">Value</td>
        </tr>
        <tr>
          <td style="padding:10px 16px;font-size:12px;color:#4a6178;border-bottom:1px solid #0f172a;">Job Name</td>
          <td style="padding:10px 16px;font-size:12px;color:#c9d7e2;font-weight:500;border-bottom:1px solid #0f172a;">${env.JOB_NAME}</td>
        </tr>
        <tr style="background:#080e18;">
          <td style="padding:10px 16px;font-size:12px;color:#4a6178;border-bottom:1px solid #0f172a;">Build Number</td>
          <td style="padding:10px 16px;font-size:12px;border-bottom:1px solid #0f172a;">
            <span style="background:#0f1d2e;color:#7dd3fc;padding:2px 9px;
                         border-radius:4px;font-weight:700;border:1px solid #1e3a5f;">#${env.BUILD_NUMBER}</span>
          </td>
        </tr>
        <tr>
          <td style="padding:10px 16px;font-size:12px;color:#4a6178;border-bottom:1px solid #0f172a;">Test Suite</td>
          <td style="padding:10px 16px;font-size:12px;border-bottom:1px solid #0f172a;">
            <span style="background:#1a1030;color:#a78bfa;padding:2px 9px;
                         border-radius:4px;font-weight:700;text-transform:uppercase;font-size:11px;
                         border:1px solid #4c1d95;">${params.TEST_SUITE}</span>
          </td>
        </tr>
        <tr style="background:#080e18;">
          <td style="padding:10px 16px;font-size:12px;color:#4a6178;border-bottom:1px solid #0f172a;">Base URL</td>
          <td style="padding:10px 16px;font-size:12px;border-bottom:1px solid #0f172a;">
            <a href="${params.BASE_URL}" style="color:#38bdf8;text-decoration:none;">${params.BASE_URL}</a>
          </td>
        </tr>
        <tr>
          <td style="padding:10px 16px;font-size:12px;color:#4a6178;border-bottom:1px solid #0f172a;">Duration</td>
          <td style="padding:10px 16px;font-size:12px;color:#c9d7e2;border-bottom:1px solid #0f172a;">${currentBuild.durationString}</td>
        </tr>
        <tr style="background:#080e18;">
          <td style="padding:10px 16px;font-size:12px;color:#4a6178;">Status</td>
          <td style="padding:10px 16px;">
            <span style="display:inline-block;padding:3px 13px;border-radius:20px;
                         font-size:11px;font-weight:700;letter-spacing:.6px;
                         background:${statusGlow};color:${statusColor};
                         border:1px solid ${statusDark};">
              ${currentBuild.currentResult}
            </span>
          </td>
        </tr>
      </table>

      <!-- Overall Summary label -->
      <p style="margin:0 0 10px;font-size:10px;font-weight:700;color:#3d5a6e;
                text-transform:uppercase;letter-spacing:1.5px;">Overall Summary</p>

      <!-- Stat cards -->
      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:14px;">
        <tr>
          <td width="25%" style="padding-right:7px;">
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="background:#071a0f;border:1px solid #166534;border-radius:10px;">
              <tr><td style="padding:14px 8px;text-align:center;">
                <p style="margin:0;font-size:28px;font-weight:900;color:#22c55e;">${env.TOTAL_PASS ?: '0'}</p>
                <p style="margin:5px 0 0;font-size:10px;color:#16a34a;font-weight:700;
                           text-transform:uppercase;letter-spacing:1px;">Passed</p>
              </td></tr>
            </table>
          </td>
          <td width="25%" style="padding-right:7px;">
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="background:#1a0505;border:1px solid #7f1d1d;border-radius:10px;">
              <tr><td style="padding:14px 8px;text-align:center;">
                <p style="margin:0;font-size:28px;font-weight:900;color:#ef4444;">${env.TOTAL_FAIL ?: '0'}</p>
                <p style="margin:5px 0 0;font-size:10px;color:#dc2626;font-weight:700;
                           text-transform:uppercase;letter-spacing:1px;">Failed</p>
              </td></tr>
            </table>
          </td>
          <td width="25%" style="padding-right:7px;">
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="background:#1c1007;border:1px solid #92400e;border-radius:10px;">
              <tr><td style="padding:14px 8px;text-align:center;">
                <p style="margin:0;font-size:28px;font-weight:900;color:#f59e0b;">${env.TOTAL_SKIP ?: '0'}</p>
                <p style="margin:5px 0 0;font-size:10px;color:#d97706;font-weight:700;
                           text-transform:uppercase;letter-spacing:1px;">Skipped</p>
              </td></tr>
            </table>
          </td>
          <td width="25%">
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="background:#080f1f;border:1px solid #1e3a7f;border-radius:10px;">
              <tr><td style="padding:14px 8px;text-align:center;">
                <p style="margin:0;font-size:28px;font-weight:900;color:#60a5fa;">${env.TOTAL_TESTS ?: '0'}</p>
                <p style="margin:5px 0 0;font-size:10px;color:#3b82f6;font-weight:700;
                           text-transform:uppercase;letter-spacing:1px;">Total</p>
              </td></tr>
            </table>
          </td>
        </tr>
      </table>

      <!-- Pass-rate bar -->
      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:26px;">
        <tr>
          <td style="padding-bottom:7px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="font-size:11px;color:#4a6178;text-transform:uppercase;
                           letter-spacing:1px;">Pass Rate</td>
                <td align="right" style="font-size:15px;font-weight:900;color:${overallColor};">
                  ${env.PASS_RATE ?: '0'}%
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td>
            <div style="background:#0f172a;border-radius:999px;height:7px;
                        overflow:hidden;border:1px solid #1e293b;">
              <div style="width:${overallBar}%;height:100%;border-radius:999px;
                          background:linear-gradient(90deg,${barGradient});"></div>
            </div>
          </td>
        </tr>
      </table>

      <!-- Results by Suite label -->
      <p style="margin:0 0 10px;font-size:10px;font-weight:700;color:#3d5a6e;
                text-transform:uppercase;letter-spacing:1.5px;">Results by Suite</p>

      ${smokeSection}
      ${regressionSection}

      <!-- CTA buttons -->
      <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:22px;">
        <tr>
          <td align="center">
            <a href="${env.BUILD_URL}" target="_blank"
               style="display:inline-block;padding:12px 26px;
                      background:linear-gradient(135deg,#1e293b,#0f172a);
                      color:#e2e8f0;text-decoration:none;font-size:13px;font-weight:700;
                      border-radius:8px;border:1px solid #334155;
                      margin-right:10px;letter-spacing:.3px;">
              &#128269; Console Log
            </a>
            <a href="${env.BUILD_URL}allure" target="_blank"
               style="display:inline-block;padding:12px 26px;
                      background:linear-gradient(135deg,#2e1065,#1e1b4b);
                      color:#c4b5fd;text-decoration:none;font-size:13px;font-weight:700;
                      border-radius:8px;border:1px solid #4c1d95;
                      letter-spacing:.3px;">
              &#128202; Allure Report
            </a>
          </td>
        </tr>
      </table>

    </td>
  </tr>

  <!-- ═══════════ FOOTER ═══════════ -->
  <tr>
    <td style="background:#080c12;
               border:1px solid #21262d;border-top:1px solid #1e293b;
               border-radius:0 0 14px 14px;
               padding:14px 28px;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td>
            <p style="margin:0;font-size:11px;color:#2a3f50;">
              Generated by
              <span style="color:#3d5a6e;font-weight:600;">Jenkins CI</span>
              &nbsp;&#183;&nbsp;
              ${env.JOB_NAME}
              <span style="color:#2a3f50;"> #${env.BUILD_NUMBER}</span>
            </p>
          </td>
          <td align="right">
            <a href="${env.BUILD_URL}"
               style="font-size:11px;color:#2a3f50;text-decoration:none;">
              Unsubscribe
            </a>
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