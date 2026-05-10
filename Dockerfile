# Official Playwright python image with chromium -pre installed
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for docker layer caching)
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt 

# Copy all project files
COPY . .

# Create directories for output
RUN mkdir -p allure-results screenshot videos

# Default command: run full suite with parallel workers
CMD ["pytest", "--alluredir=allure-results", "-n", "2", "-v", "--tb=short"]
