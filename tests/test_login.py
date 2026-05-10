import pytest
import allure
import logging
from pages.login_page import LoginPage

logger = logging.getLogger(__name__)


@allure.feature("Authentication")
@allure.story("Login / Logout")
class TestLogin:
    """
    Tests for OrangeHRM login and logout functionality.
    All tests use the 'page' fixture (not logged_in_page) because
    login itself is what's being tested here.
    """

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-LGN-001: Valid login with correct credentials")
    @allure.description("User should be redirected to dashboard after correct login.")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_valid_login(self, page, base_url, admin_credentials):
        logger.info("=== TEST: test_valid_login ===")
        login = LoginPage(page)

        with allure.step("Open the login page"):
            login.open(base_url)

        with allure.step("Perform login with valid credentials"):
            login.login(admin_credentials["username"], admin_credentials["password"])

        with allure.step("Wait for dashboard URL"):
            page.wait_for_url("**/dashboard/index", timeout=15000)

        with allure.step("Assert user is on the dashboard"):
            assert login.is_logged_in(), (
                f"Expected dashboard URL but got: {page.url}"
            )
            logger.info("PASS: Valid login redirects to dashboard")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-LGN-002: Login fails with invalid username")
    @allure.description("Invalid username should show 'Invalid credentials' error.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.negative
    def test_invalid_username(self, page, base_url):
        logger.info("=== TEST: test_invalid_username ===")
        login = LoginPage(page)

        with allure.step("Open the login page"):
            login.open(base_url)

        with allure.step("Login with invalid username"):
            login.login("invalid_user_xyz_999", "admin123")

        with allure.step("Verify error message is shown"):
            error = login.get_error_message()
            logger.info(f"Error message received: '{error}'")
            assert "Invalid credentials" in error, (
                f"Expected 'Invalid credentials' but got: '{error}'"
            )
            logger.info("PASS: Invalid username shows correct error")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-LGN-003: Login fails with invalid password")
    @allure.description("Wrong password should show 'Invalid credentials' error.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.negative
    def test_invalid_password(self, page, base_url, admin_credentials):
        logger.info("=== TEST: test_invalid_password ===")
        login = LoginPage(page)

        with allure.step("Open the login page"):
            login.open(base_url)

        with allure.step("Login with wrong password"):
            login.login(admin_credentials["username"], "WrongPassword999!")

        with allure.step("Verify error message is shown"):
            error = login.get_error_message()
            logger.info(f"Error message received: '{error}'")
            assert "Invalid credentials" in error, (
                f"Expected 'Invalid credentials' but got: '{error}'"
            )
            logger.info("PASS: Invalid password shows correct error")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-LGN-004: Login fails with empty username")
    @allure.description("Empty username field should show 'Required' validation.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_empty_username(self, page, base_url):
        logger.info("=== TEST: test_empty_username ===")
        login = LoginPage(page)

        with allure.step("Open the login page"):
            login.open(base_url)

        with allure.step("Submit form with empty username"):
            login.login("", "admin123")

        with allure.step("Verify required field validation appears"):
            errors = login.get_required_errors()
            logger.info(f"Validation errors: {errors}")
            assert any("Required" in e for e in errors), (
                f"Expected 'Required' validation, got: {errors}"
            )
            logger.info("PASS: Empty username triggers required validation")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-LGN-005: Login fails with empty password")
    @allure.description("Empty password field should show 'Required' validation.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_empty_password(self, page, base_url, admin_credentials):
        logger.info("=== TEST: test_empty_password ===")
        login = LoginPage(page)

        with allure.step("Open the login page"):
            login.open(base_url)

        with allure.step("Submit form with empty password"):
            login.login(admin_credentials["username"], "")

        with allure.step("Verify required field validation appears"):
            errors = login.get_required_errors()
            logger.info(f"Validation errors: {errors}")
            assert any("Required" in e for e in errors), (
                f"Expected 'Required' validation, got: {errors}"
            )
            logger.info("PASS: Empty password triggers required validation")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-LGN-006: Successful logout")
    @allure.description("Logged-in user should be able to log out and return to login page.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_logout(self, logged_in_page, base_url):
        logger.info("=== TEST: test_logout ===")
        login = LoginPage(logged_in_page)

        with allure.step("Verify user is currently on dashboard"):
            assert "/dashboard/index" in logged_in_page.url
            logger.info("User is on dashboard — proceeding to logout")

        with allure.step("Perform logout"):
            login.logout()

        with allure.step("Verify redirect to login page"):
            assert "/auth/login" in logged_in_page.url, (
                f"Expected login page URL but got: {logged_in_page.url}"
            )
            logger.info("PASS: Logout redirects to login page")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-LGN-007: Login page title is correct")
    @allure.description("OrangeHRM login page should have the correct browser title.")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.smoke
    def test_login_page_title(self, page, base_url):
        logger.info("=== TEST: test_login_page_title ===")
        login = LoginPage(page)

        with allure.step("Open the login page"):
            login.open(base_url)

        with allure.step("Verify page title"):
            title = page.title()
            logger.info(f"Page title: '{title}'")
            assert "OrangeHRM" in title, f"Expected 'OrangeHRM' in title, got: '{title}'"
            logger.info("PASS: Page title contains OrangeHRM")