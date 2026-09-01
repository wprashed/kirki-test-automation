"""Customer account pages (resources/views/site/account/**)."""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage
from pages.components.account_sidebar import AccountSidebar
from utils.logging_setup import log_step
from utils.money import parse_money_to_cents


class AccountOrdersPage(BasePage):
    url_fragment = "account"

    TABLE = (By.CSS_SELECTOR, ".kecom-orders-table")
    ORDER_ROWS = (By.CSS_SELECTOR, ".kecom-orders-table tbody tr, .kecom-orders-table tr")
    LOAD_MORE = (By.CSS_SELECTOR, "button.kecom-btn-primary")

    def __init__(self, driver: WebDriver, base_url: str | None = None):
        super().__init__(driver, base_url)
        self.sidebar = AccountSidebar(driver)

    def open_orders(self) -> "AccountOrdersPage":
        return self.open_page("account")

    def order_links(self) -> dict[str, str]:
        """Map of invoice/order number -> href (uuid link)."""
        rows = self.driver.find_elements(*self.ORDER_ROWS)
        links: dict[str, str] = {}
        for row in rows:
            anchors = row.find_elements(By.CSS_SELECTOR, "a[href*='orders/']")
            for a in anchors:
                links[a.text.strip()] = a.get_attribute("href")
        return links

    def has_order(self, order_number: str) -> bool:
        return order_number in self.driver.page_source


class OrderDetailsPage(BasePage):
    url_fragment = "orders/"

    TITLE = (By.CSS_SELECTOR, ".kecom-order-details-title")
    STATUS_BADGES = (By.CSS_SELECTOR, ".kecom-order-details-heading-row .kecom-badge")
    PRICING_ROWS = (By.CSS_SELECTOR, ".kecom-pricing-row")
    PRICING_LABEL = (By.CSS_SELECTOR, ".kecom-pricing-label")
    PRICING_VALUE = (By.CSS_SELECTOR, ".kecom-pricing-value")
    PRODUCT_NAMES = (By.CSS_SELECTOR, ".kecom-product-name")
    CONTACT_EMAIL = (By.CSS_SELECTOR, ".kecom-order-info-block .kecom-order-info-text")

    def open_details(self, path: str) -> "OrderDetailsPage":
        return self.open_page(path.lstrip("/"))

    def pricing(self) -> dict[str, int]:
        """Map of pricing label -> cents (Subtotal/Shipping/Taxes/Discount/Total)."""
        result: dict[str, int] = {}
        for row in self.driver.find_elements(*self.PRICING_ROWS):
            try:
                label = row.find_element(*self.PRICING_LABEL).text.strip()
                value = row.find_element(*self.PRICING_VALUE).text.strip()
            except Exception:
                continue
            if value:
                try:
                    result[label] = parse_money_to_cents(value)
                except ValueError:
                    continue
        return result

    def product_names(self) -> list[str]:
        return [el.text.strip() for el in self.driver.find_elements(*self.PRODUCT_NAMES)]

    def status_badges(self) -> list[str]:
        return [el.text.strip() for el in self.driver.find_elements(*self.STATUS_BADGES)]

    def title(self) -> str:
        return self.text_of(*self.TITLE)


class AccountDashboardPage(BasePage):
    url_fragment = "account"

    WELCOME_NAME = (By.CSS_SELECTOR, ".kecom-account-welcome-name")
    RECENT_ORDERS_TABLE = (By.CSS_SELECTOR, ".kecom-orders-table")
    EMAIL_VALUE = (By.CSS_SELECTOR, ".kecom-account-field-value")

    def open_dashboard(self) -> "AccountDashboardPage":
        return self.open_page("account")

    def welcome_name(self) -> str:
        return self.text_of(*self.WELCOME_NAME)

    def displayed_email(self) -> str:
        els = self.driver.find_elements(*self.EMAIL_VALUE)
        return els[1].text.strip() if len(els) > 1 else ""
