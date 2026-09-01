"""Money parsing/formatting helpers.

Kirki stores prices as integer minor units (cents) in `invoiced_*` and
`base_*` columns, but the UI renders localized strings (e.g. "$49.99").
Tests should parse rendered amounts to Decimal cents and compare against
expected integer-cent values from the REST API.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

_MONEY_RE = re.compile(r"([^\d\-+.,]*)\s*([\-+]?\d[\d,]*\.?\d*)\s*([^\d]*)")


def parse_money_to_cents(text: str | int) -> int:
    """Parse a rendered money string or integer into integer cents.

    Handles: "$49.99", "49.99", "USD 49.99", "€49,99", "-$5.00", 4999.
    Raises ValueError if no numeric amount can be extracted.
    """
    if isinstance(text, int):
        return text
    if text is None:
        raise ValueError("cannot parse None as money")
    cleaned = str(text).strip().replace("\u00a0", " ")
    match = _MONEY_RE.search(cleaned)
    if not match:
        raise ValueError(f"no numeric amount found in {text!r}")
    raw = match.group(2).replace(",", "")
    try:
        amount = Decimal(raw)
    except InvalidOperation as exc:  # pragma: no cover - defensive
        raise ValueError(f"cannot parse amount {raw!r} from {text!r}") from exc
    return int((amount * 100).quantize(Decimal("1")))


def cents_to_decimal(cents: int) -> Decimal:
    """Convert integer cents to a Decimal (e.g. 4999 -> Decimal('49.99'))."""
    return (Decimal(cents) / 100).quantize(Decimal("0.01"))


def format_cents(cents: int, symbol: str = "$") -> str:
    """Render cents as a display string for expected-value comparison."""
    return f"{symbol}{cents_to_decimal(cents):.2f}"


def assert_money_equal(expected_cents: int, rendered_text: str | int, symbol: str = "$"):
    """Assert a rendered money string or integer equals an expected integer-cent value."""
    actual = parse_money_to_cents(rendered_text)
    assert actual == expected_cents, (
        f"money mismatch: expected {expected_cents} cents "
        f"({format_cents(expected_cents, symbol)}), "
        f"got {actual} cents from {rendered_text!r}"
    )

