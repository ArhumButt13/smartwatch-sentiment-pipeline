"""Step 1 - Extract: collect public Mastodon posts for each search term.

Usage:
    python -m src.collect --pages 3
"""
import argparse
import os

import pandas as pd
from dotenv import load_dotenv
from mastodon import Mastodon

from src.config import RAW_FILE, SEARCH_TERMS_FILE


def parse_terms(file_path):
    """Read search terms from a text file. The first line is a header ('SEARCH TERMS')."""
    with open(file_path, "r", encoding="utf-8") as file:
        next(file)  # skip the header line
        terms = [line.strip().lstrip("#") for line in file if line.strip()]
    return terms


def connect():
    """Create a Mastodon client using the token stored in the .env file."""
    load_dotenv()
    token = os.getenv("MASTODON_ACCESS_TOKEN")
    base_url = os.getenv("MASTODON_API_BASE_URL", "https://mastodon.social")
    if not token:
        raise SystemExit("No token found. Copy .env.example to .env and add MASTODON_ACCESS_TOKEN.")
    return Mastodon(access_token=token, api_base_url=base_url)


def fetch_hashtag(client, term, pages=3, per_page=40):
    """Fetch several pages of posts for one hashtag and return them as a list of dicts."""
    rows = []
    page = client.timeline_hashtag(term, limit=per_page)
    for _ in range(pages):
        if not page:
            break
        for post in page:
            rows.append({
                "post_id": post["id"],
                "search_term": term,
                "created_at": post["created_at"],
                "language": post.get("language"),
                "url": post.get("url"),
                "content_html": post["content"],
            })
        page = client.fetch_next(page)
    return rows


def collect(pages=3):
    client = connect()
    terms = parse_terms(SEARCH_TERMS_FILE)
    all_rows = []
    for term in terms:
        rows = fetch_hashtag(client, term, pages=pages)
        print(f"#{term}: {len(rows)} posts")
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    RAW_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_FILE, index=False)
    print(f"Saved {len(df)} raw posts to {RAW_FILE}")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect Mastodon posts by hashtag.")
    parser.add_argument("--pages", type=int, default=3, help="Pages per hashtag (40 posts each)")
    args = parser.parse_args()
    collect(pages=args.pages)
