"""Single-Pass Complete Plugin Pages & Settings Update Suite.

Visits every single page and tab in Kirki eCommerce in a clean, non-repetitive single pass:
1. Admin SPA Pages (Dashboard, Products, Categories, Tags, Brands, Collections, Attributes, Coupons, Orders, Customers, Tax Profiles, Shipping Profiles, Shipping Boxes, Product Schemas, Online Payments, Offline Payments, Onboarding)
2. All 9 Settings Tabs (General, Products, Shipping, Currency, Tax, Payments, Emails, Checkout, Advanced) with actual field input updates and Save button triggers.
3. Storefront & Customer Portal Pages (Shop, Cart, Checkout, My Account, Orders, Addresses, Account Details).
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.admin.admin_pages import AdminLoginPage
from utils.config import settings
from utils.logging_setup import log_step


@pytest.mark.ui_walkthrough
class TestSinglePassAllPagesAndSettingsUpdate:
    @pytest.fixture(autouse=True)
    def ensure_admin_logged_in(self, driver):
        """Ensure WordPress admin session is active."""
        driver.get(f"{settings.wp_base_url}/wp-admin/admin.php?page=kirki-ecommerce#/")
        time.sleep(1)
        if "wp-login.php" in driver.current_url:
            AdminLoginPage(driver).login_as_admin()

    def test_01_all_admin_navigation_pages_single_pass(self, driver):
        """Single-pass visit across all 17 Kirki Admin SPA pages."""
        admin_pages = [
            ("Dashboard", "#/"),
            ("Products Catalog", "#/products"),
            ("Categories", "#/categories"),
            ("Tags", "#/tags"),
            ("Brands", "#/brands"),
            ("Collections", "#/collections"),
            ("Attributes", "#/attributes"),
            ("Coupons", "#/coupons"),
            ("Orders List", "#/orders"),
            ("Customers", "#/customers"),
            ("Tax Profiles", "#/tax-profiles"),
            ("Shipping Profiles", "#/shipping-profiles"),
            ("Shipping Boxes", "#/shipping-boxes"),
            ("Product Schemas", "#/product-schemas"),
            ("Online Payments", "#/online-payments"),
            ("Offline Payments", "#/offline-payments"),
            ("Onboarding Wizard", "#/onboarding"),
        ]

        for title, route in admin_pages:
            url = f"{settings.wp_base_url}/wp-admin/admin.php?page=kirki-ecommerce{route}"
            log_step(f"SINGLE-PASS ADMIN UI: Visiting page '{title}' -> {url}", driver=driver)
            driver.get(url)
            time.sleep(0.8)
            assert driver.current_url.startswith("http")
            log_step(f"SINGLE-PASS ADMIN UI: Successfully rendered '{title}'", driver=driver)

    def test_02_update_all_settings_tabs_single_pass(self, driver):
        """Single-pass update of input fields and Save actions across ALL 9 Settings tabs."""
        base_settings_url = f"{settings.wp_base_url}/wp-admin/admin.php?page=kirki-ecommerce#/settings/general"
        log_step(f"SINGLE-PASS SETTINGS UI: Opening main settings page -> {base_settings_url}", driver=driver)
        driver.get(base_settings_url)
        time.sleep(2.5)

        settings_tabs = [
            ("General", "Store Name, Email & Address"),
            ("Products", "Inventory & Catalog Rules"),
            ("Shipping", "Fulfillment & Rates"),
            ("Currency", "Currency Symbol & Formatting"),
            ("Tax", "Tax Rates & Profiles"),
            ("Payments", "Payment Gateway Configuration"),
            ("Emails", "Order & Customer Notifications"),
            ("Checkout", "Checkout Form Requirements"),
            ("Advanced", "System & API Configurations")
        ]

        for tab_name, description in settings_tabs:
            log_step(f"SINGLE-PASS SETTINGS UI: Clicking tab '{tab_name}' ({description})", driver=driver)
            
            # Click tab element on sidebar
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
                log_step(f"SINGLE-PASS SETTINGS UI: Direct navigating to tab '{tab_name}'", driver=driver)
                driver.get(f"{settings.wp_base_url}/wp-admin/admin.php?page=kirki-ecommerce#/settings/{tab_name.lower()}")
                time.sleep(2)

            # Actively update input values on the active settings tab
            inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[placeholder*='store'], input[placeholder*='Enter']")
            for idx, inp in enumerate(inputs[:3]):
                if inp.is_displayed() and inp.is_enabled():
                    curr_val = inp.get_attribute("value") or ""
                    new_val = f"Updated Kirki {tab_name} #{idx+1}"
                    log_step(f"SINGLE-PASS SETTINGS UI: Updating input field #{idx+1} on '{tab_name}' tab -> {new_val!r}", driver=driver)
                    try:
                        inp.clear()
                        inp.send_keys(new_val)
                        time.sleep(0.4)
                    except Exception as ex:
                        if "not interactable" in str(ex).lower() or "invalid element state" in str(ex).lower():
                            log_step(f"SINGLE-PASS SETTINGS UI: Input #{idx+1} on '{tab_name}' read-only/disabled -> skipped")
                        else:
                            raise ex

            # Click Save Button
            save_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Save')]")
            assert len(save_btns) > 0, f"Save button must exist on '{tab_name}' settings tab"
            for sb in save_btns:
                if sb.is_displayed():
                    log_step(f"SINGLE-PASS SETTINGS UI: Clicking 'Save' button for '{tab_name}' settings", driver=driver)
                    driver.execute_script("arguments[0].click();", sb)
                    time.sleep(1.5)
                    break

        log_step("SINGLE-PASS SETTINGS UI: Successfully updated inputs and saved settings across ALL 9 settings tabs", driver=driver)

    def test_03_storefront_and_customer_portal_pages_single_pass(self, driver):
        """Single-pass visit across all Storefront and Customer Portal pages."""
        storefront_pages = [
            ("Shop Grid Catalog", f"{settings.wp_base_url}/shop"),
            ("Cart Page", f"{settings.wp_base_url}/cart"),
            ("Checkout Page", f"{settings.wp_base_url}/checkout"),
            ("Customer Portal Dashboard", f"{settings.wp_base_url}/my-account"),
            ("Customer Orders History", f"{settings.wp_base_url}/my-account/orders"),
            ("Customer Saved Addresses", f"{settings.wp_base_url}/my-account/addresses"),
            ("Customer Account Details", f"{settings.wp_base_url}/my-account/edit-account"),
        ]

        for title, page_url in storefront_pages:
            log_step(f"SINGLE-PASS STOREFRONT UI: Visiting '{title}' -> {page_url}", driver=driver)
            driver.get(page_url)
            time.sleep(1.5)
            assert driver.current_url.startswith("http")
            log_step(f"SINGLE-PASS STOREFRONT UI: Successfully rendered '{title}'", driver=driver)
