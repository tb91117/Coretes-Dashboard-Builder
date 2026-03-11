"""Application configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """App settings from environment."""

    # Planner
    openai_api_key: str = ""
    planner_model: str = "gpt-4o-mini"

    # Platform keys (optional for mock)
    google_ads_customer_id: str = ""
    google_ads_developer_token: str = ""
    meta_access_token: str = ""
    amazon_access_key: str = ""
    amazon_secret_key: str = ""
    amazon_profile_id: str = ""

    env: str = "development"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
