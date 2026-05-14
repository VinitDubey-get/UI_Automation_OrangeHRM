import allure
import pytest

from pages.dynamic_table_page import DynamicTablePage


@allure.feature("Dynamic Table")
@pytest.mark.regression
class TestDynamicTable:

    @allure.story("Table renders on load")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_table_is_visible_on_page_load(self, dynamic_table_page: DynamicTablePage):
        dynamic_table_page.open()
        assert dynamic_table_page.get_row_count() >= 1

    @allure.story("Expected column headers present")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_table_contains_expected_column_headers(self, dynamic_table_page: DynamicTablePage):
        dynamic_table_page.open()
        headers = dynamic_table_page.get_column_headers()
        for expected in ("Name", "CPU", "Memory"):
            assert expected in headers, f"Expected column '{expected}' not found in {headers}"

    @allure.story("Row count within bounds")
    @allure.severity(allure.severity_level.NORMAL)
    def test_table_has_expected_number_of_data_rows(self, dynamic_table_page: DynamicTablePage):
        dynamic_table_page.open()
        row_count = dynamic_table_page.get_row_count()
        assert row_count >= 1, "Table should have at least one data row"

    @allure.story("Chrome CPU matches reference label")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_chrome_cpu_in_table_matches_reference_label(
        self, dynamic_table_page: DynamicTablePage
    ):
        dynamic_table_page.open()
        table_cpu = dynamic_table_page.get_cpu_for_process("Chrome")
        label_cpu = dynamic_table_page.get_chrome_label_cpu()
        assert (
            table_cpu == label_cpu
        ), f"Table CPU '{table_cpu}' does not match label CPU '{label_cpu}'"

    @allure.story("Data changes on reload")
    @allure.severity(allure.severity_level.NORMAL)
    def test_table_renders_valid_cpu_values_after_reload(
        self, dynamic_table_page: DynamicTablePage
    ):
        dynamic_table_page.open()
        dynamic_table_page.reload()
        table_cpu = dynamic_table_page.get_cpu_for_process("Chrome")
        label_cpu = dynamic_table_page.get_chrome_label_cpu()
        assert (
            table_cpu == label_cpu
        ), f"After reload — Table CPU '{table_cpu}' does not match label '{label_cpu}'"
