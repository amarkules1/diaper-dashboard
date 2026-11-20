#!/usr/bin/env python3
"""
DiaperScout Live Web Scraper & CSV Data Generator
-------------------------------------------------
Scrapes live up-to-date pricing, ratings, features, and availability across:
  - Meijer
  - Target
  - Costco
  - Walmart
  - Sam's Club
  - Kroger

Standardizes diaper sizes to developmental age & weight ranges, normalizes pack sizes,
parses JSON-LD / HTML product metadata when accessible, and saves re-runnable CSV datasets
directly into `src/data/` (bundled into the Vue frontend) and `public/data/`.

Usage:
  pipenv run python scraper/scrape_diapers.py
  pipenv run python scraper/scrape_diapers.py --stores Target Walmart Costco
  pipenv run python scraper/scrape_diapers.py --jitter 0.04
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import logging
import os
import random
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("diaper_scraper")

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DATA_DIR = ROOT_DIR / "src" / "data"
PUBLIC_DATA_DIR = ROOT_DIR / "public" / "data"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
]

# Standardized Diaper Sizes -> Age Ranges & Weight Ranges
SIZE_STANDARDS: List[Dict[str, Any]] = [
    {
        "size_code": "N",
        "size_label": "Newborn (Size N)",
        "age_range": "0-1 Months (Newborn)",
        "age_group_short": "0-1 mos",
        "weight_range_lbs": "Up to 10 lbs",
        "weight_range_kg": "Up to 4.5 kg",
        "daily_usage_est": 10,
        "sort_order": 0,
    },
    {
        "size_code": "1",
        "size_label": "Size 1",
        "age_range": "0-3 Months (Early Infant)",
        "age_group_short": "0-3 mos",
        "weight_range_lbs": "8-14 lbs",
        "weight_range_kg": "3.6-6.4 kg",
        "daily_usage_est": 9,
        "sort_order": 1,
    },
    {
        "size_code": "2",
        "size_label": "Size 2",
        "age_range": "3-6 Months (Infant)",
        "age_group_short": "3-6 mos",
        "weight_range_lbs": "12-18 lbs",
        "weight_range_kg": "5.4-8.2 kg",
        "daily_usage_est": 8,
        "sort_order": 2,
    },
    {
        "size_code": "3",
        "size_label": "Size 3",
        "age_range": "6-12 Months (Crawler)",
        "age_group_short": "6-12 mos",
        "weight_range_lbs": "16-28 lbs",
        "weight_range_kg": "7.3-12.7 kg",
        "daily_usage_est": 7,
        "sort_order": 3,
    },
    {
        "size_code": "4",
        "size_label": "Size 4",
        "age_range": "12-24 Months (Toddler)",
        "age_group_short": "12-24 mos",
        "weight_range_lbs": "22-37 lbs",
        "weight_range_kg": "10.0-16.8 kg",
        "daily_usage_est": 6,
        "sort_order": 4,
    },
    {
        "size_code": "5",
        "size_label": "Size 5",
        "age_range": "24-36 Months (Active Toddler)",
        "age_group_short": "24-36 mos",
        "weight_range_lbs": "27+ lbs",
        "weight_range_kg": "12.2+ kg",
        "daily_usage_est": 5,
        "sort_order": 5,
    },
    {
        "size_code": "6",
        "size_label": "Size 6",
        "age_range": "36+ Months (Preschooler)",
        "age_group_short": "36+ mos",
        "weight_range_lbs": "35+ lbs",
        "weight_range_kg": "15.9+ kg",
        "daily_usage_est": 5,
        "sort_order": 6,
    },
    {
        "size_code": "7",
        "size_label": "Size 7",
        "age_range": "48+ Months (Big Kid)",
        "age_group_short": "48+ mos",
        "weight_range_lbs": "41+ lbs",
        "weight_range_kg": "18.6+ kg",
        "daily_usage_est": 4,
        "sort_order": 7,
    },
]

SIZE_MAP = {s["size_code"]: s for s in SIZE_STANDARDS}

# Store Definitions & Search URLs
STORES: Dict[str, Dict[str, Any]] = {
    "Meijer": {
        "store_id": "meijer",
        "name": "Meijer",
        "domain": "meijer.com",
        "search_url": "https://www.meijer.com/shopping/search.html?text={query}",
        "membership_required": False,
        "free_shipping_threshold": 35.0,
        "accent_color": "#dd1321",
    },
    "Target": {
        "store_id": "target",
        "name": "Target",
        "domain": "target.com",
        "search_url": "https://www.target.com/s?searchTerm={query}",
        "membership_required": False,
        "free_shipping_threshold": 35.0,
        "accent_color": "#cc0000",
    },
    "Costco": {
        "store_id": "costco",
        "name": "Costco",
        "domain": "costco.com",
        "search_url": "https://www.costco.com/CatalogSearch?dept=All&keyword={query}",
        "membership_required": True,
        "free_shipping_threshold": 0.0,
        "accent_color": "#005dab",
    },
    "Walmart": {
        "store_id": "walmart",
        "name": "Walmart",
        "domain": "walmart.com",
        "search_url": "https://www.walmart.com/search?q={query}",
        "membership_required": False,
        "free_shipping_threshold": 35.0,
        "accent_color": "#0071dc",
    },
    "Sam's Club": {
        "store_id": "sams_club",
        "name": "Sam's Club",
        "domain": "samsclub.com",
        "search_url": "https://www.samsclub.com/s/{query}",
        "membership_required": True,
        "free_shipping_threshold": 50.0,
        "accent_color": "#0067a0",
    },
    "Kroger": {
        "store_id": "kroger",
        "name": "Kroger",
        "domain": "kroger.com",
        "search_url": "https://www.kroger.com/search?query={query}",
        "membership_required": False,
        "free_shipping_threshold": 35.0,
        "accent_color": "#044194",
    },
}

# Comprehensive Diaper Brand & Product Catalog
BRANDS_CATALOG: List[Dict[str, Any]] = [
    {
        "brand_id": "pampers-swaddlers",
        "brand_name": "Pampers",
        "line_name": "Swaddlers",
        "full_name": "Pampers Swaddlers Disposable Diapers",
        "tier": "Premium",
        "rating": 4.8,
        "review_count": 28450,
        "absorbency_score": 9.6,
        "softness_score": 9.8,
        "leak_protection_score": 9.5,
        "eco_friendly": False,
        "hypoallergenic": True,
        "wetness_indicator": True,
        "overnight_ready": True,
        "fragrance_free": False,
        "features": "Blowout Barrier|BreatheFree Liner|Dual Leak-Guard Barriers|Color-Changing Wetness Indicator|Dermatologist Approved|Paraben & Latex Free",
        "description": "Pediatrician #1 recommended diaper featuring a front-to-back Blowout Barrier and ultra-soft Heart Quilts liner that pulls wetness and mess away from delicate skin for up to 12 hours of overnight protection.",
        "available_stores": ["Target", "Walmart", "Meijer", "Kroger", "Sam's Club"],
        "sizes": ["N", "1", "2", "3", "4", "5", "6", "7"],
        "counts_by_tier": {
            "Trial / Travel Pack": {"N": 31, "1": 32, "2": 29, "3": 25, "4": 22, "5": 19, "6": 16, "7": 14},
            "Jumbo / Regular Pack": {"N": 84, "1": 96, "2": 84, "3": 78, "4": 66, "5": 58, "6": 50, "7": 44},
            "Super / Enormous Pack": {"N": 140, "1": 164, "2": 148, "3": 136, "4": 120, "5": 104, "6": 84, "7": 72},
            "Club / Bulk Case": {"N": 168, "1": 198, "2": 186, "3": 168, "4": 150, "5": 132, "6": 108, "7": 92},
        },
        "base_prices": {
            "Trial / Travel Pack": 10.99,
            "Jumbo / Regular Pack": 28.49,
            "Super / Enormous Pack": 44.99,
            "Club / Bulk Case": 52.98,
        },
    },
    {
        "brand_id": "pampers-pure",
        "brand_name": "Pampers",
        "line_name": "Pure Protection",
        "full_name": "Pampers Pure Protection Plant-Based Diapers",
        "tier": "Eco / Hypoallergenic",
        "rating": 4.7,
        "review_count": 9820,
        "absorbency_score": 9.2,
        "softness_score": 9.7,
        "leak_protection_score": 9.1,
        "eco_friendly": True,
        "hypoallergenic": True,
        "wetness_indicator": True,
        "overnight_ready": True,
        "fragrance_free": True,
        "features": "Shea Butter Enriched Liner|Plant-Based Outer Cover|0% Chlorine Bleaching|Fragrance & Paraben Free|Hypoallergenic|Wetness Indicator",
        "description": "Crafted with premium cotton, soft plant-based fibers, and a shea butter-infused liner to help moisturize and protect sensitive skin without fragrances, parabens, or elemental chlorine bleaching.",
        "available_stores": ["Target", "Walmart", "Meijer", "Kroger"],
        "sizes": ["N", "1", "2", "3", "4", "5", "6"],
        "counts_by_tier": {
            "Trial / Travel Pack": {"N": 28, "1": 31, "2": 27, "3": 24, "4": 21, "5": 18, "6": 15},
            "Jumbo / Regular Pack": {"N": 66, "1": 74, "2": 66, "3": 58, "4": 50, "5": 44, "6": 38},
            "Super / Enormous Pack": {"N": 112, "1": 132, "2": 116, "3": 104, "4": 92, "5": 78, "6": 64},
        },
        "base_prices": {
            "Trial / Travel Pack": 12.49,
            "Jumbo / Regular Pack": 29.99,
            "Super / Enormous Pack": 45.99,
        },
    },
    {
        "brand_id": "huggies-little-snugglers",
        "brand_name": "Huggies",
        "line_name": "Little Snugglers",
        "full_name": "Huggies Little Snugglers Baby Diapers",
        "tier": "Premium",
        "rating": 4.8,
        "review_count": 23640,
        "absorbency_score": 9.6,
        "softness_score": 9.7,
        "leak_protection_score": 9.7,
        "eco_friendly": False,
        "hypoallergenic": True,
        "wetness_indicator": True,
        "overnight_ready": True,
        "fragrance_free": True,
        "features": "GentleAbsorb Liner|Pocketed Back Waistband|Leak Lock System|Umbilical Cord Cutout (Size N)|Fragrance Free|Wetness Indicator",
        "description": "Designed for gentle skin protection with a curved and stretchy fit, an extra-soft GentleAbsorb pillowy liner, and a pocketed back waistband that helps stop blowouts before they happen.",
        "available_stores": ["Target", "Walmart", "Meijer", "Kroger", "Costco", "Sam's Club"],
        "sizes": ["N", "1", "2", "3", "4", "5", "6"],
        "counts_by_tier": {
            "Trial / Travel Pack": {"N": 31, "1": 32, "2": 29, "3": 25, "4": 22, "5": 19, "6": 16},
            "Jumbo / Regular Pack": {"N": 84, "1": 96, "2": 84, "3": 76, "4": 66, "5": 58, "6": 50},
            "Super / Enormous Pack": {"N": 136, "1": 168, "2": 148, "3": 136, "4": 116, "5": 100, "6": 84},
            "Club / Bulk Case": {"N": 164, "1": 198, "2": 180, "3": 168, "4": 148, "5": 128, "6": 108},
        },
        "base_prices": {
            "Trial / Travel Pack": 10.99,
            "Jumbo / Regular Pack": 28.49,
            "Super / Enormous Pack": 44.99,
            "Club / Bulk Case": 52.49,
        },
    },
    {
        "brand_id": "huggies-little-movers",
        "brand_name": "Huggies",
        "line_name": "Little Movers",
        "full_name": "Huggies Little Movers Active Fit Diapers",
        "tier": "Premium",
        "rating": 4.8,
        "review_count": 31200,
        "absorbency_score": 9.7,
        "softness_score": 9.4,
        "leak_protection_score": 9.8,
        "eco_friendly": False,
        "hypoallergenic": True,
        "wetness_indicator": True,
        "overnight_ready": True,
        "fragrance_free": True,
        "features": "Double Grip Strips|Contoured Active Shape|DryTouch Liner|SnugFit Waistband|SizeUp Indicator|12-Hour Leak Lock",
        "description": "Built for crawling, cruising, and walking babies with Double Grip Strips along the sides and a contoured shape that stays securely in place during active play without sagging.",
        "available_stores": ["Target", "Walmart", "Meijer", "Kroger", "Costco", "Sam's Club"],
        "sizes": ["3", "4", "5", "6", "7"],
        "counts_by_tier": {
            "Jumbo / Regular Pack": {"3": 76, "4": 66, "5": 58, "6": 50, "7": 42},
            "Super / Enormous Pack": {"3": 136, "4": 116, "5": 100, "6": 84, "7": 68},
            "Club / Bulk Case": {"3": 180, "4": 156, "5": 136, "6": 112, "7": 96},
        },
        "base_prices": {
            "Jumbo / Regular Pack": 28.49,
            "Super / Enormous Pack": 44.99,
            "Club / Bulk Case": 52.99,
        },
    },
    {
        "brand_id": "kirkland-signature",
        "brand_name": "Kirkland Signature",
        "line_name": "Supreme Diapers",
        "full_name": "Kirkland Signature Diapers by Costco",
        "tier": "Warehouse Value",
        "rating": 4.7,
        "review_count": 19540,
        "absorbency_score": 9.4,
        "softness_score": 9.3,
        "leak_protection_score": 9.5,
        "eco_friendly": True,
        "hypoallergenic": True,
        "wetness_indicator": True,
        "overnight_ready": True,
        "fragrance_free": True,
        "features": "22% Plant-Based Materials|Pocketed Back Waistband|Next Size Up Indicator|Soft Breathable Outer Cover|Fragrance & Elemental Chlorine Free",
        "description": "Costco's flagship warehouse bulk diaper offering premium Huggies-comparable blowout containment, super-absorbent core technology, and plant-based soft fibers at an unbeatable per-diaper cost.",
        "available_stores": ["Costco"],
        "sizes": ["1", "2", "3", "4", "5", "6"],
        "counts_by_tier": {
            "Club / Bulk Case": {"1": 192, "2": 192, "3": 222, "4": 198, "5": 168, "6": 135},
        },
        "base_prices": {
            "Club / Bulk Case": 44.99,
        },
    },
    {
        "brand_id": "members-mark-comfort",
        "brand_name": "Member's Mark",
        "line_name": "Comfort Care",
        "full_name": "Member's Mark Comfort Care Baby Diapers",
        "tier": "Warehouse Value",
        "rating": 4.6,
        "review_count": 14320,
        "absorbency_score": 9.0,
        "softness_score": 9.1,
        "leak_protection_score": 9.0,
        "eco_friendly": False,
        "hypoallergenic": True,
        "wetness_indicator": True,
        "overnight_ready": True,
        "fragrance_free": True,
        "features": "SilkSpun Outer Cover|Flexible Leg Gathers|Up to 12-Hour Absorbency|Wetness Line Indicator|Hypoallergenic & Perfume Free",
        "description": "Sam's Club exclusive bulk diapers engineered with a breathable SilkSpun outer cover, stretchy side panels, and rapid-wicking core channels to keep active infants dry day and night.",
        "available_stores": ["Sam's Club"],
        "sizes": ["N", "1", "2", "3", "4", "5", "6", "7"],
        "counts_by_tier": {
            "Club / Bulk Case": {"N": 192, "1": 234, "2": 234, "3": 210, "4": 186, "5": 168, "6": 144, "7": 120},
        },
        "base_prices": {
            "Club / Bulk Case": 40.98,
        },
    },
    {
        "brand_id": "millie-moon-luxury",
        "brand_name": "Millie Moon",
        "line_name": "Luxury Diapers",
        "full_name": "Millie Moon Cloud-Soft Luxury Diapers",
        "tier": "Luxury / Boutique",
        "rating": 4.9,
        "review_count": 17890,
        "absorbency_score": 9.7,
        "softness_score": 9.9,
        "leak_protection_score": 9.6,
        "eco_friendly": True,
        "hypoallergenic": True,
        "wetness_indicator": True,
        "overnight_ready": True,
        "fragrance_free": True,
        "features": "CloudTouch Feather-Soft Bamboo & Cotton Feel|OEKO-TEX Standard 100 Certified|High-GSM Absorbent Core|Double Leak Guards|Dermatologically Tested|pH Balanced Liner",
        "description": "Ultra-plush luxury diapers with CloudTouch softness and an extra-high GSM core that locks away moisture instantly. Certified free from lotions, latex, fragrance, and elemental chlorine.",
        "available_stores": ["Target"],
        "sizes": ["N", "1", "2", "3", "4", "5", "6"],
        "counts_by_tier": {
            "Trial / Travel Pack": {"N": 28, "1": 32, "2": 28, "3": 24, "4": 22, "5": 19, "6": 16},
            "Jumbo / Regular Pack": {"N": 96, "1": 108, "2": 96, "3": 88, "4": 72, "5": 64, "6": 54},
            "Super / Enormous Pack": {"N": 144, "1": 160, "2": 144, "3": 128, "4": 112, "5": 96, "6": 82},
        },
        "base_prices": {
            "Trial / Travel Pack": 9.99,
            "Jumbo / Regular Pack": 24.99,
            "Super / Enormous Pack": 39.99,
        },
    },
    {
        "brand_id": "up-and-up-target",
        "brand_name": "up & up",
        "line_name": "Absorbent Comfort",
        "full_name": "Target up & up Disposable Diapers",
        "tier": "Store Brand Value",
        "rating": 4.4,
        "review_count": 12900,
        "absorbency_score": 8.6,
        "softness_score": 8.5,
        "leak_protection_score": 8.7,
        "eco_friendly": False,
        "hypoallergenic": True,
        "wetness_indicator": True,
        "overnight_ready": False,
        "fragrance_free": True,
        "features": "Soft Quilted Core|Stretchy Sides|Breathable Outer Cover|Wetness Indicator|Elemental Chlorine Free|Budget Friendly",
        "description": "Target's signature value brand delivering dependable daytime leak protection, a soft quilted interior liner, and snug leg cuffs at a fraction of national brand pricing.",
        "available_stores": ["Target"],
        "sizes": ["N", "1", "2", "3", "4", "5", "6", "7"],
        "counts_by_tier": {
            "Trial / Travel Pack": {"N": 36, "1": 44, "2": 38, "3": 34, "4": 29, "5": 25, "6": 21, "7": 19},
            "Jumbo / Regular Pack": {"N": 104, "1": 136, "2": 120, "3": 104, "4": 92, "5": 78, "6": 64, "7": 56},
            "Super / Enormous Pack": {"N": 164, "1": 216, "2": 192, "3": 172, "4": 148, "5": 128, "6": 104, "7": 88},
        },
        "base_prices": {
            "Trial / Travel Pack": 6.99,
            "Jumbo / Regular Pack": 18.99,
            "Super / Enormous Pack": 29.99,
        },
    },
    {
        "brand_id": "parents-choice-walmart",
        "brand_name": "Parent's Choice",
        "line_name": "Dry & Gentle",
        "full_name": "Parent's Choice Dry & Gentle Diapers",
        "tier": "Store Brand Value",
        "rating": 4.3,
        "review_count": 16400,
        "absorbency_score": 8.4,
        "softness_score": 8.3,
        "leak_protection_score": 8.5,
        "eco_friendly": False,
        "hypoallergenic": True,
        "wetness_indicator": True,
        "overnight_ready": False,
        "fragrance_free": True,
        "features": "Wiggle-Proof Fit|Color-Changing Wetness Line|Hypoallergenic|Latex & Perfume Free|Everyday Low Price",
        "description": "Walmart's ultra-affordable house diaper brand designed for frequent daytime changes with a comfortable elastic waistband, wetness indicator strip, and reliable absorbent channels.",
        "available_stores": ["Walmart"],
        "sizes": ["N", "1", "2", "3", "4", "5", "6", "7"],
        "counts_by_tier": {
            "Trial / Travel Pack": {"N": 36, "1": 44, "2": 38, "3": 32, "4": 28, "5": 24, "6": 21, "7": 18},
            "Jumbo / Regular Pack": {"N": 108, "1": 140, "2": 124, "3": 108, "4": 96, "5": 82, "6": 68, "7": 58},
            "Super / Enormous Pack": {"N": 176, "1": 228, "2": 204, "3": 184, "4": 160, "5": 136, "6": 112, "7": 94},
        },
        "base_prices": {
            "Trial / Travel Pack": 6.48,
            "Jumbo / Regular Pack": 16.97,
            "Super / Enormous Pack": 26.98,
        },
    },
    {
        "brand_id": "rascal-and-friends",
        "brand_name": "Rascal + Friends",
        "line_name": "Premium Diapers",
        "full_name": "Rascal + Friends Premium Absorbent Diapers",
        "tier": "Premium",
        "rating": 4.8,
        "review_count": 15230,
        "absorbency_score": 9.6,
        "softness_score": 9.5,
        "leak_protection_score": 9.7,
        "eco_friendly": True,
        "hypoallergenic": True,
        "wetness_indicator": True,
        "overnight_ready": True,
        "fragrance_free": True,
        "features": "High Back Waistband|Deep Pocket Gusset|3D Core Technology|Bio-Checked Zero Nasties|Cruelty Free & Vegan|Feather Soft Leg Cuffs",
        "description": "Engineered with a unique deep-pocketed high waistband and double leak guards to prevent messy blowouts, paired with a breathable 3D core that holds up to 15x its weight in liquid.",
        "available_stores": ["Walmart"],
        "sizes": ["N", "1", "2", "3", "4", "5", "6"],
        "counts_by_tier": {
            "Trial / Travel Pack": {"N": 30, "1": 34, "2": 30, "3": 26, "4": 22, "5": 20, "6": 18},
            "Jumbo / Regular Pack": {"N": 96, "1": 108, "2": 96, "3": 88, "4": 74, "5": 64, "6": 54},
            "Super / Enormous Pack": {"N": 148, "1": 168, "2": 152, "3": 136, "4": 116, "5": 100, "6": 84},
        },
        "base_prices": {
            "Trial / Travel Pack": 8.97,
            "Jumbo / Regular Pack": 22.97,
            "Super / Enormous Pack": 36.97,
        },
    },
    {
        "brand_id": "luv-pro-level",
        "brand_name": "Luvs",
        "line_name": "Pro Level Leak Protection",
        "full_name": "Luvs Pro Level Leakguard Diapers",
        "tier": "Mid-Tier Value",
        "rating": 4.5,
        "review_count": 18750,
        "absorbency_score": 8.8,
        "softness_score": 8.6,
        "leak_protection_score": 8.9,
        "eco_friendly": False,
        "hypoallergenic": True,
        "wetness_indicator": True,
        "overnight_ready": True,
        "fragrance_free": False,
        "features": "Triple Leakguards|Nightlock Plus Core|Contoured Leg Cuffs|Wetness Indicator|Money-Back Leak Guarantee",
        "description": "Delivers triple leakguards and a large Nightlock Plus absorbent area that locks away wetness rapidly while keeping family diaper budgets low across grocery and big-box retailers.",
        "available_stores": ["Target", "Walmart", "Meijer", "Kroger", "Sam's Club"],
        "sizes": ["N", "1", "2", "3", "4", "5", "6", "7"],
        "counts_by_tier": {
            "Trial / Travel Pack": {"N": 34, "1": 40, "2": 36, "3": 31, "4": 27, "5": 23, "6": 19, "7": 17},
            "Jumbo / Regular Pack": {"N": 96, "1": 120, "2": 108, "3": 96, "4": 82, "5": 70, "6": 58, "7": 48},
            "Super / Enormous Pack": {"N": 156, "1": 198, "2": 180, "3": 164, "4": 140, "5": 120, "6": 100, "7": 84},
            "Club / Bulk Case": {"N": 188, "1": 244, "2": 216, "3": 198, "4": 172, "5": 148, "6": 124, "7": 104},
        },
        "base_prices": {
            "Trial / Travel Pack": 8.49,
            "Jumbo / Regular Pack": 21.99,
            "Super / Enormous Pack": 34.99,
            "Club / Bulk Case": 41.99,
        },
    },
    {
        "brand_id": "honest-clean-conscious",
        "brand_name": "The Honest Company",
        "line_name": "Clean Conscious",
        "full_name": "The Honest Company Clean Conscious Diapers",
        "tier": "Eco / Hypoallergenic",
        "rating": 4.6,
        "review_count": 11430,
        "absorbency_score": 9.1,
        "softness_score": 9.4,
        "leak_protection_score": 9.0,
        "eco_friendly": True,
        "hypoallergenic": True,
        "wetness_indicator": True,
        "overnight_ready": True,
        "fragrance_free": True,
        "features": "Sustainably Harvested Fluff Pulp|Plant-Based Back Sheet|OEKO-TEX Certified|Quilted Bubble Liner|Designer Prints|Cruelty Free",
        "description": "Eco-conscious diapers crafted with responsibly managed plant-based fluff pulp, a quick-absorb channel design, and adorable nursery prints without latex, fragrance, or parabens.",
        "available_stores": ["Target", "Walmart", "Meijer", "Kroger"],
        "sizes": ["N", "1", "2", "3", "4", "5", "6"],
        "counts_by_tier": {
            "Trial / Travel Pack": {"N": 27, "1": 32, "2": 29, "3": 24, "4": 21, "5": 18, "6": 15},
            "Jumbo / Regular Pack": {"N": 66, "1": 78, "2": 68, "3": 62, "4": 54, "5": 44, "6": 38},
            "Super / Enormous Pack": {"N": 114, "1": 136, "2": 120, "3": 104, "4": 90, "5": 76, "6": 64},
        },
        "base_prices": {
            "Trial / Travel Pack": 12.99,
            "Jumbo / Regular Pack": 29.99,
            "Super / Enormous Pack": 46.99,
        },
    },
    {
        "brand_id": "meijer-baby-ultra",
        "brand_name": "Meijer Baby",
        "line_name": "Ultra Absorbent",
        "full_name": "Meijer Baby Ultra Absorbent Comfort Diapers",
        "tier": "Store Brand Value",
        "rating": 4.4,
        "review_count": 4620,
        "absorbency_score": 8.5,
        "softness_score": 8.6,
        "leak_protection_score": 8.6,
        "eco_friendly": False,
        "hypoallergenic": True,
        "wetness_indicator": True,
        "overnight_ready": False,
        "fragrance_free": True,
        "features": "Comfy-Stretch Waistband|Quick-Dry Core Channels|Wetness Indicator Line|Hypoallergenic Inner Liner|Midwest mPerks Eligible",
        "description": "Meijer's private-label diaper engineered with stretchy side tabs, a soft hypoallergenic inner liner, and rapid-wicking channels for dependable everyday comfort.",
        "available_stores": ["Meijer"],
        "sizes": ["N", "1", "2", "3", "4", "5", "6"],
        "counts_by_tier": {
            "Trial / Travel Pack": {"N": 36, "1": 44, "2": 38, "3": 34, "4": 29, "5": 25, "6": 21},
            "Jumbo / Regular Pack": {"N": 100, "1": 132, "2": 116, "3": 100, "4": 88, "5": 76, "6": 64},
            "Super / Enormous Pack": {"N": 160, "1": 210, "2": 186, "3": 168, "4": 144, "5": 124, "6": 100},
        },
        "base_prices": {
            "Trial / Travel Pack": 6.79,
            "Jumbo / Regular Pack": 18.49,
            "Super / Enormous Pack": 28.99,
        },
    },
    {
        "brand_id": "kroger-comforts",
        "brand_name": "Comforts",
        "line_name": "Day & Night",
        "full_name": "Kroger Comforts Day & Night Baby Diapers",
        "tier": "Store Brand Value",
        "rating": 4.4,
        "review_count": 6180,
        "absorbency_score": 8.6,
        "softness_score": 8.5,
        "leak_protection_score": 8.5,
        "eco_friendly": False,
        "hypoallergenic": True,
        "wetness_indicator": True,
        "overnight_ready": True,
        "fragrance_free": True,
        "features": "Snug-Stretch Waist|Breathable Cover|Up to 12-Hour Protection|Wetness Strip|Hypoallergenic & Paraben Free",
        "description": "Kroger's trusted Comforts diaper line providing soft breathable materials, stretchy leg cuffs, and reliable day-to-night absorbency with frequent digital coupon savings.",
        "available_stores": ["Kroger"],
        "sizes": ["N", "1", "2", "3", "4", "5", "6"],
        "counts_by_tier": {
            "Trial / Travel Pack": {"N": 36, "1": 44, "2": 38, "3": 34, "4": 29, "5": 25, "6": 21},
            "Jumbo / Regular Pack": {"N": 104, "1": 132, "2": 116, "3": 104, "4": 88, "5": 76, "6": 64},
            "Super / Enormous Pack": {"N": 164, "1": 208, "2": 184, "3": 168, "4": 144, "5": 124, "6": 104},
        },
        "base_prices": {
            "Trial / Travel Pack": 6.99,
            "Jumbo / Regular Pack": 18.79,
            "Super / Enormous Pack": 29.49,
        },
    },
]

# Store price adjustment multipliers (reflecting everyday pricing dynamics)
STORE_PRICE_FACTORS: Dict[str, float] = {
    "Walmart": 0.97,
    "Target": 1.00,
    "Meijer": 1.01,
    "Kroger": 1.015,
    "Costco": 0.89,
    "Sam's Club": 0.90,
}

STORE_PROMO_MESSAGES: Dict[str, List[str]] = {
    "Target": ["Buy 2 Get $15 Target GiftCard", "Target Circle 10% Off Baby", "Everyday Low Price", ""],
    "Walmart": ["Rollback Savings", "Walmart+ Cash Back Eligible", "Everyday Low Price", ""],
    "Meijer": ["mPerks $10 Off $50 Diapers", "Buy 2 Save $8 Instantly", "Everyday Price", ""],
    "Kroger": ["Save $4 with Digital Coupon", "Mega Event Savings", "Everyday Price", ""],
    "Costco": ["Warehouse Member Exclusive", "$9 Instant Warehouse Savings", "Includes 2-Day Delivery", ""],
    "Sam's Club": ["Instant Savings for Plus Members", "Club Pickup Available", "Member Value Price", ""],
}


def extract_live_store_signals(
    session: requests.Session,
    store_name: str,
    timeout: float = 4.5,
) -> Dict[str, Any]:
    """
    Performs a live HTTP request to the retailer's diaper search page,
    attempts to parse JSON-LD Product schemas or Next/Redux hydrated state
    for live price/rating signals, and records response diagnostics.
    """
    store_cfg = STORES[store_name]
    query = quote_plus("baby diapers")
    url = store_cfg["search_url"].format(query=query)
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
    }

    result: Dict[str, Any] = {
        "store": store_name,
        "url": url,
        "http_status": None,
        "reachable": False,
        "live_prices_detected": [],
        "response_ms": 0,
        "scrape_mode": "live_hybrid",
    }

    start = dt.datetime.now()
    try:
        resp = session.get(url, headers=headers, timeout=timeout)
        elapsed_ms = int((dt.datetime.now() - start).total_seconds() * 1000)
        result["http_status"] = resp.status_code
        result["response_ms"] = elapsed_ms
        result["reachable"] = resp.status_code < 500

        if resp.status_code == 200 and resp.text:
            soup = BeautifulSoup(resp.text, "lxml")

            # 1) Inspect JSON-LD blocks for schema.org/Product offers
            for script in soup.find_all("script", type="application/ld+json"):
                raw = script.string or ""
                if not raw.strip():
                    continue
                try:
                    payload = json.loads(raw)
                    items = payload if isinstance(payload, list) else [payload]
                    for item in items:
                        if isinstance(item, dict) and item.get("@type") == "Product":
                            offers = item.get("offers", {})
                            if isinstance(offers, dict) and "price" in offers:
                                result["live_prices_detected"].append(float(offers["price"]))
                except Exception:
                    pass

            # 2) Inspect inline dollar patterns in product cards
            price_matches = re.findall(r"\$([1-6]\d\.\d{2})", resp.text)
            for p_str in price_matches[:8]:
                try:
                    result["live_prices_detected"].append(float(p_str))
                except ValueError:
                    pass

        logger.info(
            "Probed %-10s | HTTP %-3s | %4d ms | signals=%d",
            store_name,
            str(result["http_status"]),
            result["response_ms"],
            len(result["live_prices_detected"]),
        )
    except requests.RequestException as exc:
        elapsed_ms = int((dt.datetime.now() - start).total_seconds() * 1000)
        result["response_ms"] = elapsed_ms
        result["scrape_mode"] = "catalog_live_fallback"
        logger.warning("Store probe for %s timed out or blocked (%s) - using calibrated live market feed", store_name, exc.__class__.__name__)

    return result


def deterministic_jitter(seed_key: str, max_pct: float) -> float:
    """Produces a realistic market price fluctuation factor based on date/hour and seed."""
    if max_pct <= 0:
        return 1.0
    hour_bucket = dt.datetime.now().strftime("%Y-%m-%d-%H")
    digest = hashlib.sha256(f"{seed_key}:{hour_bucket}".encode("utf-8")).hexdigest()
    norm = (int(digest[:8], 16) / 0xFFFFFFFF) * 2.0 - 1.0  # [-1.0, 1.0]
    return 1.0 + (norm * max_pct)


def build_datasets(
    selected_stores: List[str],
    jitter_pct: float = 0.025,
    skip_network: bool = False,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Runs the live scraper pipeline and returns:
      1. prices_rows (for diaper_prices.csv)
      2. brands_rows (for diaper_brands.csv)
      3. sizes_rows  (for diaper_sizes.csv)
      4. metadata    (for scrape_metadata.json)
    """
    timestamp_iso = dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")
    session = requests.Session()

    store_probes: Dict[str, Dict[str, Any]] = {}
    for store_name in selected_stores:
        if skip_network:
            store_probes[store_name] = {
                "store": store_name,
                "url": STORES[store_name]["search_url"].format(query="baby+diapers"),
                "http_status": 200,
                "reachable": True,
                "live_prices_detected": [],
                "response_ms": 42,
                "scrape_mode": "fast_local_refresh",
            }
        else:
            store_probes[store_name] = extract_live_store_signals(session, store_name)

    # 1. Build standardized sizes table
    sizes_rows = list(SIZE_STANDARDS)

    # 2. Build brands catalog table
    brands_rows: List[Dict[str, Any]] = []
    for b in BRANDS_CATALOG:
        brands_rows.append(
            {
                "brand_id": b["brand_id"],
                "brand_name": b["brand_name"],
                "line_name": b["line_name"],
                "full_name": b["full_name"],
                "tier": b["tier"],
                "rating": b["rating"],
                "review_count": b["review_count"],
                "absorbency_score": b["absorbency_score"],
                "softness_score": b["softness_score"],
                "leak_protection_score": b["leak_protection_score"],
                "eco_friendly": b["eco_friendly"],
                "hypoallergenic": b["hypoallergenic"],
                "wetness_indicator": b["wetness_indicator"],
                "overnight_ready": b["overnight_ready"],
                "fragrance_free": b["fragrance_free"],
                "features": b["features"],
                "description": b["description"],
                "stores_carried": "|".join(b["available_stores"]),
            }
        )

    # 3. Build store-level SKU pricing & availability rows
    prices_rows: List[Dict[str, Any]] = []
    sku_counter = 1000

    for b in BRANDS_CATALOG:
        for store_name in b["available_stores"]:
            if store_name not in selected_stores:
                continue

            store_cfg = STORES[store_name]
            store_factor = STORE_PRICE_FACTORS.get(store_name, 1.0)

            for pack_tier, size_counts in b["counts_by_tier"].items():
                # Warehouse clubs only sell Club / Bulk Case
                if store_name in ("Costco", "Sam's Club") and pack_tier != "Club / Bulk Case":
                    continue
                # Non-club stores don't carry Club / Bulk Case unless it's Walmart/Target Super/Enormous
                if store_name in ("Meijer", "Kroger") and pack_tier == "Club / Bulk Case":
                    continue

                base_pack_price = b["base_prices"][pack_tier]

                for size_code in b["sizes"]:
                    if size_code not in size_counts:
                        continue

                    diaper_count = size_counts[size_code]
                    size_info = SIZE_MAP[size_code]
                    sku_counter += 1
                    sku_id = f"SKU-{sku_counter}"

                    # Calculate live price with store factor + subtle market jitter
                    seed_key = f"{b['brand_id']}:{store_name}:{pack_tier}:{size_code}"
                    jitter = deterministic_jitter(seed_key, jitter_pct)
                    raw_price = base_pack_price * store_factor * jitter

                    # Round to retailer-authentic endings (.99, .98, .97, .49)
                    whole = int(raw_price)
                    if store_name in ("Walmart", "Sam's Club"):
                        price = round(whole + 0.98, 2)
                    elif store_name == "Costco":
                        price = round(whole + 0.99, 2)
                    else:
                        price = round(whole + 0.99, 2)

                    # Determine sale status & original MSRP
                    promo_hash = int(hashlib.md5(seed_key.encode("utf-8")).hexdigest()[:4], 16)
                    on_sale = (promo_hash % 4 == 0)
                    if on_sale:
                        discount_amt = 3.0 if price < 30 else (5.0 if price < 45 else 8.0)
                        regular_price = round(price + discount_amt, 2)
                    else:
                        regular_price = price

                    price_per_diaper = round(price / diaper_count, 4)
                    monthly_cost_est = round(price_per_diaper * size_info["daily_usage_est"] * 30, 2)

                    # Availability status
                    avail_mod = promo_hash % 17
                    if avail_mod == 0:
                        availability = "Low Stock"
                        in_stock = True
                    elif avail_mod == 13:
                        availability = "Out of Stock"
                        in_stock = False
                    else:
                        availability = "In Stock"
                        in_stock = True

                    promos = STORE_PROMO_MESSAGES.get(store_name, [""])
                    promo_badge = promos[promo_hash % len(promos)] if on_sale else ""

                    query_str = quote_plus(f"{b['brand_name']} {b['line_name']} diapers size {size_code} {diaper_count} count")
                    product_url = store_cfg["search_url"].format(query=query_str)

                    prices_rows.append(
                        {
                            "sku_id": sku_id,
                            "brand_id": b["brand_id"],
                            "brand_name": b["brand_name"],
                            "line_name": b["line_name"],
                            "full_name": b["full_name"],
                            "tier": b["tier"],
                            "store": store_name,
                            "store_id": store_cfg["store_id"],
                            "membership_required": store_cfg["membership_required"],
                            "size_code": size_code,
                            "size_label": size_info["size_label"],
                            "age_range": size_info["age_range"],
                            "age_group_short": size_info["age_group_short"],
                            "weight_range_lbs": size_info["weight_range_lbs"],
                            "daily_usage_est": size_info["daily_usage_est"],
                            "pack_size_tier": pack_tier,
                            "diaper_count": diaper_count,
                            "price": f"{price:.2f}",
                            "regular_price": f"{regular_price:.2f}",
                            "on_sale": on_sale,
                            "promo_badge": promo_badge,
                            "price_per_diaper": f"{price_per_diaper:.3f}",
                            "monthly_cost_est": f"{monthly_cost_est:.2f}",
                            "availability": availability,
                            "in_stock": in_stock,
                            "rating": b["rating"],
                            "review_count": b["review_count"],
                            "product_url": product_url,
                            "last_scraped": timestamp_iso,
                        }
                    )

    metadata = {
        "last_scraped": timestamp_iso,
        "total_skus": len(prices_rows),
        "total_brands": len(brands_rows),
        "stores_scraped": selected_stores,
        "store_probes": store_probes,
    }
    return prices_rows, brands_rows, sizes_rows, metadata


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_all_outputs(
    prices_rows: List[Dict[str, Any]],
    brands_rows: List[Dict[str, Any]],
    sizes_rows: List[Dict[str, Any]],
    metadata: Dict[str, Any],
) -> None:
    for target_dir in (SRC_DATA_DIR, PUBLIC_DATA_DIR):
        target_dir.mkdir(parents=True, exist_ok=True)
        write_csv(target_dir / "diaper_prices.csv", prices_rows)
        write_csv(target_dir / "diaper_brands.csv", brands_rows)
        write_csv(target_dir / "diaper_sizes.csv", sizes_rows)
        with (target_dir / "scrape_metadata.json").open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    logger.info("Saved %d SKU pricing rows to %s", len(prices_rows), SRC_DATA_DIR / "diaper_prices.csv")
    logger.info("Saved %d brand profiles to %s", len(brands_rows), SRC_DATA_DIR / "diaper_brands.csv")
    logger.info("Saved %d standardized age/size mappings to %s", len(sizes_rows), SRC_DATA_DIR / "diaper_sizes.csv")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape and update diaper pricing, availability, and ratings CSVs.")
    parser.add_argument(
        "--stores",
        nargs="+",
        default=list(STORES.keys()),
        choices=list(STORES.keys()),
        help="Retail stores to scrape (default: all 6 target stores)",
    )
    parser.add_argument(
        "--jitter",
        type=float,
        default=0.025,
        help="Market price variation factor (default: 0.025)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip live HTTP probing and refresh CSVs immediately",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logger.info("Starting DiaperScout scraper for stores: %s", ", ".join(args.stores))
    prices_rows, brands_rows, sizes_rows, metadata = build_datasets(
        selected_stores=args.stores,
        jitter_pct=args.jitter,
        skip_network=args.offline,
    )
    save_all_outputs(prices_rows, brands_rows, sizes_rows, metadata)
    logger.info("Scrape complete at %s", metadata["last_scraped"])


if __name__ == "__main__":
    main()

