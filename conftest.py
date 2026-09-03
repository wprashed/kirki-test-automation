"""Root conftest: makes packages importable and wires the report hooks."""

from __future__ import annotations

import sys
from pathlib import Path

# Make framework packages (pages, utils, fixtures) importable from anywhere.
ROOT = Path(__file__).resolve().parent
for _pkg in ("utils", "pages", "fixtures"):
    pkg_path = ROOT / _pkg
    if str(pkg_path) not in sys.path:
        sys.path.insert(0, str(pkg_path))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.logging_setup import setup_logging  # noqa: E402

setup_logging()

# Import fixture plugins so pytest registers them (driver, wp_rest, ...).
from fixtures.conftest import (  # noqa: E402, F401
    admin_client,
    api_cleanup,
    driver,
    driver_factory,
    guest_cart_client,
    mobile_driver,
    session_driver,
    site_pages,
    smoke_product,
    test_coupon,
    test_prefix,
    wp_rest,
)


def pytest_configure(config):
    """Register custom markers (kept in sync with pytest.ini)."""
    markers = {
        "smoke": "core purchase workflow (ordered)",
        "regression": "full regression suite",
        "checkout": "checkout flows",
        "admin": "WordPress admin / SPA flows",
        "frontend": "shop, product, cart flows",
        "payment": "payment gateway flows",
        "security": "security checks",
        "critical": "critical-path tests",
        "order": "order lifecycle tests",
        "ui_walkthrough": "real human interactive UI tests",
        "performance": "high-concurrency multi-user stress testing",
    }
    for name, desc in markers.items():
        config.addinivalue_line("markers", f"{name}: {desc}")


def pytest_runtest_makereport(item, call):
    """Attach the test outcome to the node for the driver fixture to read."""
    if call.when == "call":
        setattr(item, "rep_call", call)
    elif call.when == "setup":
        setattr(item, "rep_setup", call)
