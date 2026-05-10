import allure
 
class BasePage:
    def __init__(self, page):
        self.page = page
 
    def navigate(self, url):
        with allure.step(f'Navigate to {url}'):
            self.page.goto(url)
 
    def click(self, locator):
        with allure.step(f'Click element: {locator}'):
            self.page.locator(locator).click()
 
    def fill(self, locator, value):
        with allure.step(f'Fill field with: {value}'):
            self.page.locator(locator).fill(value)
 
    def get_text(self, locator):
        return self.page.locator(locator).text_content()
 
    def is_visible(self, locator):
        return self.page.locator(locator).is_visible()
 
    def wait_for_selector(self, locator, timeout=10000):
        self.page.wait_for_selector(locator, timeout=timeout)
