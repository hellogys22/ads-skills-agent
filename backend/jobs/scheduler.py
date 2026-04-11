"""APScheduler background job definitions."""

import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)
_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone="UTC")
    return _scheduler


# ── Job functions ─────────────────────────────────────────────────────────────

async def _check_engagement_job() -> None:
    """Hourly: pull fresh engagement data for all active posts."""
    try:
        logger.info("[scheduler] Running hourly engagement check")
        from agents.analytics_agent import AnalyticsAgent

        agent = AnalyticsAgent()
        for platform in ["instagram", "facebook"]:
            await agent.get_daily_summary(platform)
    except Exception as exc:
        logger.error("[scheduler] check_engagement_job failed: %s", exc)


async def _daily_analytics_aggregation_job() -> None:
    """Daily at midnight UTC: aggregate analytics for the previous day."""
    try:
        logger.info("[scheduler] Running daily analytics aggregation")
        from datetime import timedelta

        from skills.analytics_skills import aggregate_daily_stats

        yesterday_end = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = yesterday_end - timedelta(days=1)
        for platform in ["instagram", "facebook", "youtube"]:
            await aggregate_daily_stats(platform, (yesterday_start, yesterday_end))
    except Exception as exc:
        logger.error("[scheduler] daily_analytics_aggregation_job failed: %s", exc)


async def _trend_analysis_job() -> None:
    """Daily at 6 AM UTC: refresh trend analysis for configured niches."""
    try:
        logger.info("[scheduler] Running trend analysis update")
        from agents.strategy_agent import StrategyAgent

        agent = StrategyAgent()
        await agent.analyze_trends("digital marketing", ["instagram", "facebook"])
    except Exception as exc:
        logger.error("[scheduler] trend_analysis_job failed: %s", exc)


async def _auto_post_scheduling_job() -> None:
    """Every 15 minutes: publish scheduled posts that are due."""
    try:
        from models.mongodb_models import get_scheduled_posts, update_post
        from skills.social_media_skills import post_to_instagram

        due_posts = await get_scheduled_posts(before=datetime.utcnow())
        for post in due_posts:
            post_id = str(post.get("_id", ""))
            platform = post.get("platform", "")
            try:
                if platform == "instagram":
                    result = await post_to_instagram(
                        image_url=post.get("image_url", ""),
                        caption=post.get("content", ""),
                        hashtags=post.get("hashtags", []),
                    )
                    status = "published" if result.get("success") else "failed"
                    error = None if result.get("success") else result.get("error")
                    await update_post(
                        post_id,
                        {
                            "status": status,
                            "published_at": datetime.utcnow(),
                            "external_post_id": result.get("post_id"),
                            "error_message": error,
                        },
                    )
            except Exception as post_exc:
                logger.error("auto_post failed for %s: %s", post_id, post_exc)
                await update_post(post_id, {"status": "failed", "error_message": str(post_exc)})
    except Exception as exc:
        logger.error("[scheduler] auto_post_scheduling_job failed: %s", exc)


async def _content_recommendation_job() -> None:
    """Daily at 8 AM UTC: generate new content recommendations."""
    try:
        logger.info("[scheduler] Generating content recommendations")
        from agents.content_creator import ContentCreatorAgent

        agent = ContentCreatorAgent()
        await agent.analyze_trending_topics("digital marketing", count=5)
    except Exception as exc:
        logger.error("[scheduler] content_recommendation_job failed: %s", exc)


# ── Setup ─────────────────────────────────────────────────────────────────────

def setup_scheduler() -> AsyncIOScheduler:
    """Configure and return the scheduler with all jobs registered."""
    scheduler = get_scheduler()

    scheduler.add_job(
        _check_engagement_job,
        trigger=IntervalTrigger(hours=1),
        id="check_engagement",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.add_job(
        _daily_analytics_aggregation_job,
        trigger=CronTrigger(hour=0, minute=5),
        id="daily_analytics",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.add_job(
        _trend_analysis_job,
        trigger=CronTrigger(hour=6, minute=0),
        id="trend_analysis",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.add_job(
        _auto_post_scheduling_job,
        trigger=IntervalTrigger(minutes=15),
        id="auto_post",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.add_job(
        _content_recommendation_job,
        trigger=CronTrigger(hour=8, minute=0),
        id="content_recommendations",
        replace_existing=True,
        max_instances=1,
    )
    logger.info("APScheduler configured with %d jobs", len(scheduler.get_jobs()))
    return scheduler
