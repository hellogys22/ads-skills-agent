"""MongoDB CRUD helpers for each collection."""

from datetime import datetime
from typing import Any, Optional

from bson import ObjectId
from pymongo import ReturnDocument

from models.database import (
    affiliate_products_col,
    analytics_data_col,
    campaign_schedules_col,
    content_library_col,
    performance_metrics_col,
    social_credentials_col,
    user_engagement_col,
)


def _to_str_id(doc: dict) -> dict:
    """Convert ObjectId _id to string in-place and return the doc."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def _object_id(id_str: str) -> ObjectId:
    return ObjectId(id_str)


# ── Generic helpers ───────────────────────────────────────────────────────────

async def insert_document(collection, data: dict) -> dict:
    data.setdefault("created_at", datetime.utcnow())
    data.setdefault("updated_at", datetime.utcnow())
    result = await collection.insert_one(data)
    data["_id"] = str(result.inserted_id)
    return data


async def find_document(collection, filter_: dict) -> Optional[dict]:
    doc = await collection.find_one(filter_)
    return _to_str_id(doc) if doc else None


async def find_documents(
    collection,
    filter_: dict,
    sort: Optional[list] = None,
    skip: int = 0,
    limit: int = 20,
) -> list[dict]:
    cursor = collection.find(filter_)
    if sort:
        cursor = cursor.sort(sort)
    cursor = cursor.skip(skip).limit(limit)
    return [_to_str_id(doc) async for doc in cursor]


async def update_document(collection, id_str: str, updates: dict) -> Optional[dict]:
    updates["updated_at"] = datetime.utcnow()
    doc = await collection.find_one_and_update(
        {"_id": _object_id(id_str)},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    return _to_str_id(doc) if doc else None


async def delete_document(collection, id_str: str) -> bool:
    result = await collection.delete_one({"_id": _object_id(id_str)})
    return result.deleted_count > 0


async def count_documents(collection, filter_: dict) -> int:
    return await collection.count_documents(filter_)


# ── Content Library ───────────────────────────────────────────────────────────

async def create_post(data: dict) -> dict:
    return await insert_document(content_library_col(), data)


async def get_post(post_id: str) -> Optional[dict]:
    return await find_document(content_library_col(), {"_id": _object_id(post_id)})


async def list_posts(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> list[dict]:
    f: dict[str, Any] = {}
    if platform:
        f["platform"] = platform
    if status:
        f["status"] = status
    return await find_documents(
        content_library_col(),
        f,
        sort=[("scheduled_time", 1)],
        skip=skip,
        limit=limit,
    )


async def update_post(post_id: str, updates: dict) -> Optional[dict]:
    return await update_document(content_library_col(), post_id, updates)


async def delete_post(post_id: str) -> bool:
    return await delete_document(content_library_col(), post_id)


async def get_scheduled_posts(before: datetime) -> list[dict]:
    return await find_documents(
        content_library_col(),
        {"status": "scheduled", "scheduled_time": {"$lte": before}},
        sort=[("scheduled_time", 1)],
        limit=100,
    )


# ── Analytics Data ────────────────────────────────────────────────────────────

async def record_analytics(data: dict) -> dict:
    return await insert_document(analytics_data_col(), data)


async def get_analytics(
    platform: Optional[str] = None,
    metric_type: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    limit: int = 100,
) -> list[dict]:
    f: dict[str, Any] = {}
    if platform:
        f["platform"] = platform
    if metric_type:
        f["metric_type"] = metric_type
    if start or end:
        f["timestamp"] = {}
        if start:
            f["timestamp"]["$gte"] = start
        if end:
            f["timestamp"]["$lte"] = end
    return await find_documents(
        analytics_data_col(), f, sort=[("timestamp", -1)], limit=limit
    )


# ── Affiliate Products ────────────────────────────────────────────────────────

async def create_product(data: dict) -> dict:
    return await insert_document(affiliate_products_col(), data)


async def get_product(product_id: str) -> Optional[dict]:
    return await find_document(affiliate_products_col(), {"_id": _object_id(product_id)})


async def list_products(niche: Optional[str] = None, active: bool = True) -> list[dict]:
    f: dict[str, Any] = {"active": active}
    if niche:
        f["niche"] = niche
    return await find_documents(affiliate_products_col(), f, sort=[("created_at", -1)], limit=100)


async def update_product(product_id: str, updates: dict) -> Optional[dict]:
    return await update_document(affiliate_products_col(), product_id, updates)


async def delete_product(product_id: str) -> bool:
    return await delete_document(affiliate_products_col(), product_id)


# ── Campaigns ─────────────────────────────────────────────────────────────────

async def create_campaign(data: dict) -> dict:
    return await insert_document(campaign_schedules_col(), data)


async def get_campaign(campaign_id: str) -> Optional[dict]:
    return await find_document(campaign_schedules_col(), {"_id": _object_id(campaign_id)})


async def list_campaigns(status: Optional[str] = None) -> list[dict]:
    f: dict[str, Any] = {}
    if status:
        f["status"] = status
    return await find_documents(campaign_schedules_col(), f, sort=[("created_at", -1)], limit=50)


async def update_campaign(campaign_id: str, updates: dict) -> Optional[dict]:
    return await update_document(campaign_schedules_col(), campaign_id, updates)


async def delete_campaign(campaign_id: str) -> bool:
    return await delete_document(campaign_schedules_col(), campaign_id)


# ── Social Credentials ────────────────────────────────────────────────────────

async def upsert_credentials(platform: str, data: dict) -> dict:
    data["updated_at"] = datetime.utcnow()
    doc = await social_credentials_col().find_one_and_update(
        {"platform": platform},
        {"$set": data, "$setOnInsert": {"created_at": datetime.utcnow()}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return _to_str_id(doc)


async def get_credentials(platform: str) -> Optional[dict]:
    return await find_document(social_credentials_col(), {"platform": platform})


async def delete_credentials(platform: str) -> bool:
    result = await social_credentials_col().delete_one({"platform": platform})
    return result.deleted_count > 0


# ── User Engagement ────────────────────────────────────────────────────────────

async def record_engagement(data: dict) -> dict:
    return await insert_document(user_engagement_col(), data)


async def get_engagement_summary(platform: str, start: datetime, end: datetime) -> list[dict]:
    pipeline = [
        {
            "$match": {
                "platform": platform,
                "timestamp": {"$gte": start, "$lte": end},
            }
        },
        {
            "$group": {
                "_id": "$action_type",
                "count": {"$sum": 1},
            }
        },
    ]
    return [doc async for doc in user_engagement_col().aggregate(pipeline)]


# ── Performance Metrics ────────────────────────────────────────────────────────

async def record_performance(data: dict) -> dict:
    data.setdefault("recorded_at", datetime.utcnow())
    return await insert_document(performance_metrics_col(), data)


async def get_performance_by_campaign(campaign_id: str) -> list[dict]:
    return await find_documents(
        performance_metrics_col(),
        {"campaign_id": campaign_id},
        sort=[("recorded_at", -1)],
        limit=200,
    )
