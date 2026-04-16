"""Campaign management endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from agents.coordinator import AgentCoordinator
from models.mongodb_models import (
    create_campaign,
    delete_campaign,
    get_campaign,
    list_campaigns,
    update_campaign,
)
from models.schemas import Campaign, CampaignCreate, MessageResponse

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])
logger = logging.getLogger(__name__)
_coordinator = AgentCoordinator()


@router.post("/create", response_model=Campaign)
async def create_new_campaign(payload: CampaignCreate):
    """Create a new marketing campaign."""
    data = payload.model_dump()
    data["status"] = "draft"
    doc = await create_campaign(data)
    return Campaign(**doc)


@router.get("/list")
async def list_all_campaigns(status: Optional[str] = Query(None)):
    """List campaigns, optionally filtered by status."""
    campaigns = await list_campaigns(status=status)
    return {"success": True, "campaigns": campaigns, "count": len(campaigns)}


@router.get("/status/{campaign_id}")
async def get_campaign_status(campaign_id: str):
    """Get full details and current status of a campaign."""
    campaign = await get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.post("/optimize/{campaign_id}")
async def optimize_campaign(campaign_id: str):
    """Run AI optimisation on a campaign and return recommendations."""
    campaign = await get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    result = await _coordinator.execute_task(
        "plan_strategy",
        {
            "niche": campaign.get("description", "general"),
            "platforms": campaign.get("platforms", ["instagram"]),
        },
    )
    if not result.get("success"):
        raise HTTPException(status_code=500, detail="Campaign optimisation failed")
    # Return only safe, structured fields — not raw error strings
    return {
        "success": True,
        "campaign_id": campaign_id,
        "recommendations": result.get("trends") or result.get("plan") or "",
    }


@router.put("/update/{campaign_id}", response_model=Campaign)
async def update_existing_campaign(campaign_id: str, payload: CampaignCreate):
    """Update campaign details."""
    updated = await update_campaign(campaign_id, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return Campaign(**updated)


@router.delete("/cancel/{campaign_id}", response_model=MessageResponse)
async def cancel_campaign(campaign_id: str):
    """Cancel a campaign (marks as cancelled, does not delete)."""
    updated = await update_campaign(campaign_id, {"status": "cancelled"})
    if not updated:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return MessageResponse(message="Campaign cancelled successfully")
