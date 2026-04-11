"""CrewAI Content Creator agent powered by Anthropic Claude."""

import logging
from typing import Any

from crewai import Agent, Task

from utils.claude_client import ClaudeClient

logger = logging.getLogger(__name__)


class ContentCreatorAgent:
    """Generates compelling social-media content using Claude."""

    def __init__(self) -> None:
        self.claude = ClaudeClient()
        self.agent = Agent(
            role="Social Media Content Creator",
            goal=(
                "Produce viral, on-brand content that drives engagement and conversions "
                "across Instagram, Facebook, and YouTube."
            ),
            backstory=(
                "You are a creative digital marketing strategist with expertise in "
                "storytelling, persuasion psychology, and platform-specific content "
                "formats. You stay current with trending topics and can adapt any "
                "message to resonate with diverse audiences."
            ),
            verbose=True,
            allow_delegation=False,
        )

    # ── Public methods ────────────────────────────────────────────────────────

    async def generate_post(
        self,
        product_name: str,
        product_description: str,
        platform: str,
        tone: str = "engaging",
    ) -> dict[str, Any]:
        """Generate a platform-optimised social post."""
        try:
            prompt = (
                f"Create a {tone} {platform} post promoting '{product_name}'.\n"
                f"Product description: {product_description}\n\n"
                f"Requirements:\n"
                f"- Platform: {platform}\n"
                f"- Tone: {tone}\n"
                f"- Include a clear call-to-action\n"
                f"- Optimised caption length for {platform}\n"
                f"Return only the post content."
            )
            result = await self.claude.generate_content(prompt, max_tokens=500)
            return {"success": True, "content": result.get("content", ""), "platform": platform}
        except Exception as exc:
            logger.error("generate_post failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def create_caption(
        self,
        image_description: str,
        brand_voice: str = "friendly and professional",
        max_length: int = 2200,
    ) -> dict[str, Any]:
        """Create an Instagram/Facebook caption for a given image."""
        try:
            prompt = (
                f"Write a {brand_voice} social media caption for an image showing: "
                f"{image_description}.\n"
                f"Keep it under {max_length} characters. Include an engaging hook, "
                f"value statement, and call-to-action."
            )
            result = await self.claude.generate_content(prompt, max_tokens=600)
            return {"success": True, "caption": result.get("content", "")}
        except Exception as exc:
            logger.error("create_caption failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def suggest_hashtags(
        self, topic: str, niche: str, platform: str = "instagram", count: int = 25
    ) -> dict[str, Any]:
        """Suggest trending hashtags for a topic and niche."""
        try:
            prompt = (
                f"Suggest {count} trending {platform} hashtags for the topic '{topic}' "
                f"in the '{niche}' niche. Mix high-volume, medium-volume, and niche-specific "
                f"hashtags. Return only hashtags as a comma-separated list, no # symbols."
            )
            result = await self.claude.generate_content(prompt, max_tokens=400)
            raw = result.get("content", "")
            hashtags = [h.strip().lstrip("#") for h in raw.split(",") if h.strip()]
            return {"success": True, "hashtags": hashtags[:count]}
        except Exception as exc:
            logger.error("suggest_hashtags failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def generate_video_script(
        self,
        topic: str,
        duration_minutes: int = 5,
        style: str = "educational",
    ) -> dict[str, Any]:
        """Create a YouTube video script."""
        try:
            prompt = (
                f"Write a {duration_minutes}-minute {style} YouTube video script about '{topic}'.\n"
                f"Structure:\n"
                f"1. Hook (first 15 seconds)\n"
                f"2. Introduction\n"
                f"3. Main content (3-5 key points)\n"
                f"4. Call-to-action\n"
                f"5. Outro\n\n"
                f"Include timestamps for each section."
            )
            result = await self.claude.generate_content(prompt, max_tokens=2000)
            return {"success": True, "script": result.get("content", ""), "topic": topic}
        except Exception as exc:
            logger.error("generate_video_script failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def analyze_trending_topics(self, niche: str, count: int = 10) -> dict[str, Any]:
        """Identify trending topics for content ideas in a given niche."""
        try:
            prompt = (
                f"List {count} currently trending topics and content ideas in the '{niche}' niche "
                f"that are likely to drive high engagement on social media. For each, provide:\n"
                f"- Topic title\n"
                f"- Why it's trending\n"
                f"- Suggested content angle\n"
                f"Format as a numbered list."
            )
            result = await self.claude.generate_content(prompt, max_tokens=1500)
            return {"success": True, "topics": result.get("content", ""), "niche": niche}
        except Exception as exc:
            logger.error("analyze_trending_topics failed: %s", exc)
            return {"success": False, "error": str(exc)}

    def get_crewai_agent(self) -> Agent:
        return self.agent

    def build_task(self, description: str, expected_output: str) -> Task:
        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.agent,
        )
