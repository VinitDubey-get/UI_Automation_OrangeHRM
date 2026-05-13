# ─────────────────────────────────────────────────────────────
# Base Playwright Image
# ─────────────────────────────────────────────────────────────
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

# Install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Runtime environment variables
ENV BASE_URL=https://practice.expandtesting.com \
    HEADLESS=true \
    SLOW_MO=0 \
    DEFAULT_TIMEOUT=15000 \
    APP_USERNAME=practice \
    APP_PASSWORD=SuperSecretPassword! \
    PYTHONUNBUFFERED=1

# Allure output directory
RUN mkdir -p /app/allure-results

# Volume mount
VOLUME ["/app/allure-results"]

# Default pytest entrypoint
ENTRYPOINT ["pytest"]

CMD ["tests/", "-m", "smoke or regression", "--alluredir=/app/allure-results"]