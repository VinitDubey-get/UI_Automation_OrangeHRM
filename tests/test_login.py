import pytest
import allure
from pages.login_page import LoginPage
 
@allure.feature('Authentication')
@allure.story('Login')
class TestLogin:
 
    @allure.title('Valid login with correct credentials')
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_valid_login(self, page, base_url, admin_credentials):
        login = LoginPage(page)
        login.open(base_url)
        login.login(admin_credentials['username'], admin_credentials['password'])
        page.wait_for_url('**/dashboard/index', timeout=10000)
        assert login.is_logged_in(), 'Expected to be on dashboard after login'
 
    @allure.title('Login fails with invalid username')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.negative
    def test_invalid_username(self, page, base_url):
        login = LoginPage(page)
        login.open(base_url)
        login.login('invaliduser123', 'admin123')
        error = login.get_error_message()
        assert 'Invalid credentials' in error
 
    @allure.title('Login fails with invalid password')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.negative
    def test_invalid_password(self, page, base_url, admin_credentials):
        login = LoginPage(page)
        login.open(base_url)
        login.login(admin_credentials['username'], 'wrongpassword')
        error = login.get_error_message()
        assert 'Invalid credentials' in error
 
    @allure.title('Login fails with empty credentials')
    @pytest.mark.negative
    def test_empty_credentials(self, page, base_url):
        login = LoginPage(page)
        login.open(base_url)
        login.login('', '')
        assert page.locator('.oxd-input-field-error-message').count() >= 1
 
    @allure.title('Successful logout')
    @pytest.mark.smoke
    def test_logout(self, logged_in_page, base_url):
        logged_in_page.locator('.oxd-userdropdown-tab').click()
        logged_in_page.locator("//a[normalize-space()='Logout']").click()
        logged_in_page.wait_for_url('**/auth/login')
        assert '/auth/login' in logged_in_page.url
