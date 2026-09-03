"""Full visual E2E UI Walkthrough test module: Admin & Customer side features.

Runs browser interactions across all Admin SPA sections and Storefront Customer pages
so the user can visually watch every feature in Live Browser mode.
"""

import time
import pytest
from selenium.webdriver.common.by import By
from pages.admin.admin_pages import AdminLoginPage, AdminDashboardPage
from pages.frontend.shop_page import ShopPage
from pages.frontend.product_page import ProductPage
from pages.frontend.cart_page import CartPage
from pages.frontend.checkout_page import CheckoutPage
from pages.frontend.account_pages import AccountDashboardPage
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.smoke
@pytest.mark.admin
@pytest.mark.frontend
class TestFullUiWalkthrough:
    """Visually demonstrates all Admin SPA options and Customer Storefront pages in browser."""

    def test_01_admin_full_navigation_walkthrough(self, driver):
        """Admin visual walkthrough: Login → SPA Root → All 12 Admin SPA Sections."""
        # 1. Login
        login = AdminLoginPage(driver).open_admin_login()
        login.login(settings.admin_user, settings.admin_password)
        time.sleep(1)

        # 2. Open Kirki SPA
        dashboard = AdminDashboardPage(driver).open_kirki()
        log_step("Admin SPA mounted successfully", driver=driver)
        time.sleep(1)

        admin_spa_routes = [
            ("Products List", "#/products"),
            ("Create Product Form", "#/products/new"),
            ("Categories Management", "#/categories"),
            ("Tags Management", "#/tags"),
            ("Brands Management", "#/brands"),
            ("Collections Management", "#/collections"),
            ("Product Attributes", "#/attributes"),
            ("Coupons & Discounts", "#/coupons"),
            ("Orders Management", "#/orders"),
            ("Customer Directory", "#/customers"),
            ("Shipping Profiles", "#/shipping"),
            ("Tax Profiles", "#/taxes"),
            ("Store Settings", "#/settings"),
            ("Sales Analytics & Reports", "#/reports"),
        ]

        base_admin_url = f"{settings.admin_url}/admin.php?page=kirki-ecommerce"

        for label, route in admin_spa_routes:
            target_url = f"{base_admin_url}{route}"
            driver.get(target_url)
            log_step(f"Admin section: {label} ({route})", driver=driver)
            time.sleep(1)

    def test_02_customer_full_storefront_walkthrough(self, driver, smoke_ctx):
        """Customer visual walkthrough: Shop → Product → Cart → Checkout → Account Portal."""
        # 1. Shop Page
        shop = ShopPage(driver).open_shop()
        log_step("Customer Storefront Shop Page loaded", driver=driver)
        time.sleep(1)

        # 2. Product Detail Page
        prod_slug = smoke_ctx.product_slug or "admin-test-tshirt"
        product_page = ProductPage(driver).open_product(prod_slug)
        log_step(f"Customer Product Detail Page: {prod_slug}", driver=driver)
        time.sleep(1)

        # Add to cart
        try:
            product_page.add_to_cart()
            log_step("Added product to shopping cart", driver=driver)
            time.sleep(1)
        except Exception:
            log_step("Product add to cart attempted", driver=driver)

        # 3. Cart Page
        cart_page = CartPage(driver).open_cart()
        log_step("Customer Shopping Cart Page", driver=driver)
        time.sleep(1)

        # 4. Checkout Page
        checkout_page = CheckoutPage(driver).open_checkout()
        log_step("Customer Checkout & Payment Form Page", driver=driver)
        time.sleep(1)

        # 5. Customer Account Portal
        driver.get(f"{settings.wp_base_url}/account")
        log_step("Customer Account Portal Dashboard", driver=driver)
        time.sleep(1)

        driver.get(f"{settings.wp_base_url}/account#/orders")
        log_step("Customer Account Order History", driver=driver)
        time.sleep(1)

        driver.get(f"{settings.wp_base_url}/account#/profile")
        log_step("Customer Account Profile & Address Settings", driver=driver)
        time.sleep(1)
