import allure
import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from utils.config import APP_PASSWORD, APP_USERNAME


@allure.feature("Authentication")
@pytest.mark.smoke
class TestLogin:

    @allure.story("Valid login")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_valid_login_redirects_to_secure_page(self, login_page: LoginPage):
        login_page.open()
        login_page.login(APP_USERNAME, APP_PASSWORD)
        login_page.page.wait_for_load_state("networkidle")
        expect(login_page.page).to_have_url("https://practice.expandtesting.com/secure")
        assert login_page.is_logged_in()

    @allure.story("Invalid credentials")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_invalid_credentials_shows_error(self, login_page: LoginPage):
        login_page.open()
        login_page.login("wrong_user", "wrong_pass")
        flash = login_page.get_flash_message()
        assert "invalid" in flash.lower() or "password" in flash.lower()

    @allure.story("Empty username")
    @allure.severity(allure.severity_level.NORMAL)
    def test_empty_username_shows_validation(self, login_page: LoginPage):
        login_page.open()
        login_page.login("", APP_PASSWORD)
        flash = login_page.get_flash_message()
        assert flash != ""

    @allure.story("Empty password")
    @allure.severity(allure.severity_level.NORMAL)
    def test_empty_password_shows_validation(self, login_page: LoginPage):
        login_page.open()
        login_page.login(APP_USERNAME, "")
        flash = login_page.get_flash_message()
        assert flash != ""
