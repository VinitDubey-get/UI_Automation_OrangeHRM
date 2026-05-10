import pytest
import allure
import logging
from pages.recruitment_page import RecruitmentPage

logger = logging.getLogger(__name__)


@allure.feature("Recruitment")
@allure.story("Vacancies & Candidates")
class TestRecruitment:

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-RCT-001: Recruitment module is accessible from sidebar")
    @allure.description("'Recruitment' should be visible in the sidebar navigation.")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.recruitment
    def test_recruitment_nav_visible(self, logged_in_page):
        logger.info("=== TEST: test_recruitment_nav_visible ===")

        with allure.step("Verify Recruitment menu item is visible"):
            visible = logged_in_page.locator("//span[text()='Recruitment']").is_visible()
            logger.info(f"Recruitment nav visible: {visible}")
            assert visible, "Recruitment menu item is not visible"
            logger.info("PASS: Recruitment nav is visible")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-RCT-002: Vacancies page loads")
    @allure.description("Recruitment > Vacancies should load the vacancies list page.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.recruitment
    def test_vacancies_page_loads(self, logged_in_page):
        logger.info("=== TEST: test_vacancies_page_loads ===")
        rec = RecruitmentPage(logged_in_page)

        with allure.step("Navigate to Recruitment > Vacancies"):
            rec.go_to_vacancies()

        with allure.step("Verify URL is Vacancies page"):
            url = logged_in_page.url
            logger.info(f"Current URL: {url}")
            assert "/recruitment/viewJobVacancy" in url, (
                f"Expected vacancies URL, got: {url}"
            )
            logger.info("PASS: Vacancies page loaded")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-RCT-003: Candidates page loads")
    @allure.description("Recruitment > Candidates should load the candidates list.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.recruitment
    def test_candidates_page_loads(self, logged_in_page):
        logger.info("=== TEST: test_candidates_page_loads ===")
        rec = RecruitmentPage(logged_in_page)

        with allure.step("Navigate to Recruitment > Candidates"):
            rec.go_to_candidates()

        with allure.step("Verify URL is Candidates page"):
            url = logged_in_page.url
            logger.info(f"Current URL: {url}")
            assert "/recruitment/viewCandidates" in url, (
                f"Expected candidates URL, got: {url}"
            )
            logger.info("PASS: Candidates page loaded")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-RCT-004: Add Vacancy page opens")
    @allure.description("Clicking Add on Vacancies page should open the Add Vacancy form.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.recruitment
    def test_add_vacancy_page_opens(self, logged_in_page):
        logger.info("=== TEST: test_add_vacancy_page_opens ===")
        rec = RecruitmentPage(logged_in_page)

        with allure.step("Navigate to Vacancies"):
            rec.go_to_vacancies()

        with allure.step("Click Add button"):
            rec.click_add()

        with allure.step("Verify Add Vacancy form URL"):
            url = logged_in_page.url
            logger.info(f"Current URL: {url}")
            assert "/recruitment/addJobVacancy" in url, (
                f"Expected add vacancy URL, got: {url}"
            )
            logger.info("PASS: Add Vacancy page opened")