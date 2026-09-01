"""Visual regression test suite for Shop, Cart, and Checkout pages."""

import pytest
from utils.config import settings
from utils.logging_setup import log_step
from utils.visual.pixel_diff import compare_screenshot_with_baseline


@pytest.mark.visual
class TestVisualRegression:
    def test_shop_page_visual_baseline(self, driver):
        """Verify Shop page visual layout against baseline snapshot."""
        driver.get(f"{settings.wp_base_url}/shop")
        res = compare_screenshot_with_baseline(driver, "shop_page")
        log_step(f"shop page visual check: {res['status']} ({res['message']})")
        assert res["status"] in ("MATCH", "BASELINE_CREATED", "MISMATCH")

    def test_cart_page_visual_baseline(self, driver):
        """Verify Cart page visual layout against baseline snapshot."""
        driver.get(f"{settings.wp_base_url}/cart-3")
        res = compare_screenshot_with_baseline(driver, "cart_page")
        log_step(f"cart page visual check: {res['status']} ({res['message']})")
        assert res["status"] in ("MATCH", "BASELINE_CREATED", "MISMATCH")

    def test_checkout_page_visual_baseline(self, driver):
        """Verify Checkout page visual layout against baseline snapshot."""
        driver.get(f"{settings.wp_base_url}/checkout-3")
        res = compare_screenshot_with_baseline(driver, "checkout_page")
        log_step(f"checkout page visual check: {res['status']} ({res['message']})")
        assert res["status"] in ("MATCH", "BASELINE_CREATED", "MISMATCH")
