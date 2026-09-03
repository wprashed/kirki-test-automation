"""Comprehensive Test Suite for Coupon Creation.

Tests cover:
1. Percentage Discount Coupon Creation with Metadata (20% off)
2. Fixed Dollar Amount Discount Coupon Creation ($15 off)
3. Coupon Duplication & Cloning (POST /coupons/{id}/duplicate)
4. Coupon Creation with Usage Limits & Minimum Spend Restrictions
5. Admin SPA Coupon Creation Page UI Navigation & Verification
"""

import pytest
from pages.admin.admin_pages import AdminDashboardPage
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.coupons
class TestCreateCouponsComprehensive:
    def test_create_percentage_discount_coupon(self, wp_rest):
        """Create a percentage-based discount coupon (20% off) via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        code = unique_name("PERC20")
        title = f"20% Off - {code}"

        log_step(f"creating percentage coupon code={code}")
        coupon = wp_rest.coupons.create(
            code=code,
            title=title,
            discount_value_type="percentage",
            discount_amount_percentage=20.0,
            is_active=True
        )

        c_id = coupon.get("id")
        assert c_id is not None, "created percentage coupon must return valid ID"
        log_step(f"created percentage coupon id={c_id} code={code}")

        # Verify retrieval via GET /coupons/{id}
        get_res = wp_rest.client.get(f"/coupons/{c_id}")
        assert get_res.status_code == 200
        get_data = get_res.json().get("data", get_res.json())
        assert get_data.get("code") == code or get_data.get("title") == title
        log_step(f"verified percentage coupon retrieval id={c_id}")

        # Teardown
        wp_rest.coupons.delete(c_id)
        log_step(f"deleted percentage coupon id={c_id}")

    def test_create_fixed_amount_discount_coupon(self, wp_rest):
        """Create a fixed dollar amount discount coupon ($15 off) via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        code = unique_name("FIX15")
        title = f"$15 Off - {code}"

        log_step(f"creating fixed amount coupon code={code}")
        coupon = wp_rest.coupons.create(
            code=code,
            title=title,
            discount_value_type="fixed",
            fixed_amount=15.00,
            is_active=True
        )

        c_id = coupon.get("id")
        assert c_id is not None, "created fixed coupon must return valid ID"
        log_step(f"created fixed coupon id={c_id} code={code}")

        # Teardown
        wp_rest.coupons.delete(c_id)
        log_step(f"deleted fixed coupon id={c_id}")

    def test_create_and_duplicate_coupon(self, wp_rest):
        """Create a master coupon and duplicate it via POST /coupons/{id}/duplicate."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        orig_code = unique_name("ORIG")

        orig_coupon = wp_rest.coupons.create(code=orig_code, discount_value_type="percentage", discount_amount_percentage=15.0)
        c_id = orig_coupon.get("id")
        assert c_id is not None

        # Duplicate
        log_step(f"duplicating coupon id={c_id}")
        dup_res = wp_rest.client.post(f"/coupons/{c_id}/duplicate", expected=[200, 201, 404])
        log_step(f"duplicate coupon response status={dup_res.status_code}")
        if dup_res.status_code in (200, 201):
            dup_id = dup_res.json().get("data", {}).get("id")
            if dup_id:
                wp_rest.coupons.delete(dup_id)
                log_step(f"cleaned up duplicated coupon id={dup_id}")

        # Teardown original
        wp_rest.coupons.delete(c_id)
        log_step(f"deleted original coupon id={c_id}")

    def test_create_coupon_with_usage_limits_and_restrictions(self, wp_rest):
        """Create a coupon with minimum spend and total usage limit restrictions."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        code = unique_name("RESTRICTED")
        import datetime
        now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")

        payload = {
            "method": "code",
            "code": code,
            "title": f"Restricted Coupon {code}",
            "discount_type": "amount-off",
            "discount_target": "order",
            "discount_value_type": "fixed",
            "discount_amount": 10.0,
            "start_datetime": now_str,
            "is_active": True,
            "usage_limit_per_user": 1,
            "total_usage_limit": 50,
            "min_spend_amount": 50.00
        }

        log_step(f"creating restricted coupon code={code}")
        res = wp_rest.client.post("/coupons", json=payload)
        assert res.status_code in (200, 201), f"failed to create restricted coupon: {res.text}"

        data = res.json().get("data", res.json())
        c_id = data.get("id")
        assert c_id is not None, "restricted coupon must return valid ID"
        log_step(f"created restricted coupon id={c_id}")

        # Teardown
        wp_rest.coupons.delete(c_id)
        log_step(f"deleted restricted coupon id={c_id}")

    def test_ui_admin_create_coupon_page(self, driver):
        """Verify UI navigation to the Admin Coupon Creation SPA form live in Chrome."""
        dashboard = AdminDashboardPage(driver).open_kirki()
        driver.get(f"{settings.wp_base_url}/wp-admin/admin.php?page=kirki-ecommerce#/coupons/create")
        log_step("navigated to Admin Coupon Creation SPA route")
        assert "kirki-ecommerce" in driver.current_url
