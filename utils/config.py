"""Application configuration loaded from environment / .env file.

All environment-specific values (URLs, credentials, browser options) come
from here. Nothing in the test code should hard-code a URL or credential.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# The directory that contains config/ (i.e. the framework root).
ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- WordPress ---
    wp_base_url: str = "http://tutorlms.local"
    wp_rest_prefix: str = "wp-json"

    # --- Credentials ---
    admin_user: str = "admin"
    admin_password: str = ""
    customer_user: str = "customer@example.com"
    customer_password: str = ""

    # --- Browser ---
    browser: str = "chrome"  # chrome | firefox
    headless: bool = True
    chrome_binary: str = ""
    firefox_binary: str = ""
    explicit_wait: float = 15.0
    implicit_wait: float = 0.0
    poll_interval: float = 0.25

    def model_post_init(self, __context) -> None:
        """Allow HEADLESS and WP_BASE_URL env-vars to override settings at runtime."""
        import os
        raw = os.environ.get("HEADLESS", "").strip().lower()
        if raw in ("false", "0", "no"):
            object.__setattr__(self, "headless", False)
        elif raw in ("true", "1", "yes"):
            object.__setattr__(self, "headless", True)

        url_override = os.environ.get("WP_BASE_URL", "").strip()
        if url_override:
            object.__setattr__(self, "wp_base_url", url_override.rstrip("/"))

    # --- Artifacts ---
    screenshot_dir: str = "screenshots"
    report_dir: str = "reports"
    capture_console: bool = True

    # --- Database (optional) ---
    db_host: str = ""  # TCP host or unix socket path
    db_port: int = 3306
    db_name: str = ""
    db_user: str = ""
    db_password: str = ""

    # --- WP-CLI (optional) ---
    wp_cli_path: str = ""

    # --- PayPal sandbox ---
    paypal_sandbox_email: str = ""
    paypal_sandbox_password: str = ""

    # --- Test data ---
    test_data_prefix: str = "KECOM_TEST"

    # --- Derived helpers ---
    @property
    def rest_url(self) -> str:
        """Base REST URL for the plugin API namespace."""
        return f"{self.wp_base_url.rstrip('/')}/{self.wp_rest_prefix.strip('/')}/kirki/ecommerce/v1"

    @property
    def admin_url(self) -> str:
        return f"{self.wp_base_url.rstrip('/')}/wp-admin"

    @property
    def wp_login_url(self) -> str:
        return f"{self.wp_base_url.rstrip('/')}/wp-login.php"

    @property
    def screenshot_path(self) -> Path:
        p = ROOT_DIR / self.screenshot_dir
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def report_path(self) -> Path:
        p = ROOT_DIR / self.report_dir
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def paypal_configured(self) -> bool:
        return bool(self.paypal_sandbox_email and self.paypal_sandbox_password)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
