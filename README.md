# DiaperScout — Diaper Cost, Unit Pricing & Ratings Dashboard

A Vue 3 + Vite dashboard bundled with live-scraped CSV datasets for comparing diaper costs, per-diaper unit pricing, standardized age-range sizing, and ratings across **Meijer**, **Target**, **Costco**, **Walmart**, **Sam's Club**, and **Kroger**.

## Features

- **Pipenv Python Scraper (`scraper/scrape_diapers.py`)**:
  - Uses `requests`, `beautifulsoup4`, and `lxml` managed via `Pipfile` / `pipenv`.
  - Probes live retailer endpoints and outputs three standardized CSV files directly bundled into the Vue application (`src/data/` and `public/data/`):
    - `diaper_prices.csv`: Store-level pricing, per-diaper unit cost, estimated monthly cost, pack counts, promotions, and availability.
    - `diaper_brands.csv`: Customer ratings, review counts, absorbency/softness/leak-guard scores, features, and descriptions.
    - `diaper_sizes.csv`: Diaper sizes (`N` through `7`) standardized to infant/toddler age ranges (`0-1 Months` up to `48+ Months`) and weight ranges.
- **Interactive Vue Frontend**:
  - Filter by **Diaper Size (Standardized to Age Ranges)**, **Retailer Stores** (Meijer, Target, Costco, Walmart, Sam's Club, Kroger), and **Pack Size Tiers** (Trial/Travel, Jumbo/Regular, Super/Enormous, Club/Bulk Case).
  - Compare ratings, features, performance scores, and descriptions across 12 major national, eco-friendly, and store-brand diaper lines.

## Quick Start

### 1. Run or Refresh the Scraper via Pipenv

```bash
pipenv install
pipenv run python scraper/scrape_diapers.py
```

Options:
- `--stores Target Walmart Costco Meijer Kroger "Sam's Club"`: Filter specific stores to scrape.
- `--offline`: Fast local CSV regeneration without live HTTP probes.

### 2. Run the Vue Frontend

```bash
npm install
npm run dev
```

Build for production:

```bash
npm run build
```
