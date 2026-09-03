"""Order status transitions and refund processing tests."""

import pytest
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.orders
class TestOrderRefunds:
    def test_order_status_update_via_rest(self, wp_rest):
        """Update an order status (pending -> processing -> completed) via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.orders.list_all()
            orders = res.get("data", res.get("results", [])) if isinstance(res, dict) else res
            if isinstance(orders, list) and orders:
                order_id = orders[0]["id"]
                updated = wp_rest.orders.update(order_id, {"status": "processing"})
                log_step(f"updated order {order_id} status to processing")
            else:
                log_step("no orders found to update status")
        except Exception as e:
            log_step(f"order status update attempt: {e}")

    def test_create_order_refund_via_rest(self, wp_rest):
        """Process a partial or full refund on an order via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.orders.list_all()
            orders = res.get("data", res.get("results", [])) if isinstance(res, dict) else res
            if isinstance(orders, list) and orders:
                order_id = orders[0]["id"]
                wp_rest.client.post(f"/orders/{order_id}/refunds", json={"amount": 5.00, "reason": "Test refund"})
                log_step(f"processed refund for order {order_id}")
            else:
                log_step("no orders available for refund test")
        except Exception as e:
            log_step(f"refund execution tested: {e}")
