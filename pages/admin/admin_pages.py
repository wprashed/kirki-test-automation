"""WordPress admin login page (wp-login.php)."""

from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logging_setup import log_step


class AdminLoginPage(BasePage):
    url_fragment = "wp-login.php"

    USER_LOGIN = (By.ID, "user_login")
    USER_PASS = (By.ID, "user_pass")
    SUBMIT = (By.ID, "wp-submit")
    LOGIN_FORM = (By.ID, "loginform")
    ERROR = (By.ID, "login_error")

    def open_admin_login(self) -> "AdminLoginPage":
        self.driver.get(self.base_url + "/wp-login.php")
        return self

    def login(self, username: str, password: str) -> None:
        log_step(f"WP admin login as {username}")
        self.find(*self.USER_LOGIN).send_keys(username)
        self.find(*self.USER_PASS).send_keys(password)
        self.click(self.find(*self.SUBMIT))

    def error_text(self) -> str:
        if self.exists(*self.ERROR, timeout=1):
            return self.text_of(*self.ERROR)
        return ""


class AdminDashboardPage(BasePage):
    url_fragment = "wp-admin"

    # The Kirki SPA shell (app/Menu/Root.php) mounts here.
    KIRKI_ROOT = (By.ID, "kirki-ecommerce-root")
    WP_ADMIN_BAR = (By.ID, "wpadminbar")
    HOWDY = (By.CSS_SELECTOR, "#wp-admin-bar-my-account .ab-item")

    def wait_for_dashboard(self) -> "AdminDashboardPage":
        from utils.selenium_helpers import wait_for_spa_root

        self.find(*self.WP_ADMIN_BAR)
        wait_for_spa_root(self.driver)
        return self

    def open_kirki(self) -> "AdminDashboardPage":
        """Open the Kirki eCommerce admin SPA."""
        self.open("wp-admin/admin.php?page=kirki-ecommerce")
        return self.wait_for_dashboard()

    def is_kirki_spa_loaded(self) -> bool:
        root = self.driver.find_element(*self.KIRKI_ROOT)
        return "kirki-ecommerce-root--ready" in (root.get_attribute("class") or "")

    def logout(self) -> None:
        log_step("WP admin logout")
        self.driver.get(self.base_url + "/wp-login.php?action=logout")
        from utils.selenium_helpers import wait_for_url

        wait_for_url(self.driver, "loggedout=true")
        # Confirm on the intermediate logout page.
        self.driver.get(self.base_url + "/wp-login.php")
