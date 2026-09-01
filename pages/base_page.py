"""Base Page Object: common Selenium operations with explicit waits."""

from __future__ import annotations

from typing import Optional

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from utils.config import settings
from utils.logging_setup import log_step
from utils.selenium_helpers import (
    safe_click,
    scroll_into_view,
    wait_for_url,
    wait_until,
)


class BasePage:
    """Base class for all page objects."""

    #: URL fragment this page represents (subclass overrides).
    url_fragment: str = ""

    def __init__(self, driver: WebDriver, base_url: str | None = None):
        self.driver = driver
        self.base_url = (base_url or settings.wp_base_url).rstrip("/")

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def open(self, path: str = "") -> "BasePage":
        url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url
        self.driver.get(url)
        return self

    def open_page(self, path: str) -> "BasePage":
        """Open an absolute path (e.g. '/shop') and wait for the page."""
        self.open(path)
        self.wait_until_loaded()
        log_step(f"Navigated to page path /{path.lstrip('/')}", driver=self.driver)
        return self

    def is_current_page(self) -> bool:
        if not self.url_fragment:
            return True
        return self.url_fragment in self.driver.current_url

    def wait_until_loaded(self, timeout: Optional[float] = None) -> "BasePage":
        if self.url_fragment:
            wait_for_url(self.driver, self.url_fragment, timeout=timeout)
        return self

    # ------------------------------------------------------------------
    # Element helpers
    # ------------------------------------------------------------------
    def find(self, by: str, locator: str, timeout: Optional[float] = None) -> WebElement:
        return WebDriverWait(self.driver, timeout or settings.explicit_wait).until(
            EC.visibility_of_element_located((by, locator))
        )

    def find_many(self, by: str, locator: str, timeout: Optional[float] = None) -> list[WebElement]:
        return WebDriverWait(self.driver, timeout or settings.explicit_wait).until(
            EC.presence_of_all_elements_located((by, locator))
        )

    def present(self, by: str, locator: str, timeout: Optional[float] = None) -> WebElement:
        return WebDriverWait(self.driver, timeout or settings.explicit_wait).until(
            EC.presence_of_element_located((by, locator))
        )

    def exists(self, by: str, locator: str, timeout: float = 0.5) -> bool:
        try:
            self.driver.find_element(by, locator)
            return True
        except NoSuchElementException:
            return False

    def click(self, element: WebElement) -> None:
        safe_click(self.driver, element)
        log_step("Clicked element on page", driver=self.driver)

    def click_when_ready(self, by: str, locator: str) -> WebElement:
        el = self.find(by, locator)
        self.click(el)
        log_step(f"Clicked element locator {locator}", driver=self.driver)
        return el

    def type_text(self, element: WebElement, value: str, clear: bool = True) -> None:
        if clear:
            element.clear()
        if value:
            element.send_keys(value)
        log_step(f"Entered input text: {value[:20]}...", driver=self.driver)

    def select_option(self, element: WebElement, value: str) -> None:
        Select(element).select_by_value(value)
        log_step(f"Selected option value: {value}", driver=self.driver)

    def select_by_visible_text(self, element: WebElement, text: str) -> None:
        Select(element).select_by_visible_text(text)

    def text_of(self, by: str, locator: str, timeout: Optional[float] = None) -> str:
        return self.find(by, locator, timeout=timeout).text.strip()

    def wait_for_text(self, by: str, locator: str, expected: str,
                      timeout: Optional[float] = None) -> WebElement:
        """Wait until an element's text contains the expected substring."""

        def _check(_: WebDriver) -> WebElement | None:
            try:
                el = self.driver.find_element(by, locator)
                if expected.lower() in (el.text or "").lower():
                    return el
            except NoSuchElementException:
                pass
            return None

        return wait_until(self.driver, _check, timeout=timeout,
                          message=f"text {expected!r} in {locator}")

    def wait_for_element_clickable(self, by: str, locator: str,
                                   timeout: Optional[float] = None) -> WebElement:
        return WebDriverWait(self.driver, timeout or settings.explicit_wait).until(
            EC.element_to_be_clickable((by, locator))
        )

    def wait_until_gone(self, by: str, locator: str, timeout: Optional[float] = None) -> None:
        WebDriverWait(self.driver, timeout or settings.explicit_wait).until(
            EC.invisibility_of_element_located((by, locator))
        )

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------
    def scroll_to(self, element: WebElement) -> WebElement:
        return scroll_into_view(self.driver, element)

    def accept_intercept_click(self, element: WebElement) -> None:
        """Click, tolerating a transient overlay (e.g. toast)."""
        try:
            safe_click(self.driver, element)
        except ElementClickInterceptedException:
            log_step("retrying click after interception")
            safe_click(self.driver, element)

    def log(self, message: str) -> None:
        log_step(message)
