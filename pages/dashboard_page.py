import allure
import logging
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class DashboardPage(BasePage):
    """
    Dashboard — first page after login.
    Locators verified against the live demo site.
    """

    # ── Locators ───────────────────────────────────────────────
    MAIN_MENU        = ".oxd-main-menu"
    USER_DROPDOWN    = ".oxd-userdropdown-tab"
    USER_NAME_TEXT   = ".oxd-userdropdown-name"
    DASHBOARD_HEADER = "//h6[text()='Dashboard']"
    WIDGETS          = ".oxd-grid-item"

    # Sidebar menu items — text-based locators
    MENU_ITEMS = [
        "Admin", "PIM", "Leave", "Time", "Recruitment",
        "My Info", "Performance", "Dashboard",
    ]

    # ── Methods ────────────────────────────────────────────────

    @allure.step("Verify dashboard is loaded")
    def verify_loaded(self) -> bool:
        logger.info("Verifying dashboard page is loaded")
        self.page.wait_for_selector(self.DASHBOARD_HEADER, timeout=10000)
        url_ok = "/dashboard/index" in self.page.url
        logger.info(f"Dashboard loaded: {url_ok}  (URL: {self.page.url})")
        return url_ok

    @allure.step("Get logged-in username from nav bar")
    def get_logged_in_username(self) -> str:
        name = self.page.locator(self.USER_NAME_TEXT).text_content().strip()
        logger.info(f"Logged-in user displayed: '{name}'")
        return name

    @allure.step("Verify all main menu items are visible")
    def verify_menu_items(self) -> dict:
        results = {}
        for menu in self.MENU_ITEMS:
            locator = f"//span[text()='{menu}']"
            visible = self.page.locator(locator).is_visible()
            results[menu] = visible
            status = "VISIBLE" if visible else "MISSING"
            logger.info(f"Menu item '{menu}': {status}")
        return results

    @allure.step("Count dashboard widgets")
    def get_widget_count(self) -> int:
        count = self.page.locator(self.WIDGETS).count()
        logger.info(f"Dashboard widgets visible: {count}")
        return count

    @allure.step("Verify navigation sidebar is visible")
    def is_sidebar_visible(self) -> bool:
        visible = self.page.locator(self.MAIN_MENU).is_visible()
        logger.info(f"Sidebar visible: {visible}")
        return visible