import allure
from pages.base_page import BasePage
 
class PIMPage(BasePage):
    NAV_PIM       = "//span[text()='PIM']"
    ADD_BUTTON    = "//button[normalize-space()='Add']"
    FIRST_NAME    = "//input[@name='firstName']"
    MIDDLE_NAME   = "//input[@name='middleName']"
    LAST_NAME     = "//input[@name='lastName']"
    SAVE_BUTTON   = "//button[normalize-space()='Save']"
    SEARCH_NAME   = "//label[text()='Employee Name']/../following-sibling::div//input"
    SEARCH_BTN    = "//button[normalize-space()='Search']"
    EMP_ROW       = ".oxd-table-body .oxd-table-row"
    DELETE_ICON   = "//button[@title='Delete']"
    CONFIRM_DEL   = "//button[normalize-space()='Yes, Delete']"
    SUCCESS_TOAST = ".oxd-toast"
 
    @allure.step('Navigate to PIM module')
    def go_to_pim(self):
        self.page.locator(self.NAV_PIM).click()
        self.page.wait_for_url('**/pim/viewEmployeeList')
 
    @allure.step('Add new employee')
    def add_employee(self, first, last):
        self.page.locator(self.ADD_BUTTON).click()
        self.page.locator(self.FIRST_NAME).fill(first)
        self.page.locator(self.LAST_NAME).fill(last)
        self.page.locator(self.SAVE_BUTTON).click()
        self.page.wait_for_selector(self.SUCCESS_TOAST)
 
    @allure.step('Search employee by name')
    def search_employee(self, name):
        self.go_to_pim()
        self.page.locator(self.SEARCH_NAME).fill(name)
        self.page.locator(self.SEARCH_BTN).click()
        self.page.wait_for_timeout(2000)
 
    def get_employee_count(self):
        return self.page.locator(self.EMP_ROW).count()
