"""Affiliate product management skill functions."""

import logging
from typing import Any

from models.mongodb_models import (
    create_product,
    delete_product,
    get_product,
    list_products,
    update_product,
)

logger = logging.getLogger(__name__)


async def add_affiliate_product(product_data: dict[str, Any]) -> dict[str, Any]:
    """Persist a new affiliate product to the database."""
    try:
        required = {"name", "url", "commission", "niche"}
        missing = required - set(product_data.keys())
        if missing:
            return {"success": False, "error": f"Missing required fields: {missing}"}
        doc = await create_product(
            {
                "name": product_data["name"],
                "url": str(product_data["url"]),
                "commission": float(product_data["commission"]),
                "description": product_data.get("description", ""),
                "niche": product_data["niche"],
                "image_url": str(product_data.get("image_url", "") or ""),
                "price": product_data.get("price"),
                "active": True,
                "total_clicks": 0,
                "total_conversions": 0,
                "total_revenue": 0.0,
            }
        )
        return {"success": True, "product": doc}
    except Exception as exc:
        logger.error("add_affiliate_product failed: %s", exc)
        return {"success": False, "error": str(exc)}


async def get_product_recommendations(niche: str, audience: str = "general") -> dict[str, Any]:
    """Return active products for a niche with AI-generated promotion tips."""
    from utils.claude_client import ClaudeClient

    try:
        products = await list_products(niche=niche)
        if not products:
            return {"success": True, "recommendations": [], "niche": niche}
        product_summary = "\n".join(
            f"- {p['name']}: {p.get('description', '')[:100]} (commission: {p.get('commission', 0)}%)"
            for p in products[:10]
        )
        claude = ClaudeClient()
        tips = await claude.generate_content(
            f"For the '{audience}' audience interested in '{niche}', rank and briefly explain "
            f"why each of these affiliate products would appeal to them:\n{product_summary}",
            max_tokens=600,
        )
        return {
            "success": True,
            "recommendations": products,
            "ai_ranking": tips.get("content", ""),
            "niche": niche,
            "audience": audience,
        }
    except Exception as exc:
        logger.error("get_product_recommendations failed: %s", exc)
        return {"success": False, "error": str(exc)}


async def create_product_promotion(product_id: str, platform: str) -> dict[str, Any]:
    """Generate ready-to-post promotional content for a product."""
    from utils.claude_client import ClaudeClient

    try:
        product = await get_product(product_id)
        if not product:
            return {"success": False, "error": "Product not found"}
        claude = ClaudeClient()
        result = await claude.generate_content(
            f"Create a {platform} promotional post for '{product['name']}'.\n"
            f"Description: {product.get('description', '')}\n"
            f"Commission: {product.get('commission', 0)}%\n"
            f"Include: engaging copy, 3-5 hashtags, strong CTA, affiliate disclosure.",
            max_tokens=500,
        )
        return {
            "success": True,
            "product_id": product_id,
            "platform": platform,
            "promotion": result.get("content", ""),
        }
    except Exception as exc:
        logger.error("create_product_promotion failed: %s", exc)
        return {"success": False, "error": str(exc)}


async def track_affiliate_clicks(product_url: str, clicks: int = 1) -> dict[str, Any]:
    """Increment the click counter for a product matching the given URL."""
    try:
        products = await list_products()
        matched = [p for p in products if p.get("url") == product_url]
        if not matched:
            return {"success": False, "error": "No product found for that URL"}
        product = matched[0]
        product_id = str(product["_id"])
        updated = await update_product(
            product_id,
            {"total_clicks": product.get("total_clicks", 0) + clicks},
        )
        return {"success": True, "product_id": product_id, "new_click_total": updated.get("total_clicks")}
    except Exception as exc:
        logger.error("track_affiliate_clicks failed: %s", exc)
        return {"success": False, "error": str(exc)}


async def calculate_affiliate_revenue(
    product_id: str, period: str = "all_time"
) -> dict[str, Any]:
    """Return revenue stats for a product over a time period."""
    try:
        product = await get_product(product_id)
        if not product:
            return {"success": False, "error": "Product not found"}
        total_revenue = product.get("total_revenue", 0.0)
        total_clicks = product.get("total_clicks", 0)
        total_conversions = product.get("total_conversions", 0)
        epc = (total_revenue / total_clicks) if total_clicks > 0 else 0.0
        return {
            "success": True,
            "product_id": product_id,
            "product_name": product.get("name"),
            "period": period,
            "total_revenue": round(total_revenue, 2),
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "earnings_per_click": round(epc, 4),
            "conversion_rate": (
                round(total_conversions / total_clicks * 100, 2) if total_clicks else 0.0
            ),
        }
    except Exception as exc:
        logger.error("calculate_affiliate_revenue failed: %s", exc)
        return {"success": False, "error": str(exc)}
