import pytest
import allure
import logging
from pages.pim_page import PIMPage
from utils.data_factory import generate_employee

logger = logging.getLogger(__name__)


@allure.feature("Employee Management")
@allure.story("PIM Module — Add / Search / Verify")
class TestEmployee:

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-EMP-001: PIM module loads with employee list")
    @allure.description("Navigating to PIM should show a non-empty employee table.")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.employee
    def test_pim_module_loads(self, logged_in_page):
        logger.info("=== TEST: test_pim_module_loads ===")
        pim = PIMPage(logged_in_page)

        with allure.step("Navigate to PIM module"):
            pim.go_to_pim()

        with allure.step("Verify employee list has records"):
            count = pim.get_employee_row_count()
            logger.info(f"Employee rows found: {count}")
            assert count > 0, "Expected at least one employee in the list"
            logger.info("PASS: PIM loads with employee records")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-EMP-002: Add a new employee successfully")
    @allure.description("Filling in first/last name and saving should create a new employee.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.employee
    def test_add_employee(self, logged_in_page):
        logger.info("=== TEST: test_add_employee ===")
        pim = PIMPage(logged_in_page)
        emp = generate_employee()
        logger.info(f"Generated test employee: {emp['first_name']} {emp['last_name']}")

        with allure.step("Navigate to PIM module"):
            pim.go_to_pim()

        with allure.step(f"Add employee: {emp['first_name']} {emp['last_name']}"):
            pim.add_employee(emp["first_name"], emp["last_name"])

        with allure.step("Verify redirect to employee profile page"):
            # After save, OrangeHRM redirects to /pim/viewPersonalDetails/empNumber/xxx
            assert "/pim/viewPersonalDetails/empNumber/" in logged_in_page.url, (
                f"Expected employee profile URL, got: {logged_in_page.url}"
            )
            logger.info(f"PASS: Employee created — profile URL: {logged_in_page.url}")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-EMP-003: Search for known employee 'Admin'")
    @allure.description("Searching for 'Admin' should return at least one matching row.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.employee
    def test_search_employee_found(self, logged_in_page):
        logger.info("=== TEST: test_search_employee_found ===")
        pim = PIMPage(logged_in_page)

        with allure.step("Navigate to PIM module"):
            pim.go_to_pim()

        with allure.step("Search for employee 'Admin'"):
            pim.search_employee("Admin")

        with allure.step("Verify at least one result is returned"):
            count = pim.get_employee_row_count()
            logger.info(f"Results for 'Admin': {count} rows")
            assert count >= 1, "Expected at least one result for search 'Admin'"
            logger.info("PASS: Search returns results for 'Admin'")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-EMP-004: Search returns no results for unknown name")
    @allure.description("Searching for a clearly fake name should show 'No Records Found'.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    @pytest.mark.employee
    def test_search_employee_not_found(self, logged_in_page):
        logger.info("=== TEST: test_search_employee_not_found ===")
        pim = PIMPage(logged_in_page)

        with allure.step("Navigate to PIM module"):
            pim.go_to_pim()

        with allure.step("Search for non-existent employee"):
            pim.search_employee("ZZZNOBODY99999")

        with allure.step("Verify 'No Records Found' message is displayed"):
            no_records = pim.is_no_records_shown()
            logger.info(f"No records shown: {no_records}")
            assert no_records, "Expected 'No Records Found' for unknown employee"
            logger.info("PASS: 'No Records Found' shown for unknown name")

    # ──────────────────────────────────────────────────────────
    @allure.title("TC-EMP-005: Add Employee page opens on clicking Add")
    @allure.description("Clicking Add should navigate to the Add Employee URL.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    @pytest.mark.employee
    def test_add_employee_page_opens(self, logged_in_page):
        logger.info("=== TEST: test_add_employee_page_opens ===")
        pim = PIMPage(logged_in_page)

        with allure.step("Navigate to PIM module"):
            pim.go_to_pim()

        with allure.step("Click Add Employee button"):
            pim.click_add_employee()

        with allure.step("Verify URL is the Add Employee page"):
            url = logged_in_page.url
            logger.info(f"Current URL: {url}")
            assert "/pim/addEmployee" in url, f"Expected Add Employee URL, got: {url}"
            logger.info("PASS: Add Employee page opened correctly")