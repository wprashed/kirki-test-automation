"""Order success / failed pages (site/order-success.php, site/order-failed.php)."""

from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.money import parse_money_to_cents


class OrderSuccessPage(BasePage):
    url_fragment = "checkout"

    PAGE = (By.CSS_SELECTOR, ".kecom-order-success-page")
    TITLE = (By.CSS_SELECTOR, ".kecom-order-success-title")
    ROWS = (By.CSS_SELECTOR, ".kecom-order-success-row")
    ROW_KEY = (By.CSS_SELECTOR, ".kecom-order-success-row-key")
    ROW_VALUE = (By.CSS_SELECTOR, ".kecom-order-success-row-value")
    TOTAL_VALUE = (By.CSS_SELECTOR, ".kecom-order-success-total-value")
    CONTINUE_SHOPPING = (By.CSS_SELECTOR, ".kecom-order-success-actions a")

    def wait_for_success(self) -> "OrderSuccessPage":
        from utils.selenium_helpers import wait_until

        def _ready(_) -> bool:
            try:
                return bool(self.driver.find_element(*self.PAGE))
            except Exception:
                return False

        wait_until(self.driver, _ready, message="order success page")
        return self

    def order_rows(self) -> dict[str, str]:
        """Map of row key -> value (e.g. {'Invoice Number': '...', 'Payment Status': 'Paid'})."""
        result: dict[str, str] = {}
        for row in self.driver.find_elements(*self.ROWS):
            keys = row.find_elements(*self.ROW_KEY)
            values = row.find_elements(*self.ROW_VALUE)
            for k, v in zip(keys, values):
                result[k.text.strip()] = v.text.strip()
        return result

    def invoice_number(self) -> str:
        rows = self.order_rows()
        return rows.get("Invoice Number", "")

    def payment_status(self) -> str:
        return self.order_rows().get("Payment Status", "")

    @property
    def total_cents(self) -> int:
        return parse_money_to_cents(self.text_of(*self.TOTAL_VALUE))


class OrderFailedPage(BasePage):
    url_fragment = "checkout"

    PAGE = (By.CSS_SELECTOR, ".kecom-order-failed-page")
    TITLE = (By.CSS_SELECTOR, ".kecom-order-failed-title")
    TRY_AGAIN = (By.CSS_SELECTOR, ".kecom-order-failed-actions a.kecom-btn-destructive")

    def wait_for_failed(self) -> "OrderFailedPage":
        from utils.selenium_helpers import wait_until

        wait_until(
            self.driver,
            lambda _: bool(self.driver.find_elements(*self.PAGE)),
            message="order failed page",
        )
        return self
