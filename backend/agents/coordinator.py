"""AutoGen multi-agent coordinator that orchestrates all CrewAI agents."""

import logging
from typing import Any, Optional

from crewai import Crew, Process

from agents.ad_manager import AdManagerAgent
from agents.analytics_agent import AnalyticsAgent
from agents.content_creator import ContentCreatorAgent
from agents.instagram_manager import InstagramManagerAgent
from agents.strategy_agent import StrategyAgent

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """
    Orchestrates all specialist agents via CrewAI Crews.

    Each public method builds a purpose-specific Crew from the relevant
    subset of agents and executes it with appropriate tasks.
    """

    def __init__(self) -> None:
        self.content_creator = ContentCreatorAgent()
        self.instagram_manager = InstagramManagerAgent()
        self.analytics = AnalyticsAgent()
        self.strategy = StrategyAgent()
        self.ad_manager = AdManagerAgent()

    # ── Status ────────────────────────────────────────────────────────────────

    def get_agent_status(self) -> dict[str, str]:
        return {
            "content_creator": "active",
            "instagram_manager": "active",
            "analytics": "active",
            "strategy": "active",
            "ad_manager": "active",
        }

    # ── Task execution ────────────────────────────────────────────────────────

    async def execute_task(self, task_type: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Route a task to the appropriate agent or crew."""
        dispatch: dict[str, Any] = {
            "generate_content": self._run_content_generation,
            "run_campaign": self._run_full_campaign,
            "analyze_platform": self._run_analytics,
            "optimize_ads": self._run_ad_optimization,
            "plan_strategy": self._run_strategy_planning,
            "post_instagram": self._run_instagram_post,
        }
        handler = dispatch.get(task_type)
        if handler is None:
            return {"success": False, "error": f"Unknown task type: {task_type}"}
        try:
            return await handler(parameters)
        except Exception as exc:
            logger.error("execute_task(%s) failed: %s", task_type, exc)
            return {"success": False, "error": str(exc)}

    async def run_campaign(self, campaign_data: dict[str, Any]) -> dict[str, Any]:
        """Run a full marketing campaign using all agents."""
        return await self._run_full_campaign(campaign_data)

    # ── Private crew runners ──────────────────────────────────────────────────

    async def _run_content_generation(self, params: dict) -> dict[str, Any]:
        product = params.get("product", {})
        platform = params.get("platform", "instagram")
        tone = params.get("tone", "engaging")
        result = await self.content_creator.generate_post(
            product_name=product.get("name", "Product"),
            product_description=product.get("description", ""),
            platform=platform,
            tone=tone,
        )
        hashtag_result = await self.content_creator.suggest_hashtags(
            topic=product.get("name", ""),
            niche=product.get("niche", "general"),
            platform=platform,
        )
        return {
            "success": True,
            "content": result.get("content", ""),
            "hashtags": hashtag_result.get("hashtags", []),
            "platform": platform,
        }

    async def _run_full_campaign(self, params: dict) -> dict[str, Any]:
        campaign_name = params.get("name", "New Campaign")
        budget = params.get("budget", 0.0)
        platforms = params.get("platforms", ["instagram"])
        goals = params.get("goals", ["engagement", "reach"])
        target_audience = params.get("target_audience", {})
        products = params.get("products", [])

        strategy_task = self.strategy.build_task(
            description=(
                f"Plan a {len(platforms)}-platform marketing campaign named '{campaign_name}' "
                f"with a ${budget} budget targeting {target_audience}."
            ),
            expected_output="Detailed campaign plan with platform strategy, content pillars, and KPIs.",
        )
        content_task = self.content_creator.build_task(
            description=(
                f"Create compelling content for the '{campaign_name}' campaign "
                f"across {', '.join(platforms)}."
            ),
            expected_output="A set of platform-specific posts with captions and hashtags.",
        )
        crew = Crew(
            agents=[self.strategy.get_crewai_agent(), self.content_creator.get_crewai_agent()],
            tasks=[strategy_task, content_task],
            process=Process.sequential,
            verbose=True,
        )
        crew_result = crew.kickoff()
        return {
            "success": True,
            "campaign_name": campaign_name,
            "crew_output": str(crew_result),
        }

    async def _run_analytics(self, params: dict) -> dict[str, Any]:
        platform = params.get("platform", "instagram")
        days = params.get("days", 30)
        return await self.analytics.analyze_performance(platform=platform, days=days)

    async def _run_ad_optimization(self, params: dict) -> dict[str, Any]:
        budget = params.get("budget", 0.0)
        product_ids = params.get("product_ids")
        return await self.ad_manager.optimize_spend(budget=budget, products=product_ids)

    async def _run_strategy_planning(self, params: dict) -> dict[str, Any]:
        niche = params.get("niche", "general")
        platforms = params.get("platforms", ["instagram"])
        return await self.strategy.analyze_trends(niche=niche, platforms=platforms)

    async def _run_instagram_post(self, params: dict) -> dict[str, Any]:
        image_url = params.get("image_url", "")
        caption = params.get("caption", "")
        hashtags = params.get("hashtags", [])
        return await self.instagram_manager.schedule_post(
            image_url=image_url,
            caption=caption,
            hashtags=hashtags,
        )
