import allure
import logging
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """
    OrangeHRM Login Page — https://opensource-demo.orangehrmlive.com/web/index.php/auth/login
    Locators verified against the live demo site.
    """

    # ── Locators ───────────────────────────────────────────────
    USERNAME_INPUT  = "input[name='username']"
    PASSWORD_INPUT  = "input[name='password']"
    LOGIN_BUTTON    = "button[type='submit']"
    # The error message appears in a paragraph inside the alert div
    ERROR_MSG       = ".oxd-alert-content-text"
    # Required field errors (shown under each empty input)
    REQUIRED_ERRORS = ".oxd-input-group .oxd-text--span"
    # Logo — reliable indicator that login page has loaded
    LOGIN_LOGO      = ".orangehrm-login-logo"
    # User dropdown in the nav bar (visible after login)
    USER_DROPDOWN   = ".oxd-userdropdown-tab"
    LOGOUT_LINK     = "//a[normalize-space()='Logout']"

    # ── Actions ────────────────────────────────────────────────

    @allure.step("Open OrangeHRM login page")
    def open(self, base_url: str):
        logger.info(f"Opening login page: {base_url}/auth/login")
        self.page.goto(f"{base_url}/auth/login")
        self.page.wait_for_load_state("networkidle")
        # Wait for the logo to confirm the page is ready
        self.page.wait_for_selector(self.LOGIN_LOGO, timeout=15000)
        logger.info("Login page fully loaded — logo visible")

    @allure.step("Enter username")
    def enter_username(self, username: str):
        logger.info(f"Entering username: {username}")
        self.page.locator(self.USERNAME_INPUT).fill(username)
        logger.info("Username entered")

    @allure.step("Enter password")
    def enter_password(self, password: str):
        logger.info("Entering password (masked)")
        self.page.locator(self.PASSWORD_INPUT).fill(password)
        logger.info("Password entered")

    @allure.step("Click the Login button")
    def click_login(self):
        logger.info("Clicking Login button")
        self.page.locator(self.LOGIN_BUTTON).click()
        logger.info("Login button clicked — waiting for response")

    def login(self, username: str, password: str):
        """Full login flow — broken into separate Allure steps."""
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    @allure.step("Read error message text")
    def get_error_message(self) -> str:
        logger.info("Waiting for error message to appear")
        self.page.wait_for_selector(self.ERROR_MSG, timeout=8000)
        text = self.page.locator(self.ERROR_MSG).text_content().strip()
        logger.info(f"Error message: '{text}'")
        return text

    @allure.step("Read required-field error messages")
    def get_required_errors(self) -> list[str]:
        self.page.wait_for_selector(self.REQUIRED_ERRORS, timeout=5000)
        errors = [el.text_content().strip()
                  for el in self.page.locator(self.REQUIRED_ERRORS).all()]
        logger.info(f"Required errors found: {errors}")
        return errors

    def is_logged_in(self) -> bool:
        result = "/dashboard/index" in self.page.url
        logger.info(f"Is logged in: {result}  (URL: {self.page.url})")
        return result

    @allure.step("Log out of OrangeHRM")
    def logout(self):
        logger.info("Clicking user dropdown to logout")
        self.page.locator(self.USER_DROPDOWN).click()
        self.page.locator(self.LOGOUT_LINK).click()
        self.page.wait_for_url("**/auth/login", timeout=10000)
        logger.info(f"Logged out — URL: {self.page.url}")