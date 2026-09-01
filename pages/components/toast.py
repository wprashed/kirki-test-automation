"""Add-to-cart toast feedback (site.js toast component, kecom-toast-* classes)."""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from utils.selenium_helpers import wait_until


class Toast:
    CONTAINER = (By.CSS_SELECTOR, ".kecom-toast-container")
    ITEMS = (By.CSS_SELECTOR, ".kecom-toast-item")
    TITLE = (By.CSS_SELECTOR, ".kecom-toast-title")
    DESCRIPTION = (By.CSS_SELECTOR, ".kecom-toast-description")

    def __init__(self, driver: WebDriver):
        self.driver = driver

    def texts(self) -> list[str]:
        result: list[str] = []
        for item in self.driver.find_elements(*self.ITEMS):
            text = " ".join(
                e.text for e in item.find_elements(*self.TITLE)
            ) or item.text
            if text:
                result.append(text)
        return result

    def wait_for(self, text_fragment: str, timeout: float | None = None) -> str:
        def _check(_) -> str:
            for t in self.texts():
                if text_fragment.lower() in t.lower():
                    return t
            return ""

        return wait_until(self.driver, _check, timeout=timeout,
                          message=f"toast {text_fragment!r}")
