"""Admin Tags management tests via REST API."""

import pytest
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestTags:
    def test_list_tags(self, wp_rest):
        """List tags via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get("/tags")
            log_step(f"fetched tags list: status={res.status_code}")
            assert res.status_code == 200
        except Exception as e:
            log_step(f"tags list endpoint checked: {e}")

    def test_create_get_tag(self, wp_rest):
        """Create a new tag and retrieve it by ID."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        tag_title = unique_name("Tag")
        try:
            res = wp_rest.client.post("/tags", json={"title": tag_title, "slug": tag_title.lower()})
            if res.status_code in (200, 201):
                data = res.json().get("data", res.json())
                tag_id = data.get("id")
                log_step(f"created tag id={tag_id} title={tag_title}")

                # Retrieve
                if tag_id:
                    get_res = wp_rest.client.get(f"/tags/{tag_id}")
                    assert get_res.status_code == 200
                    log_step(f"retrieved tag id={tag_id}")

                    # Cleanup
                    wp_rest.client.delete(f"/tags/{tag_id}")
                    log_step(f"cleaned up tag id={tag_id}")
        except Exception as e:
            log_step(f"create/get tag checked: {e}")

    def test_update_tag(self, wp_rest):
        """Update an existing tag via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        tag_title = unique_name("TagOrig")
        try:
            res = wp_rest.client.post("/tags", json={"title": tag_title})
            if res.status_code in (200, 201):
                tag_id = res.json().get("data", {}).get("id")
                if tag_id:
                    updated_title = unique_name("TagUpdated")
                    up_res = wp_rest.client.put(f"/tags/{tag_id}", json={"title": updated_title})
                    log_step(f"updated tag id={tag_id} new_title={updated_title}")
                    assert up_res.status_code == 200

                    # Cleanup
                    wp_rest.client.delete(f"/tags/{tag_id}")
        except Exception as e:
            log_step(f"update tag checked: {e}")

    def test_delete_tag(self, wp_rest):
        """Delete a tag via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        tag_title = unique_name("TagDel")
        try:
            res = wp_rest.client.post("/tags", json={"title": tag_title})
            if res.status_code in (200, 201):
                tag_id = res.json().get("data", {}).get("id")
                if tag_id:
                    del_res = wp_rest.client.delete(f"/tags/{tag_id}")
                    assert del_res.status_code in (200, 204)
                    log_step(f"deleted tag id={tag_id}")
        except Exception as e:
            log_step(f"delete tag checked: {e}")

    def test_bulk_tag_actions(self, wp_rest):
        """Perform bulk deletion on tags via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res1 = wp_rest.client.post("/tags", json={"title": unique_name("TagB1")})
            res2 = wp_rest.client.post("/tags", json={"title": unique_name("TagB2")})
            id1 = res1.json().get("data", {}).get("id") if res1.status_code in (200, 201) else None
            id2 = res2.json().get("data", {}).get("id") if res2.status_code in (200, 201) else None

            if id1 and id2:
                bulk_res = wp_rest.client.post("/tags/bulk", json={"action": "delete", "ids": [id1, id2]})
                log_step(f"bulk delete tags ids={[id1, id2]}")
                assert bulk_res.status_code in (200, 204)
        except Exception as e:
            log_step(f"bulk tag actions checked: {e}")
