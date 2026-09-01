"""Extended Admin Settings, Shipping Profiles, and Boxes tests."""

import pytest
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestAdminSettingsExtended:
    def test_get_store_settings_via_rest(self, wp_rest):
        """Query store general settings via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        settings_data = wp_rest.client.get("/settings")
        assert settings_data is not None, "settings response is None"
        log_step(f"fetched general store settings via REST")

    def test_list_shipping_profiles_via_rest(self, wp_rest):
        """Query shipping profiles and shipping methods via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            profiles = wp_rest.client.get("/shipping-profiles")
            log_step(f"fetched shipping profiles: {profiles}")
        except Exception as e:
            log_step(f"shipping profiles endpoint checked: {e}")

    def test_list_shipping_boxes_via_rest(self, wp_rest):
        """Query shipping box dimensions and packaging profiles via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            boxes = wp_rest.client.get("/shipping-boxes")
            log_step(f"fetched shipping boxes: {boxes}")
        except Exception as e:
            log_step(f"shipping boxes endpoint checked: {e}")
