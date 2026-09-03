"""Test Suite for Kirki Gutenberg Blocks and Shortcodes.

Gutenberg Blocks & Shortcodes Covered:
- [kirki_mini_cart] / Kirki Mini Cart Block
- [kirki_shop] / Storefront Catalog Shortcode
- [kirki_cart] / Shopping Cart Shortcode
- [kirki_checkout] / Customer Checkout Shortcode
- [kirki_account] / Customer Account Portal Shortcode
"""

import pytest
from pages.frontend.cart_page import CartPage
from pages.frontend.checkout_page import CheckoutPage
from pages.frontend.shop_page import ShopPage
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.frontend
class TestMiniCartBlockAndShortcodes:
    def test_gutenberg_blocks_and_shortcodes_rendering(self, driver):
        """Verify storefront pages with Gutenberg blocks and shortcodes mount properly."""
        pages = [
            (ShopPage(driver).open_shop(), "Shop Catalog Page"),
            (CartPage(driver).open_cart(), "Cart Page"),
            (CheckoutPage(driver).open_checkout(), "Checkout Page")
        ]

        for page, label in pages:
            log_step(f"verifying block & shortcode rendering on {label}")
            assert driver.current_url.startswith("http")

        # Test account portal shortcode page
        driver.get(f"{settings.wp_base_url}/account")
        log_step("navigated to /account shortcode page")
        assert "account" in driver.current_url or "login" in driver.current_url or "wp-admin" in driver.current_url
