"""Locust Load & High-Concurrency Performance Testing Suite for Kirki eCommerce.

Simulates 500+ simultaneous shopper users exercising:
- GET  /wp-json/kirki/ecommerce/v1/cart (Cart query)
- POST /wp-json/kirki/ecommerce/v1/cart/items (Add to Cart)
- POST /wp-json/kirki/ecommerce/v1/checkout (Checkout order submission)
"""

import random
from locust import HttpUser, between, task


class KirkiShopperUser(HttpUser):
    wait_time = between(0.5, 2.0)

    @task(4)
    def view_cart(self):
        """Simulate shoppers checking their cart."""
        self.client.get(
            "/wp-json/kirki/ecommerce/v1/cart",
            headers={"Accept": "application/json"}
        )

    @task(3)
    def add_item_to_cart(self):
        """Simulate shoppers adding items to cart."""
        self.client.post(
            "/wp-json/kirki/ecommerce/v1/cart/items",
            json={
                "product_id": 1,
                "variant_id": 1,
                "quantity": random.randint(1, 3)
            },
            headers={"Content-Type": "application/json"}
        )

    @task(1)
    def submit_checkout(self):
        """Simulate shoppers submitting guest checkout orders."""
        email = f"load_shopper_{random.randint(10000, 99999)}@example.com"
        addr = {
            "first_name": "Load",
            "last_name": "Shopper",
            "email": email,
            "phone": "555-0199",
            "address_line1": "100 Traffic Way",
            "city": "Austin",
            "state": "TX",
            "postal_code": "78701",
            "country": "US"
        }
        self.client.post(
            "/wp-json/kirki/ecommerce/v1/checkout",
            json={
                "customer": {
                    "first_name": "Load",
                    "last_name": "Shopper",
                    "email": email,
                    "phone": "555-0199"
                },
                "shipping_address": addr,
                "billing_address": addr,
                "items": [{
                    "product_id": 1,
                    "variant_id": 1,
                    "quantity": 1,
                    "price": 10.0
                }],
                "payment_method": "cod"
            },
            headers={"Content-Type": "application/json"}
        )
