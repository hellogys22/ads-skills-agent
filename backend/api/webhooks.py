"""Webhook handlers for Instagram and Facebook."""

import hashlib
import hmac
import logging

from fastapi import APIRouter, Header, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from config import get_settings
from models.mongodb_models import record_engagement
from models.schemas import ActionType
from utils.helpers import parse_webhook_payload

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
logger = logging.getLogger(__name__)
settings = get_settings()


def _verify_fb_signature(body: bytes, signature: str) -> bool:
    """Validate X-Hub-Signature-256 header."""
    if not signature.startswith("sha256="):
        return False
    expected = hmac.new(
        settings.facebook_app_secret.encode("utf-8"), body, hashlib.sha256  # type: ignore[attr-defined]
    ).hexdigest()
    provided = signature[len("sha256="):]
    return hmac.compare_digest(expected, provided)


# ── Instagram webhook ─────────────────────────────────────────────────────────

@router.get("/instagram")
async def verify_instagram_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
):
    """Instagram webhook verification (GET challenge)."""
    expected_token = settings.instagram_app_secret[:16]
    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403, detail="Webhook verification failed")


@router.post("/instagram")
async def handle_instagram_webhook(
    request: Request,
    x_hub_signature_256: str = Header(default=""),
):
    """Receive and process Instagram webhook events."""
    body = await request.body()
    if not _verify_fb_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid webhook signature")

    try:
        payload = await request.json()
        parsed = parse_webhook_payload(payload)
        field = parsed.get("field", "")

        if field == "comments":
            value = parsed.get("value", {})
            await record_engagement(
                {
                    "platform": "instagram",
                    "user_id": str(value.get("from", {}).get("id", "unknown")),
                    "action_type": ActionType.COMMENT,
                    "post_id": str(value.get("media", {}).get("id", "")),
                    "metadata": value,
                }
            )
        elif field == "likes":
            value = parsed.get("value", {})
            await record_engagement(
                {
                    "platform": "instagram",
                    "user_id": str(value.get("from", {}).get("id", "unknown")),
                    "action_type": ActionType.LIKE,
                    "metadata": value,
                }
            )
        logger.info("Instagram webhook processed: %s", field)
        return {"status": "ok"}
    except Exception as exc:
        logger.error("Instagram webhook error: %s", exc)
        raise HTTPException(status_code=500, detail="Webhook processing error")


# ── Facebook webhook ──────────────────────────────────────────────────────────

@router.get("/facebook")
async def verify_facebook_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
):
    """Facebook webhook verification (GET challenge)."""
    expected_token = settings.facebook_app_secret[:16]
    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403, detail="Webhook verification failed")


@router.post("/facebook")
async def handle_facebook_webhook(
    request: Request,
    x_hub_signature_256: str = Header(default=""),
):
    """Receive and process Facebook page webhook events."""
    body = await request.body()
    if not _verify_fb_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid webhook signature")

    try:
        payload = await request.json()
        parsed = parse_webhook_payload(payload)
        logger.info("Facebook webhook processed: field=%s", parsed.get("field"))
        return {"status": "ok"}
    except Exception as exc:
        logger.error("Facebook webhook error: %s", exc)
        raise HTTPException(status_code=500, detail="Webhook processing error")


# ── Generic verify endpoint ────────────────────────────────────────────────────

@router.get("/verify/{platform}")
async def generic_verify(
    platform: str,
    hub_mode: str = Query(alias="hub.mode", default=""),
    hub_verify_token: str = Query(alias="hub.verify_token", default=""),
    hub_challenge: str = Query(alias="hub.challenge", default=""),
):
    """Generic webhook verification for any supported platform."""
    expected_token = settings.facebook_app_secret[:16]
    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")
