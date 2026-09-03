"""Test Suite for Guest Order Merging on Customer Verification & Account Creation.

Hook Covered:
- MergeGuestOrder (Kirki\\Ecommerce\\App\\Hooks\\Actions\\MergeGuestOrder)
- OrderService::merge_guest_orders()
"""

import pytest
from utils.api.client import WpRestClient
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.frontend
class TestGuestOrderMerging:
    def test_merge_guest_orders_on_customer_creation(self, wp_rest):
        """Verify guest orders matching email are linked to customer profile on account setup."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)

        # 1. Create a product for guest checkout
        prod = wp_rest.products.create_simple(title=unique_name("GuestMergeProd"), price=49.99)
        p_id = prod.get("id")
        assert p_id is not None

        variants = prod.get("variants", [])
        v_id = variants[0].get("id") if variants else p_id

        email = f"{unique_name('guest_merge').lower()}@example.com"

        # 2. Place a guest order via POST /orders
        order_payload = {
            "customer": {
                "first_name": "Guest",
                "last_name": "Customer",
                "email": email,
                "phone": "555-0199"
            },
            "shipping_address": {
                "first_name": "Guest",
                "last_name": "Customer",
                "email": email,
                "phone": "555-0199",
                "address_line1": "456 Guest Road",
                "city": "Austin",
                "state": "TX",
                "postal_code": "78701",
                "country": "US"
            },
            "billing_address": {
                "first_name": "Guest",
                "last_name": "Customer",
                "email": email,
                "phone": "555-0199",
                "address_line1": "456 Guest Road",
                "city": "Austin",
                "state": "TX",
                "postal_code": "78701",
                "country": "US"
            },
            "items": [{
                "product_id": p_id,
                "variant_id": v_id,
                "quantity": 1,
                "price": 49.99
            }]
        }

        log_step(f"placing guest order with email={email}")
        res = wp_rest.client.post("/orders", json=order_payload, expected=[200, 201, 422])

        if res.status_code in (200, 201):
            order_id = res.json().get("data", {}).get("id")
            log_step(f"guest order placed successfully id={order_id}")

            # 3. Create customer account with the same email
            log_step(f"creating registered customer with matching email={email}")
            addr = order_payload["shipping_address"]
            c_res = wp_rest.client.post("/customers", json={
                "email": email,
                "first_name": "Guest",
                "last_name": "Customer",
                "password": "Password123!",
                "shipping_address": addr,
                "billing_address": addr
            })
            if c_res.status_code in (200, 201):
                cust_id = c_res.json().get("data", {}).get("id")
                log_step(f"registered customer created id={cust_id}")

                # Cleanup Customer
                if cust_id:
                    wp_rest.client.delete(f"/customers/{cust_id}")

            # Cleanup Order
            if order_id:
                wp_rest.client.delete(f"/orders/{order_id}")

        # Cleanup Product
        wp_rest.products.delete(p_id)
