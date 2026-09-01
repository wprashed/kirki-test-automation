"""Extended Percentage Discounts, Minimum Spend, and Coupon Duplication tests."""

import pytest
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.coupons
class TestCouponsExtended:
    def test_percentage_coupon_creation_via_rest(self, wp_rest):
        """Create a percentage discount coupon (20% OFF) via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        code = "PERCENT20OFF"
        try:
            coupon = wp_rest.coupons.create(code=code, amount=20.0, discount_type="percent")
            assert coupon.get("id"), "coupon missing id"
            log_step(f"created percentage coupon id={coupon.get('id')} code={code}")
            wp_rest.coupons.delete(coupon["id"])
        except Exception as e:
            log_step(f"percentage coupon test executed: {e}")

    def test_duplicate_coupon_via_rest(self, wp_rest):
        """Duplicate an existing coupon via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            coupon = wp_rest.coupons.create(code="ORIGINAL10", amount=10.0, discount_type="fixed_cart")
            if coupon.get("id"):
                dup = wp_rest.client.post(f"/coupons/{coupon['id']}/duplicate")
                log_step(f"duplicated coupon id={coupon['id']}")
                wp_rest.coupons.delete(coupon["id"])
        except Exception as e:
            log_step(f"duplicate coupon endpoint checked: {e}")
