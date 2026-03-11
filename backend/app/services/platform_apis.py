"""Platform API clients: create campaigns (mocked with graceful failure)."""
import logging
import uuid
from datetime import datetime

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings

logger = logging.getLogger(__name__)


def _mock_id() -> str:
    return str(uuid.uuid4())[:12]


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
)
def create_google_campaign(payload: dict) -> tuple[str | None, str]:
    """
    Create Google Ads Performance Max campaign.
    Returns (campaign_id, status).
    """
    if not settings.google_ads_developer_token:
        logger.info("Google Ads: no token, mocking creation. Payload: %s", payload)
        return _mock_id(), "created"
    # Real API call would go here
    return _mock_id(), "created"


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
)
def create_meta_campaign(payload: dict) -> tuple[str | None, str]:
    """
    Create Meta Shopping campaign.
    """
    if not settings.meta_access_token:
        logger.info("Meta: no token, mocking creation. Payload: %s", payload)
        return _mock_id(), "created"
    return _mock_id(), "created"


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
)
def create_amazon_campaign(payload: dict) -> tuple[str | None, str]:
    """
    Create Amazon Sponsored Brands campaign.
    """
    if not settings.amazon_access_key:
        logger.info("Amazon: no credentials, mocking creation. Payload: %s", payload)
        return _mock_id(), "created"
    return _mock_id(), "created"


def fetch_google_metrics(campaign_ids: list[str]) -> list[dict]:
    """Fetch metrics for Google campaigns. Mocked."""
    return [_mock_metrics_row(cid, "google", "pmax") for cid in campaign_ids]


def fetch_meta_metrics(campaign_ids: list[str]) -> list[dict]:
    """Fetch metrics for Meta campaigns. Mocked."""
    return [_mock_metrics_row(cid, "meta", "shopping") for cid in campaign_ids]


def fetch_amazon_metrics(campaign_ids: list[str]) -> list[dict]:
    """Fetch metrics for Amazon campaigns. Mocked."""
    return [_mock_metrics_row(cid, "amazon", "sponsored_brands") for cid in campaign_ids]


def _mock_metrics_row(campaign_id: str, platform: str, campaign_type: str) -> dict:
    """Generate mock metrics for display."""
    from random import uniform, randint
    spend = round(uniform(5, 150), 2)
    impressions = randint(100, 5000)
    clicks = randint(5, 200)
    ctr = clicks / impressions if impressions else 0
    conv = randint(0, 15)
    conv_val = round(conv * uniform(10, 50), 2)
    return {
        "platform": platform,
        "campaign_id": campaign_id,
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "spend": spend,
        "impressions": impressions,
        "clicks": clicks,
        "ctr": round(ctr * 100, 2),
        "conversions": conv,
        "conversion_value": conv_val,
        "currency": "USD",
    }
