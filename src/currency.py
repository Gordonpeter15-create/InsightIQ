"""Currency choices and money formatting shared by every page and the Excel report.

InsightIQ only labels values with the chosen currency; it never converts between currencies.
"""

from __future__ import annotations

from typing import NamedTuple


class Currency(NamedTuple):
    name: str
    symbol: str
    decimals: int


DEFAULT_CURRENCY = "USD"
CURRENCIES: dict[str, Currency] = {
    "USD": Currency("US dollar", "$", 2),
    "EUR": Currency("Euro", "€", 2),
    "GBP": Currency("British pound", "£", 2),
    "NGN": Currency("Nigerian naira", "₦", 2),
    "GHS": Currency("Ghanaian cedi", "GH₵", 2),
    "KES": Currency("Kenyan shilling", "KSh", 2),
    "UGX": Currency("Ugandan shilling", "USh", 0),
    "TZS": Currency("Tanzanian shilling", "TSh", 2),
    "RWF": Currency("Rwandan franc", "FRw", 0),
    "ZAR": Currency("South African rand", "R", 2),
    "XOF": Currency("West African CFA franc", "CFA", 0),
    "XAF": Currency("Central African CFA franc", "FCFA", 0),
    "EGP": Currency("Egyptian pound", "E£", 2),
    "INR": Currency("Indian rupee", "₹", 2),
    "PKR": Currency("Pakistani rupee", "Rs", 2),
    "PHP": Currency("Philippine peso", "₱", 2),
    "CAD": Currency("Canadian dollar", "CA$", 2),
    "AUD": Currency("Australian dollar", "A$", 2),
    "AED": Currency("UAE dirham", "AED", 2),
    "JPY": Currency("Japanese yen", "¥", 0),
}


def currency_info(code: str | None) -> Currency:
    """Return the currency for a code, falling back to the default for unknown codes."""
    return CURRENCIES.get(code or DEFAULT_CURRENCY, CURRENCIES[DEFAULT_CURRENCY])


def currency_label(code: str) -> str:
    info = currency_info(code)
    return f"{code} — {info.name} ({info.symbol})"


def format_money(value: float, currency: str = DEFAULT_CURRENCY) -> str:
    info = currency_info(currency)
    # Multi-letter symbols such as KSh read better with a space before the amount.
    separator = " " if info.symbol[-1].isalpha() else ""
    return f"{info.symbol}{separator}{value:,.{info.decimals}f}"


def excel_number_format(currency: str = DEFAULT_CURRENCY) -> str:
    info = currency_info(currency)
    separator = " " if info.symbol[-1].isalpha() else ""
    digits = "0." + "0" * info.decimals if info.decimals else "0"
    return f'"{info.symbol}{separator}"#,##{digits}'


def money_label(label: str, currency: str = DEFAULT_CURRENCY) -> str:
    """Add the currency symbol to a column or axis label, e.g. 'Revenue (₦)'."""
    return f"{label} ({currency_info(currency).symbol})"
