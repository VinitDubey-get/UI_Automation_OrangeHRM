from playwright.sync_api import Page, Dialog

from pages.base_page import BasePage

_PATH = "/js-dialogs"


class JsDialogsPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._alert_btn = page.get_by_role("button", name="Js Alert")
        self._confirm_btn = page.get_by_role("button", name="Js Confirm")
        self._prompt_btn = page.get_by_role("button", name="Js Prompt")
        self._result = page.locator("#dialog-response-text")

    # ------------------------------------------------------------------ actions

    def open(self) -> None:
        self.navigate(_PATH)
        self.wait_for_locator(self._alert_btn)

    def trigger_alert_and_accept(self) -> None:
        self.logger.info("Triggering JS Alert → accept")
        self.page.once("dialog", lambda d: d.accept())
        self._alert_btn.click()
        self._result.wait_for(state="visible")

    def trigger_confirm_and_accept(self) -> None:
        self.logger.info("Triggering JS Confirm → accept")
        self.page.once("dialog", lambda d: d.accept())
        self._confirm_btn.click()
        self._result.wait_for(state="visible")

    def trigger_confirm_and_dismiss(self) -> None:
        self.logger.info("Triggering JS Confirm → dismiss")
        self.page.once("dialog", lambda d: d.dismiss())
        self._confirm_btn.click()
        self._result.wait_for(state="visible")

    def trigger_prompt_and_accept(self, text: str) -> None:
        self.logger.info("Triggering JS Prompt → accept with '%s'", text)
        self.page.once("dialog", lambda d: d.accept(text))
        self._prompt_btn.click()
        self._result.wait_for(state="visible")

    def trigger_prompt_and_dismiss(self) -> None:
        self.logger.info("Triggering JS Prompt → dismiss")
        self.page.once("dialog", lambda d: d.dismiss())
        self._prompt_btn.click()
        self._result.wait_for(state="visible")

    # ------------------------------------------------------------------ queries

    def get_result_text(self) -> str:
        return self._result.inner_text().strip()