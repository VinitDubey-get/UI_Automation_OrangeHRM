import allure
import pytest

from pages.inputs_page import InputsPage


@allure.feature("Web Inputs")
@pytest.mark.regression
class TestInputs:

    @allure.story("Enter numeric value")
    @allure.severity(allure.severity_level.NORMAL)
    def test_enter_valid_number_reflects_in_field(self, inputs_page: InputsPage):
        inputs_page.open()
        inputs_page.enter_value("42")
        assert inputs_page.get_input_value() == "42"

    @allure.story("Clear input field")
    @allure.severity(allure.severity_level.NORMAL)
    def test_clear_input_results_in_empty_value(self, inputs_page: InputsPage):
        inputs_page.open()
        inputs_page.enter_value("99")
        inputs_page.clear_input()
        assert inputs_page.get_input_value() == ""

    @allure.story("Large number input")
    @allure.severity(allure.severity_level.MINOR)
    def test_large_number_is_accepted(self, inputs_page: InputsPage):
        inputs_page.open()
        inputs_page.enter_value("9999999")
        assert inputs_page.get_input_value() == "9999999"

    @allure.story("Arrow key increments value")
    @allure.severity(allure.severity_level.MINOR)
    def test_arrow_up_increments_value(self, inputs_page: InputsPage):
        inputs_page.open()
        inputs_page.enter_value("10")
        inputs_page.press_key("ArrowUp")
        assert inputs_page.get_input_value() == "11"
