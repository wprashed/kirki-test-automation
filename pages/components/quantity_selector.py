"""Quantity selector helper (used on product + cart pages)."""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


class QuantitySelector:
    INPUT = (By.CSS_SELECTOR, "input[aria-label='Quantity'], .kecom-quantity-input")
    INCREASE = (By.CSS_SELECTOR, "button[aria-label='Increase']")
    DECREASE = (By.CSS_SELECTOR, "button[aria-label='Decrease']")

    def __init__(self, driver: WebDriver, root: WebElement | None = None):
        self.driver = driver
        self.root = root

    def _find(self, by: tuple) -> WebElement:
        if self.root is not None:
            return self.root.find_element(*by)
        return self.driver.find_element(*by)

    @property
    def value(self) -> int:
        el = self._find(self.INPUT)
        return int(el.get_attribute("value") or 1)

    def set(self, quantity: int) -> None:
        el = self._find(self.INPUT)
        el.clear()
        el.send_keys(str(quantity))
        el.send_keys("\ue007")

    def increase(self) -> None:
        self._find(self.INCREASE).click()

    def decrease(self) -> None:
        self._find(self.DECREASE).click()
