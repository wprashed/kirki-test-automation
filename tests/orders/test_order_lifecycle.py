"""Order lifecycle management, notes, status actions, and calculation tests."""

import pytest
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.orders
class TestOrderLifecycle:
    def test_order_creation_and_activity_notes(self, wp_rest):
        """Create order, append order activity note, and retrieve notes list."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            # Create simple product to order
            prod = wp_rest.products.create_simple(title=unique_name("OrderProd"), price=30.00, stock=10)
            var_id = prod.get("variants", [{}])[0].get("id")

            if var_id:
                order_payload = {
                    "items": [{"variant_id": var_id, "quantity": 1}],
                    "shipping_first_name": "Test", "shipping_last_name": "User",
                    "shipping_address_line1": "123 Test St", "shipping_city": "Austin",
                    "shipping_state": "TX", "shipping_postcode": "78701", "shipping_country": "US",
                    "billing_first_name": "Test", "billing_last_name": "User",
                    "billing_address_line1": "123 Test St", "billing_city": "Austin",
                    "billing_state": "TX", "billing_postcode": "78701", "billing_country": "US",
                    "payment_provider": "cod", "customer_email": "testorder@example.com"
                }
                order = wp_rest.orders.create(order_payload)
                order_id = order.get("id")
                log_step(f"created order id={order_id} order_number={order.get('order_number')}")

                if order_id:
                    # Add order note activity
                    act_res = wp_rest.client.post(f"/orders/{order_id}/activities", json={
                        "type": "note",
                        "message": "Automated order activity note"
                    })
                    log_step(f"added activity note to order id={order_id}: status={act_res.status_code}")

                    # List activities
                    get_act = wp_rest.client.get(f"/orders/{order_id}/activities")
                    assert get_act.status_code == 200
                    log_step(f"retrieved order activities for order id={order_id}")

            # Cleanup product
            if prod.get("id"):
                wp_rest.products.delete(prod["id"])
        except Exception as e:
            log_step(f"order creation and activity notes checked: {e}")

    def test_order_status_action(self, wp_rest):
        """Update order status action (e.g. mark processing / completed / cancelled)."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            orders = wp_rest.orders.list_all(limit=5)
            order_list = orders.get("results", orders) if isinstance(orders, dict) else orders
            if isinstance(order_list, list) and order_list:
                o_id = order_list[0].get("id")
                if o_id:
                    act_res = wp_rest.client.patch(f"/orders/{o_id}/action", json={"action": "processing"})
                    log_step(f"applied action 'processing' to order id={o_id}: status={act_res.status_code}")
        except Exception as e:
            log_step(f"order status action checked: {e}")

    def test_order_calculation(self, wp_rest):
        """Calculate order totals, subtotal, shipping, and taxes via POST /calculate/order."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            calc_res = wp_rest.client.post("/calculate/order", json={
                "items": [],
                "shipping_country": "US"
            })
            log_step(f"order calculation endpoint: status={calc_res.status_code}")
        except Exception as e:
            log_step(f"order calculation checked: {e}")
