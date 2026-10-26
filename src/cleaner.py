import pandas as pd


REQUIRED_COLUMNS = {"Date", "Product", "Quantity", "Price"}


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and prepare a sales dataset for InsightIQ."""
    return clean_data_with_report(df)[0]


def clean_data_with_report(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean a sales dataset and explain every row that was removed.

    Each removed row is counted once, under the first check it fails, so the
    counts add up to the total number of rows skipped.
    """
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(sorted(missing))}.")

    original = df.copy()
    duplicates = original.duplicated()
    cleaned = original[~duplicates].copy()
    # Mixed parsing accepts normal spreadsheet date formats while invalid entries become NaT.
    cleaned["Date"] = pd.to_datetime(cleaned["Date"], errors="coerce", format="mixed")
    cleaned["Quantity"] = pd.to_numeric(cleaned["Quantity"], errors="coerce")
    cleaned["Price"] = pd.to_numeric(cleaned["Price"], errors="coerce")

    checks = [
        ("Missing or unreadable date", cleaned["Date"].isna()),
        ("Missing product name", cleaned["Product"].isna()),
        ("Missing or non-numeric quantity", cleaned["Quantity"].isna()),
        ("Missing or non-numeric price", cleaned["Price"].isna()),
        ("Negative quantity or price", (cleaned["Quantity"] < 0) | (cleaned["Price"] < 0)),
    ]
    reasons = pd.Series(pd.NA, index=cleaned.index, dtype="object")
    for reason, failed in checks:
        reasons = reasons.mask(reasons.isna() & failed, reason)

    skipped = original.loc[reasons.dropna().index].assign(Reason=reasons.dropna())
    skipped = pd.concat([original[duplicates].assign(Reason="Exact duplicate row"), skipped])
    skipped = skipped.sort_index()
    if df.attrs.get("spreadsheet_rows"):
        row_numbers = list(skipped.index)
    else:
        # Without file row numbers, assume a header on row 1 and records from row 2.
        row_numbers = [position + 2 for position in original.index.get_indexer(skipped.index)]
    skipped.insert(0, "Row", row_numbers)
    skipped.insert(1, "Reason", skipped.pop("Reason"))

    cleaned = cleaned[reasons.isna()].copy()
    cleaned["Revenue"] = cleaned["Quantity"] * cleaned["Price"]
    cleaned = cleaned.sort_values("Date").reset_index(drop=True)

    counts = skipped["Reason"].value_counts()
    report = {
        "rows_received": len(original),
        "rows_kept": len(cleaned),
        "rows_skipped": len(skipped),
        "reasons": [(reason, int(counts[reason])) for reason in
                    ["Exact duplicate row"] + [name for name, _ in checks] if reason in counts],
        "skipped_rows": skipped.reset_index(drop=True),
    }
    return cleaned, report
