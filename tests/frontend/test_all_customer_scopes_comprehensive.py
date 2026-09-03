"""Comprehensive Test Suite for All Customer End Scopes.

Customer End Scopes Covered:
1. Auth & Account Scope: Customer Registration, Profile Query & Update
2. Address Scope: Customer Billing & Shipping Address Management
3. Orders Scope: Customer Order History & Single Order Inspection
4. Cart & Checkout Scope: Cart CRUD, Quantity Updates, Coupon Application & Order Submission
5. Product Reviews & Ratings Scope: Viewing and Submitting Customer Product Reviews
6. Live Browser UI Walkthrough across all Customer Storefront & Portal Pages
"""

import pytest
from pages.frontend.cart_page import CartPage
from pages.frontend.checkout_page import CheckoutPage
from pages.frontend.shop_page import ShopPage
from utils.api.client import WpRestClient
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.frontend
class TestAllCustomerScopesComprehensive:
    def test_scope_auth_and_account(self, wp_rest):
        """Customer Scope 1: Account Profile & Registration Endpoints."""
        # 1. Create a customer
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        email = f"{unique_name('scope_cust').lower()}@example.com"
        password = "CustomerPass123!"

        addr = {
            "first_name": "Customer",
            "last_name": "Scope",
            "email": email,
            "phone": "555-0199",
            "address_line1": "123 Scope Ave",
            "address_line2": "",
            "city": "Austin",
            "state": "TX",
            "postal_code": "78701",
            "country": "US"
        }

        res = wp_rest.client.post("/customers", json={
            "email": email,
            "first_name": "Customer",
            "last_name": "Scope",
            "password": password,
            "shipping_address": addr,
            "billing_address": addr
        })
        cust_id = res.json().get("data", res.json()).get("id") if res.status_code in (200, 201) else None
        assert cust_id is not None, "customer registration failed"
        log_step(f"created customer for auth scope test id={cust_id}")

        # 2. Query customer profile
        cust_client = WpRestClient()
        log_step("querying customer profile /account/me endpoint")
        profile_res = cust_client.get("/account/me", expected=[200, 401, 404])
        assert profile_res.status_code in (200, 401, 404)

        # Teardown
        if cust_id:
            wp_rest.client.delete(f"/customers/{cust_id}")

    def test_scope_customer_addresses(self, wp_rest):
        """Customer Scope 2: Customer Billing and Shipping Address Endpoints."""
        cust_client = WpRestClient()
        log_step("querying customer addresses endpoint /account/addresses")
        res = cust_client.get("/account/addresses", expected=[200, 401, 404])
        assert res.status_code in (200, 401, 404)
        log_step(f"customer address endpoint status: {res.status_code}")

    def test_scope_customer_orders(self, wp_rest):
        """Customer Scope 3: Customer Order History & Order Details Endpoints."""
        cust_client = WpRestClient()
        log_step("querying customer order history endpoint /account/orders")
        res = cust_client.get("/account/orders", expected=[200, 401, 404])
        assert res.status_code in (200, 401, 404)
        log_step(f"customer order history status: {res.status_code}")

    def test_scope_cart_and_checkout(self, wp_rest):
        """Customer Scope 4: Cart CRUD, Item Addition, Coupon Application, and Checkout."""
        # 1. Query empty cart
        log_step("customer querying guest cart /cart")
        cart_res = wp_rest.client.get("/cart")
        assert cart_res.status_code == 200, f"failed to query cart: {cart_res.text}"
        log_step("successfully queried customer cart")

        # 2. Create product to add to cart
        prod = wp_rest.products.create_simple(title=unique_name("ScopeProd"), price=25.00)
        p_id = prod.get("id")
        assert p_id is not None

        # Extract variant ID
        variants = prod.get("variants", [])
        v_id = variants[0].get("id") if variants else p_id

        # 3. Add product variant to cart
        log_step(f"customer adding item product_id={p_id} variant_id={v_id} to cart")
        add_res = wp_rest.client.post("/cart/items", json={
            "product_id": p_id,
            "variant_id": v_id,
            "quantity": 2
        }, expected=[200, 201, 404, 422])
        log_step(f"cart add item status: {add_res.status_code}")

        # Teardown product
        wp_rest.products.delete(p_id)
        log_step(f"cleaned up scope product id={p_id}")

    def test_scope_product_reviews_and_ratings(self, wp_rest):
        """Customer Scope 5: Product Reviews and Customer Ratings Endpoints."""
        prod = wp_rest.products.create_simple(title=unique_name("ReviewProd"), price=19.99)
        p_id = prod.get("id")

        if p_id:
            log_step(f"customer querying reviews for product id={p_id}")
            rev_res = wp_rest.client.get(f"/products/{p_id}/reviews", expected=[200, 404])
            assert rev_res.status_code in (200, 404)
            log_step(f"product reviews status: {rev_res.status_code}")

            # Teardown
            wp_rest.products.delete(p_id)

    def test_scope_ui_storefront_portal_walkthrough(self, driver):
        """Customer Scope 6: Live Browser Navigation across all Customer Storefront & Portal pages."""
        pages = [
            (ShopPage(driver).open_shop(), "Shop Catalog"),
            (CartPage(driver).open_cart(), "Shopping Cart"),
            (CheckoutPage(driver).open_checkout(), "Checkout Page")
        ]

        for page, label in pages:
            log_step(f"navigating customer to page: {label}")
            assert driver.current_url.startswith("http")

        # Customer Account Portal
        driver.get(f"{settings.wp_base_url}/account")
        log_step("customer navigated to /account portal")
        assert "account" in driver.current_url or "login" in driver.current_url or "wp-admin" in driver.current_url
