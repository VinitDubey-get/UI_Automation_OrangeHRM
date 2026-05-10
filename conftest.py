import pytest
import json
import allure
import logging
import os
from playwright.sync_api import sync_playwright

# ── Logging setup ──────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(name)s  —  %(message)s",
    handlers=[
        logging.FileHandler("logs/test_run.log", mode="w"),
        logging.StreamHandler(),          # also prints to console / Jenkins
    ],
)
logger = logging.getLogger("conftest")

# ── Test data ──────────────────────────────────────────────────
with open("test_data/test_data.json") as f:
    TEST_DATA = json.load(f)


# ══════════════════════════════════════════════════════════════
#  BROWSER  (session-scoped – one browser for the whole run)
# ══════════════════════════════════════════════════════════════
@pytest.fixture(scope="session")
def browser_instance():
    logger.info("Launching Chromium browser (headless)")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,                        # False for local visual debug
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        )
        logger.info("Browser launched successfully")
        yield browser
        logger.info("Closing browser")
        browser.close()


# ══════════════════════════════════════════════════════════════
#  PAGE  (function-scoped – fresh context per test)
# ══════════════════════════════════════════════════════════════
@pytest.fixture(scope="function")
def page(browser_instance, request):
    """
    Provides a blank page.  Screenshots are captured after EVERY test
    (pass or fail) and attached to Allure so the report is never blank.
    """
    os.makedirs("screenshots", exist_ok=True)
    context = browser_instance.new_context(
        viewport={"width": 1920, "height": 1080},
    )
    pg = context.new_page()
    logger.info(f"[SETUP]  New page context created for: {request.node.name}")

    yield pg

    # ── Capture screenshot unconditionally ──────────────────
    # This is the FIX for blank screenshots:
    # We screenshot BEFORE closing context, and attach to allure directly.
    try:
        screenshot_bytes = pg.screenshot(full_page=True)
        # Determine label
        outcome = "PASS"
        if hasattr(request.node, "rep_call"):
            if request.node.rep_call.failed:
                outcome = "FAIL"
            elif request.node.rep_call.passed:
                outcome = "PASS"

        label = f"{outcome} — {request.node.name}"
        allure.attach(
            screenshot_bytes,
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )
        logger.info(f"Screenshot attached to Allure: [{label}]")

        # Also save to disk for Jenkins artifact archiving
        safe_name = request.node.name.replace("/", "_").replace(" ", "_")
        disk_path = f"screenshots/{outcome}_{safe_name}.png"
        with open(disk_path, "wb") as f:
            f.write(screenshot_bytes)
        logger.info(f"Screenshot saved to disk: {disk_path}")

    except Exception as e:
        logger.warning(f"Could not capture screenshot: {e}")

    context.close()
    logger.info(f"[TEARDOWN]  Context closed for: {request.node.name}")


# ══════════════════════════════════════════════════════════════
#  LOGGED-IN PAGE  (performs login before yielding)
# ══════════════════════════════════════════════════════════════
@pytest.fixture(scope="function")
def logged_in_page(page, request):
    """Pre-authenticated page.  Login steps are logged and Allure-stepped."""
    base   = TEST_DATA["base_url"]
    user   = TEST_DATA["admin"]["username"]
    pwd    = TEST_DATA["admin"]["password"]

    logger.info(f"[LOGIN]  Navigating to login page: {base}/auth/login")

    with allure.step("Navigate to OrangeHRM login page"):
        page.goto(f"{base}/auth/login")
        page.wait_for_load_state("networkidle")
        logger.info("Login page loaded")

    with allure.step(f"Enter username: {user}"):
        page.locator("input[name='username']").fill(user)
        logger.info(f"Username entered: {user}")

    with allure.step("Enter password"):
        page.locator("input[name='password']").fill(pwd)
        logger.info("Password entered")

    with allure.step("Click Login button"):
        page.locator("button[type='submit']").click()
        logger.info("Login button clicked")

    with allure.step("Wait for dashboard to load"):
        page.wait_for_url("**/dashboard/index", timeout=15000)
        logger.info(f"Dashboard loaded. URL: {page.url}")

    yield page


# ══════════════════════════════════════════════════════════════
#  SIMPLE FIXTURES
# ══════════════════════════════════════════════════════════════
@pytest.fixture(scope="session")
def base_url():
    return TEST_DATA["base_url"]


@pytest.fixture(scope="session")
def admin_credentials():
    return TEST_DATA["admin"]


# ══════════════════════════════════════════════════════════════
#  HOOK — store test outcome so the page fixture can read it
# ══════════════════════════════════════════════════════════════
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)