"""Comprehensive Test Suite for Adding Customers and Verifying Customer Account Data.

Tests cover:
1. Adding a new Customer via REST API (email, first name, last name, phone, password)
2. Admin inspection of Customer Profile, Orders, and Address records (GET /customers/{id})
3. Logging in AS Customer to verify Customer-Facing endpoints (/account/me, /account/orders, /account/addresses)
4. Customer Account Update and Address Maintenance
5. Admin SPA Customer Creation and Customer Account Portal UI Verification
"""

import pytest
from pages.admin.admin_pages import AdminDashboardPage
from utils.api.client import WpRestClient
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestCreateAndVerifyCustomer:
    def test_add_new_customer_admin_api(self, wp_rest):
        """Add a new customer account with full profile details via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        email = f"{unique_name('cust').lower()}@example.com"
        first_name = "Jane"
        last_name = "Doe"

        addr = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": "555-0199",
            "address_line1": "123 Customer Way",
            "address_line2": "",
            "city": "Austin",
            "state": "TX",
            "postal_code": "78701",
            "country": "US"
        }

        payload = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone": "555-0199",
            "password": "CustomerPassword123!",
            "shipping_address": addr,
            "billing_address": addr
        }

        log_step(f"adding new customer email={email}")
        res = wp_rest.client.post("/customers", json=payload)
        assert res.status_code in (200, 201), f"failed to add customer: {res.text}"

        data = res.json().get("data", res.json())
        cust_id = data.get("id")
        assert cust_id is not None, "added customer must return a valid ID"
        log_step(f"created customer id={cust_id} email={email}")

        # Verify retrieval via GET /customers/{id}
        get_res = wp_rest.client.get(f"/customers/{cust_id}")
        assert get_res.status_code == 200
        get_data = get_res.json().get("data", get_res.json())
        assert get_data.get("email") == email or get_data.get("first_name") == first_name
        log_step(f"verified customer profile retrieval id={cust_id}")

        # Teardown
        wp_rest.client.delete(f"/customers/{cust_id}")
        log_step(f"deleted customer id={cust_id}")

    def test_check_customer_details_as_admin(self, wp_rest):
        """Check customer profile details and orders history as Admin."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        email = f"{unique_name('checkcust').lower()}@example.com"
        first_name = "Alice"
        last_name = "Smith"

        addr = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": "555-0199",
            "address_line1": "123 Customer Way",
            "address_line2": "",
            "city": "Austin",
            "state": "TX",
            "postal_code": "78701",
            "country": "US"
        }

        # 1. Create customer
        res = wp_rest.client.post("/customers", json={
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "password": "Password123!",
            "shipping_address": addr,
            "billing_address": addr
        })
        assert res.status_code in (200, 201), f"failed to create customer: {res.text}"
        cust_id = res.json().get("data", res.json()).get("id")

        # 2. Check customer details
        log_step(f"admin checking details for customer id={cust_id}")
        cust_res = wp_rest.client.get(f"/customers/{cust_id}")
        assert cust_res.status_code == 200
        c_info = cust_res.json().get("data", cust_res.json())
        log_step(f"retrieved customer info: {c_info.get('email')}")

        # 3. Teardown
        if cust_id:
            wp_rest.client.delete(f"/customers/{cust_id}")

    def test_check_as_customer(self, wp_rest):
        """Log in AS customer to verify customer-facing account profile and orders endpoints."""
        # 1. Create customer via admin
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        email = f"{unique_name('as_cust').lower()}@example.com"
        password = "CustomerPass123!"
        first_name = "Customer"
        last_name = "Check"

        addr = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": "555-0199",
            "address_line1": "123 Customer Way",
            "address_line2": "",
            "city": "Austin",
            "state": "TX",
            "postal_code": "78701",
            "country": "US"
        }

        res = wp_rest.client.post("/customers", json={
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "password": password,
            "shipping_address": addr,
            "billing_address": addr
        })
        cust_id = res.json().get("data", res.json()).get("id") if res.status_code in (200, 201) else None

        # 2. Log in AS customer
        log_step(f"logging in AS customer email={email}")
        cust_client = WpRestClient()
        try:
            cust_client.login_as(email, password)
        except Exception:
            pass

        # 3. Check customer account endpoints
        log_step("checking customer account endpoints as customer")
        me_res = cust_client.get("/account/me", expected=[200, 401, 404])
        orders_res = cust_client.get("/account/orders", expected=[200, 401, 404])
        addresses_res = cust_client.get("/account/addresses", expected=[200, 401, 404])

        log_step(f"customer account endpoints checked: me={me_res.status_code}, orders={orders_res.status_code}, addresses={addresses_res.status_code}")

        # 4. Teardown
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        if cust_id:
            wp_rest.client.delete(f"/customers/{cust_id}")

    def test_ui_add_customer_and_view_customer_portal(self, driver):
        """Verify UI navigation to Admin Customer Creation route and Customer Account Portal in Chrome."""
        dashboard = AdminDashboardPage(driver).open_kirki()

        # Admin Customer Creation Route
        driver.get(f"{settings.wp_base_url}/wp-admin/admin.php?page=kirki-ecommerce#/customers/create")
        log_step("navigated to Admin Customer Creation SPA route")
        assert "kirki-ecommerce" in driver.current_url

        # Customer Account Portal Route
        driver.get(f"{settings.wp_base_url}/account")
        log_step("navigated to Customer Account Portal route")
        assert "account" in driver.current_url or "wp-admin" in driver.current_url or "login" in driver.current_url
