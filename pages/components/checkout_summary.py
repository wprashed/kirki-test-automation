"""Checkout order summary block (checkout/parts/order-summary.php).

Alpine updates these values via x-text from cartData; text may briefly show
the server-rendered placeholder before Alpine hydrates, so callers should
wait for expected values with wait_until.
"""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from utils.money import parse_money_to_cents
from utils.selenium_helpers import wait_until


class CheckoutSummary:
    ROWS = (By.CSS_SELECTOR, ".kecom-order-summary .kecom-summary-row")
    LABEL = (By.CSS_SELECTOR, ".kecom-summary-row > span:first-child")
    VALUE = (By.CSS_SELECTOR, ".kecom-summary-value")
    TOTAL = (By.CSS_SELECTOR, ".kecom-summary-row.kecom-total-row .kecom-summary-value")

    def __init__(self, driver: WebDriver):
        self.driver = driver

    def rows(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for row in self.driver.find_elements(*self.ROWS):
            try:
                label = row.find_element(*self.LABEL).text.strip()
                value_el = row.find_element(*self.VALUE)
            except Exception:
                continue
            text = value_el.text.strip()
            if text and text not in ("-", ""):
                try:
                    result[label] = parse_money_to_cents(text)
                except ValueError:
                    continue
        return result

    def get_value(self, label: str) -> int | None:
        return self.rows().get(label)

    def total_cents(self) -> int:
        return parse_money_to_cents(
            self.driver.find_element(*self.TOTAL).text
        )

    def wait_for_total(self, expected_cents: int, timeout: float | None = None) -> None:
        wait_until(
            self.driver,
            lambda _: self._safe_total() == expected_cents,
            timeout=timeout,
            message=f"checkout total {expected_cents} cents",
        )

    def _safe_total(self) -> int | None:
        try:
            return self.total_cents()
        except (ValueError, Exception):
            return None
