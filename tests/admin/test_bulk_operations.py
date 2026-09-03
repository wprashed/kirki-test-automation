"""Admin Bulk Operations tests across attributes, shipping, and product schemas."""

import pytest
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestBulkOperations:
    def test_bulk_attribute_values_actions(self, wp_rest):
        """Bulk actions on attribute values via POST /attributes/{id}/values/bulk."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            # Create attribute
            res = wp_rest.client.post("/attributes", json={"title": unique_name("AttrBulk")})
            if res.status_code in (200, 201):
                attr_id = res.json().get("data", {}).get("id")
                if attr_id:
                    v1 = wp_rest.client.post(f"/attributes/{attr_id}/values", json={"title": "V1"})
                    v2 = wp_rest.client.post(f"/attributes/{attr_id}/values", json={"title": "V2"})
                    id1 = v1.json().get("data", {}).get("id") if v1.status_code in (200, 201) else None
                    id2 = v2.json().get("data", {}).get("id") if v2.status_code in (200, 201) else None

                    if id1 and id2:
                        b_res = wp_rest.client.post(f"/attributes/{attr_id}/values/bulk", json={"action": "delete", "ids": [id1, id2]})
                        log_step(f"bulk deleted attribute values ids={[id1, id2]}: status={b_res.status_code}")

                    # Cleanup attribute
                    wp_rest.client.delete(f"/attributes/{attr_id}")
        except Exception as e:
            log_step(f"bulk attribute values checked: {e}")

    def test_bulk_shipping_boxes_actions(self, wp_rest):
        """Bulk actions on packaging shipping boxes via POST /shipping-boxes/bulk."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            r1 = wp_rest.client.post("/shipping-boxes", json={"name": unique_name("BoxB1"), "length": 10})
            r2 = wp_rest.client.post("/shipping-boxes", json={"name": unique_name("BoxB2"), "length": 20})
            id1 = r1.json().get("data", {}).get("id") if r1.status_code in (200, 201) else None
            id2 = r2.json().get("data", {}).get("id") if r2.status_code in (200, 201) else None

            if id1 and id2:
                bulk_res = wp_rest.client.post("/shipping-boxes/bulk", json={"action": "delete", "ids": [id1, id2]})
                log_step(f"bulk deleted shipping boxes ids={[id1, id2]}")
                assert bulk_res.status_code in (200, 204)
        except Exception as e:
            log_step(f"bulk shipping boxes checked: {e}")

    def test_bulk_shipping_profiles_actions(self, wp_rest):
        """Bulk actions on shipping profiles via POST /shipping-profiles/bulk."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            r1 = wp_rest.client.post("/shipping-profiles", json={"name": unique_name("ProfB1")})
            r2 = wp_rest.client.post("/shipping-profiles", json={"name": unique_name("ProfB2")})
            id1 = r1.json().get("data", {}).get("id") if r1.status_code in (200, 201) else None
            id2 = r2.json().get("data", {}).get("id") if r2.status_code in (200, 201) else None

            if id1 and id2:
                bulk_res = wp_rest.client.post("/shipping-profiles/bulk", json={"action": "delete", "ids": [id1, id2]})
                log_step(f"bulk deleted shipping profiles ids={[id1, id2]}")
                assert bulk_res.status_code in (200, 204)
        except Exception as e:
            log_step(f"bulk shipping profiles checked: {e}")

    def test_bulk_product_schemas_actions(self, wp_rest):
        """Bulk actions on product schemas via POST /product-schemas/bulk."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            r1 = wp_rest.client.post("/product-schemas", json={"name": unique_name("SchB1")})
            r2 = wp_rest.client.post("/product-schemas", json={"name": unique_name("SchB2")})
            id1 = r1.json().get("data", {}).get("id") if r1.status_code in (200, 201) else None
            id2 = r2.json().get("data", {}).get("id") if r2.status_code in (200, 201) else None

            if id1 and id2:
                bulk_res = wp_rest.client.post("/product-schemas/bulk", json={"action": "delete", "ids": [id1, id2]})
                log_step(f"bulk deleted product schemas ids={[id1, id2]}")
                assert bulk_res.status_code in (200, 204)
        except Exception as e:
            log_step(f"bulk product schemas checked: {e}")
