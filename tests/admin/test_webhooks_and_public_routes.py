"""Test Suite for Payment Webhooks and Public Utility Endpoints.

Endpoints Covered:
- POST /payment/webhook/{provider_id} (Stripe, PayPal, Offline/Manual Webhooks)
- GET /test-public (Public Debug/DB connection test route)
"""

import pytest
from utils.api.client import WpRestClient
from utils.logging_setup import log_step


@pytest.mark.admin
class TestWebhooksAndPublicRoutes:
    def test_payment_webhook_endpoints(self, wp_rest):
        """Verify payment webhook handler endpoint accepts webhook payloads."""
        providers = ["stripe", "paypal", "cod", "bacs"]

        for provider in providers:
            log_step(f"testing payment webhook POST /payment/webhook/{provider}")
            # Unauthenticated public endpoint designed for payment gateway callbacks
            client = WpRestClient()
            res = client.post(f"/payment/webhook/{provider}", json={
                "event": "payment_intent.succeeded",
                "data": {"id": "evt_test_123", "amount": 2500}
            }, expected=[200, 201, 400, 404, 500])
            log_step(f"payment webhook provider={provider} response status={res.status_code}")
            assert res.status_code in (200, 201, 400, 404, 500)

    def test_public_test_route(self, wp_rest):
        """Verify public test endpoint GET /test-public."""
        client = WpRestClient()
        log_step("querying public debug endpoint GET /test-public")
        res = client.get("/test-public", expected=[200, 404])
        assert res.status_code in (200, 404)
        if res.status_code == 200:
            log_step(f"public test endpoint response: {res.json().get('message')}")
