"""
Real-Time Webhook Notification Engine for Kirki eCommerce Automation Suite
Dispatches test execution summaries, pass/fail stats, and alert cards to Slack, Telegram, Discord, or generic HTTP endpoints.
"""

import os
import sys
import json
import requests
from utils.logging_setup import get_logger

logger = get_logger()


def send_webhook_notification(summary: dict, webhook_url: str = None) -> bool:
    """
    Sends structured test summary payload to specified webhook URL.
    Falls back to WEBHOOK_URL environment variable if webhook_url is omitted.
    """
    target_url = webhook_url or os.environ.get("WEBHOOK_URL")
    if not target_url:
        logger.info("No WEBHOOK_URL configured. Skipping webhook dispatch.")
        return False

    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    total = summary.get("total", 0)
    duration = summary.get("duration", "0.0s")
    status_emoji = "✅" if failed == 0 else "🚨"
    title = f"{status_emoji} Kirki eCommerce Test Suite Run Completed"

    # Construct Slack / Discord / Generic compatible payload
    payload = {
        "text": f"*{title}*\n• *Total Tests*: {total}\n• *Passed*: {passed}\n• *Failed*: {failed}\n• *Duration*: {duration}",
        "attachments": [
            {
                "color": "#22c55e" if failed == 0 else "#ef4444",
                "fields": [
                    {"title": "Total", "value": str(total), "short": True},
                    {"title": "Passed", "value": str(passed), "short": True},
                    {"title": "Failed", "value": str(failed), "short": True},
                    {"title": "Duration", "value": str(duration), "short": True}
                ]
            }
        ]
    }

    try:
        res = requests.post(target_url, json=payload, timeout=10)
        logger.info(f"Webhook notification dispatched to {target_url[:30]}... Response: {res.status_code}")
        return res.status_code in [200, 201, 204]
    except Exception as e:
        logger.error(f"Failed to dispatch webhook notification: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_summary = {"total": 219, "passed": 219, "failed": 0, "duration": "403.89s"}
        test_url = os.environ.get("WEBHOOK_URL", "https://httpbin.org/post")
        print(f"Testing webhook dispatch to {test_url}...")
        success = send_webhook_notification(test_summary, test_url)
        print(f"Dispatch Result: {'SUCCESS' if success else 'FAILED'}")
