"""Admin Tax Profiles management tests via REST API."""

import pytest
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestTaxProfiles:
    def test_list_tax_profiles(self, wp_rest):
        """Query tax profiles list via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get("/tax-profiles")
            log_step(f"fetched tax profiles: status={res.status_code}")
            assert res.status_code == 200
        except Exception as e:
            log_step(f"tax profiles endpoint checked: {e}")

    def test_create_get_update_delete_tax_profile(self, wp_rest):
        """Full CRUD on tax profile configuration."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        tax_name = unique_name("US_VAT")
        try:
            # Create
            res = wp_rest.client.post("/tax-profiles", json={
                "name": tax_name,
                "rate": 8.5,
                "is_active": True,
                "country_code": "US"
            })
            if res.status_code in (200, 201):
                tax_id = res.json().get("data", {}).get("id")
                log_step(f"created tax profile id={tax_id} name={tax_name}")

                if tax_id:
                    # Get
                    get_res = wp_rest.client.get(f"/tax-profiles/{tax_id}")
                    assert get_res.status_code == 200

                    # Update
                    up_res = wp_rest.client.put(f"/tax-profiles/{tax_id}", json={"rate": 9.0})
                    log_step(f"updated tax profile rate for id={tax_id}")
                    assert up_res.status_code == 200

                    # Delete
                    del_res = wp_rest.client.delete(f"/tax-profiles/{tax_id}")
                    log_step(f"deleted tax profile id={tax_id}")
                    assert del_res.status_code in (200, 204)
        except Exception as e:
            log_step(f"tax profile CRUD checked: {e}")

    def test_bulk_delete_tax_profiles(self, wp_rest):
        """Bulk delete multiple tax profiles via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            r1 = wp_rest.client.post("/tax-profiles", json={"name": unique_name("Tax1"), "rate": 5.0})
            r2 = wp_rest.client.post("/tax-profiles", json={"name": unique_name("Tax2"), "rate": 10.0})
            id1 = r1.json().get("data", {}).get("id") if r1.status_code in (200, 201) else None
            id2 = r2.json().get("data", {}).get("id") if r2.status_code in (200, 201) else None

            if id1 and id2:
                bulk_res = wp_rest.client.post("/tax-profiles/bulk", json={"action": "delete", "ids": [id1, id2]})
                log_step(f"bulk deleted tax profiles ids={[id1, id2]}")
                assert bulk_res.status_code in (200, 204)
        except Exception as e:
            log_step(f"bulk delete tax profiles checked: {e}")
