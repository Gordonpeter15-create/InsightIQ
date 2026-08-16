import numpy as np
import pandas as pd
import plotly.graph_objects as go


def forecast_revenue(df: pd.DataFrame, days_ahead: int = 7) -> pd.DataFrame | None:
    """Estimate daily revenue with a linear trend when enough daily data exists."""
    daily = df.groupby("Date", as_index=False)["Revenue"].sum().sort_values("Date")
    if daily["Date"].nunique() < 7:
        return None

    x = np.arange(len(daily))
    slope, intercept = np.polyfit(x, daily["Revenue"].to_numpy(), deg=1)
    future_dates = pd.date_range(daily["Date"].max() + pd.Timedelta(days=1), periods=days_ahead)
    future_x = np.arange(len(daily), len(daily) + days_ahead)
    prediction = np.maximum(0, slope * future_x + intercept)

    return pd.DataFrame({"Date": future_dates, "Revenue": prediction})


def forecast_revenue_chart(df: pd.DataFrame, forecast: pd.DataFrame):
    daily = df.groupby("Date", as_index=False)["Revenue"].sum().sort_values("Date")
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=daily["Date"],
            y=daily["Revenue"],
            mode="lines+markers",
            name="Actual revenue",
            line={"color": "#22C55E"},
        )
    )
    figure.add_trace(
        go.Scatter(
            x=forecast["Date"],
            y=forecast["Revenue"],
            mode="lines+markers",
            name="Forecast",
            line={"dash": "dash", "color": "#4F46E5"},
        )
    )
    return figure.update_layout(yaxis_title="Revenue", xaxis_title="", showlegend=True)
