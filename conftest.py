import pytest
import json
import allure
from playwright.sync_api import sync_playwright
 
# Load test data
with open('test_data/test_data.json') as f:
    TEST_DATA = json.load(f)
 
@pytest.fixture(scope='session')
def browser_instance():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # Set False for local debugging
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        yield browser
        browser.close()
 
@pytest.fixture(scope='function')
def page(browser_instance):
    context = browser_instance.new_context(
        viewport={'width': 1920, 'height': 1080},
        # record_video_dir='videos/'
    )
    page = context.new_page()
    yield page
    # Attach screenshot on failure
    if hasattr(page, '_failed') and page._failed:
        screenshot = page.screenshot()
        allure.attach(screenshot, name='Failure Screenshot',
                      attachment_type=allure.attachment_type.PNG)
    context.close()
 
@pytest.fixture(scope='function')
def logged_in_page(page):
    """Provide a pre-authenticated page for tests that need login."""
    page.goto(TEST_DATA['base_url'] + '/auth/login')
    page.locator("input[name='username']").fill(TEST_DATA['admin']['username'])
    page.locator("input[name='password']").fill(TEST_DATA['admin']['password'])
    page.locator("button[type='submit']").click()
    page.wait_for_url('**/dashboard/index')
    yield page

 
@pytest.fixture(scope='session')
def base_url():
    return TEST_DATA['base_url']


@pytest.fixture
def admin_credentials():
    return TEST_DATA['admin']
 
def pytest_runtest_makereport(item, call):
    """Mark page as failed for screenshot on failure."""
    if call.when == 'call' and call.excinfo:
        if hasattr(item, 'funcargs') and 'page' in item.funcargs:
            item.funcargs['page']._failed = True
