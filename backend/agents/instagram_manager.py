"""CrewAI Instagram Manager agent."""

import logging
from typing import Any, Optional

from crewai import Agent, Task

from config import get_settings
from utils.claude_client import ClaudeClient
from utils.social_media_client import InstagramClient

logger = logging.getLogger(__name__)
settings = get_settings()


class InstagramManagerAgent:
    """Manages all Instagram-related operations via the Graph API."""

    def __init__(self) -> None:
        self.client = InstagramClient(
            app_id=settings.instagram_app_id,
            app_secret=settings.instagram_app_secret,
            access_token=settings.instagram_access_token,
        )
        self.claude = ClaudeClient()
        self.agent = Agent(
            role="Instagram Marketing Manager",
            goal=(
                "Maximize Instagram engagement and follower growth by scheduling "
                "optimised posts, analysing engagement metrics, and managing "
                "community interactions."
            ),
            backstory=(
                "You are a seasoned Instagram marketing expert with deep knowledge "
                "of the Instagram Graph API, content trends, and audience psychology. "
                "You use data-driven decisions to grow brand presence organically."
            ),
            verbose=True,
            allow_delegation=False,
        )

    # ── Public methods ────────────────────────────────────────────────────────

    async def schedule_post(
        self,
        image_url: str,
        caption: str,
        hashtags: list[str],
        scheduled_time: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a media container and, optionally, publish or queue it."""
        try:
            hashtag_str = " ".join(f"#{h.lstrip('#')}" for h in hashtags)
            full_caption = f"{caption}\n\n{hashtag_str}"
            result = await self.client.create_media_container(
                image_url=image_url,
                caption=full_caption,
            )
            logger.info("Instagram media container created: %s", result.get("id"))
            return {"success": True, "container_id": result.get("id"), "caption": full_caption}
        except Exception as exc:
            logger.error("schedule_post failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def publish_post(self, container_id: str) -> dict[str, Any]:
        """Publish a previously created media container."""
        try:
            result = await self.client.publish_media(container_id)
            return {"success": True, "post_id": result.get("id")}
        except Exception as exc:
            logger.error("publish_post failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def get_analytics(self, media_id: str) -> dict[str, Any]:
        """Fetch insights for a specific media post."""
        try:
            metrics = ["impressions", "reach", "likes", "comments", "shares", "saved"]
            insights = await self.client.get_media_insights(media_id, metrics)
            return {"success": True, "insights": insights}
        except Exception as exc:
            logger.error("get_analytics failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def optimize_hashtags(self, content: str, niche: str, count: int = 30) -> list[str]:
        """Use Claude to suggest optimised hashtags for a post."""
        try:
            prompt = (
                f"Suggest {count} highly relevant and trending Instagram hashtags for the "
                f"following content in the '{niche}' niche. Return only the hashtags as a "
                f"comma-separated list without the # symbol.\n\nContent: {content}"
            )
            response = await self.claude.generate_content(prompt, max_tokens=300)
            raw = response.get("content", "")
            hashtags = [h.strip().lstrip("#") for h in raw.split(",") if h.strip()]
            return hashtags[:count]
        except Exception as exc:
            logger.error("optimize_hashtags failed: %s", exc)
            return []

    async def respond_to_comments(self, media_id: str) -> dict[str, Any]:
        """Fetch recent comments and generate AI-driven replies."""
        try:
            comments = await self.client.get_comments(media_id)
            replies: list[dict] = []
            for comment in comments.get("data", [])[:10]:
                prompt = (
                    f"Write a friendly, on-brand reply to this Instagram comment: "
                    f"'{comment.get('text', '')}'. Keep it under 100 characters."
                )
                reply_text = (await self.claude.generate_content(prompt, max_tokens=80)).get("content", "")
                replies.append({"comment_id": comment.get("id"), "reply": reply_text})
            return {"success": True, "replies": replies}
        except Exception as exc:
            logger.error("respond_to_comments failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def get_account_insights(self, period: str = "day") -> dict[str, Any]:
        """Return account-level insights (followers, impressions, reach)."""
        try:
            metrics = ["follower_count", "impressions", "reach", "profile_views"]
            insights = await self.client.get_account_insights(metrics, period)
            return {"success": True, "insights": insights}
        except Exception as exc:
            logger.error("get_account_insights failed: %s", exc)
            return {"success": False, "error": str(exc)}

    def get_crewai_agent(self) -> Agent:
        return self.agent

    def build_task(self, description: str, expected_output: str) -> Task:
        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.agent,
        )
