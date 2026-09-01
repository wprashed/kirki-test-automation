"""Product detail page (resources/views/site/shop/single.php)."""

from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logging_setup import log_step
from utils.money import parse_money_to_cents


class ProductPage(BasePage):
    url_fragment = "shop"

    TITLE = (By.CSS_SELECTOR, "h1.kecom-product-title")
    PRICE_CURRENT = (By.CSS_SELECTOR, ".kecom-product-price-current")
    PRICE_ORIGINAL = (By.CSS_SELECTOR, ".kecom-product-price-original")
    SHORT_DESCRIPTION = (By.CSS_SELECTOR, ".kecom-product-short-description")
    QUANTITY_INPUT = (By.ID, "quantity-input")
    ADD_TO_CART_BTN = (
        By.CSS_SELECTOR,
        "button.kecom-btn-primary:not(.kecom-btn-loading)",
    )
    VARIANT_OPTIONS = (By.CSS_SELECTOR, ".kecom-product-variant-option")
    VARIANT_COLORS = (By.CSS_SELECTOR, ".kecom-product-variant-color")
    OUT_OF_STOCK_BTN = (By.CSS_SELECTOR, ".kecom-product-info .kecom-btn-primary")

    def open_product(self, slug: str) -> "ProductPage":
        return self.open_page(f"shop/{slug}")

    @property
    def title(self) -> str:
        return self.text_of(*self.TITLE)

    @property
    def price_cents(self) -> int:
        return parse_money_to_cents(self.text_of(*self.PRICE_CURRENT))

    def set_quantity(self, quantity: int) -> None:
        log_step(f"set product quantity to {quantity}")
        qty = self.find(*self.QUANTITY_INPUT)
        qty.clear()
        qty.send_keys(str(quantity))

    def select_variant(self, value: str) -> None:
        """Click a non-color variant option by its visible text."""
        log_step(f"select variant {value!r}")
        for el in self.find_many(*self.VARIANT_OPTIONS):
            if (el.text or "").strip() == value:
                self.click(el)
                return
        raise AssertionError(f"variant option {value!r} not found")

    def add_to_cart(self) -> None:
        log_step("click Add to Cart on product page")
        btn = self.find(*self.ADD_TO_CART_BTN)
        self.click(btn)

    def add_to_cart_with_quantity(self, quantity: int) -> None:
        self.set_quantity(quantity)
        self.add_to_cart()

    def is_out_of_stock(self) -> bool:
        btn = self.find(*self.OUT_OF_STOCK_BTN)
        return "Out of Stock" in (btn.text or "")
