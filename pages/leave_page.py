import allure
from pages.base_page import BasePage
 
class LeavePage(BasePage):
    NAV_LEAVE     = "//span[text()='Leave']"
    APPLY_LINK    = "//a[normalize-space()='Apply']"
    LEAVE_TYPE    = "//label[text()='Leave Type']/../following-sibling::div//div[@class='oxd-select-text-input']"
    FROM_DATE     = "//label[text()='From Date']/../following-sibling::div//input"
    TO_DATE       = "//label[text()='To Date']/../following-sibling::div//input"
    COMMENT       = "//textarea"
    APPLY_BUTTON  = "//button[normalize-space()='Apply']"
    SUCCESS_TOAST = ".oxd-toast"

    
    @allure.step('Navigate to Leave → Apply')
    def go_to_apply(self):
        self.page.locator(self.NAV_LEAVE).click()
        self.page.locator(self.APPLY_LINK).click()
 
    @allure.step('Apply for leave')
    def apply_leave(self, leave_type_index=0, from_date='2025-12-01', to_date='2025-12-02'):
        self.page.locator(self.LEAVE_TYPE).click()
        options = self.page.locator('.oxd-select-dropdown .oxd-select-option')
        options.nth(leave_type_index + 1).click()
        self.page.locator(self.FROM_DATE).fill(from_date)
        self.page.keyboard.press('Tab')
        self.page.locator(self.TO_DATE).fill(to_date)
        self.page.keyboard.press('Tab')
        self.page.locator(self.COMMENT).fill('Automated test leave request')
        self.page.locator(self.APPLY_BUTTON).click()


