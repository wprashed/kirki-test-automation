"""REST API client for the Kirki eCommerce plugin.

Two auth modes (matching how the plugin actually authenticates, verified in
libraries/framework/Middlewares/AuthMiddleware.php):

- ``admin_session``: WP cookie login + ``X-WP-Nonce: wp_rest`` header.
  The admin React SPA authenticates exactly this way.
- ``guest_cart``: no login; guest cart operations use the ``kecom-cart-token``
  header (App\\Constants\\Cart::HEADER_TOKEN).

``WpRestClient`` wraps ``requests.Session`` and keeps cookies + nonce.
"""

from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urljoin

import requests
from requests import Response

from utils.config import settings
from utils.logging_setup import log_debug

_WP_LOGIN_NONCE_RE = re.compile(r'name="_wpnonce"\s+value="([^"]+)"')
_REST_NONCE_RE = re.compile(r'"rest_nonce"\s*:\s*"([^"]+)"')


class RestApiError(RuntimeError):
    def __init__(self, message: str, response: "Optional[Response]" = None):
        super().__init__(message)
        self.response = response
        self.status_code = response.status_code if response is not None else None
        self.body = response.text if response is not None else None


class WpRestClient:
    """A requests session pre-authenticated for the plugin REST API."""

    def __init__(self, session: "Optional[requests.Session]" = None):
        self.session = session or requests.Session()
        self.base_url = settings.rest_url
        self._rest_nonce: str = ""

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------
    def login_as(self, username: str, password: str) -> None:
        """Log in via wp-login.php and capture the wp_rest nonce.

        Modern WP (>= 6.x) no longer renders a `_wpnonce` on wp-login.php,
        so we POST directly with the standard field names. The test cookie
        must be present before the POST (WP bounces otherwise).
        """
        login_url = settings.wp_login_url
        # Ensure a fresh, logged-out session.
        self.session.get(login_url, timeout=30)
        self.session.get(
            f"{settings.wp_base_url.rstrip('/')}/wp-login.php",
            params={"action": "logout"},
            timeout=30,
        )
        self.session.get(login_url, timeout=30)
        # WP requires the test cookie to be set before the POST.
        self.session.cookies.set("wordpress_test_cookie", "WP Cookie check")
        data = {
            "log": username,
            "pwd": password,
            "wp-submit": "Log In",
            "redirect_to": settings.admin_url,
            "testcookie": "1",
        }
        login_resp = self.session.post(
            login_url, data=data, timeout=30, allow_redirects=False
        )
        login_resp.raise_for_status()
        # Success responds with a 302 to the admin (possibly on a custom port
        # set by the local server, e.g. tutorlms.local:10003). Fall back to
        # the request URL when no Location header is present.
        location = login_resp.headers.get("Location") or login_resp.url
        if "wp-admin" not in location:
            raise RestApiError(
                f"login failed for {username!r}: redirected to {location}",
                login_resp,
            )
        # Refresh the session cookies (WP may set the logged-in cookie under
        # multiple paths) and capture the wp_rest nonce.
        self._ensure_logged_in()
        self._rest_nonce = self._fetch_rest_nonce()

    def _ensure_logged_in(self) -> None:
        """Force the session cookie state to match the login we performed.

        WordPress sets the logged-in cookie under multiple paths in one
        response; requests' cookie jar sometimes keeps only the first. A
        follow-up GET to wp-admin refreshes the session cookies.
        """
        self.session.get(f"{settings.wp_base_url.rstrip('/')}/wp-admin/", timeout=30)

    def _fetch_rest_nonce(self) -> str:
        """Scrape the wp_rest nonce from any admin page that localizes it."""
        for url in (
            f"{settings.admin_url}/admin.php?page=kirki-ecommerce",
            f"{settings.admin_url}/",
        ):
            try:
                resp = self.session.get(url, timeout=30)
                if resp.status_code == 200:
                    match = _REST_NONCE_RE.search(resp.text)
                    if match:
                        return match.group(1)
            except requests.RequestException:
                continue
        # Fallback: hit the REST index which echoes a nonce for cookie auth.
        try:
            resp = self.session.get(
                f"{settings.wp_base_url.rstrip('/')}/{settings.wp_rest_prefix}/",
                timeout=30,
            )
            body = resp.text
            match = re.search(r'"nonce"\s*:\s*"([^"]+)"', body)
            if match:
                return match.group(1)
        except requests.RequestException:
            pass
        raise RestApiError("could not obtain a wp_rest nonce for the admin session")

    @property
    def is_authenticated(self) -> bool:
        return any(
            name.startswith("wordpress_logged_in_")
            for name in self.session.cookies.keys()
        )

    # ------------------------------------------------------------------
    # Requests
    # ------------------------------------------------------------------
    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json: dict | None = None,
        headers: dict | None = None,
        auth: bool = True,
        expected: int | None = None,
        allow_redirects: bool = True,
    ) -> Response:
        """Perform a REST request against the plugin namespace.

        ``auth=True`` adds the X-WP-Nonce header (required for cookie auth).
        Pass ``expected`` to assert a status code (raises RestApiError).
        """
        url = urljoin(self.base_url.rstrip("/") + "/", path.lstrip("/"))
        hdrs = {"Accept": "application/json"}
        if auth and self._rest_nonce:
            hdrs["X-WP-Nonce"] = self._rest_nonce
        hdrs.update(headers or {})
        resp = self.session.request(
            method,
            url,
            params=params,
            json=json,
            headers=hdrs,
            timeout=30,
            allow_redirects=allow_redirects,
        )
        if expected is not None:
            expected_codes = (expected,) if isinstance(expected, int) else tuple(expected)
            if resp.status_code not in expected_codes:
                raise RestApiError(
                    f"{method} {path} -> {resp.status_code} (expected {expected}): "
                    f"{resp.text[:500]}",
                    resp,
                )
        return resp

    def get(self, path: str, **kwargs) -> Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, json: dict | None = None, **kwargs) -> Response:
        return self.request("POST", path, json=json, **kwargs)

    def put(self, path: str, json: dict | None = None, **kwargs) -> Response:
        return self.request("PUT", path, json=json, **kwargs)

    def patch(self, path: str, json: dict | None = None, **kwargs) -> Response:
        return self.request("PATCH", path, json=json, **kwargs)

    def delete(self, path: str, **kwargs) -> Response:
        return self.request("DELETE", path, **kwargs)

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------
    def data(self, method: str, path: str, **kwargs):
        resp = self.request(method, path, **kwargs)
        try:
            return resp.json()
        except ValueError as exc:
            raise RestApiError(f"non-JSON response from {path}", resp) from exc

    def log_out(self) -> None:
        self.session.get(
            f"{settings.wp_base_url.rstrip('/')}/wp-login.php",
            params={"action": "logout", "redirect_to": settings.wp_base_url},
            timeout=30,
        )
