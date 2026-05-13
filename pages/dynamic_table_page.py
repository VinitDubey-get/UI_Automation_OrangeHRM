from typing import List

from playwright.sync_api import Page

from pages.base_page import BasePage

_PATH = "/dynamic-table"


class DynamicTablePage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._table = page.get_by_role("table")
        self._header_row = page.get_by_role("row").first
        self._chrome_label = page.locator("p.bg-warning")

    # ------------------------------------------------------------------ actions

    def open(self) -> None:
        self.navigate(_PATH)
        self.wait_for_locator(self._table)

    def reload(self) -> None:
        self.logger.info("Reloading dynamic table page")
        self.page.reload(wait_until="domcontentloaded", timeout=30000)
        self.wait_for_locator(self._table)

    # ------------------------------------------------------------------ queries

    def get_column_headers(self) -> List[str]:
        # <th> elements inside <thead> — ARIA columnheader role not explicitly set
        headers = self.page.locator("thead th").all()
        return [h.inner_text().strip() for h in headers]

    def get_row_count(self) -> int:
        # Excludes the header row
        rows = self.page.get_by_role("row").all()
        return len(rows) - 1

    def get_cpu_for_process(self, process_name: str) -> str:
        """Find the CPU value for a given process name from the table."""
        headers = self.get_column_headers()
        cpu_index = headers.index("CPU")

        rows = self.page.get_by_role("row").all()
        for row in rows[1:]:  # skip header
            cells = row.get_by_role("cell").all()
            if cells and cells[0].inner_text().strip() == process_name:
                return cells[cpu_index].inner_text().strip()
        return ""

    def get_chrome_label_cpu(self) -> str:
        """Read the CPU value from the yellow reference label."""
        self._chrome_label.wait_for(state="visible")
        # Label text: "Chrome CPU: 7.9%" → extract the value part
        text = self._chrome_label.inner_text().strip()
        return text.split(":")[-1].strip()