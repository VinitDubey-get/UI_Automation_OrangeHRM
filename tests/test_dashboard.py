import pytest
import allure
 
@allure.feature('Dashboard')
class TestDashboard:
 
    @allure.title('Dashboard loads after login')
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_dashboard_loads(self, logged_in_page):
        assert '/dashboard/index' in logged_in_page.url
 
    @allure.title('Navigation menu is visible')
    @pytest.mark.smoke
    def test_navigation_visible(self, logged_in_page):
        nav = logged_in_page.locator('.oxd-main-menu')
        assert nav.is_visible()
 
    @allure.title('All key menu items are present')
    @pytest.mark.regression
    def test_menu_items(self, logged_in_page):
        menus = ['Admin', 'PIM', 'Leave', 'Time', 'Recruitment', 'My Info']
        for menu in menus:
            locator = f"//span[text()='{menu}']"
            assert logged_in_page.locator(locator).is_visible(), \
                   f'Menu item {menu} not visible'
 
    @allure.title('Dashboard widgets are rendered')
    @pytest.mark.regression
    def test_dashboard_widgets(self, logged_in_page):
        widgets = logged_in_page.locator('.oxd-grid-item')
        assert widgets.count() > 0, 'Dashboard should have widgets'
