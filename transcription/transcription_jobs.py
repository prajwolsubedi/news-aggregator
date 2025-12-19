"""
Transcription job management for worker-based transcription system.

Server creates jobs instead of transcribing directly.
Workers pull jobs, transcribe videos, and upload results back.
"""

import uuid
from datetime import datetime
from core.database import get_db_connection


def create_transcription_job(video_id: str, video_url: str, video_title: str | None = None, priority: int = 0) -> str:
    """Create a transcription job in the database."""
    job_id = str(uuid.uuid4())
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO transcription_jobs 
                (job_id, video_id, video_url, video_title, status, priority)
                VALUES (%s, %s, %s, %s, 'PENDING', %s)
                ON CONFLICT (job_id) DO NOTHING
                """,
                (job_id, video_id, video_url, video_title, priority),
            )
        return job_id
    except Exception as e:
        print(f"✗ Error creating transcription job: {e}")
        raise


def get_pending_jobs(limit: int = 10) -> list[dict]:
    """Get pending transcription jobs (for workers to pull).
    
    Returns jobs with status 'PENDING' or stale 'CLAIMED' jobs (claimed > 30 minutes ago).
    This allows automatic retry of jobs that were claimed but never completed.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # First, reset stale CLAIMED jobs back to PENDING
            reset_stale_jobs(timeout_minutes=30)
            
            # Then get PENDING jobs (including freshly reset ones)
            cursor.execute(
                """
                SELECT job_id, video_id, video_url, video_title, priority
                FROM transcription_jobs
                WHERE status = 'PENDING'
                ORDER BY priority ASC, created_at ASC
                LIMIT %s
                """,
                (limit,),
            )
            jobs = [
                {
                    "job_id": row[0],
                    "video_id": row[1],
                    "video_url": row[2],
                    "video_title": row[3],
                    "priority": row[4],
                }
                for row in cursor.fetchall()
            ]
            return jobs
    except Exception as e:
        print(f"✗ Error fetching pending jobs: {e}")
        return []


def claim_jobs(job_ids: list[str], worker_id: str) -> bool:
    """Mark jobs as CLAIMED by a worker."""
    if not job_ids:
        return True
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            placeholders = ",".join(["%s"] * len(job_ids))
            cursor.execute(
                f"""
                UPDATE transcription_jobs
                SET status = 'CLAIMED',
                    claimed_at = %s,
                    claimed_by = %s
                WHERE job_id IN ({placeholders}) AND status = 'PENDING'
                """,
                (datetime.utcnow(), worker_id, *job_ids),
            )
        return True
    except Exception as e:
        print(f"✗ Error claiming jobs: {e}")
        import traceback

        traceback.print_exc()
        return False


def get_transcript_by_video_id(video_id: str) -> dict | None:
    """Get transcript for a video by video_id."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT video_id, transcript, language, duration, created_at
                FROM transcripts
                WHERE video_id = %s
                """,
                (video_id,),
            )
            row = cursor.fetchone()
            if row:
                return {
                    "video_id": row[0],
                    "transcript": row[1],
                    "language": row[2],
                    "duration": row[3],
                    "created_at": row[4],
                }
            return None
    except Exception as e:
        print(f"✗ Error fetching transcript: {e}")
        return None


def reset_stale_jobs(timeout_minutes: int = 30) -> int:
    """Reset jobs that have been CLAIMED for too long back to PENDING."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE transcription_jobs
                SET status = 'PENDING',
                    claimed_at = NULL,
                    claimed_by = NULL,
                    retry_count = retry_count + 1
                WHERE status = 'CLAIMED'
                AND claimed_at < NOW() - INTERVAL '%s minutes'
                """,
                (timeout_minutes,),
            )
            count = cursor.rowcount
            if count > 0:
                print(f"✓ Reset {count} stale job(s)")
            return count
    except Exception as e:
        print(f"✗ Error resetting stale jobs: {e}")
        return 0
