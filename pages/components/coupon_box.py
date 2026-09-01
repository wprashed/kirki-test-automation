"""Coupon box on checkout (checkout/parts/coupon-form.php)."""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from utils.selenium_helpers import wait_until


class CouponBox:
    INPUT = (By.ID, "coupon-code")
    APPLY_BTN = (By.CSS_SELECTOR, ".kecom-coupon-form button[type=submit]")
    ERROR = (By.CSS_SELECTOR, ".kecom-coupon-form .kecom-field-error")
    APPLIED_CODE = (By.CSS_SELECTOR, ".kecom-applied-coupon .kecom-coupon-code")
    APPLIED_BADGE = (By.CSS_SELECTOR, ".kecom-coupon-discount")
    REMOVE_BTN = (By.CSS_SELECTOR, ".kecom-applied-coupon button.kecom-btn-link")
    APPLIED_MESSAGE = (By.CSS_SELECTOR, ".kecom-applied-coupon .kecom-text-sm")

    def __init__(self, driver: WebDriver):
        self.driver = driver

    def apply(self, code: str) -> None:
        inp = self.driver.find_element(*self.INPUT)
        inp.clear()
        inp.send_keys(code)
        self.driver.find_element(*self.APPLY_BTN).click()

    def wait_for_applied(self, code: str, timeout: float | None = None) -> None:
        wait_until(
            self.driver,
            lambda _: (self.applied_code() or "").upper() == code.upper(),
            timeout=timeout,
            message=f"coupon {code!r} applied",
        )

    def applied_code(self) -> str:
        els = self.driver.find_elements(*self.APPLIED_CODE)
        return els[0].text.strip() if els else ""

    def applied_discount_badge(self) -> str:
        els = self.driver.find_elements(*self.APPLIED_BADGE)
        return els[0].text.strip() if els else ""

    def remove(self) -> None:
        self.driver.find_element(*self.REMOVE_BTN).click()

    def error_text(self) -> str:
        els = self.driver.find_elements(*self.ERROR)
        return " ".join(e.text for e in els if e.text)
