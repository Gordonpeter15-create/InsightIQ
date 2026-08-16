"""Decision-support calculations for InsightIQ's Business Advisor.

Recommendations are deliberately evidence-led: no stock level, supplier, promotion,
or customer claim is made unless that data exists in the uploaded file.
"""

from __future__ import annotations

import pandas as pd


MIN_DATES_FOR_COMPARISON = 8
SIGNIFICANT_CHANGE_PERCENT = 15.0
MIN_PREVIOUS_REVENUE_SHARE = 0.03


def _percent_change(recent: float, previous: float) -> float | None:
    return None if previous == 0 else (recent - previous) / previous * 100


def _comparison_periods(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame] | None:
    """Split the available date history into two equal, consecutive periods."""
    dates = pd.Series(df["Date"].dropna().unique()).sort_values().tolist()
    if len(dates) < MIN_DATES_FOR_COMPARISON:
        return None
    period_size = len(dates) // 2
    previous_dates = dates[-2 * period_size : -period_size]
    recent_dates = dates[-period_size:]
    return df[df["Date"].isin(previous_dates)], df[df["Date"].isin(recent_dates)]


def _product_change(previous: pd.DataFrame, recent: pd.DataFrame) -> pd.DataFrame:
    before = previous.groupby("Product").agg(
        Previous_Revenue=("Revenue", "sum"), Previous_Quantity=("Quantity", "sum")
    )
    after = recent.groupby("Product").agg(
        Recent_Revenue=("Revenue", "sum"), Recent_Quantity=("Quantity", "sum")
    )
    result = before.join(after, how="outer").fillna(0).reset_index()
    result["Revenue_Change_Percent"] = result.apply(
        lambda row: _percent_change(row["Recent_Revenue"], row["Previous_Revenue"]), axis=1
    )
    result["Quantity_Change_Percent"] = result.apply(
        lambda row: _percent_change(row["Recent_Quantity"], row["Previous_Quantity"]), axis=1
    )
    return result


def _revenue_change_explanation(
    previous: pd.DataFrame, recent: pd.DataFrame, products: pd.DataFrame
) -> dict[str, str]:
    previous_revenue, recent_revenue = float(previous["Revenue"].sum()), float(recent["Revenue"].sum())
    revenue_change = _percent_change(recent_revenue, previous_revenue)
    previous_quantity, recent_quantity = float(previous["Quantity"].sum()), float(recent["Quantity"].sum())
    quantity_change = _percent_change(recent_quantity, previous_quantity)
    previous_price = previous_revenue / previous_quantity if previous_quantity else 0
    recent_price = recent_revenue / recent_quantity if recent_quantity else 0
    price_change = _percent_change(recent_price, previous_price)

    if revenue_change is None:
        return {"headline": "Insufficient previous revenue for a reliable comparison.", "detail": ""}

    direction = "increased" if revenue_change >= 0 else "decreased"
    contribution = products.assign(Contribution=products["Recent_Revenue"] - products["Previous_Revenue"])
    contribution = contribution[contribution["Contribution"] != 0]
    contribution = contribution.sort_values("Contribution", ascending=revenue_change < 0).head(3)
    contributors = ", ".join(contribution["Product"].astype(str).tolist()) or "no individual product"
    volume_note = (
        f"Sales volume {('rose' if quantity_change >= 0 else 'fell')} {abs(quantity_change):.1f}%"
        if quantity_change is not None and abs(quantity_change) >= 5
        else "Sales volume changed only slightly"
    )
    price_note = (
        f"average selling price {('rose' if price_change >= 0 else 'fell')} {abs(price_change):.1f}%"
        if price_change is not None and abs(price_change) >= 5
        else "average selling price changed only slightly"
    )
    return {
        "headline": f"Observed: revenue {direction} {abs(revenue_change):.1f}% in the recent period.",
        "detail": (
            f"Derived: the largest product contributors were {contributors}. "
            f"{volume_note}; {price_note}. This describes the data and does not prove causation."
        ),
    }


