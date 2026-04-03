"""Datetime helpers for UTC handling."""

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return a naive UTC datetime for DB fields that store UTC values."""
    return datetime.now(UTC).replace(tzinfo=None)
