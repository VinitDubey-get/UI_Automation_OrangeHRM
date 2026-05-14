from playwright.sync_api import Page

from pages.base_page import BasePage

_PATH = "/inputs"


class InputsPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._input = page.get_by_role("spinbutton")

    # ------------------------------------------------------------------ actions

    def open(self) -> None:
        self.navigate(_PATH)
        self.wait_for_locator(self._input)

    def enter_value(self, value: str) -> None:
        self.logger.info("Entering value: %s", value)
        self._input.fill(value)

    def clear_input(self) -> None:
        self.logger.info("Clearing input field")
        self._input.clear()

    def press_key(self, key: str) -> None:
        self._input.press(key)

    # ------------------------------------------------------------------ queries

    def get_input_value(self) -> str:
        return self._input.input_value()