def _seasonal_signal(df: pd.DataFrame) -> str:
    if df["Date"].nunique() < 21:
        return "Insufficient data to determine seasonal or weekend patterns reliably."
    daily = df.groupby("Date", as_index=False)["Revenue"].sum()
    daily["Is_Weekend"] = daily["Date"].dt.dayofweek >= 5
    weekend, weekday = daily[daily["Is_Weekend"]], daily[~daily["Is_Weekend"]]
    if len(weekend) < 3 or len(weekday) < 3:
        return "Insufficient weekend and weekday observations to determine a reliable pattern."
    change = _percent_change(float(weekend["Revenue"].mean()), float(weekday["Revenue"].mean()))
    if change is not None and abs(change) >= 15:
        return f"Observed: average weekend revenue is {abs(change):.1f}% {('higher' if change > 0 else 'lower')} than weekday revenue."
    return "Observed: no strong weekend-versus-weekday revenue difference appears in the available data."


def analyze_business_advisor(df: pd.DataFrame) -> dict:
    """Return all evidence and action recommendations used by the Advisor page."""
    periods = _comparison_periods(df)
    if periods is None:
        return {
            "has_comparison": False,
            "message": f"Insufficient data to compare recent performance reliably. Upload at least {MIN_DATES_FOR_COMPARISON} different sales dates.",
            "declining": pd.DataFrame(),
            "momentum": pd.DataFrame(),
            "seasonal": _seasonal_signal(df),
            "actions": [{
                "priority": "🟡 Watch",
                "title": "Collect more daily sales history",
                "detail": "Next step: keep recording daily sales. More dates are needed before product movement can be assessed reliably.",
            }],
        }

    previous, recent = periods
    products = _product_change(previous, recent)
    material_revenue = max(float(previous["Revenue"].sum()) * MIN_PREVIOUS_REVENUE_SHARE, 1.0)
    declining = products[
        (products["Previous_Revenue"] >= material_revenue)
        & (products["Revenue_Change_Percent"] <= -SIGNIFICANT_CHANGE_PERCENT)
    ].sort_values("Revenue_Change_Percent")
    momentum = products[
        (products["Previous_Revenue"] >= material_revenue)
        & (products["Revenue_Change_Percent"] >= SIGNIFICANT_CHANGE_PERCENT)
    ].sort_values("Revenue_Change_Percent", ascending=False)

    actions: list[dict[str, str]] = []
    for row in declining.head(2).itertuples():
        actions.append({
            "priority": "🔴 High Priority",
            "title": f"Review {row.Product}",
                "detail": (
                    f"Observed: revenue fell {abs(row.Revenue_Change_Percent):.1f}% "
                    f"(${row.Previous_Revenue:,.2f} → ${row.Recent_Revenue:,.2f}). "
                    "Next step: check availability, price, shelf placement, and local demand."
                ),
        })
    for row in momentum.head(2).itertuples():
        actions.append({
            "priority": "🟢 Opportunity",
            "title": f"Watch demand for {row.Product}",
            "detail": (
                f"Observed: revenue rose {row.Revenue_Change_Percent:.1f}% and quantity moved "
                f"from {row.Previous_Quantity:,.0f} to {row.Recent_Quantity:,.0f}. "
                "Next step: review stock before the next order. Current stock is not available in this dataset."
            ),
        })
    if not actions:
        actions.append({
            "priority": "🟡 Watch",
            "title": "No major product movement detected",
            "detail": f"Observed: no material product crossed the {SIGNIFICANT_CHANGE_PERCENT:.0f}% change threshold between comparison periods. Continue monitoring.",
        })

    return {
        "has_comparison": True,
        "message": "",
        "comparison": _revenue_change_explanation(previous, recent, products),
        "declining": declining,
        "momentum": momentum,
        "seasonal": _seasonal_signal(df),
        "actions": actions,
        "previous_dates": (previous["Date"].min(), previous["Date"].max()),
        "recent_dates": (recent["Date"].min(), recent["Date"].max()),
    }
