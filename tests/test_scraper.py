"""Tests for the DiaperScout scraper and CSV output schemas."""

from pathlib import Path
import csv
from scraper.scrape_diapers import build_datasets, STORES, SIZE_STANDARDS


def test_scraper_generates_expected_stores_and_sizes():
    target_stores = ["Meijer", "Target", "Costco", "Walmart", "Sam's Club", "Kroger", "Amazon"]
    prices, brands, sizes, meta = build_datasets(selected_stores=target_stores, skip_network=True)

    assert len(sizes) == len(SIZE_STANDARDS)
    assert len(brands) >= 10
    assert len(prices) > 500

    # Ensure every target store is present in output
    found_stores = {row["store"] for row in prices}
    assert found_stores == set(target_stores)

    # Ensure standardized age_range is populated on every row
    for row in prices:
        assert row["age_range"], "Missing standardized age range"
        assert float(row["price"]) > 0
        assert float(row["price_per_diaper"]) > 0


def test_bundled_csv_files_exist():
    root = Path(__file__).resolve().parent.parent
    for fname in ("diaper_prices.csv", "diaper_brands.csv", "diaper_sizes.csv"):
        csv_path = root / "public" / "data" / fname
        assert csv_path.exists(), f"Expected CSV in data subfolder at {csv_path}"
        with csv_path.open("r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            assert len(reader) > 0

