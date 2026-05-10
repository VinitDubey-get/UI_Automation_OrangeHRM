import allure
import os
from datetime import datetime

def take_screenshot(page,name='screenshot'):
  """Attach Screenshot to Allure Report"""
  ts=datetime.now().strftime('%Y%m%d_%H%M%S')
  path=f'screenshots/{name}_{ts}.png'
  os.makedirs('screenshots',exist_ok=True)
  page.screenshot(path=path)
  with open(path, 'rb') as f:
        allure.attach(f.read(), name=name,
                      attachment_type=allure.attachment_type.PNG)
  return path


def wait_for_toast(page, timeout=5000):
    """Wait for OrangeHRM success toast message."""
    page.wait_for_selector('.oxd-toast', timeout=timeout)
    return page.locator('.oxd-toast').text_content()

