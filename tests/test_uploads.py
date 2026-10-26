import unittest

import pandas as pd

from src.uploads import find_sales_header_row


class UploadHeaderTests(unittest.TestCase):
    def test_finds_headers_below_title_and_instruction_rows(self):
        raw = pd.DataFrame([
            ["InsightIQ demo supermarket data", None, None, None],
            [None, None, None, None],
            ["Fictional practice data", None, None, None],
            [None, None, None, None],
            ["Date", "Product", "Quantity", "Price"],
            ["2026-01-01", "Rice", 4, 650],
        ])
        self.assertEqual(find_sales_header_row(raw), 4)

    def test_finds_headers_on_first_row_for_standard_uploads(self):
        raw = pd.DataFrame([
            ["Date", "Product", "Quantity", "Price"],
            ["2026-01-01", "Rice", 4, 650],
        ])
        self.assertEqual(find_sales_header_row(raw), 0)

    def test_returns_none_when_required_headers_are_missing(self):
        raw = pd.DataFrame([["Product", "Quantity", "Price"]])
        self.assertIsNone(find_sales_header_row(raw))


if __name__ == "__main__":
    unittest.main()
