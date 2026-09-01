"""Smoke workflow fixtures: shared context + step preconditions."""

from __future__ import annotations

import uuid

import pytest

from tests.smoke.context import SmokeContext
from utils.config import settings
from utils.logging_setup import log_step


@pytest.fixture(scope="package")
def smoke_ctx() -> SmokeContext:
    return SmokeContext(
        customer_email=f"{settings.test_data_prefix}_smoke_{uuid.uuid4().hex[:8]}@example.com"
    )


@pytest.fixture(scope="package", autouse=True)
def smoke_data(wp_rest, smoke_ctx):
    """Create the smoke product once (package scope) and register cleanup."""
    price = 49.99
    product = wp_rest.products.create_simple(
        title=f"{settings.test_data_prefix} Smoke {uuid.uuid4().hex[:6]}",
        price=price,
        stock=10,
        description="Smoke test product - created by automated tests",
    )
    smoke_ctx.product_title = product["title"]
    smoke_ctx.product_id = product["id"]
    smoke_ctx.product_slug = product.get("slug", "")
    variants = product.get("variants") or wp_rest.variants.get_for_product(product["id"])
    smoke_ctx.product_variant_id = variants[0]["id"]
    smoke_ctx.product_price_cents = int(round(price * 100))

    log_step(f"smoke product created: id={product['id']} {product['title']!r}")

    yield product

    # Teardown: delete the product (variants cascade), then any leftover rows.
    try:
        wp_rest.products.delete(product["id"])
    except Exception:
        pass
    try:
        from fixtures.db import cleanup_test_data

        cleanup_test_data()
    except Exception:
        pass


@pytest.fixture(scope="package")
def smoke_customer(wp_rest, smoke_ctx):
    """Ensure a customer record exists for the smoke email (REST)."""
    from utils.api.wp_rest import unique_name

    email = smoke_ctx.customer_email
    customer = wp_rest.customers.create(
        email=email,
        first_name="Smoke",
        last_name="Customer",
    )
    smoke_ctx.created_ids["customer"] = customer["id"]
    yield customer
    try:
        wp_rest.customers.delete(customer["id"])
    except Exception:
        pass
