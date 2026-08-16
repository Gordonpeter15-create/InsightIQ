import pandas as pd


def _money(value: float) -> str:
    return f"${value:,.2f}"


def answer_question(question: str, df: pd.DataFrame, performance: pd.DataFrame) -> str:
    """Answer common plain-English questions from the currently filtered sales data."""
    text = question.lower().strip()
    total_revenue = float(df["Revenue"].sum())
    best_revenue = performance.iloc[0]
    lowest_revenue = performance.iloc[-1]
    top_units = performance.sort_values("Units_Sold", ascending=False).iloc[0]
    daily = df.groupby("Date", as_index=False)["Revenue"].sum()
    highest_day = daily.loc[daily["Revenue"].idxmax()]

    for product in performance["Product"]:
        if str(product).lower() in text:
            row = performance[performance["Product"] == product].iloc[0]
            return (
                f"{product} generated {_money(float(row['Revenue']))}, "
                f"sold {int(row['Units_Sold']):,} units, and appeared in {int(row['Orders']):,} order(s)."
            )

    if any(word in text for word in ("most revenue", "best product", "top product", "highest product")):
        return f"{best_revenue['Product']} made the most revenue: {_money(float(best_revenue['Revenue']))}."

    if any(word in text for word in ("most units", "most sold", "best selling", "best-selling")):
        return f"{top_units['Product']} sold the most units: {int(top_units['Units_Sold']):,}."

    if any(word in text for word in ("lowest", "worst", "least", "underperform")):
        return f"{lowest_revenue['Product']} had the lowest revenue: {_money(float(lowest_revenue['Revenue']))}."

    if any(word in text for word in ("highest day", "highest revenue day", "best day", "top day")):
        return f"The highest-revenue day was {highest_day['Date'].date()}: {_money(float(highest_day['Revenue']))}."

    if any(word in text for word in ("total", "how much", "revenue", "sales")):
        return f"The selected data generated {_money(total_revenue)} in total revenue."

    return (
        "I can answer questions about total revenue, best or lowest products, units sold, "
        "highest-revenue days, or a specific product."
    )
