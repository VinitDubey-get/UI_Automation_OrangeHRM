from playwright.sync_api import Locator, Page

from utils.config import BASE_URL, DEFAULT_TIMEOUT
from utils.logger import get_logger


class BasePage:
    """Base class providing common Playwright helpers for all page objects."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.logger = get_logger(self.__class__.__name__)
        self.page.set_default_timeout(DEFAULT_TIMEOUT)

    def navigate(self, path: str = "") -> None:
        url = f"{BASE_URL}{path}"
        self.logger.info("Navigating to %s", url)
        self.page.goto(url)

    def get_title(self) -> str:
        return self.page.title()

    def wait_for_locator(self, locator: Locator) -> None:
        locator.wait_for(state="visible")
