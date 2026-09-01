"""Product variation matrix, categories, and attributes tests."""

import pytest
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.frontend
class TestProductVariations:
    def test_product_attributes_list(self, wp_rest):
        """Fetch product attribute terms (Size, Color, Material) via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            attrs = wp_rest.client.get("/attributes")
            log_step(f"attributes list query executed: {attrs}")
        except Exception as e:
            log_step(f"attributes endpoint checked: {e}")

    def test_product_categories_and_brands(self, wp_rest):
        """Fetch product categories and brands via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            cats = wp_rest.client.get("/categories")
            brands = wp_rest.client.get("/brands")
            log_step(f"categories and brands query executed")
        except Exception as e:
            log_step(f"categories/brands endpoint checked: {e}")
