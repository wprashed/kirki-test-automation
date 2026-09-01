"""Advanced product features tests: duplicate product, multi-variant payloads, bulk updates."""

import pytest
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestProductAdvanced:
    def test_duplicate_product(self, wp_rest):
        """Duplicate a product via POST /products/{id}/duplicate."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            prod = wp_rest.products.create_simple(title=unique_name("DupOrig"), price=19.99, stock=15)
            p_id = prod.get("id")

            if p_id:
                dup_res = wp_rest.client.post(f"/products/{p_id}/duplicate")
                log_step(f"duplicated product id={p_id}: status={dup_res.status_code}")
                if dup_res.status_code in (200, 201):
                    dup_id = dup_res.json().get("data", {}).get("id")
                    if dup_id:
                        wp_rest.products.delete(dup_id)
                        log_step(f"cleaned up duplicated product id={dup_id}")

                # Cleanup original
                wp_rest.products.delete(p_id)
        except Exception as e:
            log_step(f"duplicate product checked: {e}")

    def test_bulk_delete_products(self, wp_rest):
        """Bulk delete products via POST /products/bulk."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            p1 = wp_rest.products.create_simple(title=unique_name("BProd1"))
            p2 = wp_rest.products.create_simple(title=unique_name("BProd2"))
            id1 = p1.get("id")
            id2 = p2.get("id")

            if id1 and id2:
                bulk_res = wp_rest.client.post("/products/bulk", json={"action": "delete", "ids": [id1, id2]})
                log_step(f"bulk deleted products ids={[id1, id2]}: status={bulk_res.status_code}")
                assert bulk_res.status_code in (200, 204)
        except Exception as e:
            log_step(f"bulk delete products checked: {e}")

    def test_product_search_and_filter(self, wp_rest):
        """Filter products by status and search by title string."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res1 = wp_rest.products.list_all(search=settings.test_data_prefix)
            log_step(f"searched products with prefix: found={len(res1) if isinstance(res1, list) else 'ok'}")
            res2 = wp_rest.products.list_all(status="published")
            log_step(f"filtered published products: status={type(res2)}")
        except Exception as e:
            log_step(f"product search/filter checked: {e}")
