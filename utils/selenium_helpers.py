"""Selenium helpers: explicit waits, AJAX/SPA waits, console capture.

The framework never uses blind ``time.sleep()``. All waiting is explicit:
- ``wait_until`` polls a predicate at a short interval,
- ``wait_for_url`` waits for a URL (prefix or exact),
- ``wait_for_ajax`` / ``wait_for_spa_root`` handle dynamic content,
- ``capture_console_errors`` collects browser console errors for reports.
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from typing import Any, Callable, Optional

from selenium.common.exceptions import (
    JavascriptException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from utils.config import settings
from utils.logging_setup import log_debug, log_warning


class WaitTimeoutError(TimeoutException):
    """Raised when a polling condition never becomes true."""


def wait_until(
    driver: WebDriver,
    predicate: Callable[[WebDriver], Any],
    timeout: Optional[float] = None,
    message: str = "condition",
    interval: Optional[float] = None,
) -> Any:
    """Poll ``predicate`` until it returns a truthy value or timeout."""
    timeout = settings.explicit_wait if timeout is None else timeout
    interval = settings.poll_interval if interval is None else interval
    deadline = time.monotonic() + timeout
    last_exc: Optional[Exception] = None
    while True:
        try:
            result = predicate(driver)
            if result:
                return result
        except StaleElementReferenceException as exc:  # pragma: no cover
            last_exc = exc
        except WebDriverException as exc:  # pragma: no cover
            last_exc = exc
        if time.monotonic() >= deadline:
            break
        time.sleep(interval)
    raise WaitTimeoutError(
        f"Timed out after {timeout}s waiting for {message}"
        + (f" (last error: {last_exc})" if last_exc else "")
    )


def wait_for_url(
    driver: WebDriver,
    url_fragment: str,
    timeout: Optional[float] = None,
    exact: bool = False,
) -> str:
    """Wait until the current URL contains (or equals) ``url_fragment``."""

    def _check(d: WebDriver) -> str:
        current = d.current_url
        if exact:
            return current if current.rstrip("/") == url_fragment.rstrip("/") else ""
        return current if url_fragment in current else ""

    return wait_until(driver, _check, timeout=timeout, message=f"URL {url_fragment!r}")


def wait_for_element(
    driver: WebDriver,
    by: str,
    locator: str,
    timeout: Optional[float] = None,
) -> WebElement:
    """Wait until an element is present and visible; return it."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    return WebDriverWait(driver, timeout or settings.explicit_wait).until(
        EC.visibility_of_element_located((by, locator))
    )


def wait_for_ajax(driver: WebDriver, timeout: Optional[float] = None) -> None:
    """Wait for jQuery/Ajax activity to settle (best-effort)."""
    timeout = settings.explicit_wait if timeout is None else timeout

    def _settled(d: WebDriver) -> bool:
        try:
            return bool(
                d.execute_script(
                    "return (typeof jQuery === 'undefined' || jQuery.active === 0) "
                    "&& document.readyState === 'complete'"
                )
            )
        except JavascriptException:
            return True

    wait_until(driver, _settled, timeout=timeout, message="AJAX to settle")


def wait_for_spa_root(driver: WebDriver, timeout: Optional[float] = None) -> WebElement:
    """Wait for the Kirki admin SPA shell to be ready.

    The plugin hides the root until it has the ``--ready`` class
    (see app/Menu/Root.php inline styles).
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    root = WebDriverWait(driver, timeout or settings.explicit_wait).until(
        EC.presence_of_element_located((By.ID, "kirki-ecommerce-root"))
    )
    wait_until(
        driver,
        lambda d: "kirki-ecommerce-root--ready"
        in (d.find_element(By.ID, "kirki-ecommerce-root").get_attribute("class") or ""),
        timeout=timeout,
        message="admin SPA root to become ready",
    )
    return root


def scroll_into_view(driver: WebDriver, element: WebElement) -> WebElement:
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    return element


def safe_click(driver: WebDriver, element: WebElement) -> None:
    """Click, scrolling into view first and retrying once on staleness."""
    for _ in range(2):
        try:
            scroll_into_view(driver, element)
            element.click()
            return
        except StaleElementReferenceException:
            continue
    raise StaleElementReferenceException("element went stale while clicking")


def capture_console_errors(driver: WebDriver) -> list[str]:
    """Collect browser console errors. Best-effort per browser."""
    errors: list[str] = []
    if not settings.capture_console:
        return errors
    try:
        logs = driver.get_log("browser")
        errors = [
            f"[{entry.get('level')}] {entry.get('message')}"
            for entry in logs
            if entry.get("level") in ("SEVERE", "ERROR")
        ]
    except (WebDriverException, ValueError):
        # Firefox via geckodriver does not support get_log('browser').
        try:
            js_errors = driver.execute_script(
                "return window.__kecomTestErrors || [];"
            )
            if js_errors:
                errors = list(js_errors)
        except JavascriptException:
            pass
    return errors


def attach_console_listener(driver: WebDriver) -> None:
    """Inject a listener collecting window.onerror + unhandled rejections."""
    script = """
    window.__kecomTestErrors = window.__kecomTestErrors || [];
    window.addEventListener('error', function (e) {
      window.__kecomTestErrors.push('error: ' + (e.message || 'unknown'));
    });
    window.addEventListener('unhandledrejection', function (e) {
      window.__kecomTestErrors.push('unhandledrejection: ' + (e.reason || 'unknown'));
    });
    """
    try:
        driver.execute_script(script)
    except JavascriptException:  # pragma: no cover
        pass


def save_screenshot(driver: WebDriver, name: str) -> str | None:
    """Save a screenshot into the configured directory; return its path."""
    try:
        path = settings.screenshot_path / f"{name}-{datetime.now():%Y%m%d-%H%M%S}.png"
        driver.save_screenshot(str(path))
        return str(path)
    except WebDriverException as exc:  # pragma: no cover
        log_warning(f"screenshot failed: {exc}")
        return None


def save_page_source(driver: WebDriver, name: str) -> str | None:
    """Save page HTML for failure diagnosis; return its path."""
    try:
        html_dir = settings.report_path / "html"
        html_dir.mkdir(parents=True, exist_ok=True)
        path = html_dir / f"{name}-{datetime.now():%Y%m%d-%H%M%S}.html"
        path.write_text(driver.page_source or "", encoding="utf-8")
        return str(path)
    except WebDriverException as exc:  # pragma: no cover
        log_warning(f"page source capture failed: {exc}")
        return None
