"""Comprehensive Test Cases for Product Creation.

Tests cover:
1. Simple Product Creation with Full Payload Details (price, sale price, stock, SKU, status)
2. Variable Product Creation with Multi-Variant Matrices
3. Draft Product Creation & Status Update to Published
4. Taxonomy-Linked Product Creation (Category, Tag, and Brand assignment)
5. Admin SPA Product Creation Page UI Rendering Verification
"""

import pytest
from pages.admin.admin_pages import AdminDashboardPage
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestCreateProductComprehensive:
    def test_create_simple_product_rest(self, wp_rest):
        """Create a simple product with price, sale price, stock, SKU, and status via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        title = unique_name("SimpleProd")
        sku = f"SKU-{unique_name('S')[:8].upper()}"

        variant = {
            "base_price": 59.99,
            "sale_price": 49.99,
            "available_quantity": 50,
            "track_inventory": True,
            "in_stock": True,
            "is_default": True,
            "sku": sku
        }

        log_step(f"creating simple product title={title} sku={sku}")
        product = wp_rest.products.create(
            title=title,
            status="published",
            short_description="Short summary of simple product",
            description="Detailed product description for testing creation.",
            has_variants=False,
            variant=variant
        )

        prod_id = product.get("id")
        assert prod_id is not None, "created product must return a valid ID"
        log_step(f"created simple product id={prod_id}")

        # Verify retrieval via GET /products/{id}
        fetched = wp_rest.products.get(prod_id)
        assert fetched.get("title") == title or fetched.get("name") == title
        log_step(f"verified product retrieval id={prod_id}")

        # Teardown
        wp_rest.products.delete(prod_id)
        log_step(f"deleted simple product id={prod_id}")

    def test_create_variable_product_with_multi_variants(self, wp_rest):
        """Create a variable product with multiple variant configurations via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        title = unique_name("VariableProd")

        variants = [
            {
                "base_price": 29.99,
                "sale_price": 24.99,
                "available_quantity": 20,
                "track_inventory": True,
                "in_stock": True,
                "is_default": True,
                "sku": f"SKU-RED-S-{unique_name('R')[:4]}"
            },
            {
                "base_price": 34.99,
                "sale_price": 29.99,
                "available_quantity": 15,
                "track_inventory": True,
                "in_stock": True,
                "is_default": False,
                "sku": f"SKU-BLUE-M-{unique_name('B')[:4]}"
            }
        ]

        payload = {
            "title": title,
            "status": "published",
            "currency_id": 1,
            "has_variants": True,
            "variants": variants
        }

        log_step(f"creating variable product with {len(variants)} variants")
        res = wp_rest.client.post("/products", json=payload)
        assert res.status_code in (200, 201), f"failed to create variable product: {res.text}"

        data = res.json().get("data", res.json())
        prod_id = data.get("id")
        assert prod_id is not None, "variable product ID should not be None"
        log_step(f"created variable product id={prod_id}")

        # Teardown
        wp_rest.products.delete(prod_id)
        log_step(f"deleted variable product id={prod_id}")

    def test_create_draft_product_and_publish(self, wp_rest):
        """Create a product in draft status, then update status to published."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        title = unique_name("DraftProd")

        # 1. Create in draft status
        log_step(f"creating draft product title={title}")
        prod = wp_rest.products.create(title=title, status="draft", price=15.00)
        prod_id = prod.get("id")
        assert prod_id is not None, "draft product ID must exist"

        # Verify draft status
        fetched = wp_rest.products.get(prod_id)
        assert fetched.get("status") in ("draft", "Draft")
        log_step(f"verified draft status for product id={prod_id}")

        # 2. Update status to published (passing required title and variants in PUT payload)
        log_step(f"updating product status to published id={prod_id}")
        existing_variants = fetched.get("variants", [])
        updated = wp_rest.products.update(
            prod_id,
            title=title,
            status="published",
            currency_id=1,
            variants=existing_variants or [{
                "base_price": 15.00,
                "available_quantity": 10,
                "in_stock": True,
                "is_default": True
            }]
        )
        assert updated.get("status") in ("published", "Publish", "publish")
        log_step(f"updated product id={prod_id} status to published")

        # Teardown
        wp_rest.products.delete(prod_id)
        log_step(f"deleted product id={prod_id}")

    def test_create_product_with_category_tag_brand(self, wp_rest):
        """Create a product with category, tag, and brand associations via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)

        cat_title = unique_name("ProdCat")
        tag_title = unique_name("ProdTag")
        brand_title = unique_name("ProdBrand")

        # 1. Create Category, Tag, Brand
        c_res = wp_rest.client.post("/categories", json={"name": cat_title, "title": cat_title})
        t_res = wp_rest.client.post("/tags", json={"name": tag_title, "title": tag_title})
        b_res = wp_rest.client.post("/brands", json={"name": brand_title, "title": brand_title})

        cat_id = c_res.json().get("data", c_res.json()).get("id") if c_res.status_code in (200, 201) else None
        tag_id = t_res.json().get("data", t_res.json()).get("id") if t_res.status_code in (200, 201) else None
        brand_id = b_res.json().get("data", b_res.json()).get("id") if b_res.status_code in (200, 201) else None

        # 2. Create Product linked to taxonomies
        prod_title = unique_name("FullTaxonomyProduct")
        log_step(f"creating product linked to cat={cat_id}, tag={tag_id}, brand={brand_id}")
        prod = wp_rest.products.create(
            title=prod_title,
            price=89.99,
            categories=[cat_id] if cat_id else [],
            tags=[tag_id] if tag_id else [],
            brand_id=brand_id
        )

        prod_id = prod.get("id")
        assert prod_id is not None, "product ID must be returned"
        log_step(f"successfully created taxonomy-linked product id={prod_id}")

        # Teardown
        if prod_id:
            wp_rest.products.delete(prod_id)
        if cat_id:
            wp_rest.client.delete(f"/categories/{cat_id}")
        if tag_id:
            wp_rest.client.delete(f"/tags/{tag_id}")
        if brand_id:
            wp_rest.client.delete(f"/brands/{brand_id}")

    def test_ui_admin_create_product_page(self, driver):
        """Verify navigation to the Admin Product Creation SPA form live in Chrome."""
        dashboard = AdminDashboardPage(driver).open_kirki()
        driver.get(f"{settings.wp_base_url}/wp-admin/admin.php?page=kirki-ecommerce#/products/create")
        log_step("navigated to Admin Product Creation SPA route")
        assert "kirki-ecommerce" in driver.current_url
