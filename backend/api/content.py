"""Content generation and management endpoints."""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from agents.content_creator import ContentCreatorAgent
from models.mongodb_models import (
    create_post,
    delete_post,
    get_post,
    list_posts,
    update_post,
)
from models.schemas import (
    ContentPost,
    ContentPostCreate,
    MessageResponse,
    PaginatedResponse,
)
from skills.scheduling_skills import get_upcoming_schedule

router = APIRouter(prefix="/content", tags=["Content"])
logger = logging.getLogger(__name__)
_creator = ContentCreatorAgent()


# ── Generate ──────────────────────────────────────────────────────────────────

@router.post("/generate")
async def generate_content(
    product_name: str,
    product_description: str,
    platform: str = "instagram",
    tone: str = "engaging",
    include_hashtags: bool = True,
):
    """Use AI to generate platform-optimised content."""
    post = await _creator.generate_post(
        product_name=product_name,
        product_description=product_description,
        platform=platform,
        tone=tone,
    )
    if not post.get("success"):
        raise HTTPException(status_code=500, detail="Content generation failed")

    result = {"content": post.get("content", ""), "platform": platform}
    if include_hashtags:
        hashtags = await _creator.suggest_hashtags(
            topic=product_name, niche="general", platform=platform
        )
        result["hashtags"] = hashtags.get("hashtags", [])
    return result


# ── Schedule ──────────────────────────────────────────────────────────────────

@router.post("/schedule", response_model=ContentPost)
async def schedule_post(payload: ContentPostCreate):
    """Save a post with 'scheduled' status for later publishing."""
    data = payload.model_dump()
    data["status"] = "scheduled"
    doc = await create_post(data)
    return ContentPost(**doc)


# ── Library ───────────────────────────────────────────────────────────────────

@router.get("/library", response_model=PaginatedResponse)
async def get_content_library(
    platform: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Paginated list of content library posts."""
    skip = (page - 1) * page_size
    posts = await list_posts(platform=platform, status=status, skip=skip, limit=page_size)
    from models.mongodb_models import count_documents, content_library_col

    f = {}
    if platform:
        f["platform"] = platform
    if status:
        f["status"] = status
    total = await count_documents(content_library_col(), f)
    return PaginatedResponse(
        items=posts,
        total=total,
        page=page,
        page_size=page_size,
        has_next=(skip + len(posts)) < total,
    )


# ── Calendar ──────────────────────────────────────────────────────────────────

@router.get("/calendar")
async def get_content_calendar(days_ahead: int = Query(7, ge=1, le=90)):
    """Return upcoming scheduled posts for the content calendar view."""
    result = await get_upcoming_schedule(days_ahead=days_ahead)
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result


# ── Update ────────────────────────────────────────────────────────────────────

@router.put("/update/{post_id}", response_model=ContentPost)
async def update_content(post_id: str, payload: ContentPostCreate):
    """Update an existing post."""
    updated = await update_post(post_id, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Post not found")
    return ContentPost(**updated)


# ── Delete ────────────────────────────────────────────────────────────────────

@router.delete("/delete/{post_id}", response_model=MessageResponse)
async def delete_content(post_id: str):
    """Delete a post from the content library."""
    deleted = await delete_post(post_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Post not found")
    return MessageResponse(message="Post deleted successfully")
