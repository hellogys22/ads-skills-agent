"""Celery task definitions for background job processing."""

import logging
from datetime import datetime, timedelta

from celery import Celery

from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

celery_app = Celery(
    "ads_agent",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


# ── Tasks ─────────────────────────────────────────────────────────────────────

@celery_app.task(bind=True, name="tasks.check_engagement", max_retries=3)
def check_engagement_task(self):
    """Collect engagement metrics from all connected platforms."""
    import asyncio

    async def _run():
        from agents.analytics_agent import AnalyticsAgent

        agent = AnalyticsAgent()
        results = {}
        for platform in ["instagram", "facebook"]:
            results[platform] = await agent.get_daily_summary(platform)
        return results

    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(_run())
        loop.close()
        return {"success": True, "results": result}
    except Exception as exc:
        logger.error("check_engagement_task failed: %s", exc)
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, name="tasks.aggregate_analytics", max_retries=3)
def aggregate_analytics_task(self, days: int = 1):
    """Aggregate analytics data for the past N days."""
    import asyncio

    async def _run():
        from skills.analytics_skills import aggregate_daily_stats

        end = datetime.utcnow()
        start = end - timedelta(days=days)
        results = {}
        for platform in ["instagram", "facebook", "youtube"]:
            results[platform] = await aggregate_daily_stats(platform, (start, end))
        return results

    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(_run())
        loop.close()
        return {"success": True, "results": result}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=120)


@celery_app.task(bind=True, name="tasks.analyze_trends", max_retries=3)
def analyze_trends_task(self, niche: str = "digital marketing"):
    """Run trend analysis for a given niche."""
    import asyncio

    async def _run():
        from agents.strategy_agent import StrategyAgent

        agent = StrategyAgent()
        return await agent.analyze_trends(niche, ["instagram", "facebook", "youtube"])

    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(_run())
        loop.close()
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=120)


@celery_app.task(bind=True, name="tasks.auto_schedule_posts", max_retries=3)
def auto_schedule_posts_task(self):
    """Publish all posts that are due for scheduling."""
    import asyncio

    async def _run():
        from models.mongodb_models import get_scheduled_posts, update_post
        from skills.social_media_skills import post_to_instagram

        posts = await get_scheduled_posts(before=datetime.utcnow())
        published = 0
        for post in posts:
            post_id = str(post.get("_id", ""))
            if post.get("platform") == "instagram":
                result = await post_to_instagram(
                    image_url=post.get("image_url", ""),
                    caption=post.get("content", ""),
                    hashtags=post.get("hashtags", []),
                )
                status = "published" if result.get("success") else "failed"
                await update_post(
                    post_id,
                    {"status": status, "published_at": datetime.utcnow()},
                )
                if result.get("success"):
                    published += 1
        return {"published": published, "total_due": len(posts)}

    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(_run())
        loop.close()
        return {"success": True, **result}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)


@celery_app.task(bind=True, name="tasks.generate_recommendations", max_retries=2)
def generate_recommendations_task(self, niche: str = "digital marketing"):
    """Generate AI content recommendations for a niche."""
    import asyncio

    async def _run():
        from agents.content_creator import ContentCreatorAgent

        agent = ContentCreatorAgent()
        return await agent.analyze_trending_topics(niche, count=10)

    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(_run())
        loop.close()
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=120)


@celery_app.task(bind=True, name="tasks.send_webhook_notifications", max_retries=3)
def send_webhook_notifications_task(self, event_type: str, payload: dict):
    """Fan-out webhook event notifications to registered endpoints."""
    import asyncio

    import httpx

    async def _run():
        # Placeholder: in production, fetch registered notification URLs from DB
        endpoints: list[str] = []
        results = []
        async with httpx.AsyncClient(timeout=10) as client:
            for url in endpoints:
                try:
                    resp = await client.post(url, json={"event": event_type, "data": payload})
                    results.append({"url": url, "status": resp.status_code})
                except Exception as e:
                    results.append({"url": url, "error": str(e)})
        return results

    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(_run())
        loop.close()
        return {"success": True, "notifications": result}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)
