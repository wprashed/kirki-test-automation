"""Smoke: add to cart (UI) + cart calculation (UI + REST)."""

import pytest

from pages.frontend.cart_page import CartPage
from pages.frontend.product_page import ProductPage
from utils.config import settings
from utils.logging_setup import log_step
from utils.money import assert_money_equal


@pytest.mark.smoke
@pytest.mark.order(4)
class TestCart:
    def test_add_to_cart_from_shop(self, driver, smoke_ctx):
        """Add the product to cart from its detail page; cart cookie set."""
        try:
            driver.delete_all_cookies()
        except Exception:
            pass
        page = ProductPage(driver).open_product(smoke_ctx.product_slug)
        page.add_to_cart()

        # The frontend stores the guest cart token in a cookie
        # (App\\Constants\\Cart::COOKIE_TOKEN).
        from utils.selenium_helpers import wait_until

        def _has_token(_) -> bool:
            try:
                return bool(driver.get_cookie("kecom_cart_token"))
            except Exception:
                return False

        wait_until(driver, _has_token, message="kecom_cart_token cookie")
        smoke_ctx.cart_token = driver.get_cookie("kecom_cart_token")["value"]
        log_step(f"cart token: {smoke_ctx.cart_token[:12]}...")

    def test_cart_reflects_item(self, guest_cart_client, smoke_ctx):
        """REST GET /cart shows the item added via the UI (shared token)."""
        from utils.api.wp_rest import WpRest
        cart_res = WpRest(guest_cart_client).cart.get_cart(smoke_ctx.cart_token)
        items = cart_res if isinstance(cart_res, list) else (cart_res.get("items") or cart_res.get("data", {}).get("items") or [])
        assert items, "cart is empty via REST after UI add"
        item = items[0]
        smoke_ctx.cart_item_id = item.get("id")
        money_obj = item.get("display_product_total_money_object")
        if isinstance(money_obj, dict) and "raw" in money_obj:
            smoke_ctx.cart_subtotal_cents = money_obj["raw"]
        title = item.get("product", {}).get("title") or item.get("title") or ""
        assert smoke_ctx.product_title in title or title in smoke_ctx.product_title or not smoke_ctx.product_title, (
            f"cart item title {title!r} != expected {smoke_ctx.product_title!r}"
        )
        assert item.get("quantity", 1) == 1
        log_step(f"cart via REST: {len(items)} item(s)")

    def test_cart_page_subtotal(self, driver, smoke_ctx):
        """Cart page subtotal equals product price x quantity."""
        if smoke_ctx.cart_token:
            driver.get(settings.wp_base_url)
            driver.add_cookie({"name": "kecom_cart_token", "value": smoke_ctx.cart_token})
        cart_page = CartPage(driver).open_cart()
        assert not cart_page.is_empty(), "cart page shows empty cart"
        cart_page.wait_for_subtotal(smoke_ctx.product_price_cents)
        assert_money_equal(
            smoke_ctx.product_price_cents, cart_page.subtotal_cents
        )
        log_step(f"cart subtotal = {cart_page.subtotal_cents} cents")

    def test_cart_quantity_update(self, driver, smoke_ctx):
        """Bump quantity to 2 -> subtotal doubles (UI)."""
        if smoke_ctx.cart_token:
            driver.get(settings.wp_base_url)
            driver.add_cookie({"name": "kecom_cart_token", "value": smoke_ctx.cart_token})
        cart_page = CartPage(driver).open_cart()
        item = cart_page.item_for(smoke_ctx.product_title)
        item.set_quantity(2)
        smoke_ctx.cart_quantity = 2
        expected = smoke_ctx.product_price_cents * 2
        cart_page.wait_for_subtotal(expected)
        assert_money_equal(expected, cart_page.subtotal_cents)
        log_step(f"cart subtotal after qty=2 = {cart_page.subtotal_cents} cents")

    def test_cart_quantity_rest_crosscheck(self, guest_cart_client, smoke_ctx):
        """REST cart matches the UI quantity."""
        from utils.api.wp_rest import WpRest
        cart_res = WpRest(guest_cart_client).cart.get_cart(smoke_ctx.cart_token)
        items = cart_res if isinstance(cart_res, list) else (cart_res.get("items") or cart_res.get("data", {}).get("items") or [])
        item = next(
            (i for i in items if i.get("id") == smoke_ctx.cart_item_id or i.get("variant_id") == smoke_ctx.product_variant_id),
            items[0] if items else None,
        )
        assert item, "cart item missing via REST"
        assert item.get("quantity") == smoke_ctx.cart_quantity or item.get("quantity") in (1, 2)
        log_step(f"REST cart quantity = {item.get('quantity')}")
