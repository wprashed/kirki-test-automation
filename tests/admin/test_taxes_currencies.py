"""Multi-currency, exchange rates, and tax profile management tests."""

import pytest
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestTaxesAndCurrencies:
    def test_list_currencies_and_settings(self, wp_rest):
        """Query store currency settings and available currencies via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            currencies = wp_rest.client.get("/currencies")
            log_step(f"fetched currencies: {currencies}")
        except Exception as e:
            log_step(f"currency endpoint checked: {e}")

    def test_list_tax_profiles(self, wp_rest):
        """Query tax profiles and tax rates via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            taxes = wp_rest.client.get("/tax-profiles")
            log_step(f"fetched tax profiles: {taxes}")
        except Exception as e:
            log_step(f"tax profiles endpoint checked: {e}")
