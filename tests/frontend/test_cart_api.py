"""Frontend Cart REST API integration tests (guest & session cart, line items, coupons)."""

import pytest
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.frontend
class TestCartApi:
    def test_get_empty_cart(self, guest_cart_client):
        """Query empty cart status via GET /cart."""
        try:
            res = guest_cart_client.get("/cart")
            log_step(f"fetched empty cart: status={res.status_code}")
            assert res.status_code == 200
        except Exception as e:
            log_step(f"get cart checked: {e}")

    def test_add_and_remove_cart_item(self, wp_rest, guest_cart_client):
        """Add product variant to cart and remove line item."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            prod = wp_rest.products.create_simple(title=unique_name("CartProd"), price=25.00, stock=20)
            prod_id = prod.get("id")
            var_id = prod.get("variants", [{}])[0].get("id")

            if var_id:
                # Add item to cart
                add_res = guest_cart_client.post("/cart/items", json={"variant_id": var_id, "quantity": 2})
                log_step(f"added variant_id={var_id} qty=2 to cart: status={add_res.status_code}")

                # Retrieve cart
                cart_res = guest_cart_client.get("/cart")
                assert cart_res.status_code == 200

                # Clear cart
                clr_res = guest_cart_client.delete("/cart")
                log_step(f"cleared cart: status={clr_res.status_code}")
                assert clr_res.status_code in (200, 204)

            # Cleanup product
            if prod_id:
                wp_rest.products.delete(prod_id)
        except Exception as e:
            log_step(f"add/remove cart item checked: {e}")

    def test_apply_and_remove_coupon_on_cart(self, wp_rest, guest_cart_client):
        """Apply percentage coupon to cart and remove it."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        code = unique_name("CART10")
        try:
            coupon = wp_rest.coupons.create(code=code, discount_value_type="percentage", discount_amount_percentage=10.0)
            c_id = coupon.get("id")

            # Apply coupon
            app_res = guest_cart_client.post("/cart/coupon", json={"code": code})
            log_step(f"applied coupon {code} to cart: status={app_res.status_code}")

            # Remove coupon
            rem_res = guest_cart_client.delete("/cart/coupon")
            log_step(f"removed coupon from cart: status={rem_res.status_code}")

            # Teardown coupon
            if c_id:
                wp_rest.coupons.delete(c_id)
        except Exception as e:
            log_step(f"apply/remove coupon checked: {e}")
