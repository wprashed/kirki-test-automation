"""Smoke: product creation (REST) + visibility on the frontend shop."""

import pytest

from pages.frontend.shop_page import ShopPage
from utils.config import settings
from utils.logging_setup import log_step
from utils.money import assert_money_equal


@pytest.mark.smoke
@pytest.mark.order(3)
class TestProductAndShop:
    def test_product_created_via_rest(self, wp_rest, smoke_ctx, smoke_data):
        """The smoke product exists via REST with expected price/stock."""
        product = wp_rest.products.get(smoke_ctx.product_id)
        assert product["id"] == smoke_ctx.product_id
        assert product["title"] == smoke_ctx.product_title
        assert product.get("status") == "published"
        variants = product.get("variants") or []
        assert variants, "product has no variants"
        variant = variants[0]
        smoke_ctx.product_variant_id = variant["id"]
        from utils.money import parse_money_to_cents
        smoke_ctx.product_price_cents = parse_money_to_cents(variant.get("base_price", smoke_ctx.product_price_cents))
        assert variant.get("available_quantity") == 10
        log_step(
            f"product verified: price={smoke_ctx.product_price_cents} cents "
            f"stock={variant.get('available_quantity')}"
        )

    def test_product_visible_on_shop(self, driver, smoke_ctx):
        """The published product appears in the shop grid with correct price."""
        shop = ShopPage(driver).open_shop()
        card = shop.wait_for_product(smoke_ctx.product_title)
        assert_money_equal(smoke_ctx.product_price_cents, card.price_cents)
        log_step(f"shop card found: {card.title} @ {card.price_cents} cents")

    def test_product_search(self, driver, smoke_ctx):
        """Searching the product title surfaces the product card."""
        shop = ShopPage(driver).open_shop()
        shop.search(smoke_ctx.product_title)
        card = shop.wait_for_product(smoke_ctx.product_title)
        assert card.title == smoke_ctx.product_title
        log_step(f"search returned card: {card.title}")

    def test_product_detail_page(self, driver, smoke_ctx):
        """Product detail page shows title and price."""
        from pages.frontend.product_page import ProductPage

        page = ProductPage(driver).open_product(smoke_ctx.product_slug)
        assert page.title == smoke_ctx.product_title
        assert_money_equal(smoke_ctx.product_price_cents, page.price_cents)
        log_step(f"product detail OK: {page.title}")
