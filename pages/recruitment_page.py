import allure
import logging
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class RecruitmentPage(BasePage):
    """
    Recruitment module.
    Locators verified against:
      https://opensource-demo.orangehrmlive.com/web/index.php/recruitment/viewJobVacancy
    """

    # ── Locators ───────────────────────────────────────────────
    NAV_RECRUITMENT   = "//span[text()='Recruitment']"
    VACANCIES_LINK    = "//a[normalize-space()='Vacancies']"
    CANDIDATES_LINK   = "//a[normalize-space()='Candidates']"
    ADD_BTN           = "//button[normalize-space()='Add']"

    # Add Vacancy form
    JOB_TITLE_SELECT  = "//label[text()='Job Title']/ancestor::div[@class='oxd-input-group']//div[@class='oxd-select-text-input']"
    JOB_TITLE_OPTIONS = ".oxd-select-dropdown .oxd-select-option"
    VACANCY_NAME      = "//label[text()='Vacancy Name']/ancestor::div[@class='oxd-input-group']//input"
    SAVE_BTN          = "//button[@type='submit'][normalize-space()='Save']"

    # Search
    VACANCY_SEARCH_BTN = "//button[@type='submit'][normalize-space()='Search']"
    TABLE_ROWS         = ".oxd-table-body .oxd-table-row"

    ANY_TOAST          = ".oxd-toast"

    # ── Navigation ─────────────────────────────────────────────

    @allure.step("Navigate to Recruitment → Vacancies")
    def go_to_vacancies(self):
        logger.info("Navigating to Recruitment > Vacancies")
        self.page.locator(self.NAV_RECRUITMENT).click()
        self.page.wait_for_load_state("networkidle")
        self.page.locator(self.VACANCIES_LINK).click()
        self.page.wait_for_url("**/recruitment/viewJobVacancy", timeout=10000)
        self.page.wait_for_load_state("networkidle")
        logger.info(f"Vacancies page loaded. URL: {self.page.url}")

    @allure.step("Navigate to Recruitment → Candidates")
    def go_to_candidates(self):
        logger.info("Navigating to Recruitment > Candidates")
        self.page.locator(self.NAV_RECRUITMENT).click()
        self.page.wait_for_load_state("networkidle")
        self.page.locator(self.CANDIDATES_LINK).click()
        self.page.wait_for_url("**/recruitment/viewCandidates", timeout=10000)
        self.page.wait_for_load_state("networkidle")
        logger.info(f"Candidates page loaded. URL: {self.page.url}")

    # ── Add Vacancy ────────────────────────────────────────────

    @allure.step("Click Add button on Vacancies page")
    def click_add(self):
        logger.info("Clicking Add button")
        self.page.locator(self.ADD_BTN).click()
        self.page.wait_for_url("**/recruitment/addJobVacancy", timeout=10000)
        logger.info("Add Vacancy form opened")

    @allure.step("Select job title from dropdown")
    def select_job_title(self, index: int = 1):
        logger.info(f"Selecting job title at index {index}")
        self.page.locator(self.JOB_TITLE_SELECT).click()
        options = self.page.locator(self.JOB_TITLE_OPTIONS)
        options.wait_for(timeout=5000)
        count = options.count()
        logger.info(f"Job title options: {count}")
        safe_index = min(index, count - 1)
        job_text = options.nth(safe_index).text_content().strip()
        options.nth(safe_index).click()
        logger.info(f"Job title selected: '{job_text}'")
        return job_text

    @allure.step("Enter vacancy name")
    def enter_vacancy_name(self, name: str):
        logger.info(f"Entering vacancy name: {name}")
        self.page.locator(self.VACANCY_NAME).fill(name)
        logger.info("Vacancy name entered")

    @allure.step("Save vacancy")
    def save_vacancy(self):
        logger.info("Clicking Save on vacancy form")
        self.page.locator(self.SAVE_BTN).click()
        self.page.wait_for_load_state("networkidle")
        logger.info("Vacancy form saved")

    # ── Helpers ────────────────────────────────────────────────

    @allure.step("Get vacancy count from table")
    def get_vacancy_count(self) -> int:
        count = self.page.locator(self.TABLE_ROWS).count()
        logger.info(f"Vacancy rows in table: {count}")
        return count