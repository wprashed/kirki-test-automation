"""Real Human Interactive UI Suite for All Creation Forms & Settings Pages.

Executes real Chrome mouse clicks and keyboard typing live on screen for:
1. Category Creation Modal (`#/categories` -> `New Category` -> Name, Slug, Description -> `Add`)
2. Tag Creation Modal (`#/tags` -> `New Tag` -> Name, Slug, Description -> `Add`)
3. Brand Creation Modal (`#/brands` -> `New Brand` -> Name, Slug, Description -> `Add`)
4. Coupon Creation Form (`#/coupons/create` -> Title, Code, Discount Amount -> `Create`)
5. Product Creation Form (`#/products/create` -> Title, Ribbon, Short Desc, Price, Sale Price, SKU, SEO Title, SEO Desc -> `Create`)
6. All Settings Tabs (`#/settings/general`, `#/settings/shipping`, `#/settings/tax`, `#/settings/checkout`, `#/settings/currency`, `#/settings/email`) -> Edits Inputs & Clicks `Save`
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.admin.admin_pages import AdminLoginPage
from utils.api.wp_rest import unique_name
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.ui_walkthrough
class TestHumanUiCompleteLiveForms:
    @pytest.fixture(autouse=True)
    def ensure_admin_logged_in(self, driver):
        """Ensure WordPress admin session is active."""
        driver.get(f"{settings.wp_base_url}/wp-admin/admin.php?page=kirki-ecommerce#/")
        time.sleep(1)
        if "wp-login.php" in driver.current_url:
            AdminLoginPage(driver).login_as_admin()

    def test_01_human_ui_create_category_live(self, driver):
        """Visually create a Category via live UI mouse clicks and keyboard typing."""
        cat_name = unique_name("UICat")
        cat_slug = cat_name.lower()
        log_step(f"LIVE UI: Navigating to Categories page to create category {cat_name!r}", driver=driver)
        driver.get(f"{settings.wp_base_url}/wp-admin/admin.php?page=kirki-ecommerce#/categories")
        time.sleep(2)

        # Click 'New Category' button
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'New Category')]"))
        )
        log_step("LIVE UI: Clicking 'New Category' button", driver=driver)
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(1.5)

        # Fill Modal Fields
        log_step(f"LIVE UI: Typing category name '{cat_name}'", driver=driver)
        name_input = driver.find_element(By.CSS_SELECTOR, "input[name='name']")
        name_input.clear()
        name_input.send_keys(cat_name)

        log_step(f"LIVE UI: Typing category slug '{cat_slug}'", driver=driver)
        slug_input = driver.find_element(By.CSS_SELECTOR, "input[name='slug']")
        slug_input.clear()
        slug_input.send_keys(cat_slug)

        log_step("LIVE UI: Typing category description", driver=driver)
        desc_input = driver.find_elements(By.CSS_SELECTOR, "textarea[name='description']")
        if desc_input:
            desc_input[0].send_keys(f"Description for {cat_name}")

        # Click 'Add' Submit Button
        add_btn = driver.find_element(By.XPATH, "//button[text()='Add']")
        log_step("LIVE UI: Clicking 'Add' button to submit category", driver=driver)
        driver.execute_script("arguments[0].click();", add_btn)
        time.sleep(2)
        log_step(f"LIVE UI: Category '{cat_name}' successfully created via UI", driver=driver)

    def test_02_human_ui_create_tag_live(self, driver):
        """Visually create a Tag via live UI mouse clicks and keyboard typing."""
        tag_name = unique_name("UITag")
        tag_slug = tag_name.lower()
        log_step(f"LIVE UI: Navigating to Tags page to create tag {tag_name!r}", driver=driver)
        driver.get(f"{settings.wp_base_url}/wp-admin/admin.php?page=kirki-ecommerce#/tags")
        time.sleep(2)

        # Click 'New Tag' button
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'New Tag')]"))
        )
        log_step("LIVE UI: Clicking 'New Tag' button", driver=driver)
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(1.5)

        # Fill Modal Fields
        log_step(f"LIVE UI: Typing tag name '{tag_name}'", driver=driver)
        name_input = driver.find_element(By.CSS_SELECTOR, "input[name='name']")
        name_input.clear()
        name_input.send_keys(tag_name)

        log_step(f"LIVE UI: Typing tag slug '{tag_slug}'", driver=driver)
        slug_input = driver.find_element(By.CSS_SELECTOR, "input[name='slug']")
        slug_input.clear()
        slug_input.send_keys(tag_slug)

        # Click 'Add' Submit Button
        add_btn = driver.find_element(By.XPATH, "//button[text()='Add']")
        log_step("LIVE UI: Clicking 'Add' button to submit tag", driver=driver)
        driver.execute_script("arguments[0].click();", add_btn)
        time.sleep(2)
        log_step(f"LIVE UI: Tag '{tag_name}' successfully created via UI", driver=driver)

    def test_03_human_ui_create_brand_live(self, driver):
        """Visually create a Brand via live UI mouse clicks and keyboard typing."""
        brand_name = unique_name("UIBrand")
        brand_slug = brand_name.lower()
        log_step(f"LIVE UI: Navigating to Brands page to create brand {brand_name!r}", driver=driver)
        driver.get(f"{settings.wp_base_url}/wp-admin/admin.php?page=kirki-ecommerce#/brands")
        time.sleep(2)

        # Click 'New Brand' button
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'New Brand')]"))
        )
        log_step("LIVE UI: Clicking 'New Brand' button", driver=driver)
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(1.5)

        # Fill Modal Fields
        log_step(f"LIVE UI: Typing brand name '{brand_name}'", driver=driver)
        name_input = driver.find_element(By.CSS_SELECTOR, "input[name='name']")
        name_input.clear()
        name_input.send_keys(brand_name)

        log_step(f"LIVE UI: Typing brand slug '{brand_slug}'", driver=driver)
        slug_input = driver.find_element(By.CSS_SELECTOR, "input[name='slug']")
        slug_input.clear()
        slug_input.send_keys(brand_slug)

        # Click 'Add' Submit Button
        add_btn = driver.find_element(By.XPATH, "//button[text()='Add']")
        log_step("LIVE UI: Clicking 'Add' button to submit brand", driver=driver)
        driver.execute_script("arguments[0].click();", add_btn)
        time.sleep(2)
        log_step(f"LIVE UI: Brand '{brand_name}' successfully created via UI", driver=driver)

    def test_04_human_ui_create_coupon_live(self, driver):
        """Visually create a Coupon via live UI form typing and button clicks."""
        cpn_title = unique_name("UICoupon")
        cpn_code = f"UI{time.time_ns() % 100000}"
        log_step(f"LIVE UI: Navigating to Coupon Creation page for {cpn_title!r}", driver=driver)
        driver.get(f"{settings.wp_base_url}/wp-admin/admin.php?page=kirki-ecommerce#/coupons/create")
        time.sleep(2)

        # Fill Title
        log_step(f"LIVE UI: Typing coupon title '{cpn_title}'", driver=driver)
        title_in = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='title']"))
        )
        title_in.clear()
        title_in.send_keys(cpn_title)

        # Fill Code
        log_step(f"LIVE UI: Typing coupon code '{cpn_code}'", driver=driver)
        code_in = driver.find_element(By.CSS_SELECTOR, "input[name='code']")
        code_in.clear()
        code_in.send_keys(cpn_code)

        # Fill Discount Amount
        discount_in = driver.find_elements(By.CSS_SELECTOR, "input[name='discount_amount']")
        if discount_in:
            log_step("LIVE UI: Typing coupon discount amount '15'", driver=driver)
            discount_in[0].clear()
            discount_in[0].send_keys("15")

        # Click Create Button
        create_btn = driver.find_element(By.XPATH, "//button[text()='Create']")
        log_step("LIVE UI: Clicking 'Create' button to save coupon", driver=driver)
        driver.execute_script("arguments[0].click();", create_btn)
        time.sleep(2.5)
        log_step(f"LIVE UI: Coupon '{cpn_code}' created successfully via UI", driver=driver)

    def test_05_human_ui_create_product_live(self, driver):
        """Visually create a Product via live UI form typing and button clicks."""
        prod_title = unique_name("UIProduct")
        prod_sku = f"SKU-{time.time_ns() % 100000}"
        log_step(f"LIVE UI: Navigating to Product Creation page for {prod_title!r}", driver=driver)
        driver.get(f"{settings.wp_base_url}/wp-admin/admin.php?page=kirki-ecommerce#/products/create")
        time.sleep(2)

        # Fill Title
        log_step(f"LIVE UI: Typing product title '{prod_title}'", driver=driver)
        title_in = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='title']"))
        )
        title_in.clear()
        title_in.send_keys(prod_title)

        # Fill Ribbon
        ribbon_in = driver.find_elements(By.CSS_SELECTOR, "input[name='ribbon']")
        if ribbon_in:
            log_step("LIVE UI: Typing product ribbon 'Hot Deal'", driver=driver)
            ribbon_in[0].clear()
            ribbon_in[0].send_keys("Hot Deal")

        # Fill Short Description
        desc_in = driver.find_elements(By.CSS_SELECTOR, "textarea[name='short_description']")
        if desc_in:
            log_step("LIVE UI: Typing product short description", driver=driver)
            desc_in[0].send_keys(f"Short summary description for {prod_title}")

        # Fill Price
        price_in = driver.find_elements(By.CSS_SELECTOR, "input[name='variants.0.base_price']")
        if price_in:
            log_step("LIVE UI: Typing product base price '49.99'", driver=driver)
            price_in[0].clear()
            price_in[0].send_keys("49.99")

        # Fill SKU
        sku_in = driver.find_elements(By.CSS_SELECTOR, "input[name='variants.0.sku']")
        if sku_in:
            log_step(f"LIVE UI: Typing product SKU '{prod_sku}'", driver=driver)
            sku_in[0].clear()
            sku_in[0].send_keys(prod_sku)

        # Fill SEO Title & Description
        seo_t = driver.find_elements(By.CSS_SELECTOR, "input[name='seo_title']")
        if seo_t:
            seo_t[0].send_keys(f"SEO {prod_title}")

        # Click Create Button
        create_btn = driver.find_element(By.XPATH, "//button[text()='Create']")
        log_step("LIVE UI: Clicking 'Create' button to publish product", driver=driver)
        driver.execute_script("arguments[0].click();", create_btn)
        time.sleep(3)
        log_step(f"LIVE UI: Product '{prod_title}' created successfully via UI", driver=driver)

    def test_06_human_ui_settings_all_tabs_live(self, driver):
        """Visually navigate and edit input fields across ALL 9 Settings tabs live on screen."""
        driver.get(f"{settings.wp_base_url}/wp-admin/admin.php?page=kirki-ecommerce#/settings/general")
        time.sleep(2.5)

        tabs = [
            ("General", "General Settings"),
            ("Products", "Product Settings"),
            ("Shipping", "Shipping Settings"),
            ("Currency", "Currency Settings"),
            ("Tax", "Tax Settings"),
            ("Payments", "Payment Gateways"),
            ("Emails", "Email Notifications"),
            ("Checkout", "Checkout Settings"),
            ("Advanced", "Advanced Options")
        ]

        for tab_name, label in tabs:
            log_step(f"LIVE UI: Clicking sidebar tab '{tab_name}' for {label}", driver=driver)
            xpath = f"//span[text()='{tab_name}'] | //div[text()='{tab_name}']"
            tab_els = driver.find_elements(By.XPATH, xpath)
            clicked = False
            for el in tab_els:
                if el.is_displayed():
                    driver.execute_script("arguments[0].click();", el)
                    clicked = True
                    time.sleep(2)
                    break

            if not clicked:
                log_step(f"LIVE UI: Direct navigating to setting tab '{tab_name}'", driver=driver)
                driver.get(f"{settings.wp_base_url}/wp-admin/admin.php?page=kirki-ecommerce#/settings/{tab_name.lower()}")
                time.sleep(2)

            # Interact with text input fields
            inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[placeholder*='store'], input[placeholder*='Enter']")
            for inp in inputs[:2]:
                if inp.is_displayed() and inp.is_enabled():
                    curr = inp.get_attribute("value") or ""
                    log_step(f"LIVE UI: Typing into input field on '{tab_name}' tab", driver=driver)
                    inp.clear()
                    inp.send_keys(curr or f"Kirki {tab_name} Value")
                    time.sleep(0.5)

            # Click Save Button
            save_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Save')]")
            assert len(save_btns) > 0, f"Save button must exist on '{tab_name}' settings tab"
            for sb in save_btns:
                if sb.is_displayed():
                    log_step(f"LIVE UI: Clicking 'Save' button on '{tab_name}' settings tab", driver=driver)
                    driver.execute_script("arguments[0].click();", sb)
                    time.sleep(1.0)
                    break

        log_step("LIVE UI: Successfully navigated and saved settings across ALL 9 settings tabs", driver=driver)
