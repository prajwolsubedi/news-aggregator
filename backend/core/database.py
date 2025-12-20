import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()


@contextmanager
def get_db_connection():
    """Database connection context manager. Auto-commits on success, rolls back on error."""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise Exception("DATABASE_URL not found in environment variables")
    
    conn = psycopg2.connect(url)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_schema():
    """Initialize database schema. Returns True on success."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Subscribers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subscribers (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    subscribed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    unsubscribe_token VARCHAR(255) UNIQUE NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_subscribers_email ON subscribers(email);
                CREATE INDEX IF NOT EXISTS idx_subscribers_token ON subscribers(unsubscribe_token);
                CREATE INDEX IF NOT EXISTS idx_subscribers_active ON subscribers(is_active);
            """)
            # Transcription jobs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transcription_jobs (
                    job_id VARCHAR(255) PRIMARY KEY,
                    video_id VARCHAR(255) NOT NULL,
                    video_url TEXT NOT NULL,
                    video_title TEXT,
                    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
                    priority INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    claimed_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    claimed_by VARCHAR(255),
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0
                );
                CREATE INDEX IF NOT EXISTS idx_transcription_jobs_status ON transcription_jobs(status);
                CREATE INDEX IF NOT EXISTS idx_transcription_jobs_created_at ON transcription_jobs(created_at);
                CREATE INDEX IF NOT EXISTS idx_transcription_jobs_video_id ON transcription_jobs(video_id);
            """)
            # Transcripts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transcripts (
                    id SERIAL PRIMARY KEY,
                    video_id VARCHAR(255) UNIQUE NOT NULL,
                    job_id VARCHAR(255),
                    transcript TEXT NOT NULL,
                    language VARCHAR(10),
                    duration INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES transcription_jobs(job_id)
                );
                CREATE INDEX IF NOT EXISTS idx_transcripts_video_id ON transcripts(video_id);
                CREATE INDEX IF NOT EXISTS idx_transcripts_job_id ON transcripts(job_id);
            """)
            # Daily ranked news table: stores top 10 ranked items per day (before transcription)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_ranked_news (
                    id SERIAL PRIMARY KEY,
                    issue_date DATE NOT NULL,
                    rank INTEGER NOT NULL,
                    source VARCHAR(20) NOT NULL,
                    news_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    published_at TEXT,
                    source_link TEXT,
                    video_id TEXT,
                    summary TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(issue_date, rank)
                );
                CREATE INDEX IF NOT EXISTS idx_daily_ranked_news_issue_date
                    ON daily_ranked_news(issue_date);
                CREATE INDEX IF NOT EXISTS idx_daily_ranked_news_rank
                    ON daily_ranked_news(issue_date, rank);
            """)
            # Daily top news table: one row per run/day with final top items JSON
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_top_news (
                    id SERIAL PRIMARY KEY,
                    issue_date DATE NOT NULL,
                    top_items_json JSONB NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE UNIQUE INDEX IF NOT EXISTS idx_daily_top_news_issue_date
                    ON daily_top_news(issue_date);
                CREATE INDEX IF NOT EXISTS idx_daily_top_news_created_at
                    ON daily_top_news(created_at);
            """)
        return True
    except Exception as e:
        print(f"✗ Error initializing schema: {e}")
        return False


def get_all_active_subscribers():
    """Get all active subscribers. Returns list of dicts."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT id, email, subscribed_at, unsubscribe_token, is_active
                FROM subscribers
                WHERE is_active = TRUE
                ORDER BY subscribed_at DESC
            """)
            return cursor.fetchall()
    except Exception as e:
        print(f"✗ Error fetching subscribers: {e}")
        return []


def get_subscriber_by_email(email: str):
    """Get subscriber by email. Returns dict or None."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT id, email, subscribed_at, unsubscribe_token, is_active
                FROM subscribers WHERE email = %s
            """, (email,))
            return cursor.fetchone()
    except Exception as e:
        print(f"✗ Error fetching subscriber: {e}")
        return None


def get_subscriber_by_token(token: str):
    """Get subscriber by unsubscribe token. Returns dict or None."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT id, email, subscribed_at, unsubscribe_token, is_active
                FROM subscribers WHERE unsubscribe_token = %s
            """, (token,))
            return cursor.fetchone()
    except Exception as e:
        print(f"✗ Error fetching subscriber: {e}")
        return None


def add_subscriber(email: str, unsubscribe_token: str):
    """Add or reactivate subscriber. Returns dict or None."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                INSERT INTO subscribers (email, unsubscribe_token, is_active)
                VALUES (%s, %s, TRUE)
                ON CONFLICT (email) DO UPDATE SET
                    is_active = TRUE,
                    unsubscribe_token = EXCLUDED.unsubscribe_token,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id, email, subscribed_at, unsubscribe_token, is_active
            """, (email, unsubscribe_token))
            return cursor.fetchone()
    except Exception as e:
        print(f"✗ Error adding subscriber: {e}")
        return None


