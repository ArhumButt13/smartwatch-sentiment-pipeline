import pandas as pd

from src.clean import clean_posts, clean_text, detect_product, html_to_text
from src.sentiment import label_from_score


def test_html_and_text_cleaning():
    text = clean_text(html_to_text("<p>Hi @anna@mastodon.social see https://x.io #AppleWatch</p>"))
    assert text == "Hi see AppleWatch"


def test_detect_product():
    assert detect_product("my apple watch") == "Apple Watch"
    assert detect_product("Galaxy Watch is nice") == "Samsung Galaxy Watch"
    assert detect_product("apple watch vs galaxy watch") == "Both"
    assert detect_product("a fitness tracker") is None


def test_clean_posts_removes_duplicates_and_short_posts():
    raw = pd.DataFrame({
        "post_id": ["1", "1", "2", "3"],
        "search_term": ["AppleWatch"] * 4,
        "created_at": ["2026-01-01T00:00:00+00:00"] * 4,
        "language": ["en", "en", "en", "en"],
        "url": ["u"] * 4,
        "content_html": ["<p>I like my Apple Watch a lot</p>"] * 2 + ["<p>#AppleWatch</p>", "<p>Galaxy Watch screen is great</p>"],
    })
    clean, report = clean_posts(raw)
    assert report["after_duplicate_ids"] == 3
    assert list(clean["post_id"]) == ["1", "3"]


def test_sentiment_labels():
    assert label_from_score(0.6) == 1
    assert label_from_score(0.0) == 0
    assert label_from_score(-0.4) == -1
