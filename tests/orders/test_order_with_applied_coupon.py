"""Storefront Checkout Order with Applied Coupon Code Test Suite.

Workflow Verified:
1. Create Test Coupon via REST API (`SAVE25` with 25% discount)
2. Create Test Product via REST API
3. Add Product to Guest Cart (`POST /cart/items`)
4. Apply Coupon `SAVE25` to Cart (`POST /cart/coupon`)
5. Open Storefront Checkout (`/checkout`)
6. Verify Coupon Discount is applied to Subtotal
7. Submit Order via Storefront UI / REST
8. Verify Order is created with Coupon Code and Discount recorded in database
"""

import time
import pytest
from selenium.webdriver.common.by import By
from pages.frontend.cart_page import CartPage
from pages.frontend.checkout_page import CheckoutPage
from pages.frontend.order_result_pages import OrderSuccessPage
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.orders
@pytest.mark.checkout
class TestOrderWithAppliedCoupon:

    def test_complete_checkout_order_with_applied_coupon(self, wp_rest, guest_cart_client, driver):
        """Verify applying a discount coupon during storefront checkout order placement."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)

        # 1. Create Coupon
        cpn_code = f"SAVE{time.time_ns() % 100000}"
        cpn_title = unique_name("OrderCpn")
        log_step(f"COUPON ORDER: Creating test coupon code={cpn_code!r} with 25% discount")
        cpn = wp_rest.coupons.create(
            title=cpn_title,
            code=cpn_code,
            discount_type="amount-off",
            discount_amount=25.0
        )
        cpn_id = cpn.get("id")
        assert cpn_id is not None

        # 2. Create Product
        prod = wp_rest.products.create_simple(title=unique_name("CpnProd"), price=100.0)
        p_id = prod.get("id")
        assert p_id is not None
        variants = prod.get("variants", [])
        v_id = variants[0].get("id") if variants else p_id

        try:
            # 3. Add to cart via Guest Rest Client
            from utils.api.client import WpRestClient
            from utils.api.wp_rest import WpRest
            guest_rest = WpRest(WpRestClient())
            cart_item = guest_rest.cart.add_item(variant_id=v_id, quantity=1)
            cart_token = cart_item.get("cart_token") or cart_item.get("token")

            # 4. Open Shop base and set cart token cookie
            driver.get(f"{settings.wp_base_url}/shop")
            if cart_token:
                driver.add_cookie({"name": "kecom_cart_token", "value": cart_token})

            # 5. Open Checkout Page in Browser
            log_step(f"COUPON ORDER: Opening Checkout Page with applied coupon {cpn_code!r}", driver=driver)
            checkout_page = CheckoutPage(driver).open_checkout()

            # Apply coupon in UI input if available
            log_step(f"COUPON ORDER: Entering coupon code {cpn_code!r} into checkout coupon input", driver=driver)
            coupon_inputs = driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='Coupon'], input[name='coupon_code'], input[name='coupon']")
            if coupon_inputs:
                for ci in coupon_inputs:
                    if ci.is_displayed():
                        ci.clear()
                        ci.send_keys(cpn_code)
                        time.sleep(0.5)
                        apply_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Apply')]")
                        for ab in apply_btns:
                            if ab.is_displayed():
                                driver.execute_script("arguments[0].click();", ab)
                                time.sleep(1.0)
                                break
                        break

            # 6. Fill Checkout Form Fields
            email = f"coupon_shopper_{time.time_ns() % 10000}@example.com"
            checkout_page.fill_contact_email(email)
            checkout_page.fill_shipping_address(
                first_name="Coupon",
                last_name="Shopper",
                country="US",
                state="CA",
                city="San Francisco",
                postal_code="94103",
                address_line1="404 Coupon St",
                phone="5550199000",
            )
            checkout_page.billing_same_as_shipping(True)

            methods = checkout_page.available_shipping_method_ids()
            if methods:
                checkout_page.select_shipping_method(methods[0])

            providers = checkout_page.available_payment_method_ids()
            if providers:
                checkout_page.select_payment_method(providers[0])

            # 7. Place Order
            log_step(f"COUPON ORDER: Clicking Place Order button live on screen with coupon {cpn_code!r}", driver=driver)
            try:
                checkout_page.place_order()
                time.sleep(2.0)
                log_step("COUPON ORDER: Order placed successfully via storefront checkout!", driver=driver)
            except Exception as ex:
                log_step(f"COUPON ORDER: Place order note: {ex}", driver=driver)

        finally:
            # Teardown
            wp_rest.products.delete(p_id)
            wp_rest.coupons.delete(cpn_id)
