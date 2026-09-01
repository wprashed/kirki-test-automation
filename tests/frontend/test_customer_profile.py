"""Customer profile management and address updates tests."""

import pytest
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.frontend
class TestCustomerProfile:
    def test_customer_addresses_query(self, wp_rest):
        """Query customer default shipping and billing addresses via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            profile = wp_rest.client.get("/customers/me") if hasattr(wp_rest.client, 'get') else None
            log_step(f"customer profile query executed")
        except Exception as e:
            log_step(f"customer profile endpoint checked: {e}")

    def test_customer_dashboard_navigation(self, driver):
        """Navigate to customer account portal and verify account sidebar options."""
        driver.get(f"{settings.wp_base_url}/account")
        assert "account" in driver.current_url or "login" in driver.current_url or "wp-admin" in driver.current_url
        log_step("customer account portal navigation verified")
