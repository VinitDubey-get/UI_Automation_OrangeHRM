import allure
import logging
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class PIMPage(BasePage):
    """
    PIM (People Information Manager) module — Employee management.
    All locators verified against:
      https://opensource-demo.orangehrmlive.com/web/index.php/pim/viewEmployeeList
    """

    # ── Locators ───────────────────────────────────────────────
    # Sidebar nav
    NAV_PIM           = "//span[text()='PIM']"
    ADD_EMPLOYEE_BTN  = "//button[normalize-space()='Add']"

    # Add Employee form
    FIRST_NAME_INPUT  = "//input[@name='firstName']"
    LAST_NAME_INPUT   = "//input[@name='lastName']"
    SAVE_BTN          = "//button[@type='submit'][normalize-space()='Save']"

    # Employee list / search
    # OrangeHRM uses an autocomplete component — the name field is NOT a plain input
    # The correct locator for the search name autocomplete:
    # The autocomplete input inside the Employee Name field group
    SEARCH_EMP_NAME   = "//div[@class='oxd-input-group']//input[@placeholder]"
    SEARCH_BTN        = "//button[@type='submit'][normalize-space()='Search']"

    # Results table — each data row (not the header)
    TABLE_ROWS        = ".oxd-table-body .oxd-table-row"
    NO_RECORDS_MSG    = ".oxd-table-body .oxd-text"

    # Edit employee — first name in the personal details section
    EDIT_FIRST_NAME   = "//input[@name='firstName']"
    EDIT_LAST_NAME    = "//input[@name='lastName']"
    EDIT_SAVE_BTN     = "(//button[@type='submit'][normalize-space()='Save'])[1]"

    # Success / info toast
    SUCCESS_TOAST     = ".oxd-toast--success"
    ANY_TOAST         = ".oxd-toast"

    # ── Navigation ─────────────────────────────────────────────

    @allure.step("Navigate to PIM module")
    def go_to_pim(self):
        logger.info("Navigating to PIM module via sidebar")
        self.page.locator(self.NAV_PIM).click()
        self.page.wait_for_url("**/pim/viewEmployeeList", timeout=15000)
        self.page.wait_for_load_state("networkidle")
        logger.info(f"PIM module loaded. URL: {self.page.url}")

    # ── Add Employee ───────────────────────────────────────────

    @allure.step("Click Add Employee button")
    def click_add_employee(self):
        logger.info("Clicking Add Employee button")
        self.page.locator(self.ADD_EMPLOYEE_BTN).click()
        self.page.wait_for_url("**/pim/addEmployee", timeout=10000)
        logger.info("Add Employee form opened")

    @allure.step("Fill employee first name")
    def fill_first_name(self, first_name: str):
        logger.info(f"Filling first name: {first_name}")
        self.page.locator(self.FIRST_NAME_INPUT).fill(first_name)
        logger.info("First name filled")

    @allure.step("Fill employee last name")
    def fill_last_name(self, last_name: str):
        logger.info(f"Filling last name: {last_name}")
        self.page.locator(self.LAST_NAME_INPUT).fill(last_name)
        logger.info("Last name filled")

    @allure.step("Save employee form")
    def save_employee(self):
        logger.info("Clicking Save button on employee form")
        self.page.locator(self.SAVE_BTN).click()
        # After save, OrangeHRM redirects to the employee edit profile page
        self.page.wait_for_url("**/pim/viewPersonalDetails/empNumber/**", timeout=15000)
        logger.info(f"Employee saved — redirected to: {self.page.url}")

    def add_employee(self, first_name: str, last_name: str):
        """Complete add-employee flow broken into Allure steps."""
        self.click_add_employee()
        self.fill_first_name(first_name)
        self.fill_last_name(last_name)
        self.save_employee()

    # ── Search Employee ────────────────────────────────────────

    @allure.step("Search employee by name")
    def search_employee(self, name: str):
        logger.info(f"Searching for employee: '{name}'")
        # Use the first input field in the search form (Employee Name autocomplete)
        search_input = self.page.locator("input[placeholder='Type for hints...']")
        search_input.fill(name)
        self.page.wait_for_timeout(800)
        logger.info("Name entered in search field")
        self.page.locator(self.SEARCH_BTN).click()
        # Wait for the loading spinner to disappear instead of networkidle
        self.page.wait_for_selector(".oxd-loading-spinner", state="hidden", timeout=10000)
        self.page.wait_for_timeout(1000)
        logger.info("Search results loaded")

    @allure.step("Get employee row count from results table")
    def get_employee_row_count(self) -> int:
        count = self.page.locator(self.TABLE_ROWS).count()
        logger.info(f"Employee rows in table: {count}")
        return count

    @allure.step("Check if 'No Records Found' is shown")
    def is_no_records_shown(self) -> bool:
        try:
            # This element only exists when there are no results
            self.page.wait_for_selector(self.NO_RECORDS_MSG, timeout=5000)
            text = self.page.locator(self.NO_RECORDS_MSG).first.text_content()
            result = "No Records Found" in text
            logger.info(f"No-records message shown: {result}  (text: '{text}')")
            return result
        except Exception:
            logger.info("No-records message not found — records likely exist")
            return False

    # ── Helpers ────────────────────────────────────────────────

    @allure.step("Get the full list of employee names from the table")
    def get_employee_names(self) -> list[str]:
        # Each row has cells — the name is in the 2nd cell (index 1)
        rows = self.page.locator(self.TABLE_ROWS).all()
        names = []
        for row in rows:
            cells = row.locator(".oxd-table-cell").all()
            if len(cells) >= 2:
                name = cells[1].text_content().strip()
                names.append(name)
        logger.info(f"Employee names in table: {names}")
        return names