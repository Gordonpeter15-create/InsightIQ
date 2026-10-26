"""Upload checks, day-of-week patterns, and days-of-stock estimates."""

import io
import unittest
from datetime import date, timedelta

import pandas as pd
from openpyxl import Workbook

from src.advisor import day_of_week_pattern
from src.cleaner import clean_data, clean_data_with_report
from src.inventory import inventory_guidance
from src.uploads import read_sales_file


class NamedBytes(io.BytesIO):
    """Mimics Streamlit's UploadedFile, which exposes the file name."""

    def __init__(self, data: bytes, name: str):
        super().__init__(data)
        self.name = name


def daily_sales(revenue_by_weekday: dict[int, float], days: int = 28, start: date = date(2026, 1, 5)):
    """One Rice sale per day; 2026-01-05 is a Monday, so weekday 0 is Monday."""
    rows = []
    for offset in range(days):
        day = start + timedelta(days=offset)
        if day.weekday() in revenue_by_weekday:
            rows.append({"Date": day.isoformat(), "Product": "Rice", "Quantity": 1, "Price": revenue_by_weekday[day.weekday()]})
    return clean_data(pd.DataFrame(rows))


class UploadReportTests(unittest.TestCase):
    def test_each_skipped_row_is_counted_once_with_its_reason(self):
        raw = pd.DataFrame([
            {"Date": "2026-01-01", "Product": "Rice", "Quantity": 2, "Price": 10},
            {"Date": "2026-01-01", "Product": "Rice", "Quantity": 2, "Price": 10},
            {"Date": "not a date", "Product": "Milk", "Quantity": 1, "Price": 5},
            {"Date": "2026-01-02", "Product": None, "Quantity": 1, "Price": 5},
            {"Date": "2026-01-02", "Product": "Soap", "Quantity": "abc", "Price": 5},
            {"Date": "2026-01-02", "Product": "Soap", "Quantity": 3, "Price": None},
            {"Date": "2026-01-03", "Product": "Oil", "Quantity": -1, "Price": 5},
        ])
        cleaned, report = clean_data_with_report(raw)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual((report["rows_received"], report["rows_kept"], report["rows_skipped"]), (7, 1, 6))
        self.assertEqual(sum(count for _, count in report["reasons"]), 6)
        self.assertEqual(
            report["skipped_rows"][["Row", "Reason"]].values.tolist(),
            [
                [3, "Exact duplicate row"],
                [4, "Missing or unreadable date"],
                [5, "Missing product name"],
                [6, "Missing or non-numeric quantity"],
                [7, "Missing or non-numeric price"],
                [8, "Negative quantity or price"],
            ],
        )

    def test_clean_file_reports_nothing_skipped(self):
        raw = pd.DataFrame([{"Date": "2026-01-01", "Product": "Rice", "Quantity": 2, "Price": 10}])
        _, report = clean_data_with_report(raw)
        self.assertEqual(report["rows_skipped"], 0)
        self.assertEqual(report["reasons"], [])

    def test_clean_data_still_returns_only_the_dataframe(self):
        raw = pd.DataFrame([{"Date": "2026-01-01", "Product": "Rice", "Quantity": 2, "Price": 10}])
        self.assertIsInstance(clean_data(raw), pd.DataFrame)

    def test_csv_row_numbers_match_the_spreadsheet(self):
        csv = b"Date,Product,Quantity,Price\n2026-01-01,Rice,2,10\nbad,Milk,1,5\n"
        _, report = clean_data_with_report(read_sales_file(NamedBytes(csv, "sales.csv")))
        self.assertEqual(report["skipped_rows"]["Row"].tolist(), [3])

    def test_excel_row_numbers_account_for_title_rows(self):
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(["My supermarket sales"])
        sheet.append([])
        sheet.append(["Date", "Product", "Quantity", "Price"])
        sheet.append(["2026-01-01", "Rice", 2, 10])
        sheet.append(["2026-01-02", "Milk", "abc", 5])
        buffer = io.BytesIO()
        workbook.save(buffer)
        _, report = clean_data_with_report(read_sales_file(NamedBytes(buffer.getvalue(), "sales.xlsx")))
        self.assertEqual(report["skipped_rows"]["Row"].tolist(), [5])


