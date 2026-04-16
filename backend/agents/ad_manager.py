"""CrewAI Ad Manager — affiliate product promotions and conversion tracking."""

import logging
from typing import Any, Optional

from crewai import Agent, Task

from models.mongodb_models import get_product, list_products, update_product
from utils.claude_client import ClaudeClient

logger = logging.getLogger(__name__)


class AdManagerAgent:
    """Manages affiliate product promotions, tracks conversions, and optimises ad spend."""

    def __init__(self) -> None:
        self.claude = ClaudeClient()
        self.agent = Agent(
            role="Affiliate Ad Manager",
            goal=(
                "Maximise affiliate revenue by creating high-converting promotional "
                "content, tracking performance, and continuously optimising ad spend."
            ),
            backstory=(
                "You are a performance marketing expert specialising in affiliate "
                "marketing and conversion rate optimisation. You have a proven track "
                "record of scaling affiliate campaigns profitably across social platforms."
            ),
            verbose=True,
            allow_delegation=False,
        )

    # ── Public methods ────────────────────────────────────────────────────────

    async def create_ad_content(
        self,
        product_id: str,
        platform: str,
        ad_format: str = "feed_post",
    ) -> dict[str, Any]:
        """Generate ad copy tailored to a specific platform and format."""
        try:
            product = await get_product(product_id)
            if not product:
                return {"success": False, "error": "Product not found"}
            prompt = (
                f"Create a high-converting {platform} {ad_format} ad for:\n"
                f"Product: {product['name']}\n"
                f"Description: {product.get('description', '')}\n"
                f"Commission: {product.get('commission', 0)}%\n"
                f"URL: {product.get('url', '')}\n\n"
                f"Include: compelling headline, benefit-focused body copy, "
                f"strong CTA, and 5 relevant hashtags. "
                f"Optimise for {platform} best practices."
            )
            result = await self.claude.generate_content(prompt, max_tokens=600)
            return {
                "success": True,
                "ad_content": result.get("content", ""),
                "platform": platform,
                "product_id": product_id,
                "product_name": product["name"],
            }
        except Exception as exc:
            logger.error("create_ad_content failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def track_conversions(self, product_id: str, clicks: int, conversions: int) -> dict[str, Any]:
        """Update product conversion stats in the database."""
        try:
            product = await get_product(product_id)
            if not product:
                return {"success": False, "error": "Product not found"}
            revenue = conversions * (product.get("price", 0) or 0) * (product.get("commission", 0) / 100)
            updates = {
                "total_clicks": product.get("total_clicks", 0) + clicks,
                "total_conversions": product.get("total_conversions", 0) + conversions,
                "total_revenue": product.get("total_revenue", 0.0) + revenue,
            }
            updated = await update_product(product_id, updates)
            conversion_rate = (conversions / clicks * 100) if clicks > 0 else 0.0
            return {
                "success": True,
                "product_id": product_id,
                "new_clicks": clicks,
                "new_conversions": conversions,
                "conversion_rate": round(conversion_rate, 2),
                "revenue_generated": round(revenue, 2),
                "updated_totals": updated,
            }
        except Exception as exc:
            logger.error("track_conversions failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def optimize_spend(
        self, budget: float, products: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """Recommend budget allocation across products."""
        try:
            if products:
                product_docs = [await get_product(pid) for pid in products]
                product_docs = [p for p in product_docs if p]
            else:
                product_docs = await list_products()
            summary = "\n".join(
                f"- {p['name']}: {p.get('total_conversions', 0)} conversions, "
                f"${p.get('total_revenue', 0):.2f} revenue, {p.get('commission', 0)}% commission"
                for p in product_docs
            )
            prompt = (
                f"Given a total budget of ${budget:.2f}, recommend an optimal allocation "
                f"across these affiliate products to maximise total revenue:\n\n{summary}\n\n"
                f"Provide percentage allocations with rationale for each product."
            )
            result = await self.claude.generate_content(prompt, max_tokens=800)
            return {
                "success": True,
                "budget": budget,
                "allocation_recommendation": result.get("content", ""),
                "products_analysed": len(product_docs),
            }
        except Exception as exc:
            logger.error("optimize_spend failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def get_affiliate_performance(self, product_id: Optional[str] = None) -> dict[str, Any]:
        """Get aggregate performance stats for one or all affiliate products."""
        try:
            if product_id:
                products = [await get_product(product_id)]
                products = [p for p in products if p]
            else:
                products = await list_products()
            stats = [
                {
                    "product_id": str(p.get("_id", "")),
                    "name": p.get("name"),
                    "total_clicks": p.get("total_clicks", 0),
                    "total_conversions": p.get("total_conversions", 0),
                    "conversion_rate": (
                        round(p.get("total_conversions", 0) / p.get("total_clicks", 1) * 100, 2)
                        if p.get("total_clicks", 0) > 0
                        else 0.0
                    ),
                    "total_revenue": p.get("total_revenue", 0.0),
                }
                for p in products
            ]
            return {"success": True, "performance": stats, "total_products": len(stats)}
        except Exception as exc:
            logger.error("get_affiliate_performance failed: %s", exc)
            return {"success": False, "error": str(exc)}

    def get_crewai_agent(self) -> Agent:
        return self.agent

    def build_task(self, description: str, expected_output: str) -> Task:
        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.agent,
        )
