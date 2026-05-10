import allure
from pages.base_page import BasePage
 
class LoginPage(BasePage):
    # Locators
    USERNAME_INPUT = "input[name='username']"
    PASSWORD_INPUT = "input[name='password']"
    LOGIN_BUTTON   = "button[type='submit']"
    ERROR_MESSAGE  = ".oxd-alert-content-text"
    LOGO           = ".orangehrm-login-logo"
 
    @allure.step('Open login page')
    def open(self, base_url):
        self.page.goto(base_url + '/auth/login')
        self.page.wait_for_selector(self.LOGO)
 
    @allure.step('Login with credentials')
    def login(self, username, password):
        self.page.locator(self.USERNAME_INPUT).fill(username)
        self.page.locator(self.PASSWORD_INPUT).fill(password)
        self.page.locator(self.LOGIN_BUTTON).click()
 
    def get_error_message(self):
        self.page.wait_for_selector(self.ERROR_MESSAGE)
        return self.page.locator(self.ERROR_MESSAGE).text_content()
 
    def is_logged_in(self):
        return '/dashboard/index' in self.page.url
