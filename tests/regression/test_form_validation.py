import allure
import pytest

from pages.form_validation_page import FormValidationPage


@allure.feature("Form Validation")
@pytest.mark.regression
class TestFormValidation:

    @allure.story("Empty form submission")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_submit_empty_form_shows_all_field_errors(self, form_page: FormValidationPage):
        form_page.open()
        form_page.submit()
        assert form_page.is_name_feedback_visible()
        assert form_page.is_number_feedback_visible()
        assert form_page.is_date_feedback_visible()
        assert form_page.is_payment_feedback_visible()

    @allure.story("Missing contact name")
    @allure.severity(allure.severity_level.NORMAL)
    def test_missing_name_shows_name_feedback(self, form_page: FormValidationPage):
        form_page.open()
        form_page.fill_contact_number("1234567890")
        form_page.fill_pickup_date("2025-12-01")
        form_page.select_payment_method("cash on delivery")
        form_page.submit()
        assert form_page.is_name_feedback_visible()
        assert not form_page.is_number_feedback_visible()

    @allure.story("Missing contact number")
    @allure.severity(allure.severity_level.NORMAL)
    def test_missing_number_shows_number_feedback(self, form_page: FormValidationPage):
        form_page.open()
        form_page.fill_contact_name("Jane Doe")
        form_page.fill_pickup_date("2025-12-01")
        form_page.select_payment_method("card")
        form_page.submit()
        assert form_page.is_number_feedback_visible()
        assert not form_page.is_name_feedback_visible()

    @allure.story("Name feedback message content")
    @allure.severity(allure.severity_level.MINOR)
    def test_name_feedback_has_expected_message(self, form_page: FormValidationPage):
        form_page.open()
        form_page.submit()
        feedback = form_page.get_name_feedback()
        assert feedback != ""

    @allure.story("Valid complete form submission")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_valid_form_has_no_visible_errors(self, form_page: FormValidationPage):
        form_page.open()
        form_page.fill_valid_form()
        form_page.submit()
        assert not form_page.is_name_feedback_visible()
        assert not form_page.is_number_feedback_visible()
