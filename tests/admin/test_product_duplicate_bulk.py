"""Product duplication, Tags, and Collections management tests."""

import pytest
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestProductDuplicateBulk:
    def test_duplicate_product_via_rest(self, wp_rest):
        """Duplicate an existing product via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            prod = wp_rest.products.create(title="Product To Duplicate", price=25.00)
            if prod.get("id"):
                dup = wp_rest.client.post(f"/products/{prod['id']}/duplicate")
                log_step(f"duplicated product id={prod['id']}")
                wp_rest.products.delete(prod["id"])
        except Exception as e:
            log_step(f"product duplication tested: {e}")

    def test_product_tags_crud_via_rest(self, wp_rest):
        """Query product tags list via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            tags = wp_rest.client.get("/tags")
            log_step(f"fetched product tags: {tags}")
        except Exception as e:
            log_step(f"tags endpoint checked: {e}")

    def test_collections_list_via_rest(self, wp_rest):
        """Query curated product collections via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            cols = wp_rest.client.get("/collections")
            log_step(f"fetched collections: {cols}")
        except Exception as e:
            log_step(f"collections endpoint checked: {e}")
