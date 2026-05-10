import allure
import logging
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class LeavePage(BasePage):
    """
    Leave module — Apply Leave, Leave List.
    Locators verified against:
      https://opensource-demo.orangehrmlive.com/web/index.php/leave/applyLeave
    """

    # ── Locators ───────────────────────────────────────────────
    NAV_LEAVE     = "//span[text()='Leave']"
    APPLY_LINK    = "//a[normalize-space()='Apply']"
    LIST_LINK     = "//a[normalize-space()='Leave List']"
    MY_LEAVE_LINK = "//a[normalize-space()='My Leave']"

    # Apply Leave form
    # OrangeHRM leave type is a custom oxd-select, not a native <select>
    LEAVE_TYPE_SELECT     = "//label[text()='Leave Type']/ancestor::div[@class='oxd-input-group']//div[@class='oxd-select-text-input']"
    LEAVE_TYPE_OPTIONS    = ".oxd-select-dropdown .oxd-select-option"

    FROM_DATE_INPUT       = "//label[text()='From Date']/ancestor::div[@class='oxd-input-group']//input[@placeholder='yyyy-dd-mm']"
    TO_DATE_INPUT         = "//label[text()='To Date']/ancestor::div[@class='oxd-input-group']//input[@placeholder='yyyy-dd-mm']"

    # OrangeHRM uses yyyy-dd-mm format (unusual — note the dd before mm)
    COMMENT_INPUT         = "//label[text()='Comments']/ancestor::div[@class='oxd-input-group']//textarea"
    APPLY_BTN             = "//button[@type='submit'][normalize-space()='Apply']"

    SUCCESS_TOAST         = ".oxd-toast--success"
    ANY_TOAST             = ".oxd-toast"

    # Leave list
    LEAVE_LIST_ROWS       = ".oxd-table-body .oxd-table-row"

    # ── Navigation ─────────────────────────────────────────────

    @allure.step("Navigate to Leave module")
    def go_to_leave(self):
        logger.info("Clicking Leave in sidebar")
        self.page.locator(self.NAV_LEAVE).click()
        # Wait for the Apply sub-menu to appear — reliable indicator the menu opened
        self.page.wait_for_selector(self.APPLY_LINK, timeout=10000)
        logger.info("Leave module opened")

    @allure.step("Navigate to Apply Leave form")
    def go_to_apply_leave(self):
        logger.info("Navigating to Apply Leave page")
        self.go_to_leave()
        self.page.locator(self.APPLY_LINK).click()
        self.page.wait_for_url("**/leave/applyLeave", timeout=10000)
        # Wait for the Leave Type dropdown to be ready — it loads options via API
        # after the submit button appears, so this is the correct ready-signal.
        self.page.locator(self.LEAVE_TYPE_SELECT).wait_for(
            state="visible", timeout=15000
        )
        logger.info(f"Apply Leave page loaded. URL: {self.page.url}")

    # ── Apply Leave flow ───────────────────────────────────────

    @allure.step("Select leave type")
    def select_leave_type(self, index: int = 0):
        logger.info(f"Opening leave type dropdown (selecting index {index})")
        self.page.locator(self.LEAVE_TYPE_SELECT).click()
        options = self.page.locator(self.LEAVE_TYPE_OPTIONS)
        options.wait_for(timeout=5000)
        count = options.count()
        logger.info(f"Leave type options available: {count}")
        # index+1 because the first item is usually the placeholder
        safe_index = min(index + 1, count - 1)
        option_text = options.nth(safe_index).text_content().strip()
        options.nth(safe_index).click()
        logger.info(f"Selected leave type: '{option_text}'")

    @allure.step("Count available leave type options")
    def get_leave_type_count(self) -> int:
        """
        Opens the Leave Type dropdown, counts the selectable options,
        then closes the dropdown without making a selection.
        Uses the same locator as select_leave_type() — known to be interactable.
        """
        logger.info("Opening Leave Type dropdown to count options")
        self.page.locator(self.LEAVE_TYPE_SELECT).click()
        options = self.page.locator(self.LEAVE_TYPE_OPTIONS)
        # Wait for at least the first option to be visible
        options.first.wait_for(state="visible", timeout=8000)
        count = options.count()
        logger.info(f"Leave type options found: {count}")
        self.page.keyboard.press("Escape")
        return count

    @allure.step("Enter From Date")
    def enter_from_date(self, date: str):
        # OrangeHRM expects yyyy-dd-mm format
        logger.info(f"Entering From Date: {date}")
        from_input = self.page.locator(self.FROM_DATE_INPUT)
        from_input.fill(date)
        self.page.keyboard.press("Tab")
        self.page.wait_for_timeout(500)
        logger.info("From Date entered and Tab pressed")

    @allure.step("Enter To Date")
    def enter_to_date(self, date: str):
        logger.info(f"Entering To Date: {date}")
        to_input = self.page.locator(self.TO_DATE_INPUT)
        to_input.fill(date)
        self.page.keyboard.press("Tab")
        self.page.wait_for_timeout(500)
        logger.info("To Date entered and Tab pressed")

    @allure.step("Enter leave comment")
    def enter_comment(self, comment: str):
        logger.info(f"Entering comment: {comment}")
        self.page.locator(self.COMMENT_INPUT).fill(comment)
        logger.info("Comment entered")

    @allure.step("Click Apply button")
    def click_apply(self):
        logger.info("Clicking Apply button")
        self.page.locator(self.APPLY_BTN).click()
        self.page.wait_for_timeout(2000)
        logger.info("Apply button clicked")

    def apply_leave(
        self,
        leave_type_index: int = 0,
        from_date: str = "2025-01-15",
        to_date: str = "2025-01-15",
        comment: str = "Automated test leave request",
    ):
        """Full apply-leave flow with individual Allure steps."""
        self.go_to_apply_leave()
        self.select_leave_type(leave_type_index)
        self.enter_from_date(from_date)
        self.enter_to_date(to_date)
        self.enter_comment(comment)
        self.click_apply()

    # ── Leave list ─────────────────────────────────────────────

    @allure.step("Navigate to Leave List")
    def go_to_leave_list(self):
        logger.info("Navigating to Leave List")
        self.go_to_leave()
        self.page.locator(self.LIST_LINK).click()
        self.page.wait_for_url("**/leave/viewLeaveList", timeout=10000)
        self.page.wait_for_selector(".oxd-table", timeout=10000)
        logger.info("Leave List loaded")

    @allure.step("Navigate to My Leave")
    def go_to_my_leave(self):
        logger.info("Navigating to My Leave")
        self.go_to_leave()
        self.page.locator(self.MY_LEAVE_LINK).click()
        self.page.wait_for_url("**/leave/viewMyLeaveList", timeout=10000)
        self.page.wait_for_selector(".oxd-table", timeout=10000)
        logger.info("My Leave loaded")