"""Content generation skill functions backed by Claude."""

import logging
from typing import Any

from utils.claude_client import ClaudeClient

logger = logging.getLogger(__name__)
_claude = ClaudeClient()


async def generate_instagram_post(
    product: dict[str, Any], tone: str = "engaging", hashtag_count: int = 25
) -> dict[str, Any]:
    """Generate a complete Instagram post including caption and hashtags."""
    prompt = (
        f"Create an {tone} Instagram post promoting '{product.get('name', 'Product')}'.\n"
        f"Description: {product.get('description', '')}\n"
        f"Price: {product.get('price', 'N/A')}\n\n"
        f"Requirements:\n"
        f"- Compelling hook in first line\n"
        f"- Benefit-focused body (3-4 sentences)\n"
        f"- Clear CTA\n"
        f"- {hashtag_count} relevant hashtags at the end\n"
        f"- Maximum 2200 characters total"
    )
    result = await _claude.generate_content(prompt, max_tokens=700)
    return {"success": True, "post": result.get("content", ""), "platform": "instagram"}


async def generate_facebook_post(
    product: dict[str, Any], audience: str = "general"
) -> dict[str, Any]:
    """Generate a Facebook post tailored to a specific audience."""
    prompt = (
        f"Create a Facebook post for the '{audience}' audience promoting "
        f"'{product.get('name', 'Product')}'.\n"
        f"Description: {product.get('description', '')}\n\n"
        f"Facebook-specific requirements:\n"
        f"- Conversational tone\n"
        f"- Ask a question to boost comments\n"
        f"- Include a link placeholder [LINK]\n"
        f"- 3-5 relevant hashtags\n"
        f"- Under 500 characters for optimal reach"
    )
    result = await _claude.generate_content(prompt, max_tokens=400)
    return {"success": True, "post": result.get("content", ""), "platform": "facebook", "audience": audience}


async def create_youtube_description(
    video_topic: str, keywords: list[str], channel_name: str = ""
) -> dict[str, Any]:
    """Create an SEO-optimised YouTube video description."""
    keyword_str = ", ".join(keywords)
    prompt = (
        f"Write an SEO-optimised YouTube video description for a video about '{video_topic}'.\n"
        f"Target keywords: {keyword_str}\n"
        f"Channel: {channel_name or 'Unknown'}\n\n"
        f"Structure:\n"
        f"1. Hook paragraph (2-3 sentences with primary keyword)\n"
        f"2. What viewers will learn (bullet points)\n"
        f"3. Timestamps placeholder section\n"
        f"4. Links section (subscribe, social media placeholders)\n"
        f"5. Keyword-rich closing paragraph\n"
        f"6. Relevant hashtags (5-10)\n"
        f"Keep under 5000 characters."
    )
    result = await _claude.generate_content(prompt, max_tokens=1000)
    return {"success": True, "description": result.get("content", ""), "keywords": keywords}


async def write_viral_caption(content: str, platform: str = "instagram") -> dict[str, Any]:
    """Rewrite or enhance a caption for maximum viral potential."""
    prompt = (
        f"Transform this content into a viral {platform} caption:\n\n{content}\n\n"
        f"Apply these viral copywriting techniques:\n"
        f"- Pattern interrupt opening\n"
        f"- Emotional trigger\n"
        f"- Social proof or curiosity gap\n"
        f"- Micro-story or surprising fact\n"
        f"- Strong CTA\n"
        f"Maintain the original message but maximise shareability."
    )
    result = await _claude.generate_content(prompt, max_tokens=600)
    return {"success": True, "caption": result.get("content", ""), "platform": platform}


async def suggest_trending_hashtags(niche: str, count: int = 30) -> dict[str, Any]:
    """Suggest a tiered set of trending hashtags for a niche."""
    prompt = (
        f"Suggest {count} Instagram hashtags for the '{niche}' niche.\n"
        f"Provide a strategic mix:\n"
        f"- 10 high-volume (1M+ posts)\n"
        f"- 10 medium-volume (100K-1M posts)\n"
        f"- 10 niche-specific (<100K posts)\n"
        f"Return only the hashtags as a comma-separated list without # symbols."
    )
    result = await _claude.generate_content(prompt, max_tokens=400)
    raw = result.get("content", "")
    hashtags = [h.strip().lstrip("#") for h in raw.split(",") if h.strip()]
    return {"success": True, "hashtags": hashtags[:count], "niche": niche}
