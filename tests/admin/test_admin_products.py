"""Admin product management tests via REST and UI."""

import pytest
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestAdminProducts:
    def test_admin_create_product_via_rest(self, wp_rest):
        """Create a new product with variants via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        payload = {
            "title": "Admin Test T-Shirt",
            "slug": "admin-test-tshirt",
            "type": "simple",
            "status": "publish",
            "variant": {
                "base_price": 35.00,
                "sale_price": 28.00,
                "available_quantity": 15,
                "in_stock": True,
                "is_default": True
            }
        }
        product = wp_rest.products.create_with_payload(payload) if hasattr(wp_rest.products, 'create_with_payload') else wp_rest.products.create(title="Admin Test T-Shirt", variant=payload["variant"])
        assert product["id"], "product missing id"
        log_step(f"created admin product id={product['id']}")
        
        # Clean up
        wp_rest.products.delete(product["id"])
        log_step(f"deleted product id={product['id']}")

    def test_admin_list_products_rest(self, wp_rest):
        """List products via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        products = wp_rest.products.list_all()
        assert isinstance(products, (list, dict)), "products response is invalid"
        log_step(f"fetched products response via REST: {type(products)}")
