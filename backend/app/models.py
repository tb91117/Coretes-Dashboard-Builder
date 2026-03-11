"""Database models."""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Campaign(Base):
    """Campaign record stored after creation."""

    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(32), nullable=False)  # google | meta | amazon
    platform_campaign_id = Column(String(128), index=True)  # from API or mock
    campaign_name = Column(String(256), nullable=False)
    campaign_type = Column(String(64), nullable=False)  # pmax | shopping | sponsored_brands
    status = Column(String(32), default="active")  # active | pending | failed
    created_at = Column(DateTime, default=datetime.utcnow)
    plan_snapshot = Column(JSON)  # stored plan for reference

    metrics = relationship("CampaignMetric", back_populates="campaign", cascade="all, delete-orphan")


class CampaignMetric(Base):
    """Performance metrics for a campaign."""

    __tablename__ = "campaign_metrics"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    date = Column(String(10), nullable=False)  # YYYY-MM-DD
    spend = Column(Float, default=0.0)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    ctr = Column(Float, default=0.0)
    conversions = Column(Integer, default=0)
    conversion_value = Column(Float, default=0.0)
    currency = Column(String(4), default="USD")

    campaign = relationship("Campaign", back_populates="metrics")


class MediaPlan(Base):
    """Stored media plan for memory/reuse."""

    __tablename__ = "media_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_json = Column(JSON, nullable=False)
    objective = Column(String(32))
    daily_budget = Column(Float)
    product_categories = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
