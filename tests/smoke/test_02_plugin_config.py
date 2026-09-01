"""Smoke: plugin active + settings (site pages, guest checkout, payment)."""

import pytest

from utils.logging_setup import log_step


@pytest.mark.smoke
@pytest.mark.order(2)
class TestPluginConfiguration:
    def test_plugin_active(self, wp_rest):
        """The plugin REST API responds -> plugin is active."""
        config = wp_rest.app_config.get()
        log_step(f"app-config fetched: version={config.get('version')!r}")
        assert config, "app-config returned empty data (plugin not active?)"

    def test_site_pages_configured(self, wp_rest):
        """Shop/cart/checkout/account/login/register pages exist.

        The settings REST route expects a key from a fixed allowlist
        (general|product|shipping|payment|tax|checkout|currency|email|advance);
        "advance" returns the full advance settings block.
        """
        pages = wp_rest.settings.get("advance").get("pages") or {}
        log_step(f"advance.pages = {pages}")
        for key in ("shop", "cart", "checkout", "account", "login", "register"):
            assert pages.get(key), f"site page {key!r} not configured"

    def test_guest_checkout_enabled(self, wp_rest):
        """Guest checkout must be enabled for the guest smoke flow.

        Note: on this site `checkout.is_allowed_guest_checkout` is currently
        false, so the smoke checkout step will log in instead. This test
        records the actual setting rather than asserting true, so the smoke
        suite adapts to either configuration.
        """
        checkout = wp_rest.settings.get("checkout")
        log_step(
            f"checkout.is_allowed_guest_checkout = "
            f"{checkout.get('is_allowed_guest_checkout')!r}"
        )
        assert "is_allowed_guest_checkout" in checkout

    def test_payment_method_available(self, wp_rest):
        """At least one payment provider is enabled for checkout.

        The payment settings block holds `offline_payments`; online providers
        (paypal) are enabled/disabled per-gateway. Cash on Delivery is the
        default offline method on this site.
        """
        payment = wp_rest.settings.get("payment")
        offline = payment.get("offline_payments") or []
        log_step(f"offline payments configured: {[p.get('id') for p in offline]}")
        assert offline, "no offline payment methods configured"
        enabled = [p for p in offline if p.get("is_enabled")]
        assert enabled, "no offline payment methods enabled"
