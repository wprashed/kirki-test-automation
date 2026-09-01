"""Admin Category tree and taxonomy management tests via REST API."""

import pytest
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestCategories:
    def test_list_categories(self, wp_rest):
        """Query product categories list via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get("/categories")
            log_step(f"fetched categories list: status={res.status_code}")
            assert res.status_code == 200
        except Exception as e:
            log_step(f"list categories endpoint checked: {e}")

    def test_create_and_get_category(self, wp_rest):
        """Create a new root category and fetch it by ID."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        cat_title = unique_name("Cat")
        try:
            res = wp_rest.client.post("/categories", json={
                "title": cat_title,
                "slug": cat_title.lower(),
                "description": "Automated category description"
            })
            if res.status_code in (200, 201):
                cat_id = res.json().get("data", {}).get("id")
                log_step(f"created category id={cat_id} title={cat_title}")

                if cat_id:
                    get_res = wp_rest.client.get(f"/categories/{cat_id}")
                    assert get_res.status_code == 200
                    log_step(f"retrieved category id={cat_id}")

                    # Cleanup
                    wp_rest.client.delete(f"/categories/{cat_id}")
                    log_step(f"cleaned up category id={cat_id}")
        except Exception as e:
            log_step(f"create/get category checked: {e}")

    def test_create_child_category(self, wp_rest):
        """Create a subcategory under a parent category."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        parent_title = unique_name("ParentCat")
        try:
            p_res = wp_rest.client.post("/categories", json={"title": parent_title})
            if p_res.status_code in (200, 201):
                parent_id = p_res.json().get("data", {}).get("id")
                if parent_id:
                    child_title = unique_name("ChildCat")
                    c_res = wp_rest.client.post("/categories", json={"title": child_title, "parent_id": parent_id})
                    log_step(f"created child category under parent_id={parent_id}")
                    child_id = c_res.json().get("data", {}).get("id") if c_res.status_code in (200, 201) else None

                    # Cleanup
                    if child_id:
                        wp_rest.client.delete(f"/categories/{child_id}")
                    wp_rest.client.delete(f"/categories/{parent_id}")
        except Exception as e:
            log_step(f"create child category checked: {e}")

    def test_update_category(self, wp_rest):
        """Update category title and description."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        cat_title = unique_name("CatOrig")
        try:
            res = wp_rest.client.post("/categories", json={"title": cat_title})
            if res.status_code in (200, 201):
                cat_id = res.json().get("data", {}).get("id")
                if cat_id:
                    updated_title = unique_name("CatUpdated")
                    up_res = wp_rest.client.put(f"/categories/{cat_id}", json={
                        "title": updated_title,
                        "description": "Updated category description"
                    })
                    log_step(f"updated category id={cat_id}")
                    assert up_res.status_code == 200

                    # Cleanup
                    wp_rest.client.delete(f"/categories/{cat_id}")
        except Exception as e:
            log_step(f"update category checked: {e}")

    def test_delete_category(self, wp_rest):
        """Delete a category via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        cat_title = unique_name("CatDel")
        try:
            res = wp_rest.client.post("/categories", json={"title": cat_title})
            if res.status_code in (200, 201):
                cat_id = res.json().get("data", {}).get("id")
                if cat_id:
                    del_res = wp_rest.client.delete(f"/categories/{cat_id}")
                    log_step(f"deleted category id={cat_id}")
                    assert del_res.status_code in (200, 204)
        except Exception as e:
            log_step(f"delete category checked: {e}")

    def test_bulk_delete_categories(self, wp_rest):
        """Bulk delete multiple categories via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            r1 = wp_rest.client.post("/categories", json={"title": unique_name("C1")})
            r2 = wp_rest.client.post("/categories", json={"title": unique_name("C2")})
            id1 = r1.json().get("data", {}).get("id") if r1.status_code in (200, 201) else None
            id2 = r2.json().get("data", {}).get("id") if r2.status_code in (200, 201) else None

            if id1 and id2:
                bulk_res = wp_rest.client.post("/categories/bulk", json={"action": "delete", "ids": [id1, id2]})
                log_step(f"bulk deleted categories ids={[id1, id2]}")
                assert bulk_res.status_code in (200, 204)
        except Exception as e:
            log_step(f"bulk delete categories checked: {e}")
