import io
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest import mock

import pandas as pd
from openpyxl import load_workbook

from src import auth
from src.advisor import analyze_business_advisor
from src.ai import generate_insights
from src.cleaner import clean_data
from src.currency import (
    CURRENCIES,
    DEFAULT_CURRENCY,
    excel_number_format,
    format_money,
    money_label,
)
from src.metrics import calculate_metrics, product_performance
from src.questions import answer_question
from src.reports import build_excel_report


def sample_sales() -> pd.DataFrame:
    rows = []
    for day in range(1, 13):
        rows.append({"Date": f"2026-01-{day:02d}", "Product": "Rice", "Quantity": 10 if day <= 6 else 5, "Price": 1500})
        rows.append({"Date": f"2026-01-{day:02d}", "Product": "Milk", "Quantity": 4, "Price": 800})
    return clean_data(pd.DataFrame(rows))


class CurrencyFormattingTests(unittest.TestCase):
    def test_default_currency_keeps_previous_dollar_format(self):
        self.assertEqual(DEFAULT_CURRENCY, "USD")
        self.assertEqual(format_money(1234.5), "$1,234.50")
        self.assertEqual(excel_number_format(), '"$"#,##0.00')

    def test_symbols_and_decimals_follow_the_currency(self):
        self.assertEqual(format_money(1234.5, "NGN"), "₦1,234.50")
        self.assertEqual(format_money(1234.5, "KES"), "KSh 1,234.50")
        self.assertEqual(format_money(1234.5, "UGX"), "USh 1,234")
        self.assertEqual(excel_number_format("UGX"), '"USh "#,##0')
        self.assertEqual(money_label("Revenue", "GBP"), "Revenue (£)")

    def test_unknown_currency_falls_back_to_default(self):
        self.assertEqual(format_money(5, "ZZZ"), "$5.00")

    def test_every_currency_formats(self):
        for code in CURRENCIES:
            with self.subTest(code=code):
                self.assertTrue(format_money(1000, code))


class CurrencyInOutputsTests(unittest.TestCase):
    def setUp(self):
        self.df = sample_sales()
        self.performance = product_performance(self.df)

    def test_advisor_actions_use_chosen_currency(self):
        details = " ".join(action["detail"] for action in analyze_business_advisor(self.df, "NGN")["actions"])
        self.assertIn("₦", details)
        self.assertNotIn("$", details)

    def test_questions_and_insights_use_chosen_currency(self):
        answer = answer_question("What is the total revenue?", self.df, self.performance, "GHS")
        self.assertIn("GH₵", answer)
        insights = " ".join(generate_insights(self.df, self.performance, "EUR"))
        self.assertIn("€", insights)
        self.assertNotIn("$", insights)

    def test_excel_report_uses_chosen_currency_format(self):
        report = build_excel_report(
            self.df, calculate_metrics(self.df), self.performance, ["Insight"], "KES"
        )
        workbook = load_workbook(io.BytesIO(report))
        self.assertEqual(workbook["Executive Summary"]["B5"].number_format, excel_number_format("KES"))
        self.assertEqual(workbook["Product Performance"]["B2"].number_format, excel_number_format("KES"))


class CurrencyAccountStorageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.database = Path(self.directory.name) / "users.db"
        patcher = mock.patch.object(auth, "DATABASE_PATH", self.database)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.directory.cleanup)

    def test_new_accounts_default_to_usd_and_remember_choice(self):
        auth.initialize_auth_db()
        auth.create_user("Ada", "ada@example.com", "password123")
        self.assertEqual(auth.get_user_currency("ada@example.com"), "USD")
        auth.set_user_currency("ADA@example.com ", "NGN")
        self.assertEqual(auth.get_user_currency("ada@example.com"), "NGN")

    def test_existing_database_without_currency_column_is_upgraded(self):
        with closing(sqlite3.connect(self.database)) as connection, connection:
            connection.execute(
                "CREATE TABLE users (email TEXT PRIMARY KEY, full_name TEXT NOT NULL, "
                "password_hash TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
            )
            connection.execute(
                "INSERT INTO users (email, full_name, password_hash) VALUES ('old@example.com', 'Old', 'x$y')"
            )
        auth.initialize_auth_db()
        auth.initialize_auth_db()  # Running twice must be safe.
        self.assertEqual(auth.get_user_currency("old@example.com"), "USD")

    def test_unsupported_currency_is_rejected(self):
        auth.initialize_auth_db()
        with self.assertRaises(ValueError):
            auth.set_user_currency("ada@example.com", "ZZZ")


if __name__ == "__main__":
    unittest.main()
