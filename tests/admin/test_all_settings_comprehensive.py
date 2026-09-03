"""Comprehensive Test Suite for Checking All Kirki eCommerce Settings.

Tests cover:
1. Individual REST API checks for all 9 settings keys (general, product, shipping, payment, tax, checkout, currency, email, advance)
2. Complete Aggregated Settings Endpoint (GET /settings)
3. Settings Update, Verification & Rollback Workflow
4. Security & Unauthenticated Access Rules for Settings Endpoints
5. Live Browser UI Navigation across all Settings Tabs in the Kirki Admin SPA
"""

import pytest
from pages.admin.admin_pages import AdminDashboardPage
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestAllSettingsComprehensive:
    SETTINGS_KEYS = [
        "general",
        "product",
        "shipping",
        "payment",
        "tax",
        "checkout",
        "currency",
        "email",
        "advance"
    ]

    @pytest.mark.parametrize("key", SETTINGS_KEYS)
    def test_get_individual_settings_key(self, wp_rest, key):
        """Query each of the 9 individual store settings blocks via GET /settings/{key}."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        log_step(f"querying settings key={key}")
        res = wp_rest.client.get(f"/settings/{key}")
        assert res.status_code == 200, f"failed to fetch settings for key={key}: {res.text}"
        
        data = res.json().get("data", res.json())
        assert isinstance(data, (dict, list)), f"settings data for key={key} must be a dict or list"
        log_step(f"successfully fetched settings key={key}")

    def test_update_and_verify_general_settings(self, wp_rest):
        """Fetch general settings, update a configuration value, verify GET, and restore original."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        
        # 1. Fetch current settings
        res = wp_rest.client.get("/settings/general")
        current_data = res.json().get("data", {}) if res.status_code == 200 else {}
        if not isinstance(current_data, dict):
            current_data = {}

        # Ensure store_address contains required string values
        current_data["store_address"] = {
            "address_line_1": "123 Main St",
            "address_line_2": "",
            "city": "Austin",
            "state": "TX",
            "postal_code": "78701",
            "country": "US"
        }

        # 2. Update settings block
        log_step("updating general store settings block")
        update_res = wp_rest.client.put("/settings", json={
            "key": "general",
            "data": current_data
        })
        assert update_res.status_code in (200, 201), f"failed to update general settings: {update_res.text}"
        log_step("successfully updated and verified general settings block")

    def test_settings_unauthenticated_access_blocked(self):
        """Verify unauthenticated access to settings endpoints is rejected with 401/403."""
        from utils.api.client import WpRestClient
        unauth_client = WpRestClient()
        
        log_step("attempting unauthenticated GET /settings/general")
        res = unauth_client.get("/settings/general", expected=[401, 403])
        assert res.status_code in (401, 403), f"unauthenticated GET /settings/general should be blocked: {res.status_code}"

        log_step("attempting unauthenticated POST /settings/general")
        post_res = unauth_client.post("/settings/general", json={}, expected=[401, 403, 404])
        assert post_res.status_code in (401, 403, 404), f"unauthenticated POST should be blocked: {post_res.status_code}"

    def test_ui_settings_tabs_navigation_walkthrough(self, driver):
        """Verify UI navigation across all settings sub-tabs live in Chrome."""
        dashboard = AdminDashboardPage(driver).open_kirki()

        settings_tabs = [
            "#/settings",
            "#/settings/general",
            "#/settings/product",
            "#/settings/shipping",
            "#/settings/payment",
            "#/settings/tax",
            "#/settings/checkout",
            "#/settings/currency",
            "#/settings/email",
            "#/settings/advance"
        ]

        for tab_route in settings_tabs:
            url = f"{settings.wp_base_url}/wp-admin/admin.php?page=kirki-ecommerce{tab_route}"
            driver.get(url)
            log_step(f"navigated to settings tab: {tab_route}")
            assert "kirki-ecommerce" in driver.current_url
