"""Step 3 - Load: store the cleaned posts in a SQLite database."""
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts_clean (
    post_id      TEXT PRIMARY KEY,
    created_at   TEXT NOT NULL,
    language     TEXT,
    search_term  TEXT,
    product      TEXT NOT NULL,
    text         TEXT NOT NULL,
    url          TEXT
);
"""


def load_to_sqlite(df, db_path):
    """Write the cleaned DataFrame to the posts_clean table (replacing old rows)."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("DROP TABLE IF EXISTS posts_clean")
        conn.execute(SCHEMA)
        rows = df.assign(created_at=df["created_at"].astype(str), post_id=df["post_id"].astype(str))
        rows.to_sql("posts_clean", conn, if_exists="append", index=False)
        count = conn.execute("SELECT COUNT(*) FROM posts_clean").fetchone()[0]
    return count
