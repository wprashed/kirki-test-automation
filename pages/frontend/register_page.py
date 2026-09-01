"""Frontend registration page (resources/views/site/register.php)."""

from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logging_setup import log_step


class RegisterPage(BasePage):
    url_fragment = "register"

    FORM = (By.CSS_SELECTOR, "form.kecom-auth-form")
    FIRST_NAME = (By.ID, "kecom-first-name")
    LAST_NAME = (By.ID, "kecom-last-name")
    EMAIL = (By.ID, "kecom-email")
    PASSWORD = (By.ID, "kecom-password")
    PASSWORD_CONFIRM = (By.ID, "kecom-password_confirmation")
    SUBMIT = (By.CSS_SELECTOR, "form.kecom-auth-form button[type=submit]")
    ERROR_ALERT = (By.CSS_SELECTOR, ".kecom-alert-error")
    FIELD_ERRORS = (By.CSS_SELECTOR, ".kecom-field-error")

    def open_register(self) -> "RegisterPage":
        return self.open_page("register")

    def register(self, first_name: str, last_name: str, email: str,
                 password: str) -> None:
        log_step(f"register customer {email}")
        self.find(*self.FIRST_NAME).send_keys(first_name)
        self.find(*self.LAST_NAME).send_keys(last_name)
        self.find(*self.EMAIL).send_keys(email)
        self.find(*self.PASSWORD).send_keys(password)
        self.find(*self.PASSWORD_CONFIRM).send_keys(password)
        self.click(self.find(*self.SUBMIT))

    def field_error_texts(self) -> list[str]:
        return [el.text for el in self.find_many(*self.FIELD_ERRORS) if el.text]
