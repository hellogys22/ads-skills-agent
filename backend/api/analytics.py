"""Analytics endpoints — dashboard, performance, engagement, reach, export."""

import io
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from models.mongodb_models import get_analytics
from models.schemas import AnalyticsData, AnalyticsDataCreate
from skills.analytics_skills import (
    aggregate_daily_stats,
    compare_platform_performance,
    generate_performance_report,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])
logger = logging.getLogger(__name__)


# ── Dashboard ─────────────────────────────────────────────────────────────────

@router.get("/dashboard")
async def get_dashboard():
    """Real-time metrics summary across all platforms."""
    platforms = ["instagram", "facebook", "youtube"]
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=7)
    summary = {}
    for platform in platforms:
        result = await aggregate_daily_stats(platform, (start, end))
        summary[platform] = result.get("metrics", {})
    return {
        "success": True,
        "period": "last_7_days",
        "platforms": summary,
        "generated_at": end.isoformat(),
    }


# ── Performance ────────────────────────────────────────────────────────────────

@router.get("/performance")
async def get_performance(
    platform: Optional[str] = Query(None),
    metric: str = Query("engagement"),
    days: int = Query(30, ge=1, le=365),
):
    """Detailed performance report for one or all platforms."""
    platforms = [platform] if platform else ["instagram", "facebook", "youtube"]
    return await compare_platform_performance(platforms=platforms, metric=metric, days=days)


# ── Engagement ────────────────────────────────────────────────────────────────

@router.get("/engagement")
async def get_engagement(
    platform: str = Query("instagram"),
    days: int = Query(30, ge=1, le=365),
):
    """Engagement metrics (likes, comments, shares) for a platform."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    records = await get_analytics(
        platform=platform, metric_type="engagement", start=start, end=end, limit=500
    )
    total = sum(r.get("value", 0) for r in records)
    return {
        "success": True,
        "platform": platform,
        "period_days": days,
        "total_engagement": total,
        "data_points": records,
    }


# ── Reach ─────────────────────────────────────────────────────────────────────

@router.get("/reach")
async def get_reach(
    platform: str = Query("instagram"),
    days: int = Query(30, ge=1, le=365),
):
    """Reach and impressions for a platform."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    reach = await get_analytics(
        platform=platform, metric_type="reach", start=start, end=end, limit=500
    )
    impressions = await get_analytics(
        platform=platform, metric_type="impressions", start=start, end=end, limit=500
    )
    return {
        "success": True,
        "platform": platform,
        "period_days": days,
        "total_reach": sum(r.get("value", 0) for r in reach),
        "total_impressions": sum(r.get("value", 0) for r in impressions),
    }


# ── Export ────────────────────────────────────────────────────────────────────

@router.post("/export")
async def export_analytics(
    campaign_id: Optional[str] = None,
    platform: Optional[str] = None,
    format: str = Query("pdf", pattern="^(pdf|csv)$"),
):
    """Export analytics report as PDF or CSV."""
    if format == "csv":
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=30)
        records = await get_analytics(platform=platform, start=start, end=end, limit=1000)
        import csv
        output = io.StringIO()
        writer = csv.DictWriter(
            output, fieldnames=["platform", "metric_type", "value", "timestamp"]
        )
        writer.writeheader()
        for r in records:
            writer.writerow(
                {
                    "platform": r.get("platform", ""),
                    "metric_type": r.get("metric_type", ""),
                    "value": r.get("value", 0),
                    "timestamp": str(r.get("timestamp", "")),
                }
            )
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=analytics_export.csv"},
        )

    # PDF export using reportlab
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        report = await generate_performance_report(campaign_id or "all")
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "Analytics Performance Report")
        c.setFont("Helvetica", 11)
        text = c.beginText(50, 720)
        for line in (report.get("narrative", "") or "No data available.").split("\n"):
            text.textLine(line[:100])
        c.drawText(text)
        c.save()
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=analytics_report.pdf"},
        )
    except Exception as exc:
        logger.error("PDF export failed: %s", exc)
        raise HTTPException(status_code=500, detail="PDF generation failed")
