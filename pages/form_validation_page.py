from playwright.sync_api import Page, expect

from pages.base_page import BasePage

_PATH = "/form-validation"

# Bootstrap adds this class to <form> on submit — triggers feedback visibility
_VALIDATED_FORM = "form.was-validated"


class FormValidationPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._contact_name = page.get_by_label("Contact Name")
        self._contact_number = page.get_by_label("Contact number")
        self._pickup_date = page.get_by_label("PickUp Date")
        self._payment_method = page.get_by_label("Payment Method")
        self._submit = page.get_by_role("button", name="Register")

        # Bootstrap .invalid-feedback — in DOM always, shown only via was-validated
        self._name_feedback = page.locator("input#validationCustom01 ~ .invalid-feedback")
        self._number_feedback = page.locator("input#validationCustom02 ~ .invalid-feedback")
        self._date_feedback = page.locator("input#validationCustom03 ~ .invalid-feedback")
        self._payment_feedback = page.locator("select#validationCustom04 ~ .invalid-feedback")

    # ------------------------------------------------------------------ actions

    def open(self) -> None:
        self.navigate(_PATH)
        self.wait_for_locator(self._submit)

    def fill_contact_name(self, value: str) -> None:
        self._contact_name.fill(value)

    def fill_contact_number(self, value: str) -> None:
        self._contact_number.fill(value)

    def fill_pickup_date(self, value: str) -> None:
        self._pickup_date.fill(value)

    def select_payment_method(self, value: str) -> None:
        self._payment_method.select_option(value)

    def submit(self) -> None:
        self.logger.info("Submitting form")
        self._submit.click()
        # Wait for Bootstrap to apply was-validated to the <form> element
        expect(self.page.locator(_VALIDATED_FORM)).to_be_attached()

    def fill_valid_form(self) -> None:
        self.fill_contact_name("John Doe")
        self.fill_contact_number("1234567890")
        self.fill_pickup_date("2025-12-31")
        self.select_payment_method("card")

    # ------------------------------------------------------------------ queries
    # Bootstrap shows feedback via CSS cascade from the was-validated ancestor.
    # Playwright's is_visible() checks the element's own style, not the cascade.
    # Use evaluate() to read computedStyle, which respects the full CSS chain.

    def _is_feedback_shown(self, locator) -> bool:
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
