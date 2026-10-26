"""Downloadable sample files that match InsightIQ's supported data fields."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INVENTORY_TEMPLATE_PATH = PROJECT_ROOT / "data" / "InsightIQ_inventory_template.xlsx"
DEMO_DATASET_PATH = PROJECT_ROOT / "data" / "InsightIQ_demo_supermarket.xlsx"


def inventory_template_bytes() -> bytes:
    """Return the inventory template as Excel bytes for Streamlit downloads."""
    return INVENTORY_TEMPLATE_PATH.read_bytes()


def demo_dataset_bytes() -> bytes:
    """Return fictional supermarket data for trying every InsightIQ page."""
    return DEMO_DATASET_PATH.read_bytes()
