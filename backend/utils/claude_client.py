"""Anthropic Claude API wrapper with async support."""

import logging
from typing import Any

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ClaudeClient:
    """Async-friendly wrapper around the Anthropic Messages API."""

    MODEL = "claude-3-5-sonnet-20241022"

    def __init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    @retry(wait=wait_exponential(multiplier=1, min=2, max=30), stop=stop_after_attempt(3))
    async def generate_content(
        self,
        prompt: str,
        max_tokens: int = 1024,
        system: str = "You are a helpful digital marketing assistant.",
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """Send a prompt to Claude and return the text response."""
        try:
            response = self._client.messages.create(
                model=self.MODEL,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.content[0].text if response.content else ""
            return {
                "success": True,
                "content": content,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }
        except anthropic.APIError as exc:
            logger.error("Claude API error: %s", exc)
            return {"success": False, "content": "", "error": str(exc)}

    async def analyze_trends(self, data: dict | list) -> dict[str, Any]:
        """Analyse structured data and extract trend insights."""
        prompt = (
            f"Analyse the following social media data and identify key trends, "
            f"patterns, and actionable insights:\n\n{data}\n\n"
            f"Structure your response with: Key Trends, Opportunities, Risks, Recommendations."
        )
        return await self.generate_content(prompt, max_tokens=1200)

    async def optimize_hashtags(self, content: str, platform: str) -> dict[str, Any]:
        """Return a refined set of hashtags for the given content."""
        prompt = (
            f"Optimise hashtag strategy for this {platform} content:\n{content}\n\n"
            f"Return 20-30 hashtags mixing: brand, niche, trending, and community tags. "
            f"Format: comma-separated list, no # symbols."
        )
        return await self.generate_content(prompt, max_tokens=300)

    async def predict_engagement(self, post_data: dict) -> dict[str, Any]:
        """Predict engagement potential for a post and explain the reasoning."""
        prompt = (
            f"Predict the engagement potential (low/medium/high) for this social media post "
            f"and explain why:\n\n{post_data}\n\n"
            f"Provide: Engagement Score (1-10), Predicted Reach, Key Strength, "
            f"Main Risk, 3 Improvement Tips."
        )
        return await self.generate_content(prompt, max_tokens=600)

    async def generate_strategy(self, campaign_brief: dict) -> dict[str, Any]:
        """Generate a comprehensive marketing strategy from a campaign brief."""
        prompt = (
            f"Create a comprehensive digital marketing strategy for:\n{campaign_brief}\n\n"
            f"Include: Positioning, Messaging Framework, Channel Mix, "
            f"Content Pillars, Success Metrics, Timeline."
        )
        return await self.generate_content(prompt, max_tokens=2500)
