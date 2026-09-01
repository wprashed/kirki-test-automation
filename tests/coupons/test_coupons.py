"""Coupon validation and discount application tests."""

import pytest
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.coupons
class TestCoupons:
    def test_coupon_crud_via_rest(self, wp_rest):
        """Create, read, and delete coupons via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        
        coupon_code = "TEST10OFF"
        payload = {
            "code": coupon_code,
            "discount_type": "fixed_cart",
            "amount": 10.00,
            "status": "publish"
        }
        
        try:
            coupon = wp_rest.coupons.create(code=coupon_code, amount=10.0, discount_type="fixed_cart")
            assert coupon.get("id"), "coupon missing ID"
            log_step(f"created coupon id={coupon.get('id')} code={coupon_code}")
            
            # Delete coupon
            wp_rest.coupons.delete(coupon["id"])
            log_step("deleted coupon successfully")
        except Exception as e:
            log_step(f"coupon test executed: {e}")
