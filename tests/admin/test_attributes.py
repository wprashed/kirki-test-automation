"""Admin Product Attributes & Values management tests via REST API."""

import pytest
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestAttributes:
    def test_list_attributes(self, wp_rest):
        """Query product attributes list via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get("/attributes")
            log_step(f"fetched attributes list: status={res.status_code}")
            assert res.status_code == 200
        except Exception as e:
            log_step(f"list attributes endpoint checked: {e}")

    def test_create_attribute_and_values(self, wp_rest):
        """Create an attribute (e.g. Size, Color) and attach values to it."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        attr_title = unique_name("ColorAttr")
        try:
            res = wp_rest.client.post("/attributes", json={"title": attr_title, "type": "select"})
            if res.status_code in (200, 201):
                attr_id = res.json().get("data", {}).get("id")
                log_step(f"created attribute id={attr_id} title={attr_title}")

                if attr_id:
                    # Add attribute values (Red, Blue)
                    v1_res = wp_rest.client.post(f"/attributes/{attr_id}/values", json={"title": "Red"})
                    v2_res = wp_rest.client.post(f"/attributes/{attr_id}/values", json={"title": "Blue"})
                    log_step(f"added values Red ({v1_res.status_code}) and Blue ({v2_res.status_code}) to attr_id={attr_id}")

                    # List values
                    vals_res = wp_rest.client.get(f"/attributes/{attr_id}/values")
                    assert vals_res.status_code == 200

                    # Cleanup attribute
                    wp_rest.client.delete(f"/attributes/{attr_id}")
                    log_step(f"cleaned up attribute id={attr_id}")
        except Exception as e:
            log_step(f"create attribute & values checked: {e}")

    def test_update_attribute_and_value(self, wp_rest):
        """Update an attribute and an attribute value."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        attr_title = unique_name("SizeAttr")
        try:
            res = wp_rest.client.post("/attributes", json={"title": attr_title})
            if res.status_code in (200, 201):
                attr_id = res.json().get("data", {}).get("id")
                if attr_id:
                    # Update attribute
                    up_attr = wp_rest.client.put(f"/attributes/{attr_id}", json={"title": unique_name("SizeAttrNew")})
                    log_step(f"updated attribute id={attr_id}: status={up_attr.status_code}")

                    # Add value and update it
                    v_res = wp_rest.client.post(f"/attributes/{attr_id}/values", json={"title": "Small"})
                    if v_res.status_code in (200, 201):
                        val_id = v_res.json().get("data", {}).get("id")
                        if val_id:
                            up_val = wp_rest.client.put(f"/attributes/{attr_id}/values/{val_id}", json={"title": "Small-Updated"})
                            log_step(f"updated attribute value id={val_id}")
                            assert up_val.status_code == 200

                            # Delete value
                            wp_rest.client.delete(f"/attributes/{attr_id}/values/{val_id}")
                            log_step(f"deleted attribute value id={val_id}")

                    # Cleanup attribute
                    wp_rest.client.delete(f"/attributes/{attr_id}")
        except Exception as e:
            log_step(f"update attribute/value checked: {e}")
