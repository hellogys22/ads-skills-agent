"""General utility functions."""

import hashlib
import re
import uuid
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo


# ── Hashtag helpers ───────────────────────────────────────────────────────────

def format_instagram_hashtags(hashtags: list[str]) -> str:
    """Return a space-separated string with # prefix for each hashtag."""
    cleaned = [re.sub(r"[^\w]", "", h.lstrip("#")) for h in hashtags if h.strip()]
    return " ".join(f"#{h}" for h in cleaned if h)


def sanitize_hashtag(tag: str) -> str:
    """Remove spaces and special characters from a single hashtag."""
    return re.sub(r"[^\w]", "", tag.strip().lstrip("#"))


# ── Posting time helpers ──────────────────────────────────────────────────────

_PLATFORM_BEST_HOURS: dict[str, list[int]] = {
    "instagram": [8, 11, 14, 17, 20],
    "facebook": [9, 12, 15, 18],
    "youtube": [12, 15, 18, 20],
}


def calculate_best_posting_time(tz_name: str, platform: str) -> datetime:
    """
    Return the next upcoming optimal posting time for the platform
    in the given IANA timezone string (e.g. 'America/New_York').
    """
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("UTC")

    now = datetime.now(tz)
    best_hours = _PLATFORM_BEST_HOURS.get(platform.lower(), [9, 17])
    for hour in sorted(best_hours):
        candidate = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if candidate > now:
            return candidate
    # All today's slots have passed — return first slot tomorrow
    import datetime as dt_module
    tomorrow = now + dt_module.timedelta(days=1)
    first_hour = sorted(best_hours)[0]
    return tomorrow.replace(hour=first_hour, minute=0, second=0, microsecond=0)


# ── Content helpers ───────────────────────────────────────────────────────────

def sanitize_content(text: str, max_length: int = 2200) -> str:
    """Strip control characters and truncate to platform limits."""
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    cleaned = cleaned.strip()
    return cleaned[:max_length] if len(cleaned) > max_length else cleaned


def generate_content_id() -> str:
    """Generate a deterministic short content ID."""
    return uuid.uuid4().hex[:12]


def truncate_text(text: str, max_chars: int, ellipsis: str = "…") -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - len(ellipsis)] + ellipsis


# ── Webhook helpers ───────────────────────────────────────────────────────────

def parse_webhook_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Normalise a raw webhook payload from Instagram or Facebook into a
    consistent internal format.
    """
    entry = payload.get("entry", [{}])[0]
    changes = entry.get("changes", [{}])[0]
    return {
        "platform": payload.get("object", "unknown"),
        "entry_id": entry.get("id"),
        "field": changes.get("field"),
        "value": changes.get("value", {}),
        "received_at": datetime.now(timezone.utc).isoformat(),
    }


def verify_facebook_signature(payload: bytes, signature_header: str, app_secret: str) -> bool:
    """Validate the X-Hub-Signature-256 header from Meta webhooks."""
    import hmac

    if not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(
        app_secret.encode("utf-8"), payload, hashlib.sha256  # type: ignore[attr-defined]
    ).hexdigest()
    provided = signature_header[len("sha256="):]
    return hmac.compare_digest(expected, provided)


# ── Pagination helpers ────────────────────────────────────────────────────────

def paginate(items: list, page: int, page_size: int) -> tuple[list, int]:
    """Return a page slice and total count."""
    total = len(items)
    start = (page - 1) * page_size
    return items[start: start + page_size], total
