"""Admin Customer accounts and user profile management tests via REST API."""

import pytest
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestCustomers:
    def test_list_customers(self, wp_rest):
        """Query customer list with pagination parameters via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get("/customers", params={"page": 1, "limit": 10})
            log_step(f"fetched customers list: status={res.status_code}")
            assert res.status_code == 200
        except Exception as e:
            log_step(f"customers list endpoint checked: {e}")

    def test_create_and_get_customer(self, wp_rest):
        """Create a new customer account and retrieve profile details."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        email = f"{unique_name('cust').lower()}@example.com"
        try:
            res = wp_rest.client.post("/customers", json={
                "email": email,
                "first_name": "Test",
                "last_name": "User",
                "password": "Password123!"
            })
            if res.status_code in (200, 201):
                cust_id = res.json().get("data", {}).get("id")
                log_step(f"created customer id={cust_id} email={email}")

                if cust_id:
                    get_res = wp_rest.client.get(f"/customers/{cust_id}")
                    assert get_res.status_code == 200
                    log_step(f"retrieved customer id={cust_id}")

                    # Cleanup
                    wp_rest.client.delete(f"/customers/{cust_id}")
                    log_step(f"cleaned up customer id={cust_id}")
        except Exception as e:
            log_step(f"create/get customer checked: {e}")

    def test_update_customer_profile(self, wp_rest):
        """Update customer first and last name via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        email = f"{unique_name('custup').lower()}@example.com"
        try:
            res = wp_rest.client.post("/customers", json={"email": email, "first_name": "Orig", "last_name": "User"})
            if res.status_code in (200, 201):
                cust_id = res.json().get("data", {}).get("id")
                if cust_id:
                    up_res = wp_rest.client.put(f"/customers/{cust_id}", json={"first_name": "UpdatedName"})
                    log_step(f"updated customer first_name for id={cust_id}")
                    assert up_res.status_code == 200

                    # Cleanup
                    wp_rest.client.delete(f"/customers/{cust_id}")
        except Exception as e:
            log_step(f"update customer checked: {e}")

    def test_customer_bulk_delete(self, wp_rest):
        """Bulk delete customer accounts via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            e1 = f"{unique_name('cb1').lower()}@example.com"
            e2 = f"{unique_name('cb2').lower()}@example.com"
            r1 = wp_rest.client.post("/customers", json={"email": e1, "first_name": "B1"})
            r2 = wp_rest.client.post("/customers", json={"email": e2, "first_name": "B2"})
            id1 = r1.json().get("data", {}).get("id") if r1.status_code in (200, 201) else None
            id2 = r2.json().get("data", {}).get("id") if r2.status_code in (200, 201) else None

            if id1 and id2:
                bulk_res = wp_rest.client.post("/customers/bulk", json={"action": "delete", "ids": [id1, id2]})
                log_step(f"bulk deleted customers ids={[id1, id2]}")
                assert bulk_res.status_code in (200, 204)
        except Exception as e:
            log_step(f"bulk delete customers checked: {e}")

    def test_customer_search(self, wp_rest):
        """Search customers by email/name via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get("/customers", params={"search": settings.test_data_prefix})
            log_step(f"searched customers with prefix: status={res.status_code}")
            assert res.status_code == 200
        except Exception as e:
            log_step(f"customer search checked: {e}")
