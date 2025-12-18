"""
Transcription job management for worker-based transcription system.

Server creates jobs instead of transcribing directly.
Workers pull jobs, transcribe videos, and upload results back.
"""

import uuid
from datetime import datetime
from database import get_db_connection


def create_transcription_job(video_id: str, video_url: str, video_title: str = None, priority: int = 0) -> str:
    """
    Create a transcription job in the database.
    
    Args:
        video_id: YouTube video ID
        video_url: Full YouTube video URL
        video_title: Video title (optional)
        priority: Priority level (lower = higher priority, default: 0)
    
    Returns:
        str: Job ID (UUID)
    """
    job_id = str(uuid.uuid4())
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transcription_jobs 
                (job_id, video_id, video_url, video_title, status, priority)
                VALUES (%s, %s, %s, %s, 'PENDING', %s)
                ON CONFLICT (job_id) DO NOTHING
            """, (job_id, video_id, video_url, video_title, priority))
        
        return job_id
    except Exception as e:
        print(f"✗ Error creating transcription job: {e}")
        raise


def get_pending_jobs(limit: int = 10) -> list:
    """
    Get pending transcription jobs (for workers to pull).
    
    Args:
        limit: Maximum number of jobs to return
    
    Returns:
        list: List of job dictionaries
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT job_id, video_id, video_url, video_title, priority
                FROM transcription_jobs
                WHERE status = 'PENDING'
                ORDER BY priority ASC, created_at ASC
                LIMIT %s
            """, (limit,))
            
            jobs = []
            for row in cursor.fetchall():
                jobs.append({
                    "job_id": row[0],
                    "video_id": row[1],
                    "video_url": row[2],
                    "video_title": row[3],
                    "priority": row[4]
                })
            
            return jobs
    except Exception as e:
        print(f"✗ Error fetching pending jobs: {e}")
        return []


def claim_jobs(job_ids: list, worker_id: str) -> bool:
    """
    Mark jobs as CLAIMED by a worker.
    
    Args:
        job_ids: List of job IDs to claim
        worker_id: Worker identifier
    
    Returns:
        bool: True if successful
    """
    if not job_ids:
        return True
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Use IN clause with tuple for PostgreSQL
            placeholders = ','.join(['%s'] * len(job_ids))
            cursor.execute(f"""
                UPDATE transcription_jobs
                SET status = 'CLAIMED',
                    claimed_at = %s,
                    claimed_by = %s
                WHERE job_id IN ({placeholders}) AND status = 'PENDING'
            """, (datetime.utcnow(), worker_id) + tuple(job_ids))
        
        return True
    except Exception as e:
        print(f"✗ Error claiming jobs: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_transcript_by_video_id(video_id: str) -> dict:
    """
    Get transcript for a video by video_id.
    
    Args:
        video_id: YouTube video ID
    
    Returns:
        dict: Transcript data or None if not found
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT video_id, transcript, language, duration, created_at
                FROM transcripts
                WHERE video_id = %s
            """, (video_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "video_id": row[0],
                    "transcript": row[1],
                    "language": row[2],
                    "duration": row[3],
                    "created_at": row[4]
                }
            return None
    except Exception as e:
        print(f"✗ Error fetching transcript: {e}")
        return None


def reset_stale_jobs(timeout_minutes: int = 30) -> int:
    """
    Reset jobs that have been CLAIMED for too long back to PENDING.
    
    Args:
        timeout_minutes: Minutes after which a CLAIMED job is considered stale
    
    Returns:
        int: Number of jobs reset
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE transcription_jobs
                SET status = 'PENDING',
                    claimed_at = NULL,
                    claimed_by = NULL,
                    retry_count = retry_count + 1
                WHERE status = 'CLAIMED'
                AND claimed_at < NOW() - INTERVAL '%s minutes'
            """, (timeout_minutes,))
            
            count = cursor.rowcount
            if count > 0:
                print(f"✓ Reset {count} stale job(s)")
            return count
    except Exception as e:
        print(f"✗ Error resetting stale jobs: {e}")
        return 0
