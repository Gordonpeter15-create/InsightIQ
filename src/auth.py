import hashlib
import hmac
import secrets
import sqlite3
from contextlib import closing
from pathlib import Path

from src.currency import CURRENCIES, DEFAULT_CURRENCY


DATABASE_PATH = Path(__file__).resolve().parents[1] / "data" / "insightiq_users.db"
ITERATIONS = 310_000


def initialize_auth_db() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(DATABASE_PATH)) as connection, connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # Databases created before currency support gain the column with the previous behaviour (USD).
        columns = {row[1] for row in connection.execute("PRAGMA table_info(users)")}
        if "currency" not in columns:
            connection.execute(
                f"ALTER TABLE users ADD COLUMN currency TEXT NOT NULL DEFAULT '{DEFAULT_CURRENCY}'"
            )


def _hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return f"{salt.hex()}${password_hash.hex()}"


def create_user(full_name: str, email: str, password: str) -> tuple[bool, str]:
    full_name, email = full_name.strip(), email.strip().lower()
    if not full_name:
        return False, "Enter your name."
    if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
        return False, "Enter a valid email address."
    if len(password) < 8:
        return False, "Use a password with at least 8 characters."

    try:
        with closing(sqlite3.connect(DATABASE_PATH)) as connection, connection:
            connection.execute(
                "INSERT INTO users (email, full_name, password_hash) VALUES (?, ?, ?)",
                (email, full_name, _hash_password(password)),
            )
    except sqlite3.IntegrityError:
        return False, "An account already exists for this email."
    return True, "Account created. You can now sign in."


def authenticate_user(email: str, password: str) -> str | None:
    email = email.strip().lower()
    with closing(sqlite3.connect(DATABASE_PATH)) as connection, connection:
        row = connection.execute(
            "SELECT full_name, password_hash FROM users WHERE email = ?", (email,)
        ).fetchone()
    if row is None:
        return None

    full_name, stored_hash = row
    salt_hex, expected_hash = stored_hash.split("$", maxsplit=1)
    candidate_hash = _hash_password(password, bytes.fromhex(salt_hex)).split("$", maxsplit=1)[1]
    return full_name if hmac.compare_digest(candidate_hash, expected_hash) else None


def get_user_currency(email: str) -> str:
    with closing(sqlite3.connect(DATABASE_PATH)) as connection, connection:
        row = connection.execute(
            "SELECT currency FROM users WHERE email = ?", (email.strip().lower(),)
        ).fetchone()
    return row[0] if row and row[0] in CURRENCIES else DEFAULT_CURRENCY


def set_user_currency(email: str, currency: str) -> None:
    if currency not in CURRENCIES:
        raise ValueError(f"Unsupported currency: {currency}")
    with closing(sqlite3.connect(DATABASE_PATH)) as connection, connection:
        connection.execute(
            "UPDATE users SET currency = ? WHERE email = ?", (currency, email.strip().lower())
        )
