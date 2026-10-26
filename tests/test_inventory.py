import unittest

import pandas as pd

from src.cleaner import clean_data
from src.inventory import inventory_guidance, inventory_summary
from src.templates import (
    DEMO_DATASET_PATH,
    INVENTORY_TEMPLATE_PATH,
    demo_dataset_bytes,
    inventory_template_bytes,
)


def dataset(rows):
    return clean_data(pd.DataFrame(rows))


class InventoryGuidanceTests(unittest.TestCase):
    def test_inventory_template_is_available_for_download(self):
        self.assertTrue(INVENTORY_TEMPLATE_PATH.is_file())
        self.assertGreater(len(inventory_template_bytes()), 0)

    def test_demo_dataset_is_available_for_download(self):
        self.assertTrue(DEMO_DATASET_PATH.is_file())
        self.assertGreater(len(demo_dataset_bytes()), 0)

    def test_missing_stock_fields_never_invents_inventory(self):
        df = dataset([
            {"Date": "2026-01-01", "Product": "Rice", "Quantity": 4, "Price": 10},
        ])
        result = inventory_guidance(df)
        self.assertFalse(result["available"])
        self.assertIn("no Current Stock", result["message"])

    def test_stock_at_reorder_point_is_high_priority(self):
        df = dataset([
            {"Date": "2026-01-01", "Product": "Rice", "Quantity": 4, "Price": 10, "Current Stock": 10, "Reorder Point": 10},
            {"Date": "2026-01-02", "Product": "Rice", "Quantity": 4, "Price": 10, "Current Stock": 10, "Reorder Point": 10},
        ])
        item = inventory_guidance(df)["items"].iloc[0]
        self.assertEqual(item["Priority"], "🔴 High Priority")
        self.assertEqual(item["Recommended_Action"], "Review reorder now")
        self.assertNotIn("order exactly", item["Reason"].lower())
        self.assertNotIn("stock out", item["Reason"].lower())

    def test_near_reorder_point_is_watch(self):
        df = dataset([
            {"Date": "2026-01-01", "Product": "Oil", "Quantity": 2, "Price": 20, "Stock Level": 12, "Minimum Stock": 10},
        ])
        item = inventory_guidance(df)["items"].iloc[0]
        self.assertEqual(item["Priority"], "🟡 Watch")

    def test_lead_time_explains_observed_sales_pace_without_order_quantity(self):
        df = dataset([
            {"Date": "2026-01-01", "Product": "Soap", "Quantity": 3, "Price": 5, "Current Stock": 30, "Reorder Point": 10, "Lead Time": 4},
            {"Date": "2026-01-02", "Product": "Soap", "Quantity": 5, "Price": 5, "Current Stock": 30, "Reorder Point": 10, "Lead Time": 4},
        ])
        item = inventory_guidance(df)["items"].iloc[0]
        self.assertIn("Observed sales pace", item["Reason"])
        self.assertNotIn("order exactly", item["Reason"].lower())

    def test_summary_counts_each_product_once_by_priority(self):
        df = dataset([
            {"Date": "2026-01-01", "Product": "Rice", "Quantity": 3, "Price": 10, "Current Stock": 5, "Reorder Point": 5},
            {"Date": "2026-01-01", "Product": "Oil", "Quantity": 3, "Price": 10, "Current Stock": 12, "Reorder Point": 10},
            {"Date": "2026-01-01", "Product": "Soap", "Quantity": 3, "Price": 10, "Current Stock": 30, "Reorder Point": 10},
        ])
        summary = inventory_guidance(df)["summary"]
        self.assertEqual(summary["🔴 High Priority"], 1)
        self.assertEqual(summary["🟡 Watch"], 1)
        self.assertEqual(summary["🟢 Opportunity"], 1)

    def test_empty_summary_has_zeroes_for_each_priority(self):
        summary = inventory_summary(pd.DataFrame())
        self.assertEqual(summary, {
            "🔴 High Priority": 0,
            "🟡 Watch": 0,
            "🟢 Opportunity": 0,
        })


if __name__ == "__main__":
    unittest.main()
