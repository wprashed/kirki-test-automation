"""Shared state for the ordered smoke workflow.

The smoke suite mirrors one complete purchase journey, so the steps share
a ``SmokeContext`` (product, cart token, order id/uuid, order number, ...).
Each step is independent enough to fail on its own, but together they prove
the full workflow end to end.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SmokeContext:
    product_title: str = ""
    product_price_cents: int = 4999
    product_variant_id: Optional[int] = None
    product_id: Optional[int] = None
    product_slug: str = ""
    cart_token: str = ""
    cart_item_id: Optional[int] = None
    cart_quantity: int = 1
    cart_subtotal_cents: int = 0
    shipping_cents: int = 0
    tax_cents: int = 0
    discount_cents: int = 0
    order_total_cents: int = 0
    order_id: Optional[int] = None
    order_uuid: str = ""
    order_number: str = ""
    payment_provider: str = "paypal"
    customer_email: str = ""
    created_ids: dict = field(default_factory=dict)
