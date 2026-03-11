"""Platform mappers: MediaPlan -> platform-specific payloads."""
from app.schemas import MediaPlan


def map_to_google(plan: MediaPlan) -> dict:
    """Map plan to Google Ads Performance Max payload."""
    cp = plan.creative_pack
    return {
        "campaign_type": "performance_max",
        "name": f"PMax_{plan.product_categories[0][:20]}_{plan.daily_budget}",
        "daily_budget_micros": int(plan.daily_budget * 1_000_000),
        "bidding_strategy": "maximize_conversion_value",
        "asset_group": {
            "headlines": cp.headlines[:5],
            "long_headlines": cp.long_headlines[:5] or cp.headlines[:2],
            "descriptions": cp.descriptions[:5],
            "images": cp.image_urls[:4],
            "logo": cp.logo_url,
            "final_urls": ["https://example.com/shop"],
        },
        "geo_targets": plan.geo,
        "targeting_hints": plan.targeting_hints.keywords[:15],
    }


def map_to_meta(plan: MediaPlan) -> dict:
    """Map plan to Meta Shopping / Catalog Sales payload."""
    cp = plan.creative_pack
    return {
        "campaign_objective": "sales",
        "name": f"Meta_Shopping_{plan.product_categories[0][:15]}_{plan.daily_budget}",
        "daily_budget": plan.daily_budget,
        "ad_set": {
            "geo": plan.geo,
            "targeting": "broad",
            "optimization": "conversion_value",
        },
        "ad": {
            "primary_text": cp.primary_texts[0] if cp.primary_texts else cp.descriptions[0][:125],
            "headline": cp.headlines[0][:40] if cp.headlines else "Shop Now",
            "image_url": cp.image_urls[0] if cp.image_urls else cp.logo_url,
            "cta": "shop_now",
        },
    }


def map_to_amazon(plan: MediaPlan) -> dict:
    """Map plan to Amazon Sponsored Brands payload."""
    cp = plan.creative_pack
    brand_name = plan.product_categories[0][:20] if plan.product_categories else "Brand"
    return {
        "campaign_type": "sponsored_brands",
        "name": f"SB_{brand_name}_{plan.daily_budget}",
        "daily_budget": plan.daily_budget,
        "bidding_strategy": "dynamic_down_only",
        "ad_group": {
            "keywords": plan.targeting_hints.keywords[:10],
            "match_type": "phrase",
        },
        "creative": {
            "brand_name": brand_name,
            "headline": (cp.headlines[0][:50] if cp.headlines else f"Shop {brand_name}"),
            "logo_url": cp.logo_url,
            "landscape_image_url": cp.image_urls[0] if cp.image_urls else cp.logo_url,
        },
    }
