from playwright.sync_api import Page, expect

from pages.base_page import BasePage

_PATH = "/js-dialogs"


class JsDialogsPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._alert_btn = page.get_by_role("button", name="Js Alert")
        self._confirm_btn = page.get_by_role("button", name="Js Confirm")
        self._prompt_btn = page.get_by_role("button", name="Js Prompt")
        # The result <p> is always present in DOM; initially contains "Waiting"
        self._result = page.locator("p#result")

    # ------------------------------------------------------------------ actions

    def open(self) -> None:
        self.navigate(_PATH)
        self.wait_for_locator(self._alert_btn)

    def _wait_for_result_update(self) -> None:
        """Block until the result element text changes away from its initial state."""
        expect(self._result).not_to_have_text("Waiting", timeout=10000)

    def trigger_alert_and_accept(self) -> None:
        self.logger.info("Triggering JS Alert → accept")
        self.page.once("dialog", lambda d: d.accept())
        self._alert_btn.click()
        self._wait_for_result_update()

    def trigger_confirm_and_accept(self) -> None:
        self.logger.info("Triggering JS Confirm → accept")
        self.page.once("dialog", lambda d: d.accept())
        self._confirm_btn.click()
        self._wait_for_result_update()

    def trigger_confirm_and_dismiss(self) -> None:
        self.logger.info("Triggering JS Confirm → dismiss")
        self.page.once("dialog", lambda d: d.dismiss())
        self._confirm_btn.click()
        self._wait_for_result_update()

    def trigger_prompt_and_accept(self, text: str) -> None:
        self.logger.info("Triggering JS Prompt → accept with '%s'", text)
        self.page.once("dialog", lambda d: d.accept(text))
        self._prompt_btn.click()
        self._wait_for_result_update()

    def trigger_prompt_and_dismiss(self) -> None:
        self.logger.info("Triggering JS Prompt → dismiss")
        self.page.once("dialog", lambda d: d.dismiss())
        self._prompt_btn.click()
        self._wait_for_result_update()

    # ------------------------------------------------------------------ queries

    def get_result_text(self) -> str:
        return self._result.inner_text().strip()