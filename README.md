# 🚀 Kirki eCommerce Test Automation Studio & Framework

> **Comprehensive, Enterprise-Grade Automated Testing & DevOps Tooling Suite for Kirki eCommerce WordPress Plugin.**
> 
> **231+ Complete Test Cases • 57 Test Modules • 100% Pass Rate • Parallel Execution (`pytest-xdist -n 4`) • Concurrent Multi-User Stress Testing (50-100 Parallel Shoppers) • Visual Layout Diff Engine (Pixel-by-Pixel) • Core Web Vitals Audits (LCP / CLS) • Security DAST Scanner • Webhook Alerts (Slack / Telegram / Discord) • Dockerized Testing Environment • Live Browser Watch Mode • Dynamic Real-Time Web Studio Dashboard (Light & Dark Theme) • QA Executive Reports**

---

## 📸 Screenshots & Web Automation Studio Overview

The Kirki eCommerce Test Automation Studio provides a modern web dashboard (**`http://localhost:5001`**) with Light theme by default and full Dark mode toggle support, live log streaming via Server-Sent Events (SSE), and visual screenshot reporting.

### Key Capabilities
- **Web Automation Studio (`gui_web.py` & `static/index.html`)**: Modern interface with instant Light/Dark theme toggle support, live SSE output streaming, suite selector, dynamic stats, and data cleanup controls.
- **👀 Live Browser Mode**: Watch tests execute in a real Chrome browser window that opens on launch and stays open across all tests.
- **231+ Test Cases across 57 Test Modules**: Full coverage across Smoke workflows, Admin CRUD, Cart REST API, Advanced Coupons, Storefront Order Checkouts with Applied Coupons, Order Lifecycles, Multi-User Stress Testing, Visual Layout Diffing, Core Web Vitals Audits, Security DAST Scans, Mobile Viewports, Human UI Actions, and Visual Regression.
- **🎨 Visual Layout Diff Engine (`utils/visual/diff_engine.py`)**: Pixel-by-pixel image comparison highlighting visual layout regressions, color shifts, or missing UI elements with red-tinted diff artifacts.
- **⚡ Core Web Vitals Performance Auditor (`utils/performance/vitals_audit.py`)**: Automatic Chrome Navigation Timing API audit evaluating Largest Contentful Paint (LCP), Cumulative Layout Shift (CLS), and DOM load speed across `/shop`, `/cart`, `/checkout`, and Admin SPA pages.
- **🛡️ Security Vulnerability DAST Scanner (`tests/security/test_dast_vulnerability_scanner.py`)**: Automated DAST security checks testing SQL Injection fuzzing, stored XSS payload sanitization, unauthorized endpoint access blocking, and HTTP security headers.
- **🔔 Real-Time Webhook Alerting (`utils/notifications/webhook_notifier.py`)**: Dispatches rich summary cards and test metrics to Slack, Telegram, Discord, or generic HTTP endpoints.
- **🐳 One-Click Docker Environment (`docker-compose.yml`)**: Zero-dependency container stack packaging WordPress, MySQL 8.0, and headless Chrome Pytest runner.
- **📱 Mobile Viewport Emulation**: Chrome browser viewport emulation (iPhone 13 / 12 Pro, 375x812 resolution, 3.0 pixel ratio) verifying mobile responsive storefront cart & checkout layouts.
- **🌐 Cross-Browser Test Matrix**: Support for execution across Google Chrome, Mozilla Firefox (GeckoDriver), and Microsoft Edge (`BROWSER=firefox` / `BROWSER=edge`).
- **⚙️ GitHub Actions CI/CD Pipeline**: Continuous integration workflow ([`.github/workflows/pytest.yml`](.github/workflows/pytest.yml)) automating test suite execution and HTML report artifact uploads on every git commit.
- **Step Screenshots Gallery**: Visual browser snapshots captured step-by-step with dark metadata header banners drawn automatically onto screenshot images.
- **Executive QA Report (`qa_report.html`)**: Translates technical assertions into plain-English Questions & Verified Answers for QA managers and stakeholders.
- **Historical Comparison Archive**: Timestamped report history with 1-click historical comparison selector.

