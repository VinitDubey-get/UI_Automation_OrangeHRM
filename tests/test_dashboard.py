import pytest
import allure
import logging
from pages.dashboard_page import DashboardPage

logger = logging.getLogger(__name__)


@allure.feature("Dashboard")
@allure.story("Post-Login Dashboard Verification")
class TestDashboard:

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-DASH-001: Dashboard loads after login")
    @allure.description("After login, user should land on the dashboard page.")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_dashboard_loads(self, logged_in_page):
        logger.info("=== TEST: test_dashboard_loads ===")
        dash = DashboardPage(logged_in_page)

        with allure.step("Verify dashboard page is loaded"):
            loaded = dash.verify_loaded()
            assert loaded, f"Expected dashboard URL, got: {logged_in_page.url}"
            logger.info("PASS: Dashboard loaded successfully")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-DASH-002: Navigation sidebar is visible")
    @allure.description("Main navigation menu should be visible after login.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_navigation_visible(self, logged_in_page):
        logger.info("=== TEST: test_navigation_visible ===")
        dash = DashboardPage(logged_in_page)

        with allure.step("Verify sidebar is visible"):
            visible = dash.is_sidebar_visible()
            assert visible, "Navigation sidebar is not visible on dashboard"
            logger.info("PASS: Navigation sidebar is visible")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-DASH-003: All key menu items are present")
    @allure.description("Menu items Admin, PIM, Leave, Time, Recruitment etc should all be visible.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_menu_items_visible(self, logged_in_page):
        logger.info("=== TEST: test_menu_items_visible ===")
        dash = DashboardPage(logged_in_page)

        with allure.step("Check all menu items"):
            results = dash.verify_menu_items()

        with allure.step("Assert all menu items are visible"):
            missing = [name for name, visible in results.items() if not visible]
            logger.info(f"Menu visibility results: {results}")
            assert not missing, f"These menu items were not visible: {missing}"
            logger.info("PASS: All menu items are visible")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-DASH-004: Dashboard widgets are rendered")
    @allure.description("Dashboard should show at least one widget/card after login.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_dashboard_widgets(self, logged_in_page):
        logger.info("=== TEST: test_dashboard_widgets ===")
        dash = DashboardPage(logged_in_page)

        with allure.step("Count dashboard widgets"):
            count = dash.get_widget_count()

        with allure.step("Verify at least one widget is shown"):
            assert count > 0, f"Expected widgets on dashboard, found: {count}"
            logger.info(f"PASS: {count} dashboard widgets found")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-DASH-005: Logged-in username is shown in nav bar")
    @allure.description("The nav bar should display the admin's name.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_username_displayed(self, logged_in_page):
        logger.info("=== TEST: test_username_displayed ===")
        dash = DashboardPage(logged_in_page)

        with allure.step("Get username displayed in nav bar"):
            username = dash.get_logged_in_username()

        with allure.step("Verify username is not empty"):
            assert username, "Expected a username in the nav bar but it was empty"
            logger.info(f"PASS: Username displayed in nav bar: '{username}'")