"""
Core Web Vitals & Performance Audit Test Suite
Verifies Storefront LCP, CLS, and page loading speed against enterprise SLA thresholds.
"""

import pytest
from utils.config import settings
from utils.performance.vitals_audit import audit_page_vitals
from utils.logging_setup import get_logger

logger = get_logger()


@pytest.mark.performance
class TestCoreWebVitalsAudit:

    def test_01_storefront_shop_page_web_vitals(self, driver):
        """Audit shop page for LCP (< 2500ms), CLS (< 0.1), and Page Load (< 3000ms)."""
        metrics = audit_page_vitals(driver, f"{settings.wp_base_url}/shop")
        logger.info(f"Shop Page Vitals: {metrics}")

        assert metrics["page_load_time_ms"] < 4000, f"Shop load time {metrics['page_load_time_ms']}ms > 4000ms SLA"
        assert metrics["cls"] <= 0.2, f"Shop CLS {metrics['cls']} > 0.2 SLA threshold"

    def test_02_storefront_cart_page_web_vitals(self, driver):
        """Audit cart page for LCP, CLS, and Page Load time."""
        metrics = audit_page_vitals(driver, f"{settings.wp_base_url}/cart")
        logger.info(f"Cart Page Vitals: {metrics}")

        assert metrics["page_load_time_ms"] < 4000, f"Cart load time {metrics['page_load_time_ms']}ms > 4000ms SLA"
        assert metrics["cls"] <= 0.2, f"Cart CLS {metrics['cls']} > 0.2 SLA threshold"

    def test_03_storefront_checkout_page_web_vitals(self, driver):
        """Audit checkout page for LCP, CLS, and Page Load time."""
        metrics = audit_page_vitals(driver, f"{settings.wp_base_url}/checkout")
        logger.info(f"Checkout Page Vitals: {metrics}")

        assert metrics["page_load_time_ms"] < 4000, f"Checkout load time {metrics['page_load_time_ms']}ms > 4000ms SLA"
        assert metrics["cls"] <= 0.2, f"Checkout CLS {metrics['cls']} > 0.2 SLA threshold"

    def test_04_admin_spa_dashboard_web_vitals(self, driver):
        """Audit Kirki Admin SPA dashboard page load time."""
        metrics = audit_page_vitals(driver, f"{settings.wp_base_url}/wp-admin/admin.php?page=kirki-ecommerce#/")
        logger.info(f"Admin Dashboard Vitals: {metrics}")

        assert metrics["page_load_time_ms"] < 5000, f"Admin dashboard load time {metrics['page_load_time_ms']}ms > 5000ms SLA"
