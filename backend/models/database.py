"""MongoDB async client and collection accessors via Motor."""

import logging
from typing import Optional

import motor.motor_asyncio
from pymongo import ASCENDING, DESCENDING, IndexModel
from supabase import Client, create_client

from config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# ── Motor client (module-level singleton) ─────────────────────────────────────
_mongo_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
_db: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None


def get_mongo_client() -> motor.motor_asyncio.AsyncIOMotorClient:
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_uri)
    return _mongo_client


def get_database() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    global _db
    if _db is None:
        client = get_mongo_client()
        _db = client.get_default_database(default="ads_agent")
    return _db


# ── Collection accessors ──────────────────────────────────────────────────────

def social_credentials_col() -> motor.motor_asyncio.AsyncIOMotorCollection:
    return get_database()["social_credentials"]


def content_library_col() -> motor.motor_asyncio.AsyncIOMotorCollection:
    return get_database()["content_library"]


def analytics_data_col() -> motor.motor_asyncio.AsyncIOMotorCollection:
    return get_database()["analytics_data"]


def affiliate_products_col() -> motor.motor_asyncio.AsyncIOMotorCollection:
    return get_database()["affiliate_products"]


def campaign_schedules_col() -> motor.motor_asyncio.AsyncIOMotorCollection:
    return get_database()["campaign_schedules"]


def user_engagement_col() -> motor.motor_asyncio.AsyncIOMotorCollection:
    return get_database()["user_engagement"]


def performance_metrics_col() -> motor.motor_asyncio.AsyncIOMotorCollection:
    return get_database()["performance_metrics"]


# ── Index definitions ─────────────────────────────────────────────────────────

COLLECTION_INDEXES: dict[str, list[IndexModel]] = {
    "social_credentials": [
        IndexModel([("platform", ASCENDING), ("user_id", ASCENDING)], unique=True),
    ],
    "content_library": [
        IndexModel([("platform", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("scheduled_time", ASCENDING)]),
        IndexModel([("created_at", DESCENDING)]),
    ],
    "analytics_data": [
        IndexModel([("platform", ASCENDING), ("metric_type", ASCENDING)]),
        IndexModel([("timestamp", DESCENDING)]),
    ],
    "affiliate_products": [
        IndexModel([("niche", ASCENDING)]),
        IndexModel([("created_at", DESCENDING)]),
    ],
    "campaign_schedules": [
        IndexModel([("status", ASCENDING)]),
        IndexModel([("start_date", ASCENDING)]),
    ],
    "user_engagement": [
        IndexModel([("platform", ASCENDING), ("action_type", ASCENDING)]),
        IndexModel([("timestamp", DESCENDING)]),
    ],
    "performance_metrics": [
        IndexModel([("campaign_id", ASCENDING)]),
        IndexModel([("recorded_at", DESCENDING)]),
    ],
}


async def create_indexes() -> None:
    """Ensure all MongoDB indexes exist. Call once at startup."""
    db = get_database()
    for collection_name, indexes in COLLECTION_INDEXES.items():
        try:
            await db[collection_name].create_indexes(indexes)
            logger.info("Indexes ensured for collection: %s", collection_name)
        except Exception as exc:  # pragma: no cover
            logger.error("Failed to create indexes for %s: %s", collection_name, exc)


async def close_mongo_connection() -> None:
    global _mongo_client, _db
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
        _db = None
        logger.info("MongoDB connection closed")


# ── Supabase client ───────────────────────────────────────────────────────────

_supabase_client: Optional[Client] = None


def get_supabase() -> Client:
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            str(settings.supabase_url),
            settings.supabase_key,
        )
    return _supabase_client
