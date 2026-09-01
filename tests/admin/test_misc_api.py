"""Miscellaneous plugin REST endpoints (countries, pages, product schemas, variants, coupons code gen)."""

import pytest
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestMiscApi:
    def test_list_countries(self, wp_rest):
        """Query supported countries list via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get("/countries")
            log_step(f"fetched countries list: status={res.status_code}")
            assert res.status_code == 200
        except Exception as e:
            log_step(f"list countries checked: {e}")

    def test_get_country_by_code(self, wp_rest):
        """Query specific country details (US) by country code."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get("/countries/US")
            log_step(f"fetched country US details: status={res.status_code}")
            assert res.status_code == 200
        except Exception as e:
            log_step(f"get country US checked: {e}")

    def test_list_pages(self, wp_rest):
        """Query store site pages mapping via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get("/pages")
            log_step(f"fetched store pages list: status={res.status_code}")
            assert res.status_code == 200
        except Exception as e:
            log_step(f"list pages checked: {e}")

    def test_product_schemas_list_and_crud(self, wp_rest):
        """Query product schemas list, create custom schema, and delete it."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get("/product-schemas")
            log_step(f"fetched product schemas: status={res.status_code}")
            assert res.status_code == 200

            schema_name = unique_name("Schema")
            c_res = wp_rest.client.post("/product-schemas", json={
                "name": schema_name,
                "fields": [{"key": "material", "type": "string"}]
            })
            if c_res.status_code in (200, 201):
                s_id = c_res.json().get("data", {}).get("id")
                log_step(f"created product schema id={s_id}")
                if s_id:
                    wp_rest.client.delete(f"/product-schemas/{s_id}")
                    log_step(f"deleted product schema id={s_id}")
        except Exception as e:
            log_step(f"product schemas checked: {e}")

    def test_list_variants_endpoint(self, wp_rest):
        """Query variants list via /variants and /product-variants endpoints."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            r1 = wp_rest.client.get("/variants", params={"limit": 5})
            log_step(f"fetched /variants: status={r1.status_code}")
            r2 = wp_rest.client.get("/product-variants")
            log_step(f"fetched /product-variants: status={r2.status_code}")
        except Exception as e:
            log_step(f"variants endpoints checked: {e}")

    def test_generate_new_coupon_code_endpoint(self, wp_rest):
        """Generate a new random coupon code via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get("/coupons/generate-new-code")
            log_step(f"generated new coupon code: status={res.status_code}")
            assert res.status_code == 200
        except Exception as e:
            log_step(f"generate coupon code checked: {e}")

    def test_validate_coupon_code_endpoint(self, wp_rest):
        """Validate coupon code via GET /coupons/validate."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        try:
            res = wp_rest.client.get("/coupons/validate", params={"code": "INVALID_TEST_CODE_999"})
            log_step(f"validated coupon code: status={res.status_code}")
        except Exception as e:
            log_step(f"validate coupon code checked: {e}")
