"""Optimization suggestions from performance data."""
from typing import TYPE_CHECKING
from app.schemas import OptimizationSuggestion

if TYPE_CHECKING:
    pass


def analyze_and_suggest(campaigns_with_metrics: list[dict]) -> list[OptimizationSuggestion]:
    """
    Analyze performance and produce structured recommendations.
    """
    suggestions = []
    if not campaigns_with_metrics:
        return suggestions

    # Aggregate by platform for comparison
    by_platform: dict[str, list] = {}
    for c in campaigns_with_metrics:
        p = c.get("platform", "unknown")
        by_platform.setdefault(p, []).append(c)

    # Check CTR
    for c in campaigns_with_metrics:
        ctr = c.get("ctr") or 0
        spend = c.get("spend") or 0
        if ctr < 1.0 and spend > 20:
            suggestions.append(
                OptimizationSuggestion(
                    campaign_id=c.get("id", 0),
                    platform=c.get("platform", ""),
                    issue_detected="Low CTR",
                    recommended_action="Refresh creatives and test new headlines",
                    reasoning=f"CTR {ctr}% is below 1%. Spend ${spend:.0f} suggests opportunity.",
                    confidence=0.72,
                )
            )

    # Cross-platform reallocation
    platform_ctr: dict[str, float] = {}
    platform_spend: dict[str, float] = {}
    for p, items in by_platform.items():
        total_spend = sum(x.get("spend", 0) for x in items)
        total_clicks = sum(x.get("clicks", 0) for x in items)
        total_imp = sum(x.get("impressions", 0) for x in items)
        platform_spend[p] = total_spend
        platform_ctr[p] = (total_clicks / total_imp * 100) if total_imp else 0

    if len(platform_ctr) >= 2:
        best = max(platform_ctr, key=platform_ctr.get)
        worst = min(platform_ctr, key=platform_ctr.get)
        if platform_ctr[best] > platform_ctr[worst] * 1.5:
            c = next((x for x in campaigns_with_metrics if x.get("platform") == worst), None)
            if c:
                suggestions.append(
                    OptimizationSuggestion(
                        campaign_id=c.get("id", 0),
                        platform=worst,
                        issue_detected="Low CTR vs other platforms",
                        recommended_action=f"Reallocate ${min(30, platform_spend.get(worst, 0) * 0.2):.0f}/day from {worst.title()} to {best.title()}",
                        reasoning=f"{best.title()} CTR {platform_ctr[best]:.1f}% vs {worst.title()} {platform_ctr[worst]:.1f}%",
                        confidence=0.76,
                    )
                )

    return suggestions[:5]
