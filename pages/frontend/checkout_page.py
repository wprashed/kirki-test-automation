"""Checkout page (resources/views/site/checkout.php + parts).

Verified field IDs/names:
- contact: #contact-email (name=customer_email)
- shipping form #shipping-form: #shipping-country/state/first-name/last-name/
  address-line1/address-line2/city/postal-code/phone
- billing same checkbox (inside shipping form, x-model=billingSameAsShipping)
- billing form #billing-form: #billing-* mirror (hidden unless "same" unchecked)
- shipping method radios: input[name=shipping_method]
- payment radios: input[name=payment_provider] (value = provider id)
- coupon: #coupon-code + Apply button
- Place Order: button.kecom-pay-btn
"""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage
from pages.components.checkout_summary import CheckoutSummary
from pages.components.coupon_box import CouponBox
from utils.logging_setup import log_step
from utils.selenium_helpers import wait_until


class CheckoutPage(BasePage):
    url_fragment = "checkout"

    CONTACT_EMAIL = (By.ID, "contact-email")
    SHIPPING_FORM = (By.ID, "shipping-form")
    SHIPPING_COUNTRY = (By.ID, "shipping-country")
    SHIPPING_STATE = (By.ID, "shipping-state")
    SHIPPING_FIRST_NAME = (By.ID, "shipping-first-name")
    SHIPPING_LAST_NAME = (By.ID, "shipping-last-name")
    SHIPPING_ADDRESS1 = (By.ID, "shipping-address-line1")
    SHIPPING_ADDRESS2 = (By.ID, "shipping-address-line2")
    SHIPPING_CITY = (By.ID, "shipping-city")
    SHIPPING_POSTAL = (By.ID, "shipping-postal-code")
    SHIPPING_PHONE = (By.ID, "shipping-phone")
    BILLING_SAME_CHECKBOX = (
        By.CSS_SELECTOR,
        "#shipping-form input[type=checkbox][x-model='billingSameAsShipping']",
    )
    BILLING_FORM = (By.ID, "billing-form")
    BILLING_FIRST_NAME = (By.ID, "billing-first-name")
    BILLING_LAST_NAME = (By.ID, "billing-last-name")
    BILLING_ADDRESS1 = (By.ID, "billing-address-line1")
    BILLING_CITY = (By.ID, "billing-city")
    BILLING_STATE = (By.ID, "billing-state")
    BILLING_POSTAL = (By.ID, "billing-postal-code")
    SHIPPING_METHOD_RADIOS = (By.CSS_SELECTOR, "input[name=shipping_method]")
    PAYMENT_RADIOS = (By.CSS_SELECTOR, "input[name=payment_provider]")
    PAY_BTN = (By.CSS_SELECTOR, "button.kecom-pay-btn")
    FIELD_ERRORS = (By.CSS_SELECTOR, ".kecom-field-error:not([style*='display: none'])")

    def __init__(self, driver: WebDriver, base_url: str | None = None):
        super().__init__(driver, base_url)
        self.summary = CheckoutSummary(driver)
        self.coupon = CouponBox(driver)

    def open_checkout(self) -> "CheckoutPage":
        self.open("checkout-3")
        if not self.exists(*self.CONTACT_EMAIL, timeout=2) and not self.exists(*self.PAY_BTN, timeout=2):
            self.open("checkout")
        self.wait_until_loaded()
        return self

    # ------------------------------------------------------------------
    # Contact
    # ------------------------------------------------------------------
    def fill_contact_email(self, email: str) -> None:
        log_step(f"fill contact email {email}")
        el = self.find(*self.CONTACT_EMAIL)
        el.clear()
        el.send_keys(email)

    # ------------------------------------------------------------------
    # Shipping address
    # ------------------------------------------------------------------
    def fill_shipping_address(self, *, first_name: str, last_name: str,
                              country: str, state: str, city: str,
                              postal_code: str, address_line1: str,
                              address_line2: str = "", phone: str = "") -> None:
        log_step(f"fill shipping address for {first_name} {last_name}")
        self.find(*self.SHIPPING_FORM)
        values = {
            self.SHIPPING_FIRST_NAME: first_name,
            self.SHIPPING_LAST_NAME: last_name,
            self.SHIPPING_ADDRESS1: address_line1,
            self.SHIPPING_CITY: city,
            self.SHIPPING_POSTAL: postal_code,
        }
        if address_line2:
            values[self.SHIPPING_ADDRESS2] = address_line2
        if phone:
            values[self.SHIPPING_PHONE] = phone
        for locator, value in values.items():
            el = self.find(*locator)
            el.clear()
            el.send_keys(value)
        self._select_country_state(country, state)

    def _select_country_state(self, country: str, state: str) -> None:
        from selenium.webdriver.support.ui import Select

        country_el = self.find(*self.SHIPPING_COUNTRY)
        try:
            Select(country_el).select_by_value(country)
        except Exception:
            Select(country_el).select_by_visible_text(country)

        def _state_ready(_: WebDriver) -> bool:
            state_el = self.driver.find_element(*self.SHIPPING_STATE)
            return not state_el.get_attribute("disabled")

        wait_until(self.driver, _state_ready, message="state dropdown enabled")
        state_el = self.find(*self.SHIPPING_STATE)
        select = Select(state_el)
        try:
            select.select_by_value(state)
        except Exception:
            try:
                select.select_by_visible_text(state)
            except Exception:
                matched = False
                for opt in select.options:
                    val = opt.get_attribute("value")
                    txt = opt.text or ""
                    if val and (state.lower() in txt.lower() or state.lower() in val.lower()):
                        select.select_by_value(val)
                        matched = True
                        break
                if not matched and len(select.options) > 1:
                    select.select_by_index(1)

    def billing_same_as_shipping(self, same: bool = True) -> None:
        log_step(f"set billing-same-as-shipping = {same}")
        cb = self.find(*self.BILLING_SAME_CHECKBOX)
        if cb.is_selected() != same:
            self.click(cb)

    # ------------------------------------------------------------------
    # Billing address (only when not same as shipping)
    # ------------------------------------------------------------------
    def fill_billing_address(self, *, first_name: str, last_name: str,
                             country: str, state: str, city: str,
                             postal_code: str, address_line1: str) -> None:
        log_step(f"fill billing address for {first_name} {last_name}")
        self.find(*self.BILLING_FORM)
        values = {
            self.BILLING_FIRST_NAME: first_name,
            self.BILLING_LAST_NAME: last_name,
            self.BILLING_ADDRESS1: address_line1,
            self.BILLING_CITY: city,
            self.BILLING_POSTAL: postal_code,
        }
        for locator, value in values.items():
            el = self.find(*locator)
            el.clear()
            el.send_keys(value)
        from selenium.webdriver.support.ui import Select

        Select(self.find(*self.BILLING_STATE)).select_by_value(state)

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------
    def select_shipping_method(self, method_id: str) -> None:
        log_step(f"select shipping method {method_id}")
        for radio in self.find_many(*self.SHIPPING_METHOD_RADIOS):
            if radio.get_attribute("value") == method_id:
                self.click(radio)
                return
        raise AssertionError(f"shipping method {method_id!r} not present")

    def available_shipping_method_ids(self) -> list[str]:
        radios = self.driver.find_elements(*self.SHIPPING_METHOD_RADIOS)
        return [r.get_attribute("value") for r in radios]

    def select_payment_method(self, provider_id: str) -> None:
        log_step(f"select payment method {provider_id}")
        for radio in self.find_many(*self.PAYMENT_RADIOS):
            if radio.get_attribute("value") == provider_id:
                self.click(radio)
                return
        raise AssertionError(f"payment method {provider_id!r} not present")

    def available_payment_method_ids(self) -> list[str]:
        from utils.selenium_helpers import wait_until

        def _has_payments(_: WebDriver):
            radios = self.driver.find_elements(*self.PAYMENT_RADIOS)
            return radios if radios else None

        radios = wait_until(self.driver, _has_payments, timeout=10, message="payment methods loading")
        return [r.get_attribute("value") for r in radios]

    # ------------------------------------------------------------------
    # Place order
    # ------------------------------------------------------------------
    def place_order(self) -> None:
        log_step("click Place Order")
        btn = self.find(*self.PAY_BTN)
        self.click(btn)

    def field_error_texts(self) -> list[str]:
        return [el.text for el in self.find_many(*self.FIELD_ERRORS) if el.text]
