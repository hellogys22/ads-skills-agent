"""Affiliate product management endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from agents.ad_manager import AdManagerAgent
from models.mongodb_models import (
    create_product,
    delete_product,
    get_product,
    list_products,
    update_product,
)
from models.schemas import (
    AffiliateProduct,
    AffiliateProductCreate,
    MessageResponse,
)
from skills.product_skills import (
    add_affiliate_product,
    calculate_affiliate_revenue,
    create_product_promotion,
)

router = APIRouter(prefix="/products", tags=["Affiliate Products"])
logger = logging.getLogger(__name__)
_ad_manager = AdManagerAgent()


@router.get("/list")
async def list_affiliate_products(
    niche: Optional[str] = Query(None),
    active: bool = Query(True),
):
    """List all affiliate products, optionally filtered by niche."""
    products = await list_products(niche=niche, active=active)
    return {"success": True, "products": products, "count": len(products)}


@router.post("/add", response_model=AffiliateProduct)
async def add_product(payload: AffiliateProductCreate):
    """Add a new affiliate product."""
    result = await add_affiliate_product(payload.model_dump())
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return AffiliateProduct(**result["product"])


@router.put("/update/{product_id}", response_model=AffiliateProduct)
async def update_affiliate_product(product_id: str, payload: AffiliateProductCreate):
    """Update an existing affiliate product."""
    updated = await update_product(product_id, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return AffiliateProduct(**updated)


@router.delete("/remove/{product_id}", response_model=MessageResponse)
async def remove_product(product_id: str):
    """Soft-delete a product by marking it inactive."""
    updated = await update_product(product_id, {"active": False})
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return MessageResponse(message="Product removed successfully")


@router.get("/performance/{product_id}")
async def get_product_performance(product_id: str):
    """Retrieve performance metrics for a specific product."""
    result = await calculate_affiliate_revenue(product_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail="Product not found or no data available")
    # Construct response from known-safe fields only
    return {
        "product_id": str(result.get("product_id") or ""),
        "product_name": str(result.get("product_name") or ""),
        "period": str(result.get("period") or "all_time"),
        "total_revenue": float(result.get("total_revenue") or 0),
        "total_clicks": int(result.get("total_clicks") or 0),
        "total_conversions": int(result.get("total_conversions") or 0),
        "earnings_per_click": float(result.get("earnings_per_click") or 0),
        "conversion_rate": float(result.get("conversion_rate") or 0),
    }


@router.post("/promote/{product_id}")
async def promote_product(
    product_id: str,
    platform: str = Query("instagram"),
):
    """Generate promotional content for an affiliate product."""
    result = await create_product_promotion(product_id=product_id, platform=platform)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail="Product not found or promotion failed")
    return {
        "product_id": str(result.get("product_id") or ""),
        "platform": str(result.get("platform") or platform),
        "promotion": str(result.get("promotion") or ""),
    }
