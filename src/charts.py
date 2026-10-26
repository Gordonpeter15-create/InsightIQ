import pandas as pd
import plotly.express as px

from src.currency import DEFAULT_CURRENCY, money_label


# Matches chartCategoricalColors in .streamlit/config.toml so every chart uses the brand palette.
BRAND_COLORS = ["#6366F1", "#22C55E", "#F59E0B", "#06B6D4", "#EC4899", "#A78BFA", "#84CC16", "#F97316"]


def revenue_by_product_chart(performance: pd.DataFrame, currency: str = DEFAULT_CURRENCY):
    return px.bar(
        performance,
        x="Product",
        y="Revenue",
        text_auto=".2s",
        title="",
    ).update_layout(showlegend=False, yaxis_title=money_label("Revenue", currency), xaxis_title="")


def revenue_distribution_chart(performance: pd.DataFrame):
    return px.pie(
        performance,
        names="Product",
        values="Revenue",
        hole=0.62,
        title="",
        color_discrete_sequence=BRAND_COLORS,
    ).update_traces(marker_line_color="#0B0D12", marker_line_width=2)


def revenue_over_time_chart(df: pd.DataFrame, currency: str = DEFAULT_CURRENCY):
    daily = df.groupby("Date", as_index=False)["Revenue"].sum()
    return px.line(
        daily,
        x="Date",
        y="Revenue",
        markers=True,
        title="",
    ).update_layout(yaxis_title=money_label("Revenue", currency), xaxis_title="")


def day_of_week_chart(table: pd.DataFrame, currency: str = DEFAULT_CURRENCY):
    """Average revenue per recorded day for each weekday, from day_of_week_pattern()."""
    return px.bar(
        table,
        x="Day",
        y="Average_Revenue",
        text_auto=".2s",
        hover_data={"Recorded_Days": True},
        labels={"Recorded_Days": "Recorded days", "Average_Revenue": "Average revenue"},
        title="",
    ).update_layout(yaxis_title=money_label("Average per recorded day", currency), xaxis_title="")


def monthly_revenue_chart(df: pd.DataFrame, currency: str = DEFAULT_CURRENCY):
    monthly = df.assign(Month=df["Date"].dt.to_period("M").astype(str)).groupby(
        "Month", as_index=False
    )["Revenue"].sum()
    return px.bar(monthly, x="Month", y="Revenue", text_auto=".2s", title="").update_layout(
        yaxis_title=money_label("Revenue", currency), xaxis_title=""
    )
