"""Cart summary block (cart/parts/cart-summary.php)."""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from utils.money import parse_money_to_cents


class CartSummary:
    SUBTOTAL = (By.CSS_SELECTOR, ".kecom-cart-summary-item-value")
    ESTIMATE_TOTAL = (By.CSS_SELECTOR, ".kecom-cart-summary-total-value")
    CHECKOUT_BTN = (By.CSS_SELECTOR, ".kecom-cart-summary a.kecom-btn-primary")

    def __init__(self, driver: WebDriver):
        self.driver = driver

    @property
    def subtotal_cents(self) -> int:
        el = self.driver.find_element(*self.SUBTOTAL)
        return parse_money_to_cents(el.text)

    @property
    def estimate_total_cents(self) -> int:
        el = self.driver.find_element(*self.ESTIMATE_TOTAL)
        return parse_money_to_cents(el.text)

    def proceed_to_checkout(self) -> None:
        self.driver.find_element(*self.CHECKOUT_BTN).click()
