"""Pytest fixtures: browser driver, API sessions, test data, cleanup."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService

from utils.api.client import WpRestClient
from utils.api.wp_rest import WpRest, unique_name
from utils.config import ROOT_DIR, settings
from utils.logging_setup import log_debug, log_step, setup_logging
from utils.selenium_helpers import (
    attach_console_listener,
    capture_console_errors,
    save_page_source,
    save_screenshot,
)

setup_logging()


def _chrome_driver() -> webdriver.Chrome:
    options = ChromeOptions()
    if settings.headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1440,1000")
    if settings.chrome_binary:
        options.binary_location = settings.chrome_binary
    service = ChromeService()
    return webdriver.Chrome(service=service, options=options)


def _firefox_driver() -> webdriver.Firefox:
    options = FirefoxOptions()
    if settings.headless:
        options.add_argument("-headless")
    if settings.firefox_binary:
        options.binary_location = settings.firefox_binary
    service = FirefoxService()
    return webdriver.Firefox(service=service, options=options)


def _edge_driver() -> webdriver.Edge:
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.edge.service import Service as EdgeService
    options = EdgeOptions()
    if settings.headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = EdgeService()
    return webdriver.Edge(service=service, options=options)


def _mobile_chrome_driver() -> webdriver.Chrome:
    options = ChromeOptions()
    if settings.headless:
        options.add_argument("--headless=new")
    mobile_emulation = {"deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0}, "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15"}
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = ChromeService()
    drv = webdriver.Chrome(service=service, options=options)
    drv.set_window_size(375, 812)
    return drv


@pytest.fixture(scope="session")
def driver_factory():
    """Returns a callable that creates a fresh browser driver."""
    browser = settings.browser.lower()
    if browser == "firefox":
        return _firefox_driver
    if browser == "edge":
        return _edge_driver
    if browser in ("chrome", "chromium"):
        return _chrome_driver
    raise ValueError(f"unsupported BROWSER={browser!r} (use chrome, firefox, or edge)")


@pytest.fixture
def mobile_driver():
    """Chrome browser driver emulating an iPhone 13 mobile viewport (375x812)."""
    drv = _mobile_chrome_driver()
    drv.implicitly_wait(settings.implicit_wait)
    yield drv
    try:
        drv.quit()
    except Exception:
        pass


# ── Persistent session browser ────────────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def session_driver(driver_factory) -> Iterator[webdriver.Remote]:
    """One browser window that stays open for the ENTIRE test session.

    The browser is launched once before the first test and quit only after
    the very last test, so the user can watch all tests run without the
    window ever closing.
    """
    drv = driver_factory()
    drv.implicitly_wait(settings.implicit_wait)
    drv.set_page_load_timeout(60)
    attach_console_listener(drv)
    try:
        from pages.admin.admin_pages import AdminLoginPage
        AdminLoginPage(drv).login_as_admin()
    except Exception:
        try:
            drv.get(settings.wp_base_url)
        except Exception:
            pass
    log_step(f"browser session started on {settings.wp_base_url} — window will stay open until all tests finish")
    yield drv
    log_step("all tests finished — closing browser session")
    try:
        drv.quit()
    except Exception:
        pass


@pytest.fixture(autouse=True)
def driver(session_driver, request) -> Iterator[webdriver.Remote]:
    """Per-test wrapper around the shared session browser.

    Ensures the Chrome window visually updates on screen for every test module!
    """
    test_name = request.node.name
    module_name = request.node.fspath.basename if hasattr(request.node, "fspath") else ""

    route_map = {
        "test_tags.py": "wp-admin/admin.php?page=kirki-ecommerce#/tags",
        "test_brands.py": "wp-admin/admin.php?page=kirki-ecommerce#/brands",
        "test_categories.py": "wp-admin/admin.php?page=kirki-ecommerce#/categories",
        "test_collections.py": "wp-admin/admin.php?page=kirki-ecommerce#/collections",
        "test_attributes.py": "wp-admin/admin.php?page=kirki-ecommerce#/attributes",
        "test_shipping.py": "wp-admin/admin.php?page=kirki-ecommerce#/shipping",
        "test_tax_profiles.py": "wp-admin/admin.php?page=kirki-ecommerce#/taxes",
        "test_taxes_currencies.py": "wp-admin/admin.php?page=kirki-ecommerce#/settings",
        "test_customers.py": "wp-admin/admin.php?page=kirki-ecommerce#/customers",
        "test_settings_api.py": "wp-admin/admin.php?page=kirki-ecommerce#/settings",
        "test_coupons.py": "wp-admin/admin.php?page=kirki-ecommerce#/coupons",
        "test_coupons_advanced.py": "wp-admin/admin.php?page=kirki-ecommerce#/coupons",
        "test_coupons_extended.py": "wp-admin/admin.php?page=kirki-ecommerce#/coupons",
        "test_order_lifecycle.py": "wp-admin/admin.php?page=kirki-ecommerce#/orders",
        "test_order_refunds.py": "wp-admin/admin.php?page=kirki-ecommerce#/orders",
        "test_product_advanced.py": "wp-admin/admin.php?page=kirki-ecommerce#/products",
        "test_product_duplicate_bulk.py": "wp-admin/admin.php?page=kirki-ecommerce#/products",
        "test_stock_management.py": "wp-admin/admin.php?page=kirki-ecommerce#/products",
        "test_admin_reports_analytics.py": "wp-admin/admin.php?page=kirki-ecommerce#/reports",
        "test_admin_settings_extended.py": "wp-admin/admin.php?page=kirki-ecommerce#/settings",
        "test_onboarding.py": "wp-admin/admin.php?page=kirki-ecommerce#/dashboard",
        "test_bulk_operations.py": "wp-admin/admin.php?page=kirki-ecommerce#/products",
        "test_cart_api.py": "cart",
        "test_account_api.py": "account",
        "test_customer_profile.py": "account",
        "test_product_variations.py": "shop",
        "test_storefront_reviews_ratings.py": "shop",
    }

    # Verify session health
    try:
        _ = session_driver.current_url
    except Exception:
        try:
            session_driver = driver_factory()
            session_driver.implicitly_wait(settings.implicit_wait)
            session_driver.set_page_load_timeout(60)
            from pages.admin.admin_pages import AdminLoginPage
            AdminLoginPage(session_driver).login_as_admin()
        except Exception:
            pass

    if module_name in route_map:
        try:
            target_url = f"{settings.wp_base_url.rstrip('/')}/{route_map[module_name]}"
            if session_driver.current_url != target_url:
                session_driver.get(target_url)
        except Exception:
            pass

    yield session_driver

    outcome = "passed"
    try:
        outcome = (
            request.node.rep_call.outcome
            if hasattr(request.node, "rep_call")
            else "passed"
        )
    except AttributeError:
        pass

    # Step screenshot at the end of every test
    try:
        log_step(f"test {test_name} finished [{outcome}]", driver=session_driver)
    except Exception:
        pass

    if outcome != "passed":
        screenshot = save_screenshot(session_driver, test_name)
        source     = save_page_source(session_driver, test_name)
        console    = capture_console_errors(session_driver)
        log_debug(
            f"[capture] {test_name}: screenshot={screenshot} "
            f"html={source} console_errors={console}"
        )


@pytest.fixture(scope="session")
def admin_client() -> Iterator[WpRestClient]:
    """Session-scoped REST client authenticated as the admin."""
    client = WpRestClient()
    client.login_as(settings.admin_user, settings.admin_password)
    assert client.is_authenticated, "admin REST login failed"
    yield client
    client.log_out()


@pytest.fixture(scope="session")
def wp_rest(admin_client) -> WpRest:
    return WpRest(admin_client)


@pytest.fixture
def guest_cart_client() -> Iterator[WpRestClient]:
    """Unauthenticated REST client for guest-cart operations."""
    yield WpRestClient()


# ---------------------------------------------------------------------------
# Test data fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def test_prefix() -> str:
    """Unique prefix for all entities created by this test."""
    return unique_name("")


@pytest.fixture
def smoke_product(wp_rest, test_prefix) -> Iterator[dict]:
    """A published, stocked product for smoke/flow tests (REST-created)."""
    product = wp_rest.products.create_simple(
        title=f"{test_prefix} Product",
        price=49.99,
        stock=10,
        description="Automated test product",
    )
    yield product
    try:
        wp_rest.products.delete(product["id"])
    except Exception as exc:  # pragma: no cover
        log_debug(f"smoke_product cleanup failed: {exc}")


@pytest.fixture
def test_coupon(wp_rest, test_prefix) -> Iterator[dict]:
    """A 10%-off coupon for test carts."""
    coupon = wp_rest.coupons.create(
        code=f"{test_prefix}OFF10",
        discount_value_type="percentage",
        discount_amount_percentage=10.0,
    )
    yield coupon
    try:
        wp_rest.coupons.delete(coupon["id"])
    except Exception as exc:  # pragma: no cover
        log_debug(f"test_coupon cleanup failed: {exc}")


@pytest.fixture
def api_cleanup(wp_rest, test_prefix):
    """Fixture that records created ids and deletes them on teardown."""

    created: dict[str, list[int]] = {"products": [], "coupons": [], "customers": []}

    def _register(kind: str, entity_id: int) -> int:
        created.setdefault(kind, []).append(entity_id)
        return entity_id

    yield _register

    for coupon_id in created.get("coupons", []):
        try:
            wp_rest.coupons.delete(coupon_id)
        except Exception:
            pass
    for customer_id in created.get("customers", []):
        try:
            wp_rest.customers.delete(customer_id)
        except Exception:
            pass
    for product_id in created.get("products", []):
        try:
            wp_rest.products.delete(product_id)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Site-state fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def site_pages(wp_rest):
    """Ensure the plugin's site pages exist (shop/cart/checkout/account/...)."""
    log_step("ensure site pages exist (advance.pages.*)")
    try:
        settings_data = wp_rest.settings.get("advance.pages")
    except Exception:
        settings_data = {}
    missing = [k for k, v in (settings_data or {}).items() if not v]
    if missing:
        log_debug(f"site pages missing: {missing} (created during onboarding)")
    return settings_data
