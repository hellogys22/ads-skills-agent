"""Pydantic schemas for request / response validation."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, HttpUrl


# ── Enumerations ──────────────────────────────────────────────────────────────

class Platform(str, Enum):
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    YOUTUBE = "youtube"


class PostStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ActionType(str, Enum):
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    SAVE = "save"
    CLICK = "click"
    VIEW = "view"


class MetricType(str, Enum):
    IMPRESSIONS = "impressions"
    REACH = "reach"
    ENGAGEMENT = "engagement"
    CLICKS = "clicks"
    CONVERSIONS = "conversions"
    FOLLOWERS = "followers"
    REVENUE = "revenue"


# ── Base ──────────────────────────────────────────────────────────────────────

class MongoBase(BaseModel):
    """Shared fields for documents returned from MongoDB."""
    id: Optional[str] = Field(None, alias="_id")

    model_config = {"populate_by_name": True}


# ── ContentPost ───────────────────────────────────────────────────────────────

class ContentPostCreate(BaseModel):
    platform: Platform
    content: str = Field(..., min_length=1, max_length=2200)
    hashtags: list[str] = Field(default_factory=list)
    image_url: Optional[HttpUrl] = None
    video_url: Optional[HttpUrl] = None
    scheduled_time: Optional[datetime] = None
    campaign_id: Optional[str] = None


class ContentPost(ContentPostCreate, MongoBase):
    status: PostStatus = PostStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    external_post_id: Optional[str] = None
    error_message: Optional[str] = None


# ── AnalyticsData ─────────────────────────────────────────────────────────────

class AnalyticsDataCreate(BaseModel):
    platform: Platform
    metric_type: MetricType
    value: float
    post_id: Optional[str] = None
    campaign_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AnalyticsData(AnalyticsDataCreate, MongoBase):
    pass


# ── AffiliateProduct ──────────────────────────────────────────────────────────

class AffiliateProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    url: HttpUrl
    commission: float = Field(..., ge=0, le=100, description="Commission percentage 0-100")
    description: str = Field(default="", max_length=2000)
    niche: str = Field(..., min_length=1, max_length=100)
    image_url: Optional[HttpUrl] = None
    price: Optional[float] = Field(None, ge=0)


class AffiliateProduct(AffiliateProductCreate, MongoBase):
    active: bool = True
    total_clicks: int = 0
    total_conversions: int = 0
    total_revenue: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ── Campaign ──────────────────────────────────────────────────────────────────

class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    platforms: list[Platform] = Field(..., min_length=1)
    budget: float = Field(..., ge=0)
    start_date: datetime
    end_date: datetime
    description: Optional[str] = Field(None, max_length=1000)
    target_audience: Optional[dict[str, Any]] = None
    affiliate_product_ids: list[str] = Field(default_factory=list)


class Campaign(CampaignCreate, MongoBase):
    status: CampaignStatus = CampaignStatus.DRAFT
    spent: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ── UserEngagement ────────────────────────────────────────────────────────────

class UserEngagementCreate(BaseModel):
    platform: Platform
    user_id: str
    action_type: ActionType
    post_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UserEngagement(UserEngagementCreate, MongoBase):
    pass


# ── SocialCredentials ─────────────────────────────────────────────────────────

class SocialCredentialsCreate(BaseModel):
    platform: Platform
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    scopes: list[str] = Field(default_factory=list)
    account_id: Optional[str] = None
    account_name: Optional[str] = None


class SocialCredentials(SocialCredentialsCreate, MongoBase):
    connected: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ── AgentTask ─────────────────────────────────────────────────────────────────

class AgentTaskCreate(BaseModel):
    task_type: str = Field(..., min_length=1)
    parameters: dict[str, Any] = Field(default_factory=dict)


class AgentTask(AgentTaskCreate, MongoBase):
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# ── Generic responses ─────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
    success: bool = True


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int
    has_next: bool
