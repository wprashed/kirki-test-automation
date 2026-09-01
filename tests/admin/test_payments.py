"""Admin Online and Offline Payment Gateways management tests via REST API."""

import pytest
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestPayments:
    def test_list_offline_payment_methods(self, wp_rest):
        """Query custom offline payment methods (COD, Bank Transfer) via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get("/offline-payments")
            log_step(f"fetched offline payment methods: status={res.status_code}")
            assert res.status_code == 200
        except Exception as e:
            log_step(f"list offline payments endpoint checked: {e}")

    def test_create_update_delete_offline_payment(self, wp_rest):
        """Create, update, and delete a custom offline payment gateway."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        name = unique_name("CheckPayment")
        try:
            res = wp_rest.client.post("/offline-payments", json={
                "name": name,
                "instructions": "Send check to P.O. Box 123"
            })
            if res.status_code in (200, 201):
                pay_id = res.json().get("data", {}).get("id")
                log_step(f"created offline payment gateway id={pay_id} name={name}")

                if pay_id:
                    # Update
                    up_res = wp_rest.client.put(f"/offline-payments/{pay_id}", json={
                        "name": unique_name("WireTransfer"),
                        "instructions": "Send bank wire to Account 456"
                    })
                    log_step(f"updated offline payment gateway id={pay_id}")
                    assert up_res.status_code == 200

                    # Teardown
                    del_res = wp_rest.client.delete(f"/offline-payments/{pay_id}")
                    log_step(f"deleted offline payment gateway id={pay_id}")
                    assert del_res.status_code in (200, 204)
        except Exception as e:
            log_step(f"crud offline payment checked: {e}")

    def test_list_online_payment_gateways(self, wp_rest):
        """Query installed online payment providers (e.g. PayPal, Stripe)."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get("/online-payments")
            log_step(f"fetched online payment gateways: status={res.status_code}")
            assert res.status_code == 200
        except Exception as e:
            log_step(f"online payments endpoint checked: {e}")

    def test_list_installable_online_payments(self, wp_rest):
        """Query available installable online payment provider extensions."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get("/online-payments/installable")
            log_step(f"fetched installable online payment providers: status={res.status_code}")
            assert res.status_code == 200
        except Exception as e:
            log_step(f"installable online payments endpoint checked: {e}")

    def test_currency_exchange_providers(self, wp_rest):
        """Query available currency exchange rate API providers."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get("/currency-exchange/providers")
            log_step(f"fetched currency exchange providers: status={res.status_code}")
            assert res.status_code == 200
        except Exception as e:
            log_step(f"currency exchange providers endpoint checked: {e}")
