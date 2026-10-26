import unittest

import pandas as pd

from src.advisor import analyze_business_advisor, executive_summary
from src.cleaner import clean_data
from src.inventory import inventory_guidance


def sales_frame(product_quantities: dict[str, list[int]], price: float = 10) -> pd.DataFrame:
    """Create twelve daily records: six previous dates and six recent dates."""
    rows = []
    for product, quantities in product_quantities.items():
        for day, quantity in enumerate(quantities, start=1):
            rows.append({
                "Date": f"2026-01-{day:02d}",
                "Product": product,
                "Quantity": quantity,
                "Price": price,
            })
    return clean_data(pd.DataFrame(rows))


class BusinessAdvisorTests(unittest.TestCase):
    def test_very_few_dates_returns_safe_fallback(self):
        df = clean_data(pd.DataFrame([
            {"Date": "2026-01-01", "Product": "Rice", "Quantity": 2, "Price": 10},
            {"Date": "2026-01-02", "Product": "Rice", "Quantity": 2, "Price": 10},
        ]))
        result = analyze_business_advisor(df)
        self.assertFalse(result["has_comparison"])
        self.assertIn("Insufficient data", result["message"])

    def test_one_product_decline_is_detected(self):
        df = sales_frame({"Rice": [20] * 6 + [5] * 6})
        result = analyze_business_advisor(df)
        self.assertTrue(result["has_comparison"])
        self.assertEqual(result["declining"]["Product"].tolist(), ["Rice"])
        self.assertIn("Review Rice", [action["title"] for action in result["actions"]])

    def test_no_meaningful_change_creates_watch_action(self):
        df = sales_frame({"Rice": [10] * 12, "Oil": [5] * 12})
        result = analyze_business_advisor(df)
        self.assertTrue(result["declining"].empty)
        self.assertTrue(result["momentum"].empty)
        self.assertEqual(result["actions"][0]["priority"], "🟡 Watch")

    def test_significant_decline_and_growth_are_detected(self):
        df = sales_frame({"Rice": [20] * 6 + [5] * 6, "Oil": [4] * 6 + [15] * 6})
        result = analyze_business_advisor(df)
        self.assertIn("Rice", result["declining"]["Product"].tolist())
        self.assertIn("Oil", result["momentum"]["Product"].tolist())
        action_text = " ".join(action["detail"] for action in result["actions"])
        self.assertNotIn("stock out", action_text.lower())
        self.assertNotIn("order exactly", action_text.lower())

    def test_invalid_and_missing_dates_are_dropped_safely(self):
        raw = pd.DataFrame([
            {"Date": "not-a-date", "Product": "Rice", "Quantity": 2, "Price": 10},
            {"Date": None, "Product": "Oil", "Quantity": 2, "Price": 10},
            {"Date": "2026-01-01", "Product": "Soap", "Quantity": 2, "Price": 10},
        ])
        cleaned = clean_data(raw)
        self.assertEqual(cleaned["Product"].tolist(), ["Soap"])
        self.assertFalse(analyze_business_advisor(cleaned)["has_comparison"])

    def test_identical_product_performance_is_not_flagged(self):
        df = sales_frame({"Rice": [10] * 12, "Oil": [10] * 12})
        result = analyze_business_advisor(df)
        self.assertTrue(result["declining"].empty)
        self.assertTrue(result["momentum"].empty)
        self.assertIn("no material product", result["actions"][0]["detail"].lower())

    def test_executive_summary_prioritises_supplied_high_priority_stock(self):
        df = sales_frame({"Rice": [10] * 6 + [18] * 6, "Oil": [20] * 6 + [5] * 6})
        df["Current Stock"] = df["Product"].map({"Rice": 5, "Oil": 40})
        df["Reorder Point"] = df["Product"].map({"Rice": 5, "Oil": 10})
        summary = executive_summary(analyze_business_advisor(df), inventory_guidance(df))
        by_label = {item["label"]: item["detail"] for item in summary}
        self.assertIn("Rice stock is at or below", by_label["Main risk"])
        self.assertIn("Review Rice stock", by_label["Next step"])
        self.assertIn("Rice revenue rose", by_label["Best opportunity"])
        summary_text = " ".join(by_label.values()).lower()
        self.assertNotIn("stock out", summary_text)
        self.assertNotIn("order exactly", summary_text)

    def test_executive_summary_stays_cautious_without_comparison_data(self):
        df = clean_data(pd.DataFrame([
            {"Date": "2026-01-01", "Product": "Rice", "Quantity": 2, "Price": 10},
        ]))
        summary = executive_summary(analyze_business_advisor(df), inventory_guidance(df))
        by_label = {item["label"]: item["detail"] for item in summary}
        self.assertIn("Insufficient data", by_label["What changed"])
        self.assertIn("No material product growth", by_label["Best opportunity"])


if __name__ == "__main__":
    unittest.main()
