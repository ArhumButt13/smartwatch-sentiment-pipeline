"""Shared paths and settings for the pipeline."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SEARCH_TERMS_FILE = ROOT / "config" / "search_terms.txt"
RAW_FILE = ROOT / "data" / "raw" / "posts_raw.csv"
SAMPLE_RAW_FILE = ROOT / "data" / "sample" / "sample_posts_raw.csv"
CLEAN_FILE = ROOT / "data" / "processed" / "posts_clean.csv"
DB_FILE = ROOT / "data" / "processed" / "smartwatch_sentiment.db"
OUTPUT_DIR = ROOT / "outputs"

# Keywords used to decide which product a post talks about.
PRODUCT_KEYWORDS = {
    "Apple Watch": ["apple watch", "applewatch", "watchos"],
    "Samsung Galaxy Watch": ["galaxy watch", "galaxywatch", "samsung watch", "samsungwatch", "wear os"],
}