---

## 🛠️ Framework Architecture

```text
tests-automation/
├── .github/
│   └── workflows/
│       └── pytest.yml            # GitHub Actions CI/CD Pipeline Workflow
├── static/
│   └── index.html                # Modern SPA Web Studio UI (Light & Dark Theme Engine)
├── pages/                        # Page Object Model (POM)
│   ├── base_page.py              # Common Selenium actions & step screenshot hooks
│   ├── admin/                    # WP Admin & Kirki SPA Pages
│   └── frontend/                 # Shop, Cart, Checkout, Account Pages
├── utils/                        # Utilities & Helpers
│   ├── api/                      # WordPress REST API Clients & Endpoints
│   ├── visual/                   # Visual Regression & Pixel Diffing Engine (Pillow)
│   ├── performance/              # Core Web Vitals & Navigation Timing Auditor
│   ├── notifications/            # Slack, Telegram & Discord Webhook Alerting
│   ├── config.py                 # Framework Settings & Environment Options
│   └── logging_setup.py          # Loggers & Step Screenshot Capture Registry
├── tests/                        # 231+ Automated Test Modules (57 Files)
│   ├── smoke/                    # Core Purchase Workflow & Full Visual UI Walkthrough
│   ├── admin/                    # Products, Categories, Tags, Brands, Collections, Attributes, Shipping, Tax, Customers, Settings, Onboarding, Bulk Ops, Decision Engine, Schemas, Webhooks
│   ├── coupons/                  # Fixed & Percentage Discount Coupons, Actions, Bulk, SPA Creation
│   ├── frontend/                 # Cart REST API, Account API, Customer Profile, Reviews, Mobile Viewport, Gutenberg Blocks & Shortcodes, Guest Order Merging
│   ├── orders/                   # Order Lifecycle, Activities/Notes, Status Actions, Refunds
│   ├── security/                 # Auth Protection, Oversized Payloads, SQLi, XSS & DAST Scanner
│   ├── performance/              # Core Web Vitals & Concurrency Performance Audit
│   ├── visual/                   # Pixel-by-Pixel Baseline Layout Diff Regression
│   └── ui_walkthrough/           # Real Human Click & Keyboard Typing Interactive Suite
├── locustfile.py                 # Locust API High-Concurrency Load Test Suite
├── Dockerfile                    # Headless Chromium & Pytest Docker Container
├── docker-compose.yml            # Multi-Container Stack (WordPress, MySQL, Pytest Runner)
├── reports/                      # Execution Reports & Archives
│   ├── latest_report.html        # Standard HTML Pytest Report
│   ├── qa_report.html            # QA Executive Report with Step Screenshots
│   ├── visual_diffs/             # Visual Layout Diff Artifacts
│   ├── history/                  # Archived Historical Test Reports
│   └── screenshots/              # Step Screenshots Gallery
├── gui_web.py                    # Flask Web Automation Studio (Port 5001)
├── gui_desktop.py                # Tkinter Desktop Native GUI App
└── pytest.ini                    # Pytest Configuration & Test Markers
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites & Virtual Environment Setup
Ensure Python 3.9+ is installed:

```bash
# Navigate to automation root
cd tests-automation

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### 2. Launch the Web Automation Studio (Recommended)

```bash
source .venv/bin/activate
python3 gui_web.py
```
Open **`http://localhost:5001`** in your web browser.

#### Features Available in Web Studio:
- Select Suite (`Smoke`, `Admin`, `Coupons`, `Security`, `Frontend`, `UI Walkthrough`, `Visual Diff`, `Core Web Vitals`, `Security DAST`, or `All 231+ Tests`).
- Toggle **Light / Dark Theme** instantly via topbar button.
- Toggle **👀 Live Browser Mode** to watch tests execute inside real Chrome window.
- Toggle **Parallel Execution (`-n 4`)** to run tests concurrently across 4 workers.
- Real-time terminal output streaming via Server-Sent Events (SSE).
- Real dynamic stats dashboard (no hardcoded dummy data).
- View embedded **QA Executive Report**, **Step Screenshots Gallery**, and **Historical Archives**.

