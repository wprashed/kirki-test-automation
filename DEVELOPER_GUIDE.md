# 🛠️ Kirki eCommerce Test Automation Developer & Architecture Guide

This developer guide provides an in-depth reference manual for engineers, QA automation specialists, and DevOps contributors maintaining or extending the **Kirki eCommerce Test Automation Framework**.

---

## 📐 1. Architectural Overview & System Design

The testing framework follows enterprise software automation design patterns:

- **Page Object Model (POM)**: Enforces separation between UI test logic and DOM element selectors (`pages/`).
- **REST API Client Abstraction**: Centralized HTTP client (`WpRestClient`) handling authentication headers, cookies, rate limits, and JSON responses.
- **Fixture Registry**: Pytest fixtures (`fixtures/conftest.py`) initializing persistent browser sessions, API clients, and database cleanup.
- **Visual Regression Engine**: Pixel-by-pixel canvas diffing engine (`utils/visual/`) utilizing Pillow image processing.
- **Dynamic Executive QA Report Engine**: Abstract Syntax Tree (`ast`) docstring parser converting assertions into business Q&A format (`reports/report_generator.py`).
- **Real-Time Web Studio Dashboard**: Flask daemon (`gui_web.py`) hosting dynamic statistics, SSE log streaming, step screenshot galleries, and historical run archives.

---

## 📂 2. Directory & Component Structure

```text
tests-automation/
├── .github/workflows/pytest.yml  # GitHub Actions CI/CD Pipeline
├── static/index.html             # Modern Web Studio UI (Light & Dark Theme Engine)
├── pages/                        # Page Object Model classes
│   ├── base_page.py              # Base page with explicit wait helpers & screenshot hooks
│   ├── admin/admin_pages.py      # Admin Dashboard & Kirki SPA Sections
│   └── frontend/                 # Shop, Cart, Checkout, Account, Login, Register Pages
├── utils/                        # System utilities
│   ├── api/client.py             # WpRestClient (HTTP requests & auth)
│   ├── api/wp_rest.py            # WpRest domain wrappers & unique_name helper
│   ├── visual/diff_engine.py     # Image baseline comparison & pixel diffing (Pillow)
│   ├── performance/vitals_audit.py # Core Web Vitals Navigation Timing Auditor
│   ├── notifications/webhook_notifier.py # Slack, Telegram & Discord Alerting
│   ├── config.py                 # Framework configuration settings
│   └── logging_setup.py          # Loggers & step screenshot capture registry
├── tests/                        # 231+ Automated Test Cases (57 Files)
│   ├── smoke/                    # Core purchase workflows & UI walkthroughs
│   ├── admin/                    # Admin REST CRUD, Settings, Decision Engine, Webhooks
│   ├── coupons/                  # Coupon engine, usage limits, cloning, SPA forms
│   ├── frontend/                 # Cart API, Account API, Reviews, Mobile Viewport, Shortcodes
│   ├── orders/                   # Order lifecycle, status actions, refunds, activities
│   ├── security/                 # Auth barriers, SQLi, XSS, and DAST Scanner
│   ├── performance/              # Core Web Vitals & Multi-User Stress testing
│   ├── visual/                   # Pixel-by-pixel baseline layout diff regression
│   └── ui_walkthrough/           # Real human click-and-type interactive browser suite
├── locustfile.py                 # Locust high-concurrency API performance load test
├── Dockerfile                    # Containerized Chromium & Pytest environment
├── docker-compose.yml            # Multi-container stack (WordPress, MySQL 8.0, Pytest runner)
├── gui_web.py                    # Flask Web Automation Studio (Port 5001)
├── README.md                     # Framework documentation & quick start
└── DEVELOPER_GUIDE.md            # In-depth technical architecture manual
```

---

## 🛠️ 3. Execution Commands Quick Reference

### Running Pytest CLI
```bash
source .venv/bin/activate

# Execute full suite (231+ tests)
pytest tests/ -v --html=reports/latest_report.html --self-contained-html

# Parallel multi-worker execution (4 parallel workers)
pytest tests/ -n 4 -v

# Live Browser watch mode
HEADLESS=false pytest tests/ -v

# Run Visual Layout Diff Engine
pytest tests/visual/test_visual_layout_diff_regression.py -v

# Run Core Web Vitals Performance Audit
pytest tests/performance/test_core_web_vitals_audit.py -v

# Run Security DAST Scanner (SQLi / XSS / BOPA)
pytest tests/security/test_dast_vulnerability_scanner.py -v

# Run Mobile Responsive Viewport Suite
pytest tests/frontend/test_mobile_responsive_checkout.py -v

# Run Real Human Interactive Click & Type Suite
pytest tests/ui_walkthrough/test_human_ui_complete_flow.py -v

# Cross-Browser Execution (Firefox / Edge)
BROWSER=firefox pytest tests/ -v
BROWSER=edge pytest tests/ -v
```

### Running Web Automation Studio Dashboard
```bash
source .venv/bin/activate
python3 gui_web.py
```
Open **`http://localhost:5001`** in browser.

### Running Locust High-Concurrency API Load Tests
```bash
source .venv/bin/activate
locust -f locustfile.py --host=http://tutorlms.local --headless -u 50 -r 10 --run-time 1m
```

---

## 📝 4. Standards & Best Practices

1. **Entity Name Uniqueness**: Always use `unique_name("Prefix")` for test entities to avoid database key collision.
2. **Explicit Wait Patterns**: Use `WebDriverWait` and `wait_until()` helpers in `utils/selenium_helpers.py` instead of arbitrary `time.sleep()`.
3. **Step Logging**: Call `log_step("description", driver=self.driver)` for every major action step to populate screenshots automatically.
4. **Teardown Cleanup**: Always clean up created resources (products, coupons, categories, orders) inside `finally` or test teardown blocks.
5. **No Hardcoded Credentials**: Consume settings from `utils.config.settings` (`settings.admin_user`, `settings.admin_password`, `settings.wp_base_url`).
