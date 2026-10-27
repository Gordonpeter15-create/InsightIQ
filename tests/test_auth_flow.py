"""Sign-up and sign-in through the real sign-in screen, using a temporary accounts database."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from streamlit.testing.v1 import AppTest

from src import auth


APP = str(Path(__file__).resolve().parents[1] / "app.py")


class AuthFlowTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        patcher = mock.patch.object(auth, "DATABASE_PATH", Path(directory.name) / "users.db")
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_creating_an_account_signs_the_user_straight_in(self):
        app = AppTest.from_file(APP, default_timeout=30).run()
        app.text_input(key="signup_email").input("new.owner@example.test")
        app.text_input[2].input("New Owner")
        app.text_input[4].input("longenough1")
        app.button[1].click().run()
        self.assertFalse(app.exception)
        self.assertTrue(app.session_state["authenticated"])
        self.assertEqual(app.session_state["user_email"], "new.owner@example.test")
        self.assertEqual(app.session_state["currency"], "USD")

    def test_invalid_sign_up_keeps_the_user_on_the_form_with_a_reason(self):
        app = AppTest.from_file(APP, default_timeout=30).run()
        app.text_input[2].input("New Owner")
        app.text_input(key="signup_email").input("new.owner@example.test")
        app.text_input[4].input("short")
        app.button[1].click().run()
        self.assertFalse(app.session_state["authenticated"])
        self.assertIn("at least 8 characters", app.error[0].value)

    def test_unknown_account_points_to_create_account(self):
        app = AppTest.from_file(APP, default_timeout=30).run()
        app.text_input[0].input("nobody@example.test")
        app.text_input[1].input("whatever123")
        app.button[0].click().run()
        self.assertFalse(app.session_state["authenticated"])
        self.assertIn("Create account", app.error[0].value)


if __name__ == "__main__":
    unittest.main()
