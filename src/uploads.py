"""Helpers for reading sales uploads with a recognisable column header row."""

from __future__ import annotations

import pandas as pd

from src.cleaner import REQUIRED_COLUMNS


HEADER_SCAN_ROWS = 20
# DataFrame.attrs flag: the index holds the row numbers shown in the spreadsheet.
SPREADSHEET_ROWS = "spreadsheet_rows"


def find_sales_header_row(raw: pd.DataFrame) -> int | None:
    """Find the first row that contains InsightIQ's required sales headers."""
    for position in range(min(len(raw), HEADER_SCAN_ROWS)):
        headers = {str(value).strip() for value in raw.iloc[position].dropna()}
        if REQUIRED_COLUMNS.issubset(headers):
            return position
    return None


def dataframe_from_excel(uploaded_file) -> pd.DataFrame:
    """Read a normal spreadsheet or one with a title/instructions above its headers."""
    raw = pd.read_excel(uploaded_file, header=None)
    header_row = find_sales_header_row(raw)
    if header_row is None:
        required = ", ".join(sorted(REQUIRED_COLUMNS))
        raise ValueError(f"Could not find a header row containing: {required}.")

    dataframe = raw.iloc[header_row + 1 :].copy()
    dataframe.columns = [str(value).strip() for value in raw.iloc[header_row]]
    dataframe = dataframe.dropna(how="all")
    # pandas row 0 is spreadsheet row 1, so this keeps the row numbers people see in Excel.
    dataframe.index = dataframe.index + 1
    dataframe.attrs[SPREADSHEET_ROWS] = True
    return dataframe


def dataframe_from_csv(uploaded_file) -> pd.DataFrame:
    dataframe = pd.read_csv(uploaded_file)
    # The header is row 1, so the first record is row 2.
    dataframe.index = dataframe.index + 2
    dataframe.attrs[SPREADSHEET_ROWS] = True
    return dataframe


def read_sales_file(uploaded_file) -> pd.DataFrame:
    """Read an uploaded CSV or Excel file, indexed by its spreadsheet row numbers."""
    if uploaded_file.name.lower().endswith(".csv"):
        return dataframe_from_csv(uploaded_file)
    return dataframe_from_excel(uploaded_file)
