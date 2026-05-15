from playwright.sync_api import Page, expect

from pages.base_page import BasePage

_PATH = "/js-dialogs"


class JsDialogsPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self._alert_btn = page.get_by_role("button", name="Js Alert")
        self._confirm_btn = page.get_by_role("button", name="Js Confirm")
        self._prompt_btn = page.get_by_role("button", name="Js Prompt")

        self._result = page.locator("#dialog-response")

    # ------------------------------------------------------------------ actions

    def open(self) -> None:
        self.navigate(_PATH)
        self.wait_for_locator(self._alert_btn)

    def _wait_for_result_update(self) -> None:
        expect(self._result).not_to_have_text("Waiting", timeout=10000)

    def _handle_dialog(self, trigger_action, handler) -> None:
        self.page.once("dialog", handler)
        trigger_action()

    # ------------------------------------------------------------------ alert

    def trigger_alert_and_accept(self) -> None:
        self.logger.info("Triggering JS Alert → accept")

        self._handle_dialog(self._alert_btn.click, lambda dialog: dialog.accept())

        self._wait_for_result_update()

    # ------------------------------------------------------------------ confirm

    def trigger_confirm_and_accept(self) -> None:
        self.logger.info("Triggering JS Confirm → accept")

        self._handle_dialog(self._confirm_btn.click, lambda dialog: dialog.accept())

        self._wait_for_result_update()

    def trigger_confirm_and_dismiss(self) -> None:
        self.logger.info("Triggering JS Confirm → dismiss")

        self._handle_dialog(self._confirm_btn.click, lambda dialog: dialog.dismiss())

        self._wait_for_result_update()

    # ------------------------------------------------------------------ prompt

    def trigger_prompt_and_accept(self, text: str) -> None:
        self.logger.info("Triggering JS Prompt → accept with '%s'", text)

        self._handle_dialog(self._prompt_btn.click, lambda dialog: dialog.accept(text))

        self._wait_for_result_update()

    def trigger_prompt_and_dismiss(self) -> None:
        self.logger.info("Triggering JS Prompt → dismiss")

        self._handle_dialog(self._prompt_btn.click, lambda dialog: dialog.dismiss())

        self._wait_for_result_update()

    # ------------------------------------------------------------------ queries

    def get_result_text(self) -> str:
        text = self._result.text_content() or ""
        return text.strip()