class DayOfWeekPatternTests(unittest.TestCase):
    def test_needs_two_weeks_of_dates(self):
        result = day_of_week_pattern(daily_sales({day: 100 for day in range(7)}, days=10))
        self.assertFalse(result["available"])
        self.assertIn("Insufficient", result["message"])

    def test_identifies_strongest_and_slowest_day(self):
        revenue = {0: 100, 1: 100, 2: 100, 3: 100, 4: 120, 5: 150, 6: 110}
        result = day_of_week_pattern(daily_sales(revenue), "USD")
        self.assertTrue(result["available"])
        self.assertEqual((result["best_day"], result["slowest_day"]), ("Saturday", "Monday"))
        self.assertAlmostEqual(result["difference_percent"], 50.0)
        self.assertIn("Saturday is the strongest day", result["message"])
        self.assertIn("$150.00", result["message"])

    def test_even_sales_are_described_as_even(self):
        result = day_of_week_pattern(daily_sales({day: 100 + day for day in range(7)}))
        self.assertTrue(result["available"])
        self.assertIn("fairly even", result["message"])

    def test_weekdays_without_sales_are_reported_not_assumed(self):
        result = day_of_week_pattern(daily_sales({day: 100 for day in range(6)}))
        self.assertIn("No sales are recorded on Sunday", result["message"])
        self.assertNotIn("closed", result["message"])


class DaysOfStockTests(unittest.TestCase):
    def stock_dataset(self, rice_quantities: list[int], milk_quantities: list[int]):
        rows = []
        for day, (rice, milk) in enumerate(zip(rice_quantities, milk_quantities), start=1):
            rows.append({"Date": f"2026-01-{day:02d}", "Product": "Rice", "Quantity": rice, "Price": 10,
                         "Current Stock": 30, "Reorder Point": 5, "Lead Time": 5})
            rows.append({"Date": f"2026-01-{day:02d}", "Product": "Milk", "Quantity": milk, "Price": 5,
                         "Current Stock": 40, "Reorder Point": 5, "Lead Time": 2})
        return clean_data(pd.DataFrame(rows))

    def test_days_of_stock_is_stock_divided_by_observed_pace(self):
        items = inventory_guidance(self.stock_dataset([10, 10], [4, 4]))["items"].set_index("Product")
        self.assertAlmostEqual(items.loc["Rice", "Days_Of_Stock"], 3.0)
        self.assertAlmostEqual(items.loc["Milk", "Days_Of_Stock"], 10.0)
        self.assertIn("shorter than the stated 5-day lead time", items.loc["Rice", "Reason"])
        self.assertIn("at least the stated 2-day lead time", items.loc["Milk", "Reason"])
        self.assertIn("Estimate:", items.loc["Rice", "Reason"])

    def test_no_sales_gives_no_estimate(self):
        items = inventory_guidance(self.stock_dataset([10, 10], [0, 0]))["items"].set_index("Product")
        self.assertTrue(pd.isna(items.loc["Milk", "Days_Of_Stock"]))
        self.assertNotIn("Estimate:", items.loc["Milk", "Reason"])

    def test_stock_above_reorder_point_but_short_of_lead_time_moves_to_watch(self):
        # Rice is above its reorder point but covers only 3 days against a 5-day lead time.
        items = inventory_guidance(self.stock_dataset([10, 10], [4, 4]))["items"].set_index("Product")
        self.assertEqual(items.loc["Rice", "Priority"], "🟡 Watch")
        self.assertEqual(items.loc["Rice", "Recommended_Action"], "Check stock before the next order")
        self.assertIn("Moved to Watch", items.loc["Rice", "Reason"])
        # Milk covers 10 days against a 2-day lead time, so it stays an Opportunity.
        self.assertEqual(items.loc["Milk", "Priority"], "🟢 Opportunity")

    def test_lead_time_rule_never_downgrades_high_priority(self):
        rows = [{"Date": f"2026-01-0{day}", "Product": "Rice", "Quantity": 10, "Price": 10,
                 "Current Stock": 4, "Reorder Point": 5, "Lead Time": 5} for day in (1, 2)]
        item = inventory_guidance(clean_data(pd.DataFrame(rows)))["items"].iloc[0]
        self.assertEqual(item["Priority"], "🔴 High Priority")


if __name__ == "__main__":
    unittest.main()
