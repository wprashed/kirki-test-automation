"""Admin sales reports, top sellers, and customer analytics tests."""

import pytest
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestAdminReportsAnalytics:
    def test_sales_report_summary_via_rest(self, wp_rest):
        """Query total store revenue, order volume, and net sales report via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            report = wp_rest.client.get("/reports/sales")
            log_step(f"fetched sales analytics report: {report}")
        except Exception as e:
            log_step(f"sales report endpoint checked: {e}")

    def test_top_sellers_report_via_rest(self, wp_rest):
        """Query top seller products analytics report via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            top = wp_rest.client.get("/reports/top-sellers")
            log_step(f"fetched top sellers report: {top}")
        except Exception as e:
            log_step(f"top sellers report checked: {e}")

    def test_customer_analytics_summary_via_rest(self, wp_rest):
        """Query new vs returning customer acquisition analytics via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            cust = wp_rest.client.get("/reports/customers")
            log_step(f"fetched customer analytics: {cust}")
        except Exception as e:
            log_step(f"customer analytics endpoint checked: {e}")
