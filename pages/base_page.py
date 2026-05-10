import allure
import logging

logger = logging.getLogger(__name__)


class BasePage:
    """
    All page objects inherit from this.
    Every browser interaction is wrapped with:
      - allure.step()  → shows in the Allure report step-by-step
      - logger.info()  → written to logs/test_run.log and Jenkins console
    """

    def __init__(self, page):
        self.page = page

    # ── Navigation ─────────────────────────────────────────────
    def navigate(self, url: str):
        with allure.step(f"Navigate to: {url}"):
            logger.info(f"Navigating to: {url}")
            self.page.goto(url)
            self.page.wait_for_load_state("networkidle")
            logger.info(f"Page loaded. Current URL: {self.page.url}")

    # ── Interactions ───────────────────────────────────────────
    def click(self, locator: str, description: str = ""):
        label = description or locator
        with allure.step(f"Click: {label}"):
            logger.info(f"Clicking element: {label}")
            self.page.locator(locator).click()
            logger.info(f"Clicked: {label}")

    def fill(self, locator: str, value: str, field_name: str = ""):
        label = field_name or locator
        with allure.step(f"Fill '{label}' with: {value}"):
            logger.info(f"Filling field '{label}' with value: {value}")
            self.page.locator(locator).clear()
            self.page.locator(locator).fill(value)
            logger.info(f"Field '{label}' filled successfully")

    def select_option(self, locator: str, option_text: str, field_name: str = ""):
        label = field_name or locator
        with allure.step(f"Select '{option_text}' from dropdown: {label}"):
            logger.info(f"Selecting '{option_text}' from: {label}")
            self.page.locator(locator).click()
            self.page.locator(f".oxd-select-option >> text='{option_text}'").click()
            logger.info(f"Selected: {option_text}")

    # ── Waits ──────────────────────────────────────────────────
    def wait_for_url(self, pattern: str, timeout: int = 15000):
        with allure.step(f"Wait for URL pattern: {pattern}"):
            logger.info(f"Waiting for URL: {pattern}")
            self.page.wait_for_url(pattern, timeout=timeout)
            logger.info(f"URL matched. Current URL: {self.page.url}")

    def wait_for_selector(self, locator: str, timeout: int = 10000):
        with allure.step(f"Wait for element: {locator}"):
            logger.info(f"Waiting for selector: {locator}")
            self.page.wait_for_selector(locator, timeout=timeout)
            logger.info(f"Element found: {locator}")

    def wait_for_toast(self, timeout: int = 8000) -> str:
        with allure.step("Wait for success/error toast message"):
            logger.info("Waiting for toast notification")
            self.page.wait_for_selector(".oxd-toast", timeout=timeout)
            text = self.page.locator(".oxd-toast").text_content()
            logger.info(f"Toast message: {text}")
            return text

    # ── State queries ──────────────────────────────────────────
    def get_text(self, locator: str) -> str:
        text = self.page.locator(locator).text_content()
        logger.info(f"Got text from '{locator}': {text}")
        return text

    def is_visible(self, locator: str) -> bool:
        visible = self.page.locator(locator).is_visible()
        logger.info(f"Element '{locator}' visible: {visible}")
        return visible

    def get_current_url(self) -> str:
        url = self.page.url
        logger.info(f"Current URL: {url}")
        return url