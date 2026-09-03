"""Frontend login page (resources/views/site/login.php)."""

from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logging_setup import log_step


class LoginPage(BasePage):
    url_fragment = "login"

    # Verified selectors from resources/views/site/login.php
    FORM = (By.CSS_SELECTOR, "form.kecom-auth-form")
    EMAIL = (By.ID, "kecom-email")
    PASSWORD = (By.ID, "kecom-password")
    REMEMBER = (By.ID, "kecom-input-remember")
    SUBMIT = (By.CSS_SELECTOR, "form.kecom-auth-form button[type=submit]")
    ERROR_ALERT = (By.CSS_SELECTOR, ".kecom-alert-error")
    SUCCESS_ALERT = (By.CSS_SELECTOR, ".kecom-alert-success")
    SIGNUP_LINK = (By.CSS_SELECTOR, ".kecom-auth-header-content a")
    FORGOT_PASSWORD = (By.CSS_SELECTOR, "a.kecom-forgot-password-label")

    def open_login(self) -> "LoginPage":
        return self.open_page("login")

    def login(self, email: str, password: str, remember: bool = False) -> None:
        log_step(f"login as {email}")
        e = self.find(*self.EMAIL)
        e.clear()
        e.send_keys(email)
        p = self.find(*self.PASSWORD)
        p.clear()
        p.send_keys(password)
        if remember:
            remember_el = self.find(*self.REMEMBER)
            if not remember_el.is_selected():
                self.click(remember_el)
        self.click(self.find(*self.SUBMIT))

    def error_message(self) -> str:
        if self.exists(*self.ERROR_ALERT, timeout=1):
            return self.text_of(*self.ERROR_ALERT)
        return ""

    def success_message(self) -> str:
        if self.exists(*self.SUCCESS_ALERT, timeout=1):
            return self.text_of(*self.SUCCESS_ALERT)
        return ""