def deactivate_subscriber(token: str):
    """Deactivate subscriber by token. Returns True if deactivated."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE subscribers
                SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE unsubscribe_token = %s AND is_active = TRUE
            """, (token,))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"✗ Error deactivating subscriber: {e}")
        return False


def get_subscriber_count():
    """Get count of active subscribers."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM subscribers WHERE is_active = TRUE")
            return cursor.fetchone()[0]
    except Exception as e:
        print(f"✗ Error getting count: {e}")
        return 0


def create_daily_top_news(issue_date, top_items):
    """Insert a daily_top_news row for a given date and list of items.

    top_items should be a JSON-serializable Python object (typically a list of dicts).
    Returns the inserted row id or None on failure.
    """
    import json

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO daily_top_news (issue_date, top_items_json)
                VALUES (%s, %s)
                ON CONFLICT (issue_date) DO UPDATE SET
                    top_items_json = EXCLUDED.top_items_json,
                    created_at = CURRENT_TIMESTAMP
                RETURNING id
                """,
                (issue_date, json.dumps(top_items)),
            )
            row = cursor.fetchone()
            return row[0] if row else None
    except Exception as e:
        print(f"✗ Error creating daily_top_news: {e}")
        return None


def get_latest_daily_top_news():
    """Fetch the most recent daily_top_news entry.

    Returns a dict with keys: id, issue_date, top_items, created_at
    or None if nothing is found / on error.
    """
    import json
    from psycopg2.extras import RealDictCursor

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                SELECT id, issue_date, top_items_json, created_at
                FROM daily_top_news
                ORDER BY issue_date DESC, created_at DESC
                LIMIT 1
                """
            )
            row = cursor.fetchone()
            if not row:
                return None

            # Convert JSONB to Python structure and normalize key name
            top_items = row.get("top_items_json")
            if isinstance(top_items, str):
                try:
                    top_items = json.loads(top_items)
                except Exception:
                    pass

            return {
                "id": row.get("id"),
                "issue_date": row.get("issue_date"),
                "top_items": top_items,
                "created_at": row.get("created_at"),
            }
    except Exception as e:
        print(f"✗ Error fetching latest daily_top_news: {e}")
        return None


def insert_daily_ranked_news(issue_date, ranked_items):
    """Insert top 10 ranked news items into daily_ranked_news table.

    Deletes any existing rows for the given issue_date first, then inserts
    up to 10 items with their rank (1-10).

    Args:
        issue_date: date object for the issue
        ranked_items: list of dicts, each with keys:
            - rank (1-10)
            - source ('website' or 'youtube')
            - news_id
            - title
            - published_at
            - source_link
            - video_id (for YouTube, None for websites)
            - summary (for websites, None for YouTube)

    Returns:
        int: number of rows inserted, or None on error
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Delete existing rows for this date
            cursor.execute(
                "DELETE FROM daily_ranked_news WHERE issue_date = %s",
                (issue_date,)
            )
            # Insert new rows
            inserted = 0
            for item in ranked_items[:10]:  # Ensure max 10 items
                cursor.execute(
                    """
                    INSERT INTO daily_ranked_news
                    (issue_date, rank, source, news_id, title, published_at, source_link, video_id, summary)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        issue_date,
                        item.get("rank"),
                        item.get("source"),
                        item.get("news_id"),
                        item.get("title", ""),
                        item.get("published_at"),
                        item.get("source_link"),
                        item.get("video_id"),
                        item.get("summary"),
                    ),
                )
                inserted += 1
            return inserted
    except Exception as e:
        print(f"✗ Error inserting daily_ranked_news: {e}")
        return None


def get_daily_ranked_news(issue_date):
    """Fetch ranked news items for a given issue_date.

    Returns a list of dicts ordered by rank ASC, or empty list if not found.
    Each dict contains: id, issue_date, rank, source, news_id, title,
    published_at, source_link, video_id, summary, created_at
    """
    from psycopg2.extras import RealDictCursor

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                SELECT id, issue_date, rank, source, news_id, title,
                       published_at, source_link, video_id, summary, created_at
                FROM daily_ranked_news
                WHERE issue_date = %s
                ORDER BY rank ASC
                """,
                (issue_date,),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows] if rows else []
    except Exception as e:
        print(f"✗ Error fetching daily_ranked_news: {e}")
        return []


if __name__ == "__main__":
    """Test database connection and schema initialization."""
    if not os.getenv("DATABASE_URL"):
        print("✗ Error: DATABASE_URL not found in environment variables")
        exit(1)
    
    try:
        with get_db_connection() as conn:
            print("✓ Database connection successful")
        
        if init_schema():
            print("✓ Schema initialized")
            print(f"✓ Active subscribers: {get_subscriber_count()}")
        else:
            print("✗ Schema initialization failed")
            exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        exit(1)
