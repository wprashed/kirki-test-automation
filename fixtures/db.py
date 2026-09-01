"""Direct database helpers for verification and cleanup.

Uses the Local by Flywheel MySQL socket (or TCP host) from settings.
All destructive queries are scoped to test-created rows only
(TEST_DATA_PREFIX + captured IDs), never broad deletes.
"""

from __future__ import annotations

import contextlib
from typing import Any, Iterator

from utils.config import settings
from utils.logging_setup import log_debug, log_warning

try:
    import pymysql

    HAS_PYMYSQL = True
except ImportError:  # pragma: no cover
    HAS_PYMYSQL = False


@contextlib.contextmanager
def db_connection() -> Iterator[Any]:
    """Yield a pymysql connection configured from settings."""
    if not HAS_PYMYSQL:
        raise RuntimeError(
            "pymysql is required for database helpers. Add it to requirements.txt."
        )
    kwargs: dict[str, Any] = {
        "user": settings.db_user,
        "password": settings.db_password,
        "database": settings.db_name,
        "autocommit": True,
        "cursorclass": pymysql.cursors.DictCursor,
    }
    host = settings.db_host
    if host.startswith("/") or host.startswith("."):
        kwargs["unix_socket"] = host
    else:
        kwargs["host"] = host or "localhost"
        kwargs["port"] = settings.db_port
    conn = pymysql.connect(**kwargs)
    try:
        yield conn
    finally:
        conn.close()


def query_one(sql: str, params: tuple = ()) -> dict | None:
    with db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()


def query_all(sql: str, params: tuple = ()) -> list[dict]:
    with db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return list(cur.fetchall())


def execute(sql: str, params: tuple = ()) -> None:
    with db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)


# ---------------------------------------------------------------------------
# Test-data cleanup helpers
# ---------------------------------------------------------------------------

def _product_ids_by_prefix(prefix: str) -> list[int]:
    rows = query_all(
        "SELECT id FROM kirki_ecommerce_products WHERE title LIKE %s", (f"{prefix}%",)
    )
    return [r["id"] for r in rows]


def cleanup_test_data(prefix: str | None = None) -> None:
    """Delete test-created rows (products, variants, coupons, customers, carts).

    Order matters: FK references must be removed before parents.
    Scoped strictly to rows whose titles/codes match the prefix.
    """
    prefix = prefix or settings.test_data_prefix
    log_debug(f"cleaning test data with prefix {prefix!r}")
    try:
        product_ids = _product_ids_by_prefix(prefix)

        # Order items + orders for test customers.
        customer_ids = [
            r["id"]
            for r in query_all(
                "SELECT id FROM kirki_ecommerce_customers WHERE email LIKE %s",
                (f"{prefix}%",),
            )
        ]
        if customer_ids:
            placeholders = ",".join(["%s"] * len(customer_ids))
            order_ids = [
                r["id"]
                for r in query_all(
                    f"SELECT id FROM kirki_ecommerce_orders "
                    f"WHERE customer_id IN ({placeholders})",
                    tuple(customer_ids),
                )
            ]
            if order_ids:
                oh = ",".join(["%s"] * len(order_ids))
                execute(
                    f"DELETE FROM kirki_ecommerce_order_items WHERE order_id IN ({oh})",
                    tuple(order_ids),
                )
                execute(
                    f"DELETE FROM kirki_ecommerce_order_activities WHERE order_id IN ({oh})",
                    tuple(order_ids),
                )
                execute(
                    f"DELETE FROM kirki_ecommerce_refunds WHERE order_id IN ({oh})",
                    tuple(order_ids),
                )
                execute(
                    f"DELETE FROM kirki_ecommerce_orders WHERE id IN ({oh})",
                    tuple(order_ids),
                )
            execute(
                f"DELETE FROM kirki_ecommerce_addresses WHERE customer_id IN ({placeholders})",
                tuple(customer_ids),
            )
            execute(
                f"DELETE FROM kirki_ecommerce_carts WHERE customer_id IN ({placeholders})",
                tuple(customer_ids),
            )
            execute(
                f"DELETE FROM kirki_ecommerce_customers WHERE id IN ({placeholders})",
                tuple(customer_ids),
            )

        # Cart items/carts keyed by the guest cart token (cannot be matched
        # by prefix - only ever delete carts we created via the API).
        # Carts for guest checkout get removed via their token; we only clean
        # carts that reference our products.
        if product_ids:
            ph = ",".join(["%s"] * len(product_ids))
            cart_item_rows = query_all(
                f"SELECT cart_id FROM kirki_ecommerce_cart_items "
                f"WHERE product_id IN ({ph})",
                tuple(product_ids),
            )
            cart_ids = list({r["cart_id"] for r in cart_item_rows})
            if cart_ids:
                ch = ",".join(["%s"] * len(cart_ids))
                execute(
                    f"DELETE FROM kirki_ecommerce_cart_items WHERE cart_id IN ({ch})",
                    tuple(cart_ids),
                )
                execute(
                    f"DELETE FROM kirki_ecommerce_carts WHERE id IN ({ch})",
                    tuple(cart_ids),
                )

            # Coupon product/usage links then products.
            coupon_ids = [
                r["id"]
                for r in query_all(
                    "SELECT id FROM kirki_ecommerce_coupons WHERE code LIKE %s "
                    "OR title LIKE %s",
                    (f"{prefix}%", f"{prefix}%"),
                )
            ]
            if coupon_ids:
                cph = ",".join(["%s"] * len(coupon_ids))
                execute(
                    f"DELETE FROM kirki_ecommerce_coupon_usage WHERE coupon_id IN ({cph})",
                    tuple(coupon_ids),
                )
                execute(
                    f"DELETE FROM kirki_ecommerce_coupons WHERE id IN ({cph})",
                    tuple(coupon_ids),
                )

            execute(
                f"DELETE FROM kirki_ecommerce_variants WHERE product_id IN ({ph})",
                tuple(product_ids),
            )
            execute(
                f"DELETE FROM kirki_ecommerce_products WHERE id IN ({ph})",
                tuple(product_ids),
            )
    except Exception as exc:  # pragma: no cover
        log_warning(f"cleanup_test_data failed (continuing): {exc}")
