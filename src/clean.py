"""Step 2 - Transform: clean the raw posts and tag the product they mention."""
import re

import pandas as pd
from bs4 import BeautifulSoup

from src.config import PRODUCT_KEYWORDS

URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
MENTION_PATTERN = re.compile(r"@\w+(@[\w.]+)?")
SPACE_PATTERN = re.compile(r"\s+")


def html_to_text(html):
    """Mastodon returns posts as HTML. Keep only the visible text."""
    if not isinstance(html, str):
        return ""
    return BeautifulSoup(html, "html.parser").get_text(separator=" ")


def clean_text(text):
    """Remove links and @mentions, keep hashtag words, and normalise spaces."""
    text = URL_PATTERN.sub(" ", text)
    text = MENTION_PATTERN.sub(" ", text)
    text = text.replace("#", "")
    text = SPACE_PATTERN.sub(" ", text)
    return text.strip()


def detect_product(text):
    """Return which product a post is about: Apple, Samsung, Both or None."""
    lower = text.lower()
    found = [name for name, words in PRODUCT_KEYWORDS.items() if any(w in lower for w in words)]
    if len(found) == 2:
        return "Both"
    if len(found) == 1:
        return found[0]
    return None


def clean_posts(raw_df, language="en", min_words=3):
    """Run all cleaning steps and return a tidy DataFrame plus a small cleaning report."""
    df = raw_df.copy()
    report = {"raw_rows": len(df)}

    # The same post can appear under several hashtags -> keep one copy.
    df = df.drop_duplicates(subset="post_id")
    report["after_duplicate_ids"] = len(df)

    df["text"] = df["content_html"].apply(html_to_text).apply(clean_text)

    # Keep posts in the chosen language (posts without a language tag are kept).
    if language:
        df = df[df["language"].isna() | (df["language"] == language)]
    report["after_language_filter"] = len(df)

    # Drop very short posts and reposts with identical text.
    df = df[df["text"].str.split().str.len() >= min_words]
    df = df.drop_duplicates(subset="text")
    report["after_short_and_duplicate_text"] = len(df)

    df["product"] = df["text"].apply(detect_product)
    df = df[df["product"].notna()]
    report["after_product_filter"] = len(df)

    df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
    df = df[["post_id", "created_at", "language", "search_term", "product", "text", "url"]]
    return df.reset_index(drop=True), report
