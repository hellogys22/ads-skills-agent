"""Social media posting and scheduling skill functions."""

import logging
from datetime import datetime
from typing import Any

from config import get_settings

logger = logging.getLogger(__name__)


async def post_to_instagram(
    image_url: str, caption: str, hashtags: list[str]
) -> dict[str, Any]:
    """Create and immediately publish an Instagram post."""
    from utils.social_media_client import InstagramClient

    settings = get_settings()
    client = InstagramClient(
        app_id=settings.instagram_app_id,
        app_secret=settings.instagram_app_secret,
        access_token=settings.instagram_access_token,
    )
    try:
        hashtag_str = " ".join(f"#{h.lstrip('#')}" for h in hashtags)
        full_caption = f"{caption}\n\n{hashtag_str}".strip()
        container = await client.create_media_container(
            image_url=image_url, caption=full_caption
        )
        container_id = container.get("id")
        if not container_id:
            return {"success": False, "error": "Failed to create media container"}
        publish = await client.publish_media(container_id)
        await client.aclose()
        return {
            "success": True,
            "post_id": publish.get("id"),
            "platform": "instagram",
            "caption_length": len(full_caption),
        }
    except Exception as exc:
        logger.error("post_to_instagram failed: %s", exc)
        return {"success": False, "error": str(exc)}


async def post_to_facebook(content: str, page_id: str) -> dict[str, Any]:
    """Publish a text post to a Facebook page."""
    from utils.social_media_client import FacebookClient

    settings = get_settings()
    # Use the Facebook page access token; fall back to empty string if not configured
    fb_token = settings.facebook_page_access_token or ""
    client = FacebookClient(
        app_id=settings.facebook_app_id,
        app_secret=settings.facebook_app_secret,
        page_id=page_id,
        page_access_token=fb_token,
    )
    try:
        result = await client.create_post(message=content)
        await client.aclose()
        return {"success": True, "post_id": result.get("id"), "platform": "facebook"}
    except Exception as exc:
        logger.error("post_to_facebook failed: %s", exc)
        return {"success": False, "error": str(exc)}


async def upload_youtube_video(
    title: str, description: str, video_path: str
) -> dict[str, Any]:
    """Upload a video to YouTube."""
    from utils.social_media_client import YouTubeClient

    settings = get_settings()
    client = YouTubeClient(api_key=settings.youtube_api_key, access_token=None)
    try:
        result = await client.upload_video(
            title=title, description=description, video_path=video_path
        )
        await client.aclose()
        return {"success": True, "video_id": result.get("id"), "platform": "youtube"}
    except Exception as exc:
        logger.error("upload_youtube_video failed: %s", exc)
        return {"success": False, "error": str(exc)}


async def schedule_cross_platform_post(
    content: str,
    platforms: list[str],
    scheduled_time: datetime,
    image_url: str = "",
    hashtags: list[str] | None = None,
) -> dict[str, Any]:
    """Persist a cross-platform post to the content library for later publishing."""
    from models.mongodb_models import create_post

    hashtags = hashtags or []
    results: list[dict] = []
    for platform in platforms:
        doc = await create_post(
            {
                "platform": platform,
                "content": content,
                "hashtags": hashtags,
                "image_url": image_url,
                "scheduled_time": scheduled_time,
                "status": "scheduled",
            }
        )
        results.append({"platform": platform, "post_id": doc.get("_id")})
    return {"success": True, "scheduled": results, "scheduled_time": scheduled_time.isoformat()}


async def get_platform_followers(platform: str) -> dict[str, Any]:
    """Return follower/fan count for the configured account on a platform."""
    settings = get_settings()
    try:
        if platform == "instagram":
            from utils.social_media_client import InstagramClient

            client = InstagramClient(
                app_id=settings.instagram_app_id,
                app_secret=settings.instagram_app_secret,
                access_token=settings.instagram_access_token,
            )
            profile = await client.get_user_profile()
            await client.aclose()
            return {"success": True, "platform": platform, "account": profile}
        elif platform == "facebook":
            from utils.social_media_client import FacebookClient

            client = FacebookClient(
                app_id=settings.facebook_app_id,
                app_secret=settings.facebook_app_secret,
                page_id=settings.facebook_page_id,
                page_access_token=settings.facebook_page_access_token or "",
            )
            info = await client.get_page_info()
            await client.aclose()
            return {
                "success": True,
                "platform": platform,
                "followers": info.get("followers_count", 0),
                "fans": info.get("fan_count", 0),
            }
        else:
            return {"success": False, "error": f"Unsupported platform: {platform}"}
    except Exception as exc:
        logger.error("get_platform_followers(%s) failed: %s", platform, exc)
        return {"success": False, "error": str(exc)}
