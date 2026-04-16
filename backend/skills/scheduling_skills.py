"""Post scheduling skill functions."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from utils.helpers import calculate_best_posting_time

logger = logging.getLogger(__name__)

_PLATFORM_BEST_HOURS: dict[str, list[int]] = {
    "instagram": [8, 11, 14, 17, 20],
    "facebook": [9, 12, 15, 18],
    "youtube": [12, 15, 18, 20],
}


async def get_optimal_posting_times(
    platform: str, audience_timezone: str = "UTC"
) -> dict[str, Any]:
    """Return the next 7 optimal posting slots for a platform."""
    best_hours = _PLATFORM_BEST_HOURS.get(platform.lower(), [9, 17])
    slots: list[dict] = []
    for day_offset in range(7):
        base = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        base += timedelta(days=day_offset)
        for hour in best_hours:
            dt = base.replace(hour=hour)
            slots.append(
                {
                    "datetime": dt.isoformat(),
                    "platform": platform,
                    "timezone": audience_timezone,
                    "day_of_week": dt.strftime("%A"),
                    "score": round(0.75 + (hour % 4) * 0.05, 2),
                }
            )
    return {
        "success": True,
        "platform": platform,
        "timezone": audience_timezone,
        "optimal_slots": slots,
    }


async def create_content_calendar(
    products: list[dict],
    frequency: int,
    platforms: list[str],
    weeks: int = 4,
) -> dict[str, Any]:
    """Build a structured content calendar and persist posts to the DB."""
    from models.mongodb_models import create_post

    calendar: list[dict] = []
    start_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    post_days = [i for i in range(7) if i % max(1, 7 // frequency) == 0]

    for week in range(weeks):
        for day_offset in post_days:
            for platform in platforms:
                best_hour = _PLATFORM_BEST_HOURS.get(platform, [12])[0]
                scheduled_dt = start_date + timedelta(weeks=week, days=day_offset, hours=best_hour)
                product = products[(week + day_offset) % len(products)] if products else {}
                post_doc = await create_post(
                    {
                        "platform": platform,
                        "content": f"[DRAFT] Promoting {product.get('name', 'product')}",
                        "hashtags": [],
                        "scheduled_time": scheduled_dt,
                        "status": "draft",
                        "product_id": str(product.get("_id", "")),
                    }
                )
                calendar.append(
                    {
                        "post_id": post_doc.get("_id"),
                        "platform": platform,
                        "scheduled_time": scheduled_dt.isoformat(),
                        "product": product.get("name", ""),
                    }
                )
    return {
        "success": True,
        "calendar": calendar,
        "total_posts": len(calendar),
        "weeks": weeks,
        "platforms": platforms,
    }


async def schedule_post_queue(posts: list[dict], schedule: list[datetime]) -> dict[str, Any]:
    """Assign scheduled times from the schedule list to posts and persist them."""
    from models.mongodb_models import create_post

    if len(posts) != len(schedule):
        return {"success": False, "error": "posts and schedule lists must have equal length"}
    saved: list[dict] = []
    for post, dt in zip(posts, schedule):
        post["scheduled_time"] = dt
        post.setdefault("status", "scheduled")
        doc = await create_post(post)
        saved.append({"post_id": doc.get("_id"), "scheduled_time": dt.isoformat()})
    return {"success": True, "scheduled_posts": saved}


async def reschedule_failed_post(post_id: str) -> dict[str, Any]:
    """Move a failed post to the next optimal slot."""
    from models.mongodb_models import get_post, update_post

    post = await get_post(post_id)
    if not post:
        return {"success": False, "error": "Post not found"}
    if post.get("status") != "failed":
        return {"success": False, "error": "Post is not in 'failed' state"}
    platform = post.get("platform", "instagram")
    new_time = calculate_best_posting_time("UTC", platform)
    updated = await update_post(post_id, {"scheduled_time": new_time, "status": "scheduled", "error_message": None})
    return {
        "success": True,
        "post_id": post_id,
        "new_scheduled_time": new_time.isoformat(),
        "updated": updated,
    }


async def get_upcoming_schedule(days_ahead: int = 7) -> dict[str, Any]:
    """Fetch all posts scheduled within the next N days."""
    from models.mongodb_models import get_scheduled_posts

    cutoff = datetime.now(timezone.utc) + timedelta(days=days_ahead)
    posts = await get_scheduled_posts(before=cutoff)
    return {
        "success": True,
        "upcoming_posts": posts,
        "count": len(posts),
        "days_ahead": days_ahead,
    }
