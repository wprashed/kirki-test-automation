"""Locust load and stress testing script for Kirki eCommerce REST API."""

import random
from locust import HttpUser, task, between

class KirkiStoreUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def browse_shop_api(self):
        """Simulate user browsing products via REST API."""
        self.client.get("/wp-json/kirki-ecommerce/v1/products", name="GET /products")

    @task(2)
    def browse_categories_api(self):
        """Simulate user browsing categories via REST API."""
        self.client.get("/wp-json/kirki-ecommerce/v1/categories", name="GET /categories")

    @task(2)
    def view_cart_api(self):
        """Simulate user checking cart status via REST API."""
        self.client.get("/wp-json/kirki-ecommerce/v1/cart", name="GET /cart")

    @task(1)
    def add_to_cart_api(self):
        """Simulate user adding item to cart via REST API."""
        self.client.post(
            "/wp-json/kirki-ecommerce/v1/cart/items",
            json={"product_id": 1, "quantity": 1},
            name="POST /cart/items"
        )
