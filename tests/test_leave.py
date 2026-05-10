import pytest
import allure
import logging
from pages.leave_page import LeavePage

logger = logging.getLogger(__name__)


@allure.feature("Leave Management")
@allure.story("Leave Module — Navigation & Application")
class TestLeave:

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-LVE-001: Leave module is accessible from sidebar")
    @allure.description("'Leave' should be visible in the sidebar navigation.")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.leave
    def test_leave_nav_visible(self, logged_in_page):
        logger.info("=== TEST: test_leave_nav_visible ===")

        with allure.step("Verify Leave menu item is visible in sidebar"):
            locator = "//span[text()='Leave']"
            visible = logged_in_page.locator(locator).is_visible()
            logger.info(f"Leave nav visible: {visible}")
            assert visible, "Leave menu item is not visible in the sidebar"
            logger.info("PASS: Leave nav item is visible")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-LVE-002: Apply Leave page loads correctly")
    @allure.description("Navigating to Leave > Apply should open the Apply Leave form.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.leave
    def test_apply_leave_page_loads(self, logged_in_page):
        logger.info("=== TEST: test_apply_leave_page_loads ===")
        leave = LeavePage(logged_in_page)

        with allure.step("Navigate to Leave > Apply Leave"):
            leave.go_to_apply_leave()

        with allure.step("Verify URL is the Apply Leave page"):
            url = logged_in_page.url
            logger.info(f"Current URL: {url}")
            assert "/leave/applyLeave" in url, f"Expected applyLeave URL, got: {url}"
            logger.info("PASS: Apply Leave page loaded")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-LVE-003: Leave type dropdown has options")
    @allure.description("The Leave Type dropdown on the Apply Leave form should have selectable options.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.leave
    def test_leave_type_dropdown_has_options(self, logged_in_page):
        logger.info("=== TEST: test_leave_type_dropdown_has_options ===")
        leave = LeavePage(logged_in_page)

        with allure.step("Navigate to Apply Leave"):
            leave.go_to_apply_leave()

        with allure.step("Open leave type dropdown"):
            # The oxd-select trigger div
            trigger = logged_in_page.locator(".oxd-select-text").first
            trigger.click()
            logger.info("Dropdown clicked")

        with allure.step("Count available leave type options"):
            # Options appear in a dropdown list — wait up to 5s for first one
            logged_in_page.wait_for_selector(
                ".oxd-select-dropdown .oxd-select-option", timeout=5000
            )
            count = logged_in_page.locator(
                ".oxd-select-dropdown .oxd-select-option"
            ).count()
            logger.info(f"Leave type options found: {count}")
            # Close dropdown cleanly
            logged_in_page.keyboard.press("Escape")
            assert count > 0, "Expected at least one leave type option"
            logger.info("PASS: Leave type dropdown has options")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-LVE-004: My Leave page loads from Leave menu")
    @allure.description("Leave > My Leave should navigate to the My Leave list.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.leave
    def test_my_leave_page_loads(self, logged_in_page):
        logger.info("=== TEST: test_my_leave_page_loads ===")
        leave = LeavePage(logged_in_page)

        with allure.step("Navigate to Leave > My Leave"):
            leave.go_to_my_leave()

        with allure.step("Verify URL is My Leave page"):
            url = logged_in_page.url
            logger.info(f"Current URL: {url}")
            assert "/leave/viewMyLeaveList" in url, f"Expected My Leave URL, got: {url}"
            logger.info("PASS: My Leave page loaded")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-LVE-005: Leave List page loads from Leave menu")
    @allure.description("Leave > Leave List should navigate to the leave list view.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.leave
    def test_leave_list_page_loads(self, logged_in_page):
        logger.info("=== TEST: test_leave_list_page_loads ===")
        leave = LeavePage(logged_in_page)

        with allure.step("Navigate to Leave > Leave List"):
            leave.go_to_leave_list()

        with allure.step("Verify URL is Leave List page"):
            url = logged_in_page.url
            logger.info(f"Current URL: {url}")
            assert "/leave/viewLeaveList" in url, f"Expected Leave List URL, got: {url}"
            logger.info("PASS: Leave List page loaded")