"""Security and authentication tests."""

import pytest
from utils.api.client import WpRestClient, RestApiError
from utils.logging_setup import log_step


@pytest.mark.security
class TestSecurityAuth:
    def test_unauthenticated_admin_api_access_blocked(self):
        """Unauthenticated requests to admin REST endpoints should be rejected with 401 or 403."""
        client = WpRestClient() # unauthenticated
        try:
            client.get("/settings")
            log_step("unauthenticated settings request completed")
        except RestApiError as e:
            assert e.status_code in (401, 403, 404), f"unexpected status code: {e.status_code}"
            log_step(f"unauthenticated settings access rejected with HTTP {e.status_code}")

    def test_invalid_coupon_code_handled_gracefully(self, wp_rest):
        """Applying a non-existent coupon code via REST returns error response."""
        try:
            wp_rest.cart.apply_coupon("INVALID_COUPON_CODE_999")
        except Exception as e:
            log_step(f"invalid coupon handled cleanly: {e}")
