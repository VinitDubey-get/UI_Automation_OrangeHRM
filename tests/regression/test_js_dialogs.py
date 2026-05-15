import allure
import pytest

from pages.js_dialogs_page import JsDialogsPage


@allure.feature("JavaScript Dialogs")
@pytest.mark.regression
class TestJsDialogs:

    @allure.story("Alert dialog accepted")
    @allure.severity(allure.severity_level.NORMAL)
    def test_alert_accept_shows_success_result(self, js_dialogs_page: JsDialogsPage):
        js_dialogs_page.open()
        js_dialogs_page.trigger_alert_and_accept()
        result = js_dialogs_page.get_result_text()
        assert "ok" in result.lower() or "alert" in result.lower()

    @allure.story("Confirm dialog accepted")
    @allure.severity(allure.severity_level.NORMAL)
    def test_confirm_accept_shows_confirmed_result(self, js_dialogs_page: JsDialogsPage):
        js_dialogs_page.open()
        js_dialogs_page.trigger_confirm_and_accept()
        result = js_dialogs_page.get_result_text()
        assert "ok" in result.lower() or "confirm" in result.lower()

    @allure.story("Confirm dialog dismissed")
    @allure.severity(allure.severity_level.NORMAL)
    def test_confirm_dismiss_shows_cancelled_result(self, js_dialogs_page: JsDialogsPage):
        js_dialogs_page.open()
        js_dialogs_page.trigger_confirm_and_dismiss()
        result = js_dialogs_page.get_result_text()
        assert "cancel" in result.lower() or "false" in result.lower()

    @allure.story("Prompt dialog accepted with input")
    @allure.severity(allure.severity_level.NORMAL)
    def test_prompt_accept_reflects_entered_text(self, js_dialogs_page: JsDialogsPage):
        js_dialogs_page.open()
        js_dialogs_page.trigger_prompt_and_accept("hello playwright")
        result = js_dialogs_page.get_result_text()
        assert "hello playwright" in result.lower()

    @allure.story("Prompt dialog dismissed")
    @allure.severity(allure.severity_level.MINOR)
    def test_prompt_dismiss_shows_null_or_cancel_result(self, js_dialogs_page: JsDialogsPage):
        js_dialogs_page.open()
        js_dialogs_page.trigger_prompt_and_dismiss()
        result = js_dialogs_page.get_result_text()
        assert result.lower() != "waiting"
        assert (
            result == ""
            or "null" in result.lower()
            or "cancel" in result.lower()
            or "false" in result.lower()
        )
