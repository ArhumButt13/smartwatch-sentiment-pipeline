"""Step 4 - Score: give every post a sentiment label of -1, 0 or +1.

Uses VADER, a rule-based sentiment model made for short social-media text.
It needs no training data, which makes it a transparent baseline.
"""
import sqlite3

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

POSITIVE_CUTOFF = 0.05
NEGATIVE_CUTOFF = -0.05


def label_from_score(compound):
    """Standard VADER thresholds: >= 0.05 positive, <= -0.05 negative, else neutral."""
    if compound >= POSITIVE_CUTOFF:
        return 1
    if compound <= NEGATIVE_CUTOFF:
        return -1
    return 0


def score_posts(db_path):
    analyzer = SentimentIntensityAnalyzer()
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql("SELECT post_id, product, text FROM posts_clean", conn)
        df["compound"] = df["text"].apply(lambda t: analyzer.polarity_scores(t)["compound"])
        df["sentiment"] = df["compound"].apply(label_from_score)
        df[["post_id", "compound", "sentiment"]].to_sql("post_sentiment", conn, if_exists="replace", index=False)
    return df
