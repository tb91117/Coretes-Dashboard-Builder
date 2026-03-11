"""Pydantic schemas for validation and API."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# --- Input / Create ---
class CreateCampaignInput(BaseModel):
    objective: str = Field(..., pattern="^(sales|leads)$")
    daily_budget: float = Field(..., ge=1, le=100000)
    product_categories: list[str] = Field(..., min_length=1)
    country: Optional[str] = None
    language: Optional[str] = None


# --- Media Plan (Planner output) ---
class CreativePack(BaseModel):
    headlines: list[str] = Field(default_factory=list, min_length=1)
    descriptions: list[str] = Field(default_factory=list, min_length=1)
    long_headlines: list[str] = Field(default_factory=list)
    primary_texts: list[str] = Field(default_factory=list)
    callouts: list[str] = Field(default_factory=list)
    image_urls: list[str] = Field(default_factory=list)
    logo_url: Optional[str] = None


class TargetingHints(BaseModel):
    keywords: list[str] = Field(default_factory=list)
    audiences: list[str] = Field(default_factory=list)
    placements: list[str] = Field(default_factory=list)


class MediaPlan(BaseModel):
    objective: str
    daily_budget: float
    geo: list[str] = Field(default_factory=lambda: ["US"])
    lang: list[str] = Field(default_factory=lambda: ["en"])
    product_categories: list[str] = Field(default_factory=list)
    creative_pack: CreativePack
    targeting_hints: TargetingHints = Field(default_factory=TargetingHints)
    bidding_strategy: str = "maximize_conversion_value"


# --- Campaign display ---
class CampaignResponse(BaseModel):
    id: int
    platform: str
    platform_campaign_id: Optional[str]
    campaign_name: str
    campaign_type: str
    status: str
    spend: float = 0.0
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    conversions: int = 0
    conversion_value: float = 0.0
    currency: str = "USD"

    class Config:
        from_attributes = True


# --- Optimization suggestion ---
class OptimizationSuggestion(BaseModel):
    campaign_id: int
    platform: str
    issue_detected: str
    recommended_action: str
    reasoning: str
    confidence: float = Field(..., ge=0, le=1)
