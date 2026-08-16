import pandas as pd


REQUIRED_COLUMNS = {"Date", "Product", "Quantity", "Price"}


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and prepare a sales dataset for InsightIQ."""
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(sorted(missing))}.")

    cleaned = df.copy().drop_duplicates()
    cleaned["Date"] = pd.to_datetime(cleaned["Date"], errors="coerce")
    cleaned["Quantity"] = pd.to_numeric(cleaned["Quantity"], errors="coerce")
    cleaned["Price"] = pd.to_numeric(cleaned["Price"], errors="coerce")
    cleaned = cleaned.dropna(subset=["Date", "Product", "Quantity", "Price"])
    cleaned = cleaned[(cleaned["Quantity"] >= 0) & (cleaned["Price"] >= 0)]
    cleaned["Revenue"] = cleaned["Quantity"] * cleaned["Price"]
    return cleaned.sort_values("Date").reset_index(drop=True)
