"""Typed helpers over the plugin REST API.

Endpoints verified in routes/api.php (namespace kirki/ecommerce/v1).
Each method returns parsed JSON and supports cleanup-oriented design:
fixtures create entities here and delete them in teardown.
"""

from __future__ import annotations

import uuid
from typing import Any

from utils.api.client import WpRestClient
from utils.config import settings
from utils.logging_setup import log_debug


def unique_name(base: str = "Test") -> str:
    """Return a unique, prefix-marked name for test entities."""
    return f"{settings.test_data_prefix}_{base}_{uuid.uuid4().hex[:10]}"


class ProductsApi:
    def __init__(self, client: WpRestClient):
        self.client = client

    def create(self, *, title: str, price: float = 49.99, stock: int = 10,
               status: str = "published", short_description: str = "",
               description: str = "", has_variants: bool = False,
               currency_id: int = 1, variant: dict | None = None,
               categories: list[int] | None = None, tags: list[int] | None = None,
               brand_id: int | None = None, **extra) -> dict:
        """Create a product with a variant and optional taxonomies (POST /products)."""
        payload: dict[str, Any] = {
            "title": title,
            "status": status,
            "short_description": short_description,
            "description": description,
            "has_variants": has_variants,
            "currency_id": currency_id,
        }
        if categories:
            payload["categories"] = categories
        if tags:
            payload["tags"] = tags
        if brand_id:
            payload["brand_id"] = brand_id
        payload.update(extra)

        if variant is not None:
            payload["variants"] = [variant]
        elif "variants" not in payload:
            payload["variants"] = [{
                "base_price": float(price),
                "available_quantity": stock,
                "track_inventory": True,
                "in_stock": True,
                "is_default": True,
                "sku": f"SKU-{uuid.uuid4().hex[:8].upper()}"
            }]

        resp = self.client.post("/products", json=payload, expected=(200, 201))
        data = resp.json().get("data", resp.json())
        log_debug(f"created product id={data.get('id')} {data.get('title')!r}")
        return data

    def create_simple(self, **kwargs) -> dict:
        """Create a simple (non-variant) product with a single variant."""
        price = kwargs.pop("price", 49.99)
        stock = kwargs.pop("stock", 10)
        variant = {
            "base_price": float(price),
            "available_quantity": stock,
            "track_inventory": True,
            "in_stock": True,
            "is_default": True,
            "sku": f"SKU-{uuid.uuid4().hex[:8].upper()}",
        }
        variant.update(kwargs.pop("variant", {}) or {})
        return self.create(variant=variant, **kwargs)

    def get(self, product_id: int) -> dict:
        return self.client.get(f"/products/{product_id}", expected=200).json()["data"]

    def update(self, product_id: int, **payload) -> dict:
        resp = self.client.put(f"/products/{product_id}", json=payload, expected=200)
        return resp.json()["data"]

    def delete(self, product_id: int) -> None:
        self.client.delete(f"/products/{product_id}", expected=200)

    def list_all(self, **params) -> list[dict]:
        resp = self.client.get("/products", params={"limit": 100, **params},
                               expected=200)
        return resp.json()["data"]


class VariantsApi:
    def __init__(self, client: WpRestClient):
        self.client = client

    def get_for_product(self, product_id: int) -> list[dict]:
        resp = self.client.get(f"/products/{product_id}", expected=200)
        return resp.json()["data"].get("variants", [])


class CouponsApi:
    def __init__(self, client: WpRestClient):
        self.client = client

    def create(self, *, code: str, title: str = "Test Coupon",
               discount_value_type: str = "percentage",
               discount_amount_percentage: float = 10.0,
               is_active: bool = True, **extra) -> dict:
        """Create a coupon via REST API (POST /coupons)."""
        import datetime
        now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        fixed_val = float(extra.pop("fixed_amount", 5.0))

        payload: dict[str, Any] = {
            "method": "code",
            "code": code,
            "title": title,
            "discount_type": "amount-off",
            "discount_target": "order",
            "discount_value_type": discount_value_type,
            "discount_amount": discount_amount_percentage if discount_value_type == "percentage" else fixed_val,
            "start_datetime": now_str,
            "is_active": is_active,
        }
        if discount_value_type == "percentage":
            payload["discount_amount_percentage"] = discount_amount_percentage
        else:
            payload["base_discount_amount_fixed"] = int(round(fixed_val * 100))
        payload.update(extra)

        resp = self.client.post("/coupons", json=payload, expected=(200, 201))
        data = resp.json().get("data", resp.json())
        log_debug(f"created coupon id={data.get('id')} code={data.get('code')!r}")
        return data

    def get(self, coupon_id: int) -> dict:
        return self.client.get(f"/coupons/{coupon_id}", expected=200).json()["data"]

    def delete(self, coupon_id: int) -> None:
        self.client.delete(f"/coupons/{coupon_id}", expected=200)


