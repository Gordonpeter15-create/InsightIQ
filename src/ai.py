import pandas as pd


def generate_insights(df: pd.DataFrame, performance: pd.DataFrame) -> list[str]:
    """Generate transparent, rule-based business insights from the selected data."""
    total_revenue = float(df["Revenue"].sum())
    best = performance.iloc[0]
    lowest = performance.iloc[-1]
    share = (float(best["Revenue"]) / total_revenue * 100) if total_revenue else 0

    insights = [
        f"🏆 {best['Product']} generates {share:.1f}% of the selected revenue.",
        f"📉 {lowest['Product']} has the lowest revenue at ${lowest['Revenue']:,.2f}.",
    ]
    if share >= 60:
        insights.append("⚠️ Revenue is concentrated in one product; diversify products or strengthen alternatives.")
    else:
        insights.append("✅ Revenue is spread across products, reducing reliance on a single item.")
    return insights
