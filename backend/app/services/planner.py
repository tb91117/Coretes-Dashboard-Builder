"""Planner agent: structured media plan generation with validation."""
import json
import logging
from typing import Any

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings
from app.schemas import MediaPlan, CreativePack, TargetingHints

logger = logging.getLogger(__name__)

MAX_PLANNING_STEPS = 5
from pathlib import Path

PLATFORM_POLICIES_PATH = Path(__file__).resolve().parent.parent.parent.parent / "platform_policies.md"


def _load_policies() -> str:
    """Load platform policies for retrieval injection."""
    try:
        with Path(PLATFORM_POLICIES_PATH).open("r") as f:
            return f.read()
    except FileNotFoundError:
        return "No policy file found. Use standard character limits."


def _build_system_prompt(policies: str) -> str:
    return f"""You are a media planning specialist. Generate a structured campaign plan in strict JSON.

Platform constraints (must respect):
{policies}

Output ONLY valid JSON matching this schema. No markdown, no explanation:
{{
  "objective": "sales" | "leads",
  "daily_budget": number,
  "geo": ["US"] or given country codes,
  "lang": ["en"] or given languages,
  "product_categories": ["..."] from input,
  "creative_pack": {{
    "headlines": ["max 30 chars each", ...],
    "descriptions": ["max 90 chars each", ...],
    "long_headlines": ["max 90 chars each", ...],
    "primary_texts": ["max 125 chars for Meta", ...],
    "callouts": ["Free returns", "Fast shipping", ...],
    "image_urls": ["https://placeholder.com/hero1.jpg", ...],
    "logo_url": "https://placeholder.com/logo.png"
  }},
  "targeting_hints": {{
    "keywords": ["relevant keywords"],
    "audiences": ["target segments"],
    "placements": ["shopping surfaces"]
  }},
  "bidding_strategy": "maximize_conversion_value"
}}"""


def _build_user_prompt(objective: str, daily_budget: float, categories: list[str], country: str | None, lang: str | None) -> str:
    geo = [country] if country else ["US"]
    langs = [lang] if lang else ["en"]
    return f"""Create a media plan with:
- Objective: {objective}
- Daily budget: ${daily_budget}
- Product categories: {', '.join(categories)}
- Geo: {geo}
- Language: {langs}

Generate compelling headlines and descriptions for these products. Use placeholder image URLs like https://picsum.photos/400/400?random=1"""


