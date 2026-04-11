"""Analytics skill functions for metrics collection and reporting."""

import logging
from datetime import datetime, timedelta
from typing import Any

from models.mongodb_models import get_analytics, get_performance_by_campaign

logger = logging.getLogger(__name__)


async def get_instagram_insights(media_id: str, metrics: list[str]) -> dict[str, Any]:
    """Fetch Instagram media insights via the stored client (placeholder for DI)."""
    from config import get_settings
    from utils.social_media_client import InstagramClient

    settings = get_settings()
    client = InstagramClient(
        app_id=settings.instagram_app_id,
        app_secret=settings.instagram_app_secret,
        access_token=settings.instagram_access_token,
    )
    try:
        result = await client.get_media_insights(media_id, metrics)
        await client.aclose()
        return {"success": True, "insights": result}
    except Exception as exc:
        logger.error("get_instagram_insights failed: %s", exc)
        return {"success": False, "error": str(exc)}


def calculate_engagement_rate(
    likes: int, comments: int, shares: int, followers: int
) -> dict[str, Any]:
    """Return standard engagement rate and component breakdown."""
    if followers <= 0:
        return {"success": False, "error": "followers must be > 0"}
    total = likes + comments + shares
    rate = (total / followers) * 100
    return {
        "success": True,
        "engagement_rate": round(rate, 4),
        "total_interactions": total,
        "breakdown": {"likes": likes, "comments": comments, "shares": shares},
        "followers": followers,
    }


async def aggregate_daily_stats(
    platform: str, date_range: tuple[datetime, datetime]
) -> dict[str, Any]:
    """Aggregate all metrics for a platform within a date range."""
    start, end = date_range
    metric_types = ["impressions", "reach", "engagement", "clicks", "followers"]
    aggregated: dict[str, float] = {}
    for metric in metric_types:
        records = await get_analytics(
            platform=platform, metric_type=metric, start=start, end=end, limit=500
        )
        aggregated[metric] = sum(r.get("value", 0) for r in records)
    return {
        "success": True,
        "platform": platform,
        "period": {"start": start.isoformat(), "end": end.isoformat()},
        "metrics": aggregated,
    }


async def compare_platform_performance(
    platforms: list[str], metric: str, days: int = 30
) -> dict[str, Any]:
    """Compare a specific metric across multiple platforms."""
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    comparison: dict[str, float] = {}
    for platform in platforms:
        records = await get_analytics(
            platform=platform, metric_type=metric, start=start, end=end, limit=200
        )
        comparison[platform] = sum(r.get("value", 0) for r in records)
    best = max(comparison, key=comparison.get) if comparison else None
    return {
        "success": True,
        "metric": metric,
        "period_days": days,
        "comparison": comparison,
        "best_platform": best,
    }


async def generate_performance_report(campaign_id: str) -> dict[str, Any]:
    """Compile a performance summary for a campaign."""
    from utils.claude_client import ClaudeClient

    records = await get_performance_by_campaign(campaign_id)
    if not records:
        return {"success": False, "error": "No performance data found for this campaign"}
    total_impressions = sum(r.get("impressions", 0) for r in records)
    total_clicks = sum(r.get("clicks", 0) for r in records)
    total_conversions = sum(r.get("conversions", 0) for r in records)
    total_spend = sum(r.get("spend", 0) for r in records)
    ctr = (total_clicks / total_impressions * 100) if total_impressions else 0
    cpc = (total_spend / total_clicks) if total_clicks else 0
    claude = ClaudeClient()
    summary = await claude.generate_content(
        f"Write a concise performance summary for campaign '{campaign_id}' with these stats: "
        f"Impressions: {total_impressions}, Clicks: {total_clicks}, "
        f"Conversions: {total_conversions}, CTR: {ctr:.2f}%, CPC: ${cpc:.2f}, Spend: ${total_spend:.2f}.",
        max_tokens=400,
    )
    return {
        "success": True,
        "campaign_id": campaign_id,
        "impressions": total_impressions,
        "clicks": total_clicks,
        "conversions": total_conversions,
        "ctr": round(ctr, 4),
        "cpc": round(cpc, 4),
        "total_spend": total_spend,
        "narrative": summary.get("content", ""),
    }
