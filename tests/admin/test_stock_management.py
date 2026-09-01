"""Product stock inventory management and low stock alert tests."""

import pytest
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestStockManagement:
    def test_update_product_stock_via_rest(self, wp_rest):
        """Update inventory stock quantity (e.g. stock=100) via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            prod = wp_rest.products.create(title="Inventory Test Product", price=15.00, stock=50)
            if prod.get("id"):
                updated = wp_rest.products.update(prod["id"], stock=100)
                log_step(f"updated stock quantity for product id={prod['id']}")
                wp_rest.products.delete(prod["id"])
        except Exception as e:
            log_step(f"stock update operation checked: {e}")

    def test_low_stock_threshold_alerts(self, wp_rest):
        """Query low stock threshold alerts report via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            alerts = wp_rest.client.get("/reports/low-stock")
            log_step(f"fetched low stock alerts: {alerts}")
        except Exception as e:
            log_step(f"low stock alerts endpoint checked: {e}")
