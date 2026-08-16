import pandas as pd
import plotly.express as px


def revenue_by_product_chart(performance: pd.DataFrame):
    return px.bar(
        performance,
        x="Product",
        y="Revenue",
        color="Product",
        text_auto=".2s",
        title="",
    ).update_layout(showlegend=False, yaxis_title="Revenue", xaxis_title="")


def revenue_distribution_chart(performance: pd.DataFrame):
    return px.pie(
        performance,
        names="Product",
        values="Revenue",
        hole=0.55,
        title="",
    )


def revenue_over_time_chart(df: pd.DataFrame):
    daily = df.groupby("Date", as_index=False)["Revenue"].sum()
    return px.line(
        daily,
        x="Date",
        y="Revenue",
        markers=True,
        title="",
    ).update_layout(yaxis_title="Revenue", xaxis_title="")


def monthly_revenue_chart(df: pd.DataFrame):
    monthly = df.assign(Month=df["Date"].dt.to_period("M").astype(str)).groupby(
        "Month", as_index=False
    )["Revenue"].sum()
    return px.bar(monthly, x="Month", y="Revenue", text_auto=".2s", title="").update_layout(
        yaxis_title="Revenue", xaxis_title=""
    )
