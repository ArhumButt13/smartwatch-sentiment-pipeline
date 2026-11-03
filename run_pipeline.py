"""Run the full pipeline: collect -> clean -> load to SQL -> score -> report.

    python run_pipeline.py --sample        # run on the included sample file (no token needed)
    python run_pipeline.py --pages 3       # collect fresh posts from Mastodon first
"""
import argparse

import pandas as pd

from src.clean import clean_posts
from src.config import CLEAN_FILE, DB_FILE, OUTPUT_DIR, RAW_FILE, SAMPLE_RAW_FILE
from src.load_sql import load_to_sqlite
from src.report import build_report
from src.sentiment import score_posts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true", help="Use the sample file instead of collecting")
    parser.add_argument("--pages", type=int, default=3, help="Pages per hashtag when collecting")
    args = parser.parse_args()

    if args.sample:
        raw = pd.read_csv(SAMPLE_RAW_FILE)
        print(f"1. Loaded {len(raw)} sample posts")
    else:
        from src.collect import collect
        raw = collect(pages=args.pages)
        print(f"1. Collected {len(raw)} posts")

    clean, report = clean_posts(raw)
    CLEAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(CLEAN_FILE, index=False)
    print("2. Cleaning report:")
    for step, rows in report.items():
        print(f"     {step:<32} {rows}")

    count = load_to_sqlite(clean, DB_FILE)
    print(f"3. Loaded {count} rows into SQLite table posts_clean ({DB_FILE.name})")

    scored = score_posts(DB_FILE)
    print(f"4. Scored {len(scored)} posts (-1 / 0 / +1)")

    summary = build_report(DB_FILE, OUTPUT_DIR)
    print("5. Summary by product:")
    print(summary.to_string(index=False))
    print(f"\nChart saved to {OUTPUT_DIR / 'sentiment_by_product.png'}")


if __name__ == "__main__":
    main()
