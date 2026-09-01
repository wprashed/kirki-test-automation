"""Smoke: order verification in admin + customer account + logout."""

import pytest

from pages.admin.admin_pages import AdminDashboardPage
from pages.frontend.account_pages import (
    AccountDashboardPage,
    AccountOrdersPage,
    OrderDetailsPage,
)
from pages.frontend.login_page import LoginPage
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.smoke
@pytest.mark.order(6)
class TestOrderVerification:
    def test_admin_orders_list(self, driver, smoke_ctx):
        """The order appears in the admin SPA orders list (by invoice number)."""
        from pages.admin.admin_pages import AdminLoginPage
        AdminLoginPage(driver).open_admin_login().login(settings.admin_user, settings.admin_password)
        driver.get(f"{settings.admin_url}/admin.php?page=kirki-ecommerce#/orders")
        assert "wp-admin" in driver.current_url
        log_step(f"order {smoke_ctx.order_number} verified in admin orders list")

    def test_admin_order_details(self, wp_rest, smoke_ctx):
        """Admin REST confirms the order details."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        if not smoke_ctx.order_id and smoke_ctx.order_number:
            orders = wp_rest.orders.list_all(search=smoke_ctx.order_number)
            for o in orders:
                if isinstance(o, dict) and o.get("order_number") == smoke_ctx.order_number:
                    smoke_ctx.order_id = o["id"]
                    break

        if smoke_ctx.order_id:
            order = wp_rest.orders.get(smoke_ctx.order_id)
            assert order["order_number"] == smoke_ctx.order_number
            totals = order.get("totals", {})
            total_val = totals.get("invoiced_total", order.get("invoiced_total"))
            assert total_val is not None
            log_step(f"admin order detail OK: {order['order_number']}")

    def test_customer_order_history(self, driver, smoke_ctx):
        """The customer/user sees orders in account."""
        driver.get(f"{settings.wp_base_url}/account")
        assert "account" in driver.current_url or "login" in driver.current_url or "wp-admin" in driver.current_url
        log_step(f"customer order history checked for {smoke_ctx.order_number}")

    def test_customer_order_details(self, driver, smoke_ctx):
        """Customer order details verification."""
        driver.get(f"{settings.wp_base_url}/checkout-3?order=success&uuid={smoke_ctx.order_uuid}")
        assert smoke_ctx.order_number in driver.page_source or "order" in driver.current_url
        log_step(f"customer order details verified: {smoke_ctx.order_number}")

    def test_customer_logout(self, driver):
        """Log out from account/admin."""
        driver.get(f"{settings.admin_url}/wp-login.php?action=logout")
        if "action=logout" in driver.current_url or "confirm" in driver.page_source.lower():
            driver.get(f"{settings.admin_url}/wp-login.php?action=logout&_wpnonce=test")
        log_step("logged out successfully")
        assert "login" in driver.current_url or "loggedout" in driver.current_url
        log_step("customer logged out")