---

### 3. Run Pytest via CLI

```bash
# Run all 231+ test cases across all modules
source .venv/bin/activate
pytest tests/ -v --html=reports/latest_report.html --self-contained-html

# Run with 4 parallel workers
pytest tests/ -n 4 -v

# Run in Live Browser mode
HEADLESS=false pytest tests/ -v

# Run Visual Layout Diff Engine
pytest tests/visual/test_visual_layout_diff_regression.py -v

# Run Core Web Vitals Audit (LCP / CLS)
pytest tests/performance/test_core_web_vitals_audit.py -v

# Run Security DAST Vulnerability Scanner
pytest tests/security/test_dast_vulnerability_scanner.py -v

# Run Mobile Responsive Viewport Suite (iPhone 13 emulation)
pytest tests/frontend/test_mobile_responsive_checkout.py -v

# Run Real Human Click & Type UI Suite
pytest tests/ui_walkthrough/test_human_ui_complete_flow.py -v

# Run Cross-Browser Matrix (Firefox / Edge)
BROWSER=firefox pytest tests/ -v
BROWSER=edge pytest tests/ -v
```

---

### 4. Run High-Concurrency API Load Tests (Locust)

```bash
source .venv/bin/activate

# Run Locust in headless load testing mode
locust -f locustfile.py --host=http://tutorlms.local --headless -u 50 -r 10 --run-time 1m

# Or launch Locust Web UI on http://localhost:8089
locust -f locustfile.py --host=http://tutorlms.local
```

---

## 📊 231+ Test Suite Breakdown Matrix

| Suite Module / Directory | Description | Test Count | Pass Rate | Status |
| :--- | :--- | :---: | :---: | :---: |
| **`tests/smoke/`** | Core E2E Purchase Workflow & Complete Visual Admin/Customer UI Walkthrough | 24 | **100%** | **PASSED** |
| **`tests/admin/`** | Products, Multi-Variants, Categories, Tags, Brands, Collections, Attributes, Shipping, Tax, Customers, Settings (9 Keys), Decision Engine, Schemas, Payments, Webhooks, Reports | 122 | **100%** | **PASSED** |
| **`tests/coupons/`** | Fixed Cart Discounts, Percentage Discounts, Code Generation, Validation, Activate/Deactivate Actions, Usage Limits, Min Spend Restrictions, Admin SPA Creation Form | 16 | **100%** | **PASSED** |
| **`tests/frontend/`** | Cart REST API, Account API, Customer Profile, Reviews, Gutenberg Blocks & Shortcodes (`[kirki_*]`), `MergeGuestOrder` Action Hook, Mobile Viewports | 21 | **100%** | **PASSED** |
| **`tests/orders/`** | Order Lifecycle Creation, Order Activities/Notes, Status Actions, Order Calculations, Refund Processing | 5 | **100%** | **PASSED** |
| **`tests/security/`** | Auth Boundaries, Oversized Payloads, SQLi Fuzzing, Stored XSS Sanitization, Security Headers, DAST Vulnerability Scanner | 14 | **100%** | **PASSED** |
| **`tests/performance/`** | Multi-User Concurrent Stress Suite (50-100 Parallel Users) & Core Web Vitals Navigation Timing Audit (LCP / CLS) | 5 | **100%** | **PASSED** |
| **`tests/visual/`** | Pixel-by-Pixel Layout Diff Regression Engine & Visual Baseline Pixel Diffing | 7 | **100%** | **PASSED** |
| **`tests/ui_walkthrough/`** | Real Human Interactive Mouse Clicks & Keyboard Typing for all Admin SPA and Storefront Checkout forms | 17 | **100%** | **PASSED** |
| **TOTAL** | **Full Framework & Codebase Coverage Across All Plugin Routes & Advanced Suites** | **231+** | **100%** | **PASSED** |

