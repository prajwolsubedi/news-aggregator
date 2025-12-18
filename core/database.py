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
