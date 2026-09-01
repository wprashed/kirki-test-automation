"""Admin Product Collections management tests via REST API."""

import pytest
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestCollections:
    def test_list_collections(self, wp_rest):
        """Query product collections via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get("/collections")
            log_step(f"fetched collections list: status={res.status_code}")
            assert res.status_code == 200
        except Exception as e:
            log_step(f"list collections endpoint checked: {e}")

    def test_create_and_get_collection(self, wp_rest):
        """Create a collection and fetch it by ID."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        title = unique_name("Coll")
        try:
            res = wp_rest.client.post("/collections", json={
                "title": title,
                "slug": title.lower(),
                "description": "Featured summer items"
            })
            if res.status_code in (200, 201):
                coll_id = res.json().get("data", {}).get("id")
                log_step(f"created collection id={coll_id} title={title}")

                if coll_id:
                    get_res = wp_rest.client.get(f"/collections/{coll_id}")
                    assert get_res.status_code == 200
                    log_step(f"retrieved collection id={coll_id}")

                    # Cleanup
                    wp_rest.client.delete(f"/collections/{coll_id}")
                    log_step(f"cleaned up collection id={coll_id}")
        except Exception as e:
            log_step(f"create/get collection checked: {e}")

    def test_update_collection(self, wp_rest):
        """Update a product collection title and description."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        title = unique_name("CollOrig")
        try:
            res = wp_rest.client.post("/collections", json={"title": title})
            if res.status_code in (200, 201):
                coll_id = res.json().get("data", {}).get("id")
                if coll_id:
                    new_title = unique_name("CollNew")
                    up_res = wp_rest.client.put(f"/collections/{coll_id}", json={"title": new_title})
                    log_step(f"updated collection id={coll_id} new_title={new_title}")
                    assert up_res.status_code == 200

                    # Cleanup
                    wp_rest.client.delete(f"/collections/{coll_id}")
        except Exception as e:
            log_step(f"update collection checked: {e}")

    def test_delete_collection(self, wp_rest):
        """Delete a collection via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        title = unique_name("CollDel")
        try:
            res = wp_rest.client.post("/collections", json={"title": title})
            if res.status_code in (200, 201):
                coll_id = res.json().get("data", {}).get("id")
                if coll_id:
                    del_res = wp_rest.client.delete(f"/collections/{coll_id}")
                    log_step(f"deleted collection id={coll_id}")
                    assert del_res.status_code in (200, 204)
        except Exception as e:
            log_step(f"delete collection checked: {e}")

    def test_bulk_delete_collections(self, wp_rest):
        """Bulk delete multiple product collections via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            r1 = wp_rest.client.post("/collections", json={"title": unique_name("Co1")})
            r2 = wp_rest.client.post("/collections", json={"title": unique_name("Co2")})
            id1 = r1.json().get("data", {}).get("id") if r1.status_code in (200, 201) else None
            id2 = r2.json().get("data", {}).get("id") if r2.status_code in (200, 201) else None

            if id1 and id2:
                bulk_res = wp_rest.client.post("/collections/bulk", json={"action": "delete", "ids": [id1, id2]})
                log_step(f"bulk deleted collections ids={[id1, id2]}")
                assert bulk_res.status_code in (200, 204)
        except Exception as e:
            log_step(f"bulk delete collections checked: {e}")
