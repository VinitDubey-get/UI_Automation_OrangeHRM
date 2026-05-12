from contextlib import contextmanager
from typing import Generator

import allure
from playwright.sync_api import Page


def attach_screenshot(page: Page, name: str = "screenshot") -> None:
    """Capture a full-page screenshot and attach it to the Allure report."""
    try:
        screenshot_bytes = page.screenshot(full_page=True)
        allure.attach(
            body=screenshot_bytes,
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception:
        # Never fail a test because of a screenshot issue
        pass


@contextmanager
def allure_step(description: str) -> Generator[None, None, None]:
    """Wrap a block of code in an Allure step for cleaner reporting."""
    with allure.step(description):
        yield