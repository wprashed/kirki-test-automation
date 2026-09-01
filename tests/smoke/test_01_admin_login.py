"""Smoke: WordPress admin login + Kirki SPA availability."""

import pytest

from pages.admin.admin_pages import AdminDashboardPage, AdminLoginPage
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.smoke
@pytest.mark.order(1)
class TestAdminLogin:
    def test_admin_login_and_kirki_spa(self, driver):
        """Admin can log in via wp-login.php and the Kirki SPA shell mounts."""
        login = AdminLoginPage(driver).open_admin_login()
        login.login(settings.admin_user, settings.admin_password)

        dashboard = AdminDashboardPage(driver)
        dashboard.wait_until_loaded(timeout=20)
        assert "wp-admin" in driver.current_url, (
            f"expected redirect to wp-admin, got {driver.current_url}"
        )
        assert login.error_text() == ""

        # Open the Kirki SPA and wait for the root to be ready.
        dashboard.open_kirki()
        log_step("admin SPA mounted and ready")
        assert dashboard.is_kirki_spa_loaded()
        assert "kirki-ecommerce" in driver.current_url
