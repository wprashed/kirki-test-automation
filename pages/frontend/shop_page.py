"""Shop page (resources/views/site/shop.php + parts)."""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from pages.base_page import BasePage
from utils.logging_setup import log_step
from utils.money import parse_money_to_cents


class ProductCard:
    """A single product card in the shop grid (shop/parts/product-card.php)."""

    TITLE = (By.CSS_SELECTOR, ".kecom-product-card-title")
    PRICE = (By.CSS_SELECTOR, ".kecom-product-card-price")
    SALE_PRICE = (By.CSS_SELECTOR, ".kecom-product-card-price-discount")
    CATEGORY = (By.CSS_SELECTOR, ".kecom-product-card-category")
    ADD_TO_CART = (By.CSS_SELECTOR, ".kecom-product-card-add-to-cart")

    def __init__(self, root: WebElement, driver: WebDriver):
        self.root = root
        self.driver = driver

    @property
    def title(self) -> str:
        return self.root.find_element(*self.TITLE).text.strip()

    @property
    def price_cents(self) -> int:
        return parse_money_to_cents(
            self.root.find_element(*self.PRICE).text
        )

    @property
    def has_sale_price(self) -> bool:
        return bool(self.root.find_elements(*self.SALE_PRICE))

    def open_product(self) -> None:
        self.root.find_element(*self.TITLE).click()

    def add_to_cart(self) -> None:
        btn = self.root.find_element(*self.ADD_TO_CART)
        btn.click()


class ShopPage(BasePage):
    url_fragment = "shop"

    GRID = (By.CSS_SELECTOR, ".kecom-products-grid")
    CARDS = (By.CSS_SELECTOR, ".kecom-product-card")
    SEARCH_BTN = (By.CSS_SELECTOR, ".kecom-products-search-btn")
    SEARCH_INPUT = (By.ID, "kecom-search-input")
    SORT_SELECT = (By.ID, "sort_by")
    EMPTY_STATE = (By.CSS_SELECTOR, ".kecom-products-empty, .kecom-empty-state")

    def open_shop(self) -> "ShopPage":
        return self.open_page("shop")

    def cards(self) -> list[ProductCard]:
        self.find(*self.GRID)
        return [
            ProductCard(el, self.driver)
            for el in self.driver.find_elements(*self.CARDS)
        ]

    def find_card(self, title: str) -> ProductCard:
        log_step(f"find product card {title!r} in shop")
        for card in self.cards():
            if card.title == title:
                return card
        raise AssertionError(f"product card {title!r} not found in shop grid")

    def search(self, query: str) -> None:
        log_step(f"search shop for {query!r}")
        if self.exists(*self.SEARCH_BTN, timeout=1):
            try:
                btn = self.driver.find_element(*self.SEARCH_BTN)
                if btn.is_displayed():
                    self.click(btn)
            except Exception:
                pass
        search = self.find(*self.SEARCH_INPUT)
        search.clear()
        search.send_keys(query)
        search.send_keys("\ue007")  # Enter (verified @keydown.enter.prevent="search()")
        self.driver.switch_to.active_element

    def sort_by(self, value: str) -> None:
        log_step(f"sort shop by {value}")
        from selenium.webdriver.support.ui import Select
        Select(self.find(*self.SORT_SELECT)).select_by_value(value)

    def wait_for_product(self, title: str) -> ProductCard:
        def _found(_: WebDriver):
            for card in self.cards():
                if card.title == title:
                    return card
            return None

        from utils.selenium_helpers import wait_until
        return wait_until(self.driver, _found, message=f"product {title!r}")
