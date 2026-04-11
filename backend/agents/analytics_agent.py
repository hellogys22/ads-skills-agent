"""CrewAI Analytics Agent — tracks and reports engagement metrics."""

import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from crewai import Agent, Task

from models.mongodb_models import get_analytics, get_engagement_summary
from utils.claude_client import ClaudeClient
from utils.social_media_client import FacebookClient, InstagramClient

logger = logging.getLogger(__name__)


class AnalyticsAgent:
    """Aggregates performance data across platforms and generates reports."""

    def __init__(
        self,
        instagram_client: Optional[InstagramClient] = None,
        facebook_client: Optional[FacebookClient] = None,
    ) -> None:
        self.instagram = instagram_client
        self.facebook = facebook_client
        self.claude = ClaudeClient()
        self.agent = Agent(
            role="Social Media Analytics Specialist",
            goal=(
                "Deliver accurate, actionable performance insights that help the "
                "team make data-driven decisions and continuously improve ROI."
            ),
            backstory=(
                "You are an expert data analyst specialising in social media KPIs. "
                "You excel at pattern recognition, trend forecasting, and translating "
                "raw metrics into clear strategic recommendations."
            ),
            verbose=True,
            allow_delegation=False,
        )

    # ── Public methods ────────────────────────────────────────────────────────

    async def get_engagement_rate(
        self,
        platform: str,
        likes: int,
        comments: int,
        shares: int,
        followers: int,
    ) -> dict[str, Any]:
        """Calculate engagement rate using standard formula."""
        if followers == 0:
            return {"success": False, "error": "Followers count cannot be zero"}
        total_interactions = likes + comments + shares
        rate = (total_interactions / followers) * 100
        return {
            "success": True,
            "platform": platform,
            "engagement_rate": round(rate, 4),
            "total_interactions": total_interactions,
            "followers": followers,
        }

    async def track_reach(
        self, platform: str, start: datetime, end: datetime
    ) -> dict[str, Any]:
        """Retrieve reach metrics from the database for a date range."""
        try:
            records = await get_analytics(
                platform=platform,
                metric_type="reach",
                start=start,
                end=end,
                limit=200,
            )
            total_reach = sum(r.get("value", 0) for r in records)
            return {
                "success": True,
                "platform": platform,
                "total_reach": total_reach,
                "data_points": len(records),
                "period": {"start": start.isoformat(), "end": end.isoformat()},
            }
        except Exception as exc:
            logger.error("track_reach failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def analyze_performance(
        self, platform: str, days: int = 30
    ) -> dict[str, Any]:
        """Analyse overall performance for the past N days."""
        try:
            end = datetime.utcnow()
            start = end - timedelta(days=days)
            metrics = ["impressions", "reach", "engagement", "clicks"]
            results: dict[str, Any] = {"platform": platform, "period_days": days}
            for metric in metrics:
                records = await get_analytics(
                    platform=platform, metric_type=metric, start=start, end=end
                )
                results[metric] = {
                    "total": sum(r.get("value", 0) for r in records),
                    "count": len(records),
                }
            return {"success": True, **results}
        except Exception as exc:
            logger.error("analyze_performance failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def generate_report(
        self, campaign_id: str, platform: Optional[str] = None
    ) -> dict[str, Any]:
        """Generate an AI-narrated performance report for a campaign."""
        try:
            end = datetime.utcnow()
            start = end - timedelta(days=30)
            data = await get_analytics(platform=platform, start=start, end=end)
            summary_prompt = (
                f"Analyse these social media metrics and write a concise performance "
                f"report for campaign '{campaign_id}':\n{data}\n\n"
                f"Include: key wins, areas for improvement, and 3 actionable recommendations."
            )
            narrative = await self.claude.generate_content(summary_prompt, max_tokens=800)
            return {
                "success": True,
                "campaign_id": campaign_id,
                "report": narrative.get("content", ""),
                "raw_data_points": len(data),
            }
        except Exception as exc:
            logger.error("generate_report failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def get_daily_summary(self, platform: str) -> dict[str, Any]:
        """Return engagement summary for today."""
        try:
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            summary = await get_engagement_summary(platform, today, datetime.utcnow())
            return {"success": True, "platform": platform, "summary": summary, "date": today.date().isoformat()}
        except Exception as exc:
            logger.error("get_daily_summary failed: %s", exc)
            return {"success": False, "error": str(exc)}

    def get_crewai_agent(self) -> Agent:
        return self.agent

    def build_task(self, description: str, expected_output: str) -> Task:
        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.agent,
        )
