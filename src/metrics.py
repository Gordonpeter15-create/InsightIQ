import pandas as pd


def calculate_metrics(df: pd.DataFrame) -> dict[str, float | int]:
    total_revenue = float(df["Revenue"].sum())
    total_orders = len(df)
    total_items = int(df["Quantity"].sum())
    average_order = total_revenue / total_orders if total_orders else 0.0
    return {
        "revenue": total_revenue,
        "orders": total_orders,
        "items": total_items,
        "average_order": average_order,
    }


def product_performance(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Product", as_index=False)
        .agg(Revenue=("Revenue", "sum"), Units_Sold=("Quantity", "sum"), Orders=("Product", "size"))
        .sort_values("Revenue", ascending=False)
        .reset_index(drop=True)
    )
