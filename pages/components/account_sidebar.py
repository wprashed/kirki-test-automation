"""Account sidebar navigation (site/account/sidebar.php)."""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from utils.logging_setup import log_step


class AccountSidebar:
    NAV_LINKS = (By.CSS_SELECTOR, ".kecom-account-nav a, .kecom-account-sidebar a")
    LOGOUT_LINK = (By.CSS_SELECTOR, ".kecom-account-nav-link-logout")

    def __init__(self, driver: WebDriver):
        self.driver = driver

    def go_to(self, label: str) -> None:
        log_step(f"account sidebar -> {label}")
        for link in self.driver.find_elements(*self.NAV_LINKS):
            if label.lower() in (link.text or "").lower():
                link.click()
                return
        raise AssertionError(f"account nav link {label!r} not found")

    def logout(self) -> None:
        log_step("account sidebar -> logout")
        self.driver.find_element(*self.LOGOUT_LINK).click()
