"""Evidence-led inventory guidance for supermarket sales data.

Specific stock risk is only calculated when an uploaded file includes stock fields.
Without those fields, this module reports the limitation rather than guessing.
"""

from __future__ import annotations

import re

import pandas as pd


STOCK_ALIASES = {"currentstock", "stocklevel", "stockonhand", "onhandstock"}
REORDER_ALIASES = {"reorderpoint", "minimumstock", "minstock"}
LEAD_TIME_ALIASES = {"leadtime", "leadtimedays", "supplierleaddays"}
PRIORITIES = ("🔴 High Priority", "🟡 Watch", "🟢 Opportunity")


def _normalise(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _find_column(df: pd.DataFrame, aliases: set[str]) -> str | None:
    return next((column for column in df.columns if _normalise(column) in aliases), None)


def inventory_columns(df: pd.DataFrame) -> dict[str, str | None]:
    """Identify supported optional inventory columns without modifying the source dataframe."""
    return {
        "stock": _find_column(df, STOCK_ALIASES),
        "reorder_point": _find_column(df, REORDER_ALIASES),
        "lead_time": _find_column(df, LEAD_TIME_ALIASES),
    }


def inventory_summary(items: pd.DataFrame) -> dict[str, int]:
    """Return product counts for the three inventory review states."""
    counts = items["Priority"].value_counts() if "Priority" in items else pd.Series(dtype=int)
    return {priority: int(counts.get(priority, 0)) for priority in PRIORITIES}


def inventory_guidance(df: pd.DataFrame) -> dict:
    """Return safe inventory status and product-level guidance.

    Uses the latest supplied stock/reorder values for each product. It never
    predicts stock-outs or recommends exact order quantities.
    """
    columns = inventory_columns(df)
    if columns["stock"] is None:
        return {
            "available": False,
            "message": (
                "Inventory guidance is limited because this file has no Current Stock or Stock Level column. "
                "Add current stock and a reorder point for product-level stock risk guidance."
            ),
            "items": pd.DataFrame(),
            "summary": inventory_summary(pd.DataFrame()),
            "columns": columns,
        }

    stock_column = columns["stock"]
    working = df.copy().sort_values("Date")
    working["_stock"] = pd.to_numeric(working[stock_column], errors="coerce")
    reorder_column = columns["reorder_point"]
    lead_time_column = columns["lead_time"]
    if reorder_column:
        working["_reorder"] = pd.to_numeric(working[reorder_column], errors="coerce")
    if lead_time_column:
        working["_lead_time"] = pd.to_numeric(working[lead_time_column], errors="coerce")

    days_observed = max(df["Date"].nunique(), 1)
    sales_rate = df.groupby("Product")["Quantity"].sum().div(days_observed).rename("Average_Daily_Units")
    rows: list[dict] = []
    for product, group in working.groupby("Product", sort=False):
        latest = group.dropna(subset=["_stock"]).tail(1)
        if latest.empty:
            continue
        record = latest.iloc[0]
        stock = float(record["_stock"])
        reorder = float(record["_reorder"]) if reorder_column and pd.notna(record.get("_reorder")) else None
        lead_time = float(record["_lead_time"]) if lead_time_column and pd.notna(record.get("_lead_time")) else None
        daily_units = float(sales_rate.get(product, 0))

        if reorder is None:
            priority = "🟡 Watch"
            action = "Add a reorder point"
            reason = f"Current stock is {stock:,.0f}, but no reorder point is available for comparison."
        elif stock <= reorder:
            priority = "🔴 High Priority"
            action = "Review reorder now"
            reason = f"Current stock ({stock:,.0f}) is at or below its reorder point ({reorder:,.0f})."
        elif stock <= reorder * 1.25:
            priority = "🟡 Watch"
            action = "Monitor stock closely"
            reason = f"Current stock ({stock:,.0f}) is close to its reorder point ({reorder:,.0f})."
        else:
            priority = "🟢 Opportunity"
            action = "Continue monitoring"
            reason = f"Current stock ({stock:,.0f}) is above its reorder point ({reorder:,.0f})."

        if lead_time is not None and lead_time > 0:
            expected_demand = daily_units * lead_time
            reason += (
                f" Observed sales pace is {daily_units:.1f} units per recorded day; "
                f"that is about {expected_demand:.1f} units over the stated {lead_time:.0f}-day lead time."
            )

        # Simple arithmetic estimate: supplied stock divided by the observed sales pace.
        days_of_stock = stock / daily_units if daily_units > 0 else None
        if days_of_stock is not None:
            reason += f" Estimate: at the observed pace, current stock covers about {days_of_stock:.1f} recorded day(s) of sales"
            if lead_time is not None and lead_time > 0:
                comparison = "shorter than" if days_of_stock < lead_time else "at least"
                reason += f", {comparison} the stated {lead_time:.0f}-day lead time"
            reason += "."
            # Above the reorder point but not covering the supplied lead time still deserves a look.
            if priority == "🟢 Opportunity" and lead_time is not None and lead_time > 0 and days_of_stock < lead_time:
                priority = "🟡 Watch"
                action = "Check stock before the next order"
                reason += " Moved to Watch: stock is above the reorder point but may not cover the lead time at this pace."
        rows.append({
            "Product": product,
            "Current_Stock": stock,
            "Reorder_Point": reorder,
            "Lead_Time_Days": lead_time,
            "Average_Daily_Units": daily_units,
            "Days_Of_Stock": days_of_stock,
            "Priority": priority,
            "Recommended_Action": action,
            "Reason": reason,
        })

    items = pd.DataFrame(rows)
    if not items.empty:
        rank = {"🔴 High Priority": 0, "🟡 Watch": 1, "🟢 Opportunity": 2}
        items["_rank"] = items["Priority"].map(rank)
        items = items.sort_values(["_rank", "Product"]).drop(columns="_rank").reset_index(drop=True)
    return {
        "available": True,
        "message": "Inventory guidance uses the latest stock values supplied in the uploaded data.",
        "items": items,
        "summary": inventory_summary(items),
        "columns": columns,
    }
