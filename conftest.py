import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from pages.dynamic_table_page import DynamicTablePage
from pages.form_validation_page import FormValidationPage
from pages.inputs_page import InputsPage
from pages.js_dialogs_page import JsDialogsPage
from pages.login_page import LoginPage
from utils.allure_helpers import attach_screenshot
from utils.config import HEADLESS, SLOW_MO

# ─────────────────────────────────────────────────────────────────── playwright


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Browser:
    browser = playwright_instance.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO)
    yield browser
    browser.close()


# ──────────────────────────────────────────────────────────────────── context


@pytest.fixture(scope="function")
def context(browser: Browser) -> BrowserContext:
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 720},
        locale="en-US",
    )
    yield ctx
    ctx.close()


# ────────────────────────────────────────────────────────────────────── page


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    pg = context.new_page()
    yield pg
    pg.close()


# ──────────────────────────────────────────────────────────────── page objects


@pytest.fixture(scope="function")
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture(scope="function")
def inputs_page(page: Page) -> InputsPage:
    return InputsPage(page)


@pytest.fixture(scope="function")
def form_page(page: Page) -> FormValidationPage:
    return FormValidationPage(page)


@pytest.fixture(scope="function")
def dynamic_table_page(page: Page) -> DynamicTablePage:
    return DynamicTablePage(page)


@pytest.fixture(scope="function")
def js_dialogs_page(page: Page) -> JsDialogsPage:
    return JsDialogsPage(page)


# ────────────────────────────────────────────────────────── screenshot on fail


@pytest.fixture(autouse=True)
def auto_screenshot(page: Page, request: pytest.FixtureRequest):
    yield
    # rep_call is set by pytest after the test body runs
    report = getattr(request.node, "rep_call", None)
    if report and report.failed:
        attach_screenshot(page, name=f"FAIL_{request.node.name}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
