"""Step 5 - Report: compare sentiment between the two products."""
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

SUMMARY_SQL = """
SELECT p.product,
       COUNT(*)                                          AS posts,
       ROUND(AVG(s.compound), 3)                         AS avg_compound,
       ROUND(100.0 * SUM(s.sentiment = 1)  / COUNT(*), 1) AS pct_positive,
       ROUND(100.0 * SUM(s.sentiment = 0)  / COUNT(*), 1) AS pct_neutral,
       ROUND(100.0 * SUM(s.sentiment = -1) / COUNT(*), 1) AS pct_negative
FROM posts_clean p
JOIN post_sentiment s ON s.post_id = p.post_id
WHERE p.product != 'Both'
GROUP BY p.product
ORDER BY p.product;
"""


def build_report(db_path, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        summary = pd.read_sql(SUMMARY_SQL, conn)
    summary.to_csv(output_dir / "sentiment_summary.csv", index=False)

    chart = summary.set_index("product")[["pct_negative", "pct_neutral", "pct_positive"]]
    ax = chart.plot(kind="bar", color=["#c0392b", "#95a5a6", "#27ae60"], figsize=(7, 4))
    ax.set_ylabel("Share of posts (%)")
    ax.set_xlabel("")
    ax.set_title("Sentiment of Mastodon posts by product")
    ax.legend(["Negative (-1)", "Neutral (0)", "Positive (+1)"])
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_dir / "sentiment_by_product.png", dpi=150)
    plt.close()
    return summary
