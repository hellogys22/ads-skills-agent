"""OAuth connection endpoints for social platforms."""

import logging
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse

from config import get_settings
from models.mongodb_models import delete_credentials, get_credentials, upsert_credentials
from models.schemas import MessageResponse, SocialCredentials, SocialCredentialsCreate

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)
settings = get_settings()


# ── Instagram OAuth ────────────────────────────────────────────────────────────

@router.post("/connect-instagram")
async def connect_instagram():
    """Return the Instagram OAuth authorisation URL."""
    params = {
        "client_id": settings.instagram_app_id,
        "redirect_uri": f"{settings.api_base_url}/auth/callback/instagram",
        "scope": "instagram_basic,instagram_content_publish,instagram_manage_insights",
        "response_type": "code",
    }
    auth_url = f"https://api.instagram.com/oauth/authorize?{urlencode(params)}"
    return {"auth_url": auth_url}


@router.get("/callback/instagram")
async def instagram_callback(code: str = Query(...)):
    """Handle Instagram OAuth callback and exchange code for tokens."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.instagram.com/oauth/access_token",
                data={
                    "client_id": settings.instagram_app_id,
                    "client_secret": settings.instagram_app_secret,
                    "grant_type": "authorization_code",
                    "redirect_uri": f"{settings.api_base_url}/auth/callback/instagram",
                    "code": code,
                },
            )
            resp.raise_for_status()
            token_data = resp.json()

        expires_at = datetime.now(timezone.utc) + timedelta(days=60)
        await upsert_credentials(
            "instagram",
            {
                "platform": "instagram",
                "access_token": token_data.get("access_token", ""),
                "account_id": str(token_data.get("user_id", "")),
                "expires_at": expires_at,
                "connected": True,
            },
        )
        return RedirectResponse(url=f"{settings.frontend_url}/settings?platform=instagram&status=connected")
    except Exception as exc:
        logger.error("Instagram callback failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))


# ── Facebook OAuth ─────────────────────────────────────────────────────────────

@router.post("/connect-facebook")
async def connect_facebook():
    """Return the Facebook OAuth authorisation URL."""
    params = {
        "client_id": settings.facebook_app_id,
        "redirect_uri": f"{settings.api_base_url}/auth/callback/facebook",
        "scope": "pages_manage_posts,pages_read_engagement,pages_show_list",
        "response_type": "code",
    }
    auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(params)}"
    return {"auth_url": auth_url}


@router.get("/callback/facebook")
async def facebook_callback(code: str = Query(...)):
    """Handle Facebook OAuth callback."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://graph.facebook.com/v18.0/oauth/access_token",
                params={
                    "client_id": settings.facebook_app_id,
                    "client_secret": settings.facebook_app_secret,
                    "redirect_uri": f"{settings.api_base_url}/auth/callback/facebook",
                    "code": code,
                },
            )
            resp.raise_for_status()
            token_data = resp.json()

        expires_in = token_data.get("expires_in", 5183944)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        await upsert_credentials(
            "facebook",
            {
                "platform": "facebook",
                "access_token": token_data.get("access_token", ""),
                "expires_at": expires_at,
                "connected": True,
            },
        )
        return RedirectResponse(url=f"{settings.frontend_url}/settings?platform=facebook&status=connected")
    except Exception as exc:
        logger.error("Facebook callback failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))


# ── YouTube OAuth ──────────────────────────────────────────────────────────────

@router.post("/connect-youtube")
async def connect_youtube():
    """Return the Google OAuth authorisation URL for YouTube."""
    params = {
        "client_id": settings.youtube_client_id,
        "redirect_uri": f"{settings.api_base_url}/auth/callback/youtube",
        "scope": "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly",
        "response_type": "code",
        "access_type": "offline",
    }
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return {"auth_url": auth_url}


@router.get("/callback/youtube")
async def youtube_callback(code: str = Query(...)):
    """Handle YouTube/Google OAuth callback."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.youtube_client_id,
                    "client_secret": settings.youtube_client_secret,
                    "redirect_uri": f"{settings.api_base_url}/auth/callback/youtube",
                    "grant_type": "authorization_code",
                    "code": code,
                },
            )
            resp.raise_for_status()
            token_data = resp.json()

        expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_data.get("expires_in", 3600))
        await upsert_credentials(
            "youtube",
            {
                "platform": "youtube",
                "access_token": token_data.get("access_token", ""),
                "refresh_token": token_data.get("refresh_token"),
                "expires_at": expires_at,
                "connected": True,
            },
        )
        return RedirectResponse(url=f"{settings.frontend_url}/settings?platform=youtube&status=connected")
    except Exception as exc:
        logger.error("YouTube callback failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))


# ── Token refresh ──────────────────────────────────────────────────────────────

@router.post("/refresh/{platform}", response_model=MessageResponse)
async def refresh_token(platform: str):
    """Refresh the access token for a connected platform."""
    creds = await get_credentials(platform)
    if not creds:
        raise HTTPException(status_code=404, detail=f"{platform} not connected")
    try:
        if platform == "youtube" and creds.get("refresh_token"):
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": settings.youtube_client_id,
                        "client_secret": settings.youtube_client_secret,
                        "refresh_token": creds["refresh_token"],
                        "grant_type": "refresh_token",
                    },
                )
                resp.raise_for_status()
                new_tokens = resp.json()
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=new_tokens.get("expires_in", 3600))
            await upsert_credentials(platform, {"access_token": new_tokens["access_token"], "expires_at": expires_at})
            return MessageResponse(message=f"{platform} token refreshed successfully")
        raise HTTPException(status_code=400, detail=f"Token refresh not supported for {platform}")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Disconnect ─────────────────────────────────────────────────────────────────

@router.delete("/disconnect/{platform}", response_model=MessageResponse)
async def disconnect_platform(platform: str):
    """Remove stored credentials for a platform."""
    deleted = await delete_credentials(platform)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"{platform} was not connected")
    return MessageResponse(message=f"{platform} disconnected successfully")
