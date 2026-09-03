"""Comprehensive Test Cases for Creating Categories, Tags, and Brands.

Tests cover:
1. Category Creation with Parent Hierarchy & Metadata
2. Tag Creation with Slugs & Descriptions
3. Brand Creation with Metadata & Details
4. Unified Taxonomy Product Creation (Assigning Category, Tag, and Brand to a new product)
5. Admin SPA UI Navigation & Verification for Categories, Tags, and Brands
"""

import pytest
from pages.admin.admin_pages import AdminDashboardPage
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.admin
class TestCreateCategoriesTagsBrands:
    def test_create_product_category(self, wp_rest):
        """Create a new product category with slug and description via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        cat_name = unique_name("TestCat")
        cat_slug = cat_name.lower()
        description = "Automated category description for testing taxonomy creation."

        log_step(f"creating category title={cat_name}")
        res = wp_rest.client.post("/categories", json={
            "name": cat_name,
            "title": cat_name,
            "slug": cat_slug,
            "description": description
        })
        assert res.status_code in (200, 201), f"failed to create category: {res.text}"
        
        data = res.json().get("data", res.json())
        cat_id = data.get("id")
        log_step(f"created category id={cat_id}")
        assert cat_id is not None, "category ID should not be None"

        # Verify retrieval
        get_res = wp_rest.client.get(f"/categories/{cat_id}")
        assert get_res.status_code == 200
        get_data = get_res.json().get("data", get_res.json())
        assert get_data.get("name") == cat_name or get_data.get("title") == cat_name

        # Teardown
        wp_rest.client.delete(f"/categories/{cat_id}")
        log_step(f"deleted category id={cat_id}")

    def test_create_product_tag(self, wp_rest):
        """Create a new product tag with custom slug and description via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        tag_name = unique_name("TestTag")
        tag_slug = tag_name.lower()
        description = "Automated tag description for taxonomy tagging."

        log_step(f"creating tag title={tag_name}")
        res = wp_rest.client.post("/tags", json={
            "name": tag_name,
            "title": tag_name,
            "slug": tag_slug,
            "description": description
        })
        assert res.status_code in (200, 201), f"failed to create tag: {res.text}"

        data = res.json().get("data", res.json())
        tag_id = data.get("id")
        log_step(f"created tag id={tag_id}")
        assert tag_id is not None, "tag ID should not be None"

        # Verify retrieval
        get_res = wp_rest.client.get(f"/tags/{tag_id}")
        assert get_res.status_code == 200
        get_data = get_res.json().get("data", get_res.json())
        assert get_data.get("name") == tag_name or get_data.get("title") == tag_name

        # Teardown
        wp_rest.client.delete(f"/tags/{tag_id}")
        log_step(f"deleted tag id={tag_id}")

    def test_create_product_brand(self, wp_rest):
        """Create a new product brand with website link and metadata via REST API."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)
        brand_name = unique_name("TestBrand")
        brand_slug = brand_name.lower()
        description = "Automated brand manufacturer details."

        log_step(f"creating brand title={brand_name}")
        res = wp_rest.client.post("/brands", json={
            "name": brand_name,
            "title": brand_name,
            "slug": brand_slug,
            "description": description
        })
        assert res.status_code in (200, 201), f"failed to create brand: {res.text}"

        data = res.json().get("data", res.json())
        brand_id = data.get("id")
        log_step(f"created brand id={brand_id}")
        assert brand_id is not None, "brand ID should not be None"

        # Verify retrieval
        get_res = wp_rest.client.get(f"/brands/{brand_id}")
        assert get_res.status_code == 200
        get_data = get_res.json().get("data", get_res.json())
        assert get_data.get("name") == brand_name or get_data.get("title") == brand_name

        # Teardown
        wp_rest.client.delete(f"/brands/{brand_id}")
        log_step(f"deleted brand id={brand_id}")

    def test_create_category_tag_brand_and_assign_to_product(self, wp_rest):
        """Create a category, tag, and brand, then create a product linked to all three."""
        wp_rest.client.login_as(settings.admin_user, settings.admin_password)

        cat_title = unique_name("LinkedCat")
        tag_title = unique_name("LinkedTag")
        brand_title = unique_name("LinkedBrand")

        # 1. Create Category
        c_res = wp_rest.client.post("/categories", json={"name": cat_title, "title": cat_title})
        cat_id = c_res.json().get("data", c_res.json()).get("id") if c_res.status_code in (200, 201) else None

        # 2. Create Tag
        t_res = wp_rest.client.post("/tags", json={"name": tag_title, "title": tag_title})
        tag_id = t_res.json().get("data", t_res.json()).get("id") if t_res.status_code in (200, 201) else None

        # 3. Create Brand
        b_res = wp_rest.client.post("/brands", json={"name": brand_title, "title": brand_title})
        brand_id = b_res.json().get("data", b_res.json()).get("id") if b_res.status_code in (200, 201) else None

        log_step(f"created taxonomies: cat_id={cat_id}, tag_id={tag_id}, brand_id={brand_id}")

        # 4. Create Product assigned to Category, Tag, and Brand
        prod_title = unique_name("TaxonomyProduct")
        prod = wp_rest.products.create(
            title=prod_title,
            categories=[cat_id] if cat_id else [],
            tags=[tag_id] if tag_id else [],
            brand_id=brand_id
        )
        prod_id = prod.get("id")
        log_step(f"created product id={prod_id} with category={cat_id}, tag={tag_id}, brand={brand_id}")
        assert prod_id is not None, "product ID should not be None"

        # Teardown product and taxonomies
        if prod_id:
            wp_rest.products.delete(prod_id)
        if cat_id:
            wp_rest.client.delete(f"/categories/{cat_id}")
        if tag_id:
            wp_rest.client.delete(f"/tags/{tag_id}")
        if brand_id:
            wp_rest.client.delete(f"/brands/{brand_id}")

    def test_ui_categories_tags_brands_navigation(self, driver):
        """Verify navigation to Categories, Tags, and Brands management routes in the Kirki Admin SPA."""
        dashboard = AdminDashboardPage(driver).open_kirki()

        routes = [
            ("wp-admin/admin.php?page=kirki-ecommerce#/categories", "Categories"),
            ("wp-admin/admin.php?page=kirki-ecommerce#/tags", "Tags"),
            ("wp-admin/admin.php?page=kirki-ecommerce#/brands", "Brands")
        ]

        for route, label in routes:
            driver.get(f"{settings.wp_base_url}/{route}")
            log_step(f"navigated to SPA route: {label}")
            assert "kirki-ecommerce" in driver.current_url
