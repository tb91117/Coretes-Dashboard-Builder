"""API routes."""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Campaign, CampaignMetric, MediaPlan as MediaPlanModel
from app.schemas import (
    CreateCampaignInput,
    MediaPlan,
    CampaignResponse,
    OptimizationSuggestion,
)
from app.services.planner import generate_plan
from app.services.mappers import map_to_google, map_to_meta, map_to_amazon
from app.services.platform_apis import (
    create_google_campaign,
    create_meta_campaign,
    create_amazon_campaign,
    fetch_google_metrics,
    fetch_meta_metrics,
    fetch_amazon_metrics,
)
from app.services.optimization import analyze_and_suggest

router = APIRouter()


@router.get("/campaigns", response_model=list[CampaignResponse])
def list_campaigns(
    platform: Optional[str] = None,
    campaign_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all campaigns with aggregated metrics."""
    q = db.query(Campaign)
    if platform:
        q = q.filter(Campaign.platform == platform)
    if campaign_type:
        q = q.filter(Campaign.campaign_type == campaign_type)
    campaigns = q.all()

    # Aggregate metrics (last 7 days)
    since = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    result = []
    for c in campaigns:
        metrics = (
            db.query(CampaignMetric)
            .filter(CampaignMetric.campaign_id == c.id, CampaignMetric.date >= since)
            .all()
        )
        # If no metrics, use mock from platform API
        if not metrics:
            rows = []
            if c.platform == "google":
                rows = fetch_google_metrics([c.platform_campaign_id or str(c.id)])
            elif c.platform == "meta":
                rows = fetch_meta_metrics([c.platform_campaign_id or str(c.id)])
            elif c.platform == "amazon":
                rows = fetch_amazon_metrics([c.platform_campaign_id or str(c.id)])
            if rows:
                r = rows[0]
                m = CampaignMetric(
                    campaign_id=c.id,
                    date=r["date"],
                    spend=r["spend"],
                    impressions=r["impressions"],
                    clicks=r["clicks"],
                    ctr=r["ctr"],
                    conversions=r["conversions"],
                    conversion_value=r["conversion_value"],
                    currency=r.get("currency", "USD"),
                )
                db.add(m)
                db.commit()
                metrics = [m]

        agg = {
            "spend": sum(m.spend for m in metrics),
            "impressions": sum(m.impressions for m in metrics),
            "clicks": sum(m.clicks for m in metrics),
            "conversions": sum(m.conversions for m in metrics),
            "conversion_value": sum(m.conversion_value for m in metrics),
        }
        ctr = agg["clicks"] / agg["impressions"] * 100 if agg["impressions"] else 0
        result.append(
            CampaignResponse(
                id=c.id,
                platform=c.platform,
                platform_campaign_id=c.platform_campaign_id,
                campaign_name=c.campaign_name,
                campaign_type=c.campaign_type,
                status=c.status,
                spend=round(agg["spend"], 2),
                impressions=agg["impressions"],
                clicks=agg["clicks"],
                ctr=round(ctr, 2),
                conversions=agg["conversions"],
                conversion_value=round(agg["conversion_value"], 2),
            )
        )
    return result


@router.post("/planner/generate", response_model=MediaPlan)
def planner_generate(input: CreateCampaignInput):
    """Generate a media plan from minimal input."""
    return generate_plan(
        objective=input.objective,
        daily_budget=input.daily_budget,
        product_categories=input.product_categories,
        country=input.country,
        language=input.language,
    )


@router.post("/campaigns/create-all")
def create_all_campaigns(
    plan: MediaPlan,
    db: Session = Depends(get_db),
):
    """
    Create campaigns on all three platforms from the plan.
    Each platform fails independently.
    """
    results = []

    # Google
    try:
        payload = map_to_google(plan)
        cid, status = create_google_campaign(payload)
        camp = Campaign(
            platform="google",
            platform_campaign_id=cid,
            campaign_name=payload["name"],
            campaign_type="pmax",
            status="active" if status == "created" else "pending",
            plan_snapshot=plan.model_dump(),
        )
        db.add(camp)
        db.commit()
        db.refresh(camp)
        results.append({"platform": "google", "id": camp.id, "status": status})
    except Exception as e:
        results.append({"platform": "google", "error": str(e)})

    # Meta
    try:
        payload = map_to_meta(plan)
        cid, status = create_meta_campaign(payload)
        camp = Campaign(
            platform="meta",
            platform_campaign_id=cid,
            campaign_name=payload["name"],
            campaign_type="shopping",
            status="active" if status == "created" else "pending",
            plan_snapshot=plan.model_dump(),
        )
        db.add(camp)
        db.commit()
        db.refresh(camp)
        results.append({"platform": "meta", "id": camp.id, "status": status})
    except Exception as e:
        results.append({"platform": "meta", "error": str(e)})

    # Amazon
    try:
        payload = map_to_amazon(plan)
        cid, status = create_amazon_campaign(payload)
        camp = Campaign(
            platform="amazon",
            platform_campaign_id=cid,
            campaign_name=payload["name"],
            campaign_type="sponsored_brands",
            status="active" if status == "created" else "pending",
            plan_snapshot=plan.model_dump(),
        )
        db.add(camp)
        db.commit()
        db.refresh(camp)
        results.append({"platform": "amazon", "id": camp.id, "status": status})
    except Exception as e:
        results.append({"platform": "amazon", "error": str(e)})

    # Store plan for memory
    mp = MediaPlanModel(
        plan_json=plan.model_dump(),
        objective=plan.objective,
        daily_budget=plan.daily_budget,
        product_categories=",".join(plan.product_categories),
    )
    db.add(mp)
    db.commit()

    return {"results": results}


@router.get("/campaigns/{campaign_id}/metrics")
def get_campaign_metrics(campaign_id: int, db: Session = Depends(get_db)):
    """Get metrics for a single campaign."""
    c = db.get(Campaign, campaign_id)
    if not c:
        raise HTTPException(404, "Campaign not found")
    since = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    metrics = (
        db.query(CampaignMetric)
        .filter(CampaignMetric.campaign_id == campaign_id, CampaignMetric.date >= since)
        .all()
    )
    if not metrics:
        # Fetch mock
        if c.platform == "google":
            rows = fetch_google_metrics([c.platform_campaign_id or str(c.id)])
        elif c.platform == "meta":
            rows = fetch_meta_metrics([c.platform_campaign_id or str(c.id)])
        elif c.platform == "amazon":
            rows = fetch_amazon_metrics([c.platform_campaign_id or str(c.id)])
        else:
            rows = []
        for r in rows:
            m = CampaignMetric(
                campaign_id=c.id,
                date=r["date"],
                spend=r["spend"],
                impressions=r["impressions"],
                clicks=r["clicks"],
                ctr=r["ctr"],
                conversions=r["conversions"],
                conversion_value=r["conversion_value"],
                currency=r.get("currency", "USD"),
            )
            db.add(m)
        db.commit()
        metrics = db.query(CampaignMetric).filter(CampaignMetric.campaign_id == campaign_id, CampaignMetric.date >= since).all()
    return [{"date": m.date, "spend": m.spend, "impressions": m.impressions, "clicks": m.clicks, "ctr": m.ctr, "conversions": m.conversions, "conversion_value": m.conversion_value} for m in metrics]


@router.get("/optimization/suggestions", response_model=list[OptimizationSuggestion])
def get_optimization_suggestions(db: Session = Depends(get_db)):
    """Get optimization suggestions based on performance data."""
    campaigns = db.query(Campaign).all()
    since = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    data = []
    for c in campaigns:
        metrics = (
            db.query(CampaignMetric)
            .filter(CampaignMetric.campaign_id == c.id, CampaignMetric.date >= since)
            .all()
        )
        if not metrics:
            # Use mock
            if c.platform == "google":
                rows = fetch_google_metrics([c.platform_campaign_id or str(c.id)])
            elif c.platform == "meta":
                rows = fetch_meta_metrics([c.platform_campaign_id or str(c.id)])
            elif c.platform == "amazon":
                rows = fetch_amazon_metrics([c.platform_campaign_id or str(c.id)])
            else:
                rows = []
            for r in rows:
                m = CampaignMetric(
                    campaign_id=c.id,
                    date=r["date"],
                    spend=r["spend"],
                    impressions=r["impressions"],
                    clicks=r["clicks"],
                    ctr=r["ctr"],
                    conversions=r["conversions"],
                    conversion_value=r["conversion_value"],
                    currency=r.get("currency", "USD"),
                )
                db.add(m)
                data.append({
                    "id": c.id,
                    "platform": c.platform,
                    "spend": r.get("spend", 0),
                    "impressions": r.get("impressions", 0),
                    "clicks": r.get("clicks", 0),
                    "ctr": r.get("ctr", 0),
                    "conversions": r.get("conversions", 0),
                    "conversion_value": r.get("conversion_value", 0),
                })
            db.commit()
        else:
            agg = {
                "spend": sum(m.spend for m in metrics),
                "impressions": sum(m.impressions for m in metrics),
                "clicks": sum(m.clicks for m in metrics),
                "ctr": sum(m.clicks for m in metrics) / sum(m.impressions for m in metrics) * 100 if sum(m.impressions for m in metrics) else 0,
                "conversions": sum(m.conversions for m in metrics),
                "conversion_value": sum(m.conversion_value for m in metrics),
            }
            data.append({
                "id": c.id,
                "platform": c.platform,
                **agg,
            })
    return analyze_and_suggest(data)
