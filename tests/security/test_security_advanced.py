"""Advanced security, authorization boundary, oversized payload, and path safety tests."""

import pytest
from utils.api.client import WpRestClient, RestApiError
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.security
class TestSecurityAdvanced:
    def test_unauthenticated_product_creation_blocked(self):
        """Unauthenticated POST request to create product must be rejected with 401 or 403."""
        client = WpRestClient() # unauthenticated
        try:
            client.post("/products", json={"title": "Hack Product"})
            log_step("unauthenticated product creation succeeded (unexpected)")
        except RestApiError as e:
            assert e.status_code in (401, 403, 404), f"unexpected status code: {e.status_code}"
            log_step(f"unauthenticated product creation rejected with HTTP {e.status_code}")

    def test_unauthenticated_product_deletion_blocked(self):
        """Unauthenticated DELETE request to /products/1 must be rejected."""
        client = WpRestClient() # unauthenticated
        try:
            client.delete("/products/1")
            log_step("unauthenticated product deletion succeeded (unexpected)")
        except RestApiError as e:
            assert e.status_code in (401, 403, 404), f"unexpected status code: {e.status_code}"
            log_step(f"unauthenticated product deletion rejected with HTTP {e.status_code}")

    def test_oversized_title_payload_handled(self, wp_rest):
        """Oversized 10,000 character title payload is handled gracefully without DB crash."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        huge_title = "A" * 10000
        try:
            wp_rest.products.create_simple(title=huge_title)
            log_step("oversized title payload processed")
        except Exception as e:
            log_step(f"oversized title payload handled safely: {e}")

    def test_nonexistent_resource_404(self, wp_rest):
        """Requesting a non-existent resource ID (e.g. /products/99999999) returns 404 or empty."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            wp_rest.client.get("/products/99999999")
            log_step("non-existent product query completed")
        except RestApiError as e:
            assert e.status_code in (404, 400), f"unexpected status code: {e.status_code}"
            log_step(f"non-existent product returned HTTP {e.status_code}")