class CustomersApi:
    def __init__(self, client: WpRestClient):
        self.client = client

    def create(self, *, email: str, first_name: str = "Test",
               last_name: str = "Customer", **extra) -> dict:
        addr = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": "5551234567",
            "address_line1": "1 Market St",
            "city": "San Francisco",
            "state": "CA",
            "country": "US",
            "postal_code": "94103",
        }
        payload = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "shipping_address": addr,
            "billing_address": addr,
            **extra,
        }
        resp = self.client.post("/customers", json=payload, expected=201)
        data = resp.json()["data"]
        log_debug(f"created customer id={data.get('id')} email={data.get('email')!r}")
        return data

    def get(self, customer_id: int) -> dict:
        return self.client.get(f"/customers/{customer_id}", expected=200).json()["data"]

    def delete(self, customer_id: int) -> None:
        self.client.delete(f"/customers/{customer_id}", expected=200)


class OrdersApi:
    def __init__(self, client: WpRestClient):
        self.client = client

    def create(self, payload: dict) -> dict:
        resp = self.client.post("/orders", json=payload, expected=[200, 201])
        return resp.json()["data"]

    def get(self, order_id: int) -> dict:
        return self.client.get(f"/orders/{order_id}", expected=200).json()["data"]

    def list_all(self, **params) -> list[dict]:
        resp = self.client.get("/orders", params={"limit": 100, **params},
                               expected=200)
        data = resp.json()["data"]
        if isinstance(data, dict):
            return data.get("results", [])
        return data if isinstance(data, list) else []

    def action(self, order_id: int, action: str) -> dict:
        """Perform an order action (verified values from
        resources/data/order-state-matrix.json)."""
        resp = self.client.patch(f"/orders/{order_id}/action",
                                 json={"action": action}, expected=200)
        return resp.json()["data"]


class CartApi:
    """Frontend (guest or logged-in) cart operations."""

    def __init__(self, client: WpRestClient):
        self.client = client

    def get_cart(self, cart_token: str | None = None) -> dict:
        headers = {"kecom-cart-token": cart_token} if cart_token else {}
        resp = self.client.get("/cart", headers=headers, auth=False, expected=200)
        return resp.json()["data"]

    def add_item(self, variant_id: int, quantity: int = 1,
                 cart_token: str | None = None) -> dict:
        headers = {"kecom-cart-token": cart_token} if cart_token else {}
        resp = self.client.post("/cart/items", json={
            "variant_id": variant_id,
            "quantity": quantity,
        }, headers=headers, auth=False, expected=200)
        return resp.json()["data"]

    def update_item(self, item_id: int, quantity: int,
                    cart_token: str | None = None) -> dict:
        headers = {"kecom-cart-token": cart_token} if cart_token else {}
        resp = self.client.put(f"/cart/items/{item_id}", json={
            "quantity": quantity,
        }, headers=headers, auth=False, expected=200)
        return resp.json()["data"]

    def remove_item(self, item_id: int, cart_token: str | None = None) -> dict:
        headers = {"kecom-cart-token": cart_token} if cart_token else {}
        resp = self.client.delete(f"/cart/items/{item_id}", headers=headers,
                                  auth=False, expected=200)
        return resp.json()["data"]

    def empty(self, cart_token: str | None = None) -> dict:
        headers = {"kecom-cart-token": cart_token} if cart_token else {}
        resp = self.client.delete("/cart", headers=headers, auth=False,
                                  expected=200)
        return resp.json()["data"]

    def apply_coupon(self, code: str, cart_token: str | None = None) -> dict:
        headers = {"kecom-cart-token": cart_token} if cart_token else {}
        resp = self.client.post("/cart/coupon", json={"code": code},
                                headers=headers, auth=False)
        if resp.status_code != 200:
            raise AssertionError(f"apply_coupon failed: {resp.status_code} {resp.text[:300]}")
        return resp.json()["data"]


class SettingsApi:
    def __init__(self, client: WpRestClient):
        self.client = client

    def get(self, key: str) -> dict:
        return self.client.get(f"/settings/{key}", expected=200).json()["data"]

    def update(self, key: str, data: dict) -> dict:
        resp = self.client.put("/settings", json={"key": key, "data": data}, expected=200)
        return resp.json()["data"]


class AppConfigApi:
    def __init__(self, client: WpRestClient):
        self.client = client

    def get(self) -> dict:
        return self.client.get("/app-config", expected=200).json()["data"]


class OfflinePaymentsApi:
    def __init__(self, client: WpRestClient):
        self.client = client

    def list_all(self) -> list[dict]:
        resp = self.client.get("/offline-payments", expected=200)
        return resp.json()["data"]

    def create(self, *, name: str, instructions: str = "Test instructions") -> dict:
        resp = self.client.post("/offline-payments", json={
            "name": name,
            "instructions": instructions,
            "is_enabled": True,
        }, expected=201)
        return resp.json()["data"]

    def delete(self, payment_id: int) -> None:
        self.client.delete(f"/offline-payments/{payment_id}", expected=200)


class WpRest:
    """Aggregated API accessor."""

    def __init__(self, client: WpRestClient):
        self.client = client
        self.products = ProductsApi(client)
        self.variants = VariantsApi(client)
        self.coupons = CouponsApi(client)
        self.customers = CustomersApi(client)
        self.orders = OrdersApi(client)
        self.cart = CartApi(client)
        self.settings = SettingsApi(client)
        self.app_config = AppConfigApi(client)
        self.offline_payments = OfflinePaymentsApi(client)
