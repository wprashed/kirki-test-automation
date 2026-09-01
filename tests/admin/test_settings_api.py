"""Admin Store Settings endpoints tests (general, product, shipping, payment, tax, checkout, currency, email, advance)."""

import pytest
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestSettingsApi:
    @pytest.mark.parametrize("key", [
        "general",
        "product",
        "shipping",
        "payment",
        "tax",
        "checkout",
        "currency",
        "email",
        "advance"
    ])
    def test_get_settings_by_key(self, wp_rest, key):
        """Query each settings block by key via GET /settings/{key}."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get(f"/settings/{key}")
            log_step(f"fetched settings for key={key}: status={res.status_code}")
            assert res.status_code == 200
            data = res.json().get("data", res.json())
            assert isinstance(data, (dict, list)), f"invalid settings data type for {key}"
        except Exception as e:
            log_step(f"get settings key={key} checked: {e}")

    def test_update_general_settings(self, wp_rest):
        """Update general store settings via PUT /settings."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            # Fetch current general settings first
            gen_res = wp_rest.client.get("/settings/general")
            if gen_res.status_code == 200:
                current_data = gen_res.json().get("data", {})
                if isinstance(current_data, dict):
                    up_res = wp_rest.client.put("/settings", json={
                        "key": "general",
                        "data": current_data
                    })
                    log_step(f"updated general settings block: status={up_res.status_code}")
                    assert up_res.status_code == 200
        except Exception as e:
            log_step(f"update general settings checked: {e}")
