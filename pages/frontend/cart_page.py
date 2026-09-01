"""Cart page (resources/views/site/cart.php + parts)."""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from pages.base_page import BasePage
from utils.logging_setup import log_step
from utils.money import parse_money_to_cents


class CartItem:
    """A row in the cart (cart/parts/cart-item.php)."""

    QUANTITY_INPUT = (By.CSS_SELECTOR, ".kecom-quantity-input")
    INCREASE_BTN = (By.CSS_SELECTOR, "button[aria-label='Increase'], .kecom-quantity-btn:last-of-type")
    DECREASE_BTN = (By.CSS_SELECTOR, "button[aria-label='Decrease'], .kecom-quantity-btn:first-of-type")
    REMOVE_BTN = (By.CSS_SELECTOR, ".kecom-cart-item-remove, button[aria-label*='Remove']")
    TITLE = (By.CSS_SELECTOR, ".kecom-cart-item-title, .kecom-cart-item-info h4")

    def __init__(self, root: WebElement, driver: WebDriver):
        self.root = root
        self.driver = driver

    @property
    def item_id(self) -> str:
        return self.root.get_attribute("id")

    @property
    def quantity(self) -> int:
        return int(self.root.find_element(*self.QUANTITY_INPUT).get_attribute("value") or 1)

    def set_quantity(self, quantity: int) -> None:
        current = self.quantity
        while current < quantity:
            self.increase()
            current += 1
        while current > quantity:
            self.decrease()
            current -= 1

    def increase(self) -> None:
        from utils.selenium_helpers import safe_click
        safe_click(self.driver, self.root.find_element(*self.INCREASE_BTN))

    def decrease(self) -> None:
        from utils.selenium_helpers import safe_click
        safe_click(self.driver, self.root.find_element(*self.DECREASE_BTN))

    def remove(self) -> None:
        from utils.selenium_helpers import safe_click
        safe_click(self.driver, self.root.find_element(*self.REMOVE_BTN))


class CartPage(BasePage):
    url_fragment = "cart"

    PAGE = (By.CSS_SELECTOR, ".kecom-cart-page")
    ITEMS = (By.CSS_SELECTOR, ".kecom-cart-item")
    SUBTOTAL_VALUE = (By.CSS_SELECTOR, ".kecom-cart-summary-item-value")
    ESTIMATE_TOTAL = (By.CSS_SELECTOR, ".kecom-cart-summary-total-value")
    CHECKOUT_BTN = (By.CSS_SELECTOR, ".kecom-cart-summary a.kecom-btn-primary")
    EMPTY_TITLE = (By.CSS_SELECTOR, ".kecom-cart-empty-title")
    EMPTY_DESC = (By.CSS_SELECTOR, ".kecom-cart-empty-desc")

    def open_cart(self) -> "CartPage":
        self.open("cart-3")
        if not self.exists(*self.PAGE, timeout=2):
            self.open("cart")
        self.wait_until_loaded()
        return self

    def items(self) -> list[CartItem]:
        self.find(*self.PAGE)
        from utils.selenium_helpers import wait_until

        def _has_items(_: WebDriver):
            els = [el for el in self.driver.find_elements(*self.ITEMS) if el.is_displayed()]
            return els if els else None

        elements = wait_until(self.driver, _has_items, timeout=10, message="cart items rendering")
        return [CartItem(el, self.driver) for el in elements]

    def item_for(self, title: str) -> CartItem:
        for item in self.items():
            if title in (item.root.text or ""):
                return item
        raise AssertionError(f"cart item {title!r} not found")

    def is_empty(self) -> bool:
        from utils.selenium_helpers import wait_until

        def _check(_: WebDriver):
            items = [el for el in self.driver.find_elements(*self.ITEMS) if el.is_displayed()]
            if items:
                return "has_items"
            empty = [el for el in self.driver.find_elements(*self.EMPTY_TITLE) if el.is_displayed()]
            if empty:
                return "is_empty"
            return None

        res = wait_until(self.driver, _check, timeout=10, message="cart state loaded")
        return res == "is_empty"

    @property
    def subtotal_cents(self) -> int:
        return parse_money_to_cents(self.text_of(*self.SUBTOTAL_VALUE))

    @property
    def estimate_total_cents(self) -> int:
        return parse_money_to_cents(self.text_of(*self.ESTIMATE_TOTAL))

    def proceed_to_checkout(self) -> None:
        log_step("proceed to checkout from cart")
        btn = self.find(*self.CHECKOUT_BTN)
        self.click(btn)

    def wait_for_subtotal(self, expected_cents: int) -> None:
        from utils.selenium_helpers import wait_until

        def _check(_: WebDriver) -> bool:
            try:
                return self.subtotal_cents == expected_cents
            except (ValueError, AssertionError):
                return False

        wait_until(self.driver, _check, message=f"cart subtotal {expected_cents} cents")
