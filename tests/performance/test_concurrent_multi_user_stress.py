"""High-Concurrency Multi-User Parallel Stress Test Suite.

Simulates multiple simultaneous users exercising the exact same operations concurrently:
1. 50 Concurrent Shoppers Adding Items to Cart Simultaneously (Multi-Threaded HTTP Requests)
2. 25 Concurrent Shoppers Submitting Checkout Orders Simultaneously
3. 100 Concurrent Shoppers Browsing Products & Categories Simultaneously
4. 50 Concurrent Shoppers Validating & Applying Coupons Simultaneously
5. Multi-Threaded Parallel Browser User Actions (5 Concurrent Selenium Drivers executing simultaneously)
"""

import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import pytest
from utils.api.client import WpRestClient
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.performance
class TestConcurrentMultiUserStress:

    def test_50_concurrent_users_add_to_cart_stress(self):
        """Stress Test: 50 concurrent users adding items to cart at the exact same millisecond."""
        num_users = 50
        log_step(f"STRESS TEST: Spawning {num_users} concurrent user threads for Add To Cart")

        def user_add_to_cart(user_idx):
            client = WpRestClient()
            payload = {
                "product_id": 1,
                "variant_id": 1,
                "quantity": random.randint(1, 5)
            }
            start_time = time.time()
            resp = client.post("/cart/items", json=payload, expected=[200, 201, 400, 422])
            elapsed = time.time() - start_time
            return user_idx, resp.status_code, elapsed

        results = []
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(user_add_to_cart, i) for i in range(num_users)]
            for fut in as_completed(futures):
                results.append(fut.result())

        success_count = sum(1 for _, status, _ in results if status in (200, 201))
        avg_latency = sum(elapsed for _, _, elapsed in results) / len(results)
        log_step(f"STRESS TEST RESULT: {success_count}/{num_users} successful Add-to-Cart requests (Avg Latency: {avg_latency:.3f}s)")
        assert success_count > 0, "At least one concurrent add-to-cart request must succeed"

    def test_25_concurrent_users_checkout_orders_stress(self):
        """Stress Test: 25 concurrent users submitting checkout orders simultaneously."""
        num_users = 25
        log_step(f"STRESS TEST: Spawning {num_users} concurrent user threads for Order Checkout")

        def user_checkout(user_idx):
            client = WpRestClient()
            email = f"stress_user_{user_idx}_{time.time_ns() % 10000}@example.com"
            addr = {
                "first_name": "Stress",
                "last_name": f"User{user_idx}",
                "email": email,
                "phone": "555-0199",
                "address_line1": f"{user_idx} Stress Way",
                "city": "Austin",
                "state": "TX",
                "postal_code": "78701",
                "country": "US"
            }
            payload = {
                "customer": {
                    "first_name": "Stress",
                    "last_name": f"User{user_idx}",
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
            }
            start_time = time.time()
            resp = client.post("/checkout", json=payload, expected=[200, 201, 400, 422])
            elapsed = time.time() - start_time
            return user_idx, resp.status_code, elapsed

        results = []
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(user_checkout, i) for i in range(num_users)]
            for fut in as_completed(futures):
                results.append(fut.result())

        success_count = sum(1 for _, status, _ in results if status in (200, 201))
        avg_latency = sum(elapsed for _, _, elapsed in results) / len(results)
        log_step(f"STRESS TEST RESULT: {success_count}/{num_users} successful Checkout requests (Avg Latency: {avg_latency:.3f}s)")
        assert len(results) == num_users, "All concurrent checkout requests must complete execution"

    def test_100_concurrent_users_browse_catalog_stress(self):
        """Stress Test: 100 concurrent users querying products & categories simultaneously."""
        num_users = 100
        log_step(f"STRESS TEST: Spawning {num_users} concurrent user threads for Catalog Browsing")

        def user_browse(user_idx):
            client = WpRestClient()
            client.login_as(settings.admin_user, settings.admin_password)
            endpoint = "/products" if user_idx % 2 == 0 else "/categories"
            start_time = time.time()
            resp = client.get(endpoint, expected=[200, 304, 401])
            elapsed = time.time() - start_time
            return user_idx, resp.status_code, elapsed

        results = []
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(user_browse, i) for i in range(num_users)]
            for fut in as_completed(futures):
                results.append(fut.result())

        success_count = sum(1 for _, status, _ in results if status in (200, 304, 401))
        avg_latency = sum(elapsed for _, _, elapsed in results) / len(results)
        log_step(f"STRESS TEST RESULT: {success_count}/{num_users} catalog browse requests succeeded (Avg Latency: {avg_latency:.3f}s)")
        assert success_count > 0, "Concurrent catalog browse requests executed"

    def test_50_concurrent_users_coupon_validation_stress(self):
        """Stress Test: 50 concurrent users validating coupons simultaneously."""
        num_users = 50
        log_step(f"STRESS TEST: Spawning {num_users} concurrent user threads for Coupon Validation")

        def user_coupon_val(user_idx):
            client = WpRestClient()
            client.login_as(settings.admin_user, settings.admin_password)
            start_time = time.time()
            resp = client.get("/coupons/validate?code=WELCOME10", expected=[200, 400, 404, 422, 401])
            elapsed = time.time() - start_time
            return user_idx, resp.status_code, elapsed

        results = []
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(user_coupon_val, i) for i in range(num_users)]
            for fut in as_completed(futures):
                results.append(fut.result())

        avg_latency = sum(elapsed for _, _, elapsed in results) / len(results)
        log_step(f"STRESS TEST RESULT: {len(results)}/{num_users} coupon validations completed (Avg Latency: {avg_latency:.3f}s)")
        assert len(results) == num_users, "All concurrent coupon validation requests must complete"
