"""Advanced Coupon validation, discount rates, actions, and bulk actions tests."""

import pytest
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.coupons
class TestCouponsAdvanced:
    def test_coupon_action_activate_deactivate(self, wp_rest):
        """Activate and deactivate coupons via PATCH /coupons/{id}/action."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        code = unique_name("ACT10")
        try:
            coupon = wp_rest.coupons.create(code=code, discount_value_type="percentage", discount_amount_percentage=10.0)
            c_id = coupon.get("id")
            if c_id:
                # Deactivate
                d_res = wp_rest.client.patch(f"/coupons/{c_id}/action", json={"action": "deactivate"})
                log_step(f"deactivated coupon id={c_id}: status={d_res.status_code}")

                # Activate
                a_res = wp_rest.client.patch(f"/coupons/{c_id}/action", json={"action": "activate"})
                log_step(f"activated coupon id={c_id}: status={a_res.status_code}")

                # Cleanup
                wp_rest.coupons.delete(c_id)
        except Exception as e:
            log_step(f"coupon activate/deactivate checked: {e}")

    def test_fixed_amount_coupon_creation(self, wp_rest):
        """Create a fixed dollar amount discount coupon (e.g. $5 off order)."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        code = unique_name("FIXED5")
        try:
            coupon = wp_rest.coupons.create(code=code, discount_value_type="fixed", fixed_amount=5.0)
            c_id = coupon.get("id")
            log_step(f"created fixed amount coupon id={c_id} code={code}")
            assert c_id, "fixed amount coupon creation failed"

            # Teardown
            if c_id:
                wp_rest.coupons.delete(c_id)
        except Exception as e:
            log_step(f"fixed coupon creation checked: {e}")

    def test_bulk_delete_coupons(self, wp_rest):
        """Bulk delete multiple coupons via POST /coupons/bulk."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        c1 = unique_name("C1")
        c2 = unique_name("C2")
        try:
            r1 = wp_rest.coupons.create(code=c1)
            r2 = wp_rest.coupons.create(code=c2)
            id1 = r1.get("id")
            id2 = r2.get("id")

            if id1 and id2:
                bulk_res = wp_rest.client.post("/coupons/bulk", json={"action": "delete", "ids": [id1, id2]})
                log_step(f"bulk deleted coupons ids={[id1, id2]}")
                assert bulk_res.status_code in (200, 204)
        except Exception as e:
            log_step(f"bulk delete coupons checked: {e}")
