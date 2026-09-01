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


@pytest.fixture(scope="session")
def driver_factory():
    """Returns a callable that creates a fresh browser driver."""
    browser = settings.browser.lower()
    if browser == "firefox":
        return _firefox_driver
    if browser == "chrome":
        return _chrome_driver
    raise ValueError(f"unsupported BROWSER={browser!r} (use chrome or firefox)")


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
    log_step("browser session started — window will stay open until all tests finish")
    yield drv
    log_step("all tests finished — closing browser session")
    try:
        drv.quit()
    except Exception:
        pass


@pytest.fixture
def driver(session_driver, request) -> Iterator[webdriver.Remote]:
    """Per-test wrapper around the shared session browser.

    Yields the same driver instance for every test — the browser is NEVER
    closed between tests.  Only failure artifacts (screenshot / page-source /
    console log) are captured per-test when a test fails.
    """
    test_name = request.node.name

    yield session_driver          # ← same window, no quit()

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
