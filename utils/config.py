import os

BASE_URL: str = os.getenv("BASE_URL", "https://practice.expandtesting.com")
HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"
SLOW_MO: int = int(os.getenv("SLOW_MO", "0"))
DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "10000"))  # ms

# Login credentials (used only by auth module)
APP_USERNAME: str = os.getenv("APP_USERNAME", "practice")
APP_PASSWORD: str = os.getenv("APP_PASSWORD", "SuperSecretPassword!")