def _extract_json(text: str) -> dict:
    """Extract JSON from model output, handle code blocks."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return json.loads(text)


def _validate_and_repair(plan: dict) -> tuple[dict | None, list[str]]:
    """Validate plan against schema, return issues."""
    issues = []
    try:
        cp = plan.get("creative_pack", {})
        th = plan.get("targeting_hints", {})
        for h in cp.get("headlines", [])[:5]:
            if len(h) > 30:
                issues.append(f"Headline too long ({len(h)}): {h[:20]}...")
        for d in cp.get("descriptions", [])[:3]:
            if len(d) > 90:
                issues.append(f"Description too long ({len(d)}): {d[:30]}...")
        # Basic schema check
        if not plan.get("objective") or plan.get("objective") not in ("sales", "leads"):
            plan["objective"] = "sales"
        if not isinstance(plan.get("creative_pack"), dict):
            plan["creative_pack"] = {
                "headlines": ["Shop Now"],
                "descriptions": ["Discover great products"],
                "long_headlines": [],
                "primary_texts": [],
                "callouts": ["Free shipping"],
                "image_urls": ["https://picsum.photos/400/400"],
                "logo_url": "https://picsum.photos/128/128",
            }
        if not isinstance(plan.get("targeting_hints"), dict):
            plan["targeting_hints"] = {"keywords": [], "audiences": [], "placements": []}
        return plan, issues
    except Exception as e:
        issues.append(str(e))
        return None, issues


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((json.JSONDecodeError, KeyError, TypeError)),
)
def generate_plan(
    objective: str,
    daily_budget: float,
    product_categories: list[str],
    country: str | None = None,
    language: str | None = None,
) -> MediaPlan:
    """
    Generate a structured media plan with validation and retries.
    """
    policies = _load_policies()

    use_real_api = bool(settings.openai_api_key and len(settings.openai_api_key) > 20 and not settings.openai_api_key.startswith("sk-mock"))
    for step in range(MAX_PLANNING_STEPS):
        try:
            # Use real API if key present, else mock
            if use_real_api:
                client = OpenAI(api_key=settings.openai_api_key)
                response = client.chat.completions.create(
                    model=settings.planner_model,
                    messages=[
                        {"role": "system", "content": _build_system_prompt(policies)},
                        {"role": "user", "content": _build_user_prompt(objective, daily_budget, product_categories, country, language)},
                    ],
                    temperature=0.3,
                )
                text = response.choices[0].message.content or "{}"
            else:
                # Mock plan when no API key
                text = json.dumps(_mock_plan(objective, daily_budget, product_categories, country, language))

            raw = _extract_json(text)
            plan, issues = _validate_and_repair(raw)
            if plan is None:
                raise ValueError("Validation failed: " + "; ".join(issues))
            return MediaPlan(
                objective=plan["objective"],
                daily_budget=plan["daily_budget"],
                geo=plan.get("geo", ["US"]),
                lang=plan.get("lang", ["en"]),
                product_categories=plan.get("product_categories", product_categories),
                creative_pack=CreativePack(**plan["creative_pack"]),
                targeting_hints=TargetingHints(**plan["targeting_hints"]),
                bidding_strategy=plan.get("bidding_strategy", "maximize_conversion_value"),
            )
        except Exception as e:
            logger.warning("Plan step %s failed: %s", step + 1, e)
            if step == MAX_PLANNING_STEPS - 1:
                return _mock_plan_schema(objective, daily_budget, product_categories)
            continue

    return _mock_plan_schema(objective, daily_budget, product_categories)


def _mock_plan(objective: str, budget: float, categories: list[str], country: str | None, lang: str | None) -> dict:
    geo = [country] if country else ["US"]
    langs = [lang] if lang else ["en"]
    return {
        "objective": objective,
        "daily_budget": budget,
        "geo": geo,
        "lang": langs,
        "product_categories": categories,
        "creative_pack": {
            "headlines": [f"Shop {c}"[:30] for c in categories[:3]],
            "descriptions": [f"Discover premium {c}. Free shipping on orders over $50."[:90] for c in categories[:2]],
            "long_headlines": [f"Explore our {c} collection - Quality & style"[:90] for c in categories[:2]],
            "primary_texts": [f"Find the best {c} online. Fast delivery."[:125] for c in categories[:2]],
            "callouts": ["Free returns", "Fast shipping"],
            "image_urls": ["https://picsum.photos/400/400?random=1", "https://picsum.photos/600/600?random=2"],
            "logo_url": "https://picsum.photos/128/128",
        },
        "targeting_hints": {
            "keywords": [f"{c} best" for c in categories[:3]] + ["free shipping"],
            "audiences": ["shoppers", "deal seekers"],
            "placements": ["shopping surfaces"],
        },
        "bidding_strategy": "maximize_conversion_value",
    }


def _mock_plan_schema(objective: str, budget: float, categories: list[str]) -> MediaPlan:
    raw = _mock_plan(objective, budget, categories, None, None)
    return MediaPlan(
        objective=raw["objective"],
        daily_budget=raw["daily_budget"],
        geo=raw["geo"],
        lang=raw["lang"],
        product_categories=raw["product_categories"],
        creative_pack=CreativePack(**raw["creative_pack"]),
        targeting_hints=TargetingHints(**raw["targeting_hints"]),
        bidding_strategy=raw["bidding_strategy"],
    )
