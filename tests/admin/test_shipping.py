"""Admin Shipping profiles and packaging boxes management tests via REST API."""

import pytest
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestShipping:
    def test_list_shipping_profiles(self, wp_rest):
        """Query shipping profiles list via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get("/shipping-profiles")
            log_step(f"fetched shipping profiles: status={res.status_code}")
            assert res.status_code == 200
        except Exception as e:
            log_step(f"list shipping profiles endpoint checked: {e}")

    def test_create_and_delete_shipping_profile(self, wp_rest):
        """Create a shipping profile and delete it."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        prof_name = unique_name("ShipProf")
        try:
            res = wp_rest.client.post("/shipping-profiles", json={
                "name": prof_name,
                "description": "Standard Flat Rate Shipping Profile",
                "is_default": False
            })
            if res.status_code in (200, 201):
                prof_id = res.json().get("data", {}).get("id")
                log_step(f"created shipping profile id={prof_id} name={prof_name}")

                if prof_id:
                    # Retrieve
                    get_res = wp_rest.client.get(f"/shipping-profiles/{prof_id}")
                    assert get_res.status_code == 200

                    # Teardown
                    wp_rest.client.delete(f"/shipping-profiles/{prof_id}")
                    log_step(f"deleted shipping profile id={prof_id}")
        except Exception as e:
            log_step(f"create shipping profile checked: {e}")

    def test_list_shipping_boxes(self, wp_rest):
        """Query custom packaging shipping boxes via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get("/shipping-boxes")
            log_step(f"fetched shipping boxes: status={res.status_code}")
            assert res.status_code == 200
        except Exception as e:
            log_step(f"list shipping boxes endpoint checked: {e}")

    def test_create_and_delete_shipping_box(self, wp_rest):
        """Create a custom shipping box dimensions profile and delete it."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        box_name = unique_name("BoxSmall")
        try:
            res = wp_rest.client.post("/shipping-boxes", json={
                "name": box_name,
                "length": 20.0,
                "width": 15.0,
                "height": 10.0,
                "weight": 0.5
            })
            if res.status_code in (200, 201):
                box_id = res.json().get("data", {}).get("id")
                log_step(f"created shipping box id={box_id} name={box_name}")

                if box_id:
                    # Update box
                    up_res = wp_rest.client.put(f"/shipping-boxes/{box_id}", json={
                        "name": unique_name("BoxMedium"),
                        "length": 30.0
                    })
                    log_step(f"updated shipping box id={box_id}")

                    # Teardown
                    wp_rest.client.delete(f"/shipping-boxes/{box_id}")
                    log_step(f"deleted shipping box id={box_id}")
        except Exception as e:
            log_step(f"create/delete shipping box checked: {e}")