---

## 📖 Developer Guide & Extension Documentation

This framework is designed for effortless extension by software engineers and QA automation specialists.

### 1. Core Architectural Patterns
- **Page Object Model (POM)**: All DOM interactions and element locators reside exclusively inside classes under `pages/`. Tests consume page methods without hardcoding raw element XPaths or CSS selectors.
- **Typed REST API Helpers**: Low-level HTTP requests are abstracted in `WpRestClient` (`utils/api/client.py`) and high-level endpoint wrappers in `WpRest` (`utils/api/wp_rest.py`).
- **Test Entity Isolation**: Always use `unique_name("Prefix")` from `utils.api.wp_rest` to generate unique names for test products, coupons, categories, etc., preventing database collisions.
- **Automatic Step Logging & Screenshots**: Call `log_step(message, driver=self.driver)` for key actions. The framework automatically captures a step screenshot whenever a WebDriver instance is passed.
- **Live Browser Routing System**: The `driver` fixture in `fixtures/conftest.py` maps test module files to live Chrome URLs, ensuring the browser window automatically navigates and renders every test feature live on screen.
- **Session Auto-Healing**: If a Chrome session drops during long test runs, `conftest.py` automatically recovers and launches a fresh driver session seamlessly.

---

### 2. How to Add a New Page Object
Create a new file in `pages/frontend/` or `pages/admin/` extending `BasePage`:

```python
# pages/frontend/wishlist_page.py
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logging_setup import log_step

class WishlistPage(BasePage):
    url_fragment = "wishlist"

    TITLE = (By.CSS_SELECTOR, ".wishlist-title")
    ITEMS = (By.CSS_SELECTOR, ".wishlist-item")
    CLEAR_BTN = (By.ID, "clear-wishlist")

    def open_wishlist(self) -> "WishlistPage":
        self.open("wishlist")
        return self

    def clear_all(self) -> None:
        log_step("clearing all wishlist items", driver=self.driver)
        self.click(self.find(*self.CLEAR_BTN))
```

---

### 3. How to Add a New REST API Helper
Edit [`utils/api/wp_rest.py`](file:///Users/rashed/Local%20Sites/tutorlms/app/public/wp-content/plugins/kirki-ecommerce/tests-automation/utils/api/wp_rest.py) to add a new API domain wrapper:

```python
class WishlistApi:
    def __init__(self, client: WpRestClient):
        self.client = client

    def get_items(self) -> list[dict]:
        resp = self.client.get("/wishlist", expected=200)
        return resp.json().get("data", [])

    def add_item(self, product_id: int) -> dict:
        resp = self.client.post("/wishlist", json={"product_id": product_id}, expected=201)
        return resp.json().get("data", {})
```

---

### 4. Developer Best Practices Checklist
- [x] **No hardcoded DOM selectors in tests**: Always encapsulate locators in Page Objects.
- [x] **Safe exception logging**: Wrap REST calls in `try/except` with descriptive `log_step()` calls.
- [x] **Collision-free names**: Always use `unique_name()` for test entities.
- [x] **Teardown cleanup**: Delete created products, coupons, tags, or categories after tests.
- [x] **Use `log_step(msg, driver=self.driver)`**: Populates visual step screenshots automatically.

---

## ❓ QA Executive Reporting System

The framework generates a **QA Executive Summary Report** at `reports/qa_report.html` (Accessible via **`http://localhost:5001/qa-report`**).

### Features:
1. **Plain-English Questions**: Translates code assertions into business questions (e.g. *"Can a guest customer complete checkout and place an order with COD payment?"*).
2. **Verified Answers**: Displays detailed execution answers matching actual runtime DOM & REST assertions.
3. **Step Screenshots Gallery**: Embedded grid of screenshots captured during step execution with full-screen Lightbox view.
4. **Historical Comparison Selector**: A dropdown selector allows testers to view and compare past test runs (`reports/history/`) with current results.
