"""
Automated Visual Layout Diff Regression Suite
Captures baseline screenshots and performs pixel-by-pixel diffing to catch layout regressions.
"""

import os
import pytest
from utils.config import settings
from utils.visual.diff_engine import compare_images, BASELINES_DIR, DIFFS_DIR
from utils.logging_setup import get_logger

logger = get_logger()


@pytest.mark.visual
class TestVisualLayoutDiffRegression:

    def test_01_storefront_shop_page_visual_layout_diff(self, driver):
        """Verify storefront shop page against visual layout baseline."""
        driver.get(f"{settings.wp_base_url}/shop")
        driver.implicitly_wait(3)

        current_path = os.path.join(DIFFS_DIR, "current_shop_page.png")
        baseline_path = os.path.join(BASELINES_DIR, "baseline_shop_page.png")
        diff_path = os.path.join(DIFFS_DIR, "diff_shop_page.png")

        driver.save_screenshot(current_path)
        result = compare_images(baseline_path, current_path, diff_path, threshold=0.03)

        logger.info(f"Shop Page Visual Diff Result: {result['message']}")
        assert result["passed"], result["message"]

    def test_02_storefront_cart_page_visual_layout_diff(self, driver):
        """Verify storefront cart page against visual layout baseline."""
        driver.get(f"{settings.wp_base_url}/cart")
        driver.implicitly_wait(3)

        current_path = os.path.join(DIFFS_DIR, "current_cart_page.png")
        baseline_path = os.path.join(BASELINES_DIR, "baseline_cart_page.png")
        diff_path = os.path.join(DIFFS_DIR, "diff_cart_page.png")

        driver.save_screenshot(current_path)
        result = compare_images(baseline_path, current_path, diff_path, threshold=0.03)

        logger.info(f"Cart Page Visual Diff Result: {result['message']}")
        assert result["passed"], result["message"]

    def test_03_storefront_checkout_page_visual_layout_diff(self, driver):
        """Verify storefront checkout page against visual layout baseline."""
        driver.get(f"{settings.wp_base_url}/checkout")
        driver.implicitly_wait(3)

        current_path = os.path.join(DIFFS_DIR, "current_checkout_page.png")
        baseline_path = os.path.join(BASELINES_DIR, "baseline_checkout_page.png")
        diff_path = os.path.join(DIFFS_DIR, "diff_checkout_page.png")

        driver.save_screenshot(current_path)
        result = compare_images(baseline_path, current_path, diff_path, threshold=0.03)

        logger.info(f"Checkout Page Visual Diff Result: {result['message']}")
        assert result["passed"], result["message"]

    def test_04_admin_dashboard_visual_layout_diff(self, driver):
        """Verify Kirki Admin SPA dashboard against visual layout baseline."""
        driver.get(f"{settings.wp_base_url}/wp-admin/admin.php?page=kirki-ecommerce#/")
        driver.implicitly_wait(5)

        current_path = os.path.join(DIFFS_DIR, "current_admin_dashboard.png")
        baseline_path = os.path.join(BASELINES_DIR, "baseline_admin_dashboard.png")
        diff_path = os.path.join(DIFFS_DIR, "diff_admin_dashboard.png")

        driver.save_screenshot(current_path)
        result = compare_images(baseline_path, current_path, diff_path, threshold=0.04)

        logger.info(f"Admin Dashboard Visual Diff Result: {result['message']}")
        assert result["passed"], result["message"]
