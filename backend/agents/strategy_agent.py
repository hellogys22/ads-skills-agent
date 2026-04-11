"""CrewAI Strategy Agent — campaign planning and content calendar."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from crewai import Agent, Task

from utils.claude_client import ClaudeClient

logger = logging.getLogger(__name__)


class StrategyAgent:
    """Creates content calendars, plans campaigns, and recommends posting times."""

    # Best posting hours per platform (UTC, as a starting baseline)
    _PLATFORM_BEST_HOURS: dict[str, list[int]] = {
        "instagram": [8, 12, 17, 19],
        "facebook": [9, 13, 16, 19],
        "youtube": [14, 17, 20],
    }

    def __init__(self) -> None:
        self.claude = ClaudeClient()
        self.agent = Agent(
            role="Digital Marketing Strategist",
            goal=(
                "Develop data-driven marketing strategies and content calendars that "
                "maximise reach, engagement, and conversion across all platforms."
            ),
            backstory=(
                "You are a senior digital marketing strategist with 10+ years of "
                "experience running multi-platform campaigns. You blend creativity "
                "with analytics to craft strategies that consistently outperform KPIs."
            ),
            verbose=True,
            allow_delegation=True,
        )

    # ── Public methods ────────────────────────────────────────────────────────

    async def create_content_calendar(
        self,
        products: list[dict],
        frequency_per_week: int,
        platforms: list[str],
        weeks: int = 4,
    ) -> dict[str, Any]:
        """Generate a multi-week content calendar for the given products."""
        try:
            product_list = "\n".join(
                f"- {p.get('name', 'Unknown')}: {p.get('description', '')}" for p in products
            )
            prompt = (
                f"Create a {weeks}-week social media content calendar posting "
                f"{frequency_per_week} times per week on {', '.join(platforms)}.\n\n"
                f"Products to promote:\n{product_list}\n\n"
                f"For each post include:\n"
                f"- Day and time\n"
                f"- Platform\n"
                f"- Content type (image/video/story/reel)\n"
                f"- Topic/theme\n"
                f"- Product featured\n"
                f"Format as a structured table."
            )
            result = await self.claude.generate_content(prompt, max_tokens=2500)
            return {
                "success": True,
                "calendar": result.get("content", ""),
                "weeks": weeks,
                "platforms": platforms,
            }
        except Exception as exc:
            logger.error("create_content_calendar failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def plan_campaign(
        self,
        campaign_name: str,
        budget: float,
        target_audience: dict,
        goals: list[str],
        duration_days: int = 30,
    ) -> dict[str, Any]:
        """Create a comprehensive campaign plan."""
        try:
            prompt = (
                f"Create a detailed {duration_days}-day digital marketing campaign plan:\n\n"
                f"Campaign: {campaign_name}\n"
                f"Budget: ${budget:,.2f}\n"
                f"Target Audience: {target_audience}\n"
                f"Goals: {', '.join(goals)}\n\n"
                f"Include:\n"
                f"1. Campaign strategy overview\n"
                f"2. Platform allocation and budget breakdown\n"
                f"3. Content pillars (at least 4)\n"
                f"4. KPIs and success metrics\n"
                f"5. Weekly milestones\n"
                f"6. Risk mitigation strategies"
            )
            result = await self.claude.generate_content(prompt, max_tokens=3000)
            return {
                "success": True,
                "plan": result.get("content", ""),
                "campaign_name": campaign_name,
                "duration_days": duration_days,
            }
        except Exception as exc:
            logger.error("plan_campaign failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def recommend_posting_times(
        self, platform: str, audience_timezone: str = "UTC"
    ) -> dict[str, Any]:
        """Recommend optimal posting times for a platform."""
        base_hours = self._PLATFORM_BEST_HOURS.get(platform.lower(), [9, 12, 17, 20])
        slots = []
        for day_offset in range(7):
            day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            day += timedelta(days=day_offset)
            for hour in base_hours:
                slots.append(
                    {
                        "datetime": day.replace(hour=hour).isoformat(),
                        "platform": platform,
                        "timezone": audience_timezone,
                        "score": 0.8 + (hour % 3) * 0.05,
                    }
                )
        return {"success": True, "platform": platform, "recommended_slots": slots}

    async def analyze_trends(self, niche: str, platforms: list[str]) -> dict[str, Any]:
        """Analyse current social media trends for a niche."""
        try:
            prompt = (
                f"Analyse current social media trends for the '{niche}' niche on "
                f"{', '.join(platforms)}. Provide:\n"
                f"1. Top 5 trending content formats\n"
                f"2. Popular hashtags and keywords\n"
                f"3. Emerging topics to capitalise on\n"
                f"4. Competitor content strategies\n"
                f"5. Recommended content mix (percentages per type)"
            )
            result = await self.claude.generate_content(prompt, max_tokens=1500)
            return {
                "success": True,
                "trends": result.get("content", ""),
                "niche": niche,
                "platforms": platforms,
            }
        except Exception as exc:
            logger.error("analyze_trends failed: %s", exc)
            return {"success": False, "error": str(exc)}

    def get_crewai_agent(self) -> Agent:
        return self.agent

    def build_task(self, description: str, expected_output: str) -> Task:
        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.agent,
        )
