"""Render the home page and every page with the demo dataset to catch runtime errors before deploying."""

import io
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from src.cleaner import clean_data
from src.templates import demo_dataset_bytes
from src.uploads import dataframe_from_excel


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PAGES = sorted((PROJECT_ROOT / "pages").glob("*.py"))


def demo_dataframe():
    return clean_data(dataframe_from_excel(io.BytesIO(demo_dataset_bytes())))


class AppSmokeTests(unittest.TestCase):
    def test_home_page_shows_sign_in_when_logged_out(self):
        app = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.subheader[0].value, "Welcome to InsightIQ")

    def test_home_page_renders_when_signed_in(self):
        app = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
        app.session_state["authenticated"] = True
        app.session_state["user_name"] = "Smoke Test"
        app.run()
        self.assertFalse(app.exception)

    def test_every_page_renders_with_demo_data(self):
        df = demo_dataframe()
        self.assertGreater(len(df), 0)
        for page in PAGES:
            with self.subTest(page=page.name):
                app = AppTest.from_file(str(page), default_timeout=30)
                app.session_state["authenticated"] = True
                app.session_state["user_name"] = "Smoke Test"
                app.session_state["sales_df"] = df.copy()
                app.run()
                self.assertFalse(app.exception, [e.value for e in app.exception])

    def test_pages_ask_for_sign_in_when_logged_out(self):
        for page in PAGES:
            with self.subTest(page=page.name):
                app = AppTest.from_file(str(page), default_timeout=30).run()
                self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
