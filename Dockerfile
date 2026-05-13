# ─────────────────────────────────────────────────────────────────────────────
# Base: official Playwright image — Chromium + all OS deps pre-installed
# ─────────────────────────────────────────────────────────────────────────────
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

# Install Python dependencies first (cached layer — only re-runs on requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Non-root user for security
RUN useradd -ms /bin/bash testrunner

# Copy project source with correct ownership
COPY --chown=testrunner:testrunner . .

# Switch to non-root user
USER testrunner

# ─────────────────────────────────────────────────────────────────────────────
# Runtime defaults — all overridable via docker run -e
# ─────────────────────────────────────────────────────────────────────────────
ENV BASE_URL=https://practice.expandtesting.com \
    HEADLESS=true \
    SLOW_MO=0 \
    DEFAULT_TIMEOUT=15000 \
    APP_USERNAME=practice \
    APP_PASSWORD=SuperSecretPassword! \
    PYTHONUNBUFFERED=1

# Allure results volume mount point
VOLUME ["/app/allure-results"]

# pytest as entrypoint — CMD is overridable at docker run time
ENTRYPOINT ["pytest"]
CMD ["tests/", "-m", "smoke or regression", "--alluredir=allure-results"]