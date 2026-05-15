import re

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import expect

from pages.base_page import BasePage

_PATH = "/form-validation"

# Bootstrap adds this class to <form> on submit — triggers feedback visibility
_VALIDATED_FORM = "form.was-validated"


class FormValidationPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._form = page.locator("form.needs-validation")
        self._contact_name = page.get_by_label("Contact Name")
        self._contact_number = page.locator("input[name='contactnumber']")
        self._pickup_date = page.locator("input[type='date']")
        self._payment_method = page.get_by_label("Payment Method")
        self._submit = page.get_by_role("button", name="Register")

        # Bootstrap .invalid-feedback — in DOM always, shown only via was-validated
        self._name_feedback = (
            page.locator("label:has-text('Contact Name')")
            .locator("..")
            .locator(".invalid-feedback")
        )
        self._number_feedback = (
            page.locator("label:has-text('Contact number')")
            .locator("..")
            .locator(".invalid-feedback")
        )
        self._date_feedback = (
            page.locator("label:has-text('PickUp Date')").locator("..").locator(".invalid-feedback")
        )
        self._payment_feedback = (
            page.locator("label:has-text('Payment Method')")
            .locator("..")
            .locator(".invalid-feedback")
        )

    # ------------------------------------------------------------------ actions

    def open(self) -> None:
        self.navigate(_PATH)
        self.wait_for_locator(self._submit)
        self._clear_autofill()

    def fill_contact_name(self, value: str) -> None:
        self._contact_name.fill(value)

    def fill_contact_number(self, value: str) -> None:
        self._contact_number.fill(value)

    def fill_pickup_date(self, value: str) -> None:
        self._pickup_date.fill(value)

    def select_payment_method(self, value: str) -> None:
        self._payment_method.select_option(label=value)

    def submit(self) -> None:
        self.logger.info("Submitting form")
        self._submit.scroll_into_view_if_needed()
        self._submit.click()
        # Valid submissions navigate to confirmation; invalid ones stay and add was-validated.
        try:
            self.page.wait_for_url("**/form-confirmation", timeout=5000)
        except PlaywrightTimeoutError:
            expect(self._form).to_have_class(re.compile(r"\bwas-validated\b"))

    def fill_valid_form(self) -> None:
        self.fill_contact_name("John Doe")
        self.fill_contact_number("123-1234567")
        self.fill_pickup_date("2025-12-31")
        self.select_payment_method("card")

    def _clear_autofill(self) -> None:
        # Ensure prior runs or browser autofill do not affect validation
        self._contact_name.fill("")
        self._contact_number.fill("")
        self._pickup_date.fill("")

    # ------------------------------------------------------------------ queries
    # Bootstrap shows feedback via CSS cascade from the was-validated ancestor.
    # Playwright's is_visible() checks the element's own style, not the cascade.
    # Use evaluate() to read computedStyle, which respects the full CSS chain.

    def _is_feedback_shown(self, locator) -> bool:
        if locator.count() == 0:
            return False
        return locator.evaluate("el => getComputedStyle(el).display !== 'none'")

    def is_name_feedback_visible(self) -> bool:
        return self._is_feedback_shown(self._name_feedback)

    def is_number_feedback_visible(self) -> bool:
        return self._is_feedback_shown(self._number_feedback)

    def is_date_feedback_visible(self) -> bool:
        return self._is_feedback_shown(self._date_feedback)

    def is_payment_feedback_visible(self) -> bool:
        return self._is_feedback_shown(self._payment_feedback)

    def get_name_feedback(self) -> str:
        return self._name_feedback.inner_text().strip()

    def get_number_feedback(self) -> str:
        return self._number_feedback.inner_text().strip()
