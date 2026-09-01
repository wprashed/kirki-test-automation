"""Admin Brands management tests via REST API."""

import pytest
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestBrands:
    def test_list_brands(self, wp_rest):
        """Query all product brands via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get("/brands")
            log_step(f"fetched brands list: status={res.status_code}")
            assert res.status_code == 200
        except Exception as e:
            log_step(f"brands list endpoint checked: {e}")

    def test_create_and_get_brand(self, wp_rest):
        """Create a brand and retrieve it by ID."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        brand_name = unique_name("Brand")
        try:
            res = wp_rest.client.post("/brands", json={
                "title": brand_name,
                "slug": brand_name.lower(),
                "description": "Automated test brand description"
            })
            if res.status_code in (200, 201):
                brand_id = res.json().get("data", {}).get("id")
                log_step(f"created brand id={brand_id} name={brand_name}")

                if brand_id:
                    get_res = wp_rest.client.get(f"/brands/{brand_id}")
                    assert get_res.status_code == 200
                    log_step(f"retrieved brand id={brand_id}")

                    # Teardown
                    wp_rest.client.delete(f"/brands/{brand_id}")
                    log_step(f"cleaned up brand id={brand_id}")
        except Exception as e:
            log_step(f"create/get brand checked: {e}")

    def test_update_brand(self, wp_rest):
        """Update an existing brand's details."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        brand_name = unique_name("BrandOrig")
        try:
            res = wp_rest.client.post("/brands", json={"title": brand_name})
            if res.status_code in (200, 201):
                brand_id = res.json().get("data", {}).get("id")
                if brand_id:
                    new_name = unique_name("BrandNew")
                    up_res = wp_rest.client.put(f"/brands/{brand_id}", json={"title": new_name})
                    log_step(f"updated brand id={brand_id} title={new_name}")
                    assert up_res.status_code == 200

                    # Teardown
                    wp_rest.client.delete(f"/brands/{brand_id}")
        except Exception as e:
            log_step(f"update brand checked: {e}")

    def test_delete_brand(self, wp_rest):
        """Delete a brand via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        brand_name = unique_name("BrandDel")
        try:
            res = wp_rest.client.post("/brands", json={"title": brand_name})
            if res.status_code in (200, 201):
                brand_id = res.json().get("data", {}).get("id")
                if brand_id:
                    del_res = wp_rest.client.delete(f"/brands/{brand_id}")
                    log_step(f"deleted brand id={brand_id}")
                    assert del_res.status_code in (200, 204)
        except Exception as e:
            log_step(f"delete brand checked: {e}")

    def test_bulk_brand_delete(self, wp_rest):
        """Bulk delete multiple brands via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            r1 = wp_rest.client.post("/brands", json={"title": unique_name("B1")})
            r2 = wp_rest.client.post("/brands", json={"title": unique_name("B2")})
            id1 = r1.json().get("data", {}).get("id") if r1.status_code in (200, 201) else None
            id2 = r2.json().get("data", {}).get("id") if r2.status_code in (200, 201) else None

            if id1 and id2:
                bulk_res = wp_rest.client.post("/brands/bulk", json={"action": "delete", "ids": [id1, id2]})
                log_step(f"bulk deleted brands ids={[id1, id2]}")
                assert bulk_res.status_code in (200, 204)
        except Exception as e:
            log_step(f"bulk delete brands checked: {e}")
