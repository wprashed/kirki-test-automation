"""Slack and Discord Webhook Notification Utility."""

import json
import os
import requests
from utils.logging_setup import log_step

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

def send_slack_notification(total: int, passed: int, failed: int, pass_rate: float, duration: float) -> bool:
    """Send summary notification card to Slack incoming webhook."""
    if not SLACK_WEBHOOK_URL:
        log_step("SLACK_WEBHOOK_URL not configured. Skipping Slack alert.")
        return False

    color = "#10B981" if failed == 0 else "#EF4444"
    status_title = "✅ Test Suite Passed" if failed == 0 else "❌ Test Suite Failures Detected"

    payload = {
        "text": f"Kirki eCommerce Test Automation Summary: {status_title}",
        "attachments": [
            {
                "color": color,
                "title": status_title,
                "fields": [
                    {"title": "Total Tests", "value": str(total), "short": True},
                    {"title": "Passed", "value": str(passed), "short": True},
                    {"title": "Failed", "value": str(failed), "short": True},
                    {"title": "Pass Rate", "value": f"{pass_rate:.1f}%", "short": True},
                    {"title": "Duration", "value": f"{duration:.2f}s", "short": True}
                ],
                "footer": "Kirki eCommerce Automation System"
            }
        ]
    }

    try:
        res = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        log_step(f"Slack webhook status: {res.status_code}")
        return res.status_code == 200
    except Exception as e:
        log_step(f"Slack webhook error: {e}")
        return False


def send_discord_notification(total: int, passed: int, failed: int, pass_rate: float, duration: float) -> bool:
    """Send summary embed notification to Discord incoming webhook."""
    if not DISCORD_WEBHOOK_URL:
        log_step("DISCORD_WEBHOOK_URL not configured. Skipping Discord alert.")
        return False

    color = 0x10B981 if failed == 0 else 0xEF4444
    status_title = "✅ Kirki Test Suite Passed" if failed == 0 else "❌ Kirki Test Suite Failures"

    payload = {
        "embeds": [
            {
                "title": status_title,
                "color": color,
                "fields": [
                    {"name": "Total", "value": str(total), "inline": True},
                    {"name": "Passed", "value": str(passed), "inline": True},
                    {"name": "Failed", "value": str(failed), "inline": True},
                    {"name": "Pass Rate", "value": f"{pass_rate:.1f}%", "inline": True},
                    {"name": "Duration", "value": f"{duration:.2f}s", "inline": True}
                ]
            }
        ]
    }

    try:
        res = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
        log_step(f"Discord webhook status: {res.status_code}")
        return res.status_code in (200, 204)
    except Exception as e:
        log_step(f"Discord webhook error: {e}")
        return False
