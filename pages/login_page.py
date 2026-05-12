from playwright.sync_api import Page, expect

from pages.base_page import BasePage

_PATH = "/login"


class LoginPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Locators
        self._username = page.get_by_label("Username")
        self._password = page.get_by_label("Password")
        self._submit = page.get_by_role("button", name="Login")
        self._flash = page.locator("#flash")
        self._logout = page.get_by_role("link", name="Logout")

    # ------------------------------------------------------------------ actions

    def open(self) -> None:
        self.navigate(_PATH)
        self.wait_for_locator(self._submit)

    def login(self, username: str, password: str) -> None:
        self.logger.info("Logging in as '%s'", username)
        self._username.fill(username)
        self._password.fill(password)
        self._submit.click()

    # ------------------------------------------------------------------ queries

    def get_flash_message(self) -> str:
        self._flash.wait_for(state="visible")
        return self._flash.inner_text().strip()

    def is_logged_in(self) -> bool:
        return self._logout.is_visible()