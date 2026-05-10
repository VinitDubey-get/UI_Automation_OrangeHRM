import pytest
import allure
from pages.pim_page import PIMPage
from utils.data_factory import generate_employee
 
@allure.feature('Employee Management')
@allure.story('PIM Module')
class TestEmployee:
 
    @allure.title('Add a new employee successfully')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.employee
    def test_add_employee(self, logged_in_page):
        emp = generate_employee()
        pim = PIMPage(logged_in_page)
        pim.go_to_pim()
        pim.add_employee(emp['first_name'], emp['last_name'])
        assert logged_in_page.locator('.oxd-toast').is_visible()
 
    @allure.title('Search for an existing employee')
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.employee
    def test_search_employee(self, logged_in_page):
        pim = PIMPage(logged_in_page)
        pim.search_employee('Admin')
        count = pim.get_employee_count()
        assert count >= 1, 'Expected at least one employee in search results'
 
    @allure.title('Search returns no results for unknown name')
    @pytest.mark.negative
    @pytest.mark.employee
    def test_search_no_results(self, logged_in_page):
        pim = PIMPage(logged_in_page)
        pim.search_employee('ZZZNOBODY12345')
        msg = logged_in_page.locator('.oxd-table-body .oxd-text').text_content()
        assert 'No Records Found' in msg
 
    @allure.title('Employee list loads with data')
    @pytest.mark.smoke
    @pytest.mark.employee
    def test_employee_list_not_empty(self, logged_in_page):
        pim = PIMPage(logged_in_page)
        pim.go_to_pim()
        count = pim.get_employee_count()
        assert count > 0, 'Employee list should not be empty'
