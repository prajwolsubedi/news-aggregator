"""
Cleanup task for stale transcription jobs.

Resets jobs that have been CLAIMED for too long back to PENDING.
This should be run periodically (e.g., every 30 minutes).
"""

from transcription_jobs import reset_stale_jobs


def cleanup_stale_jobs(timeout_minutes: int = 30):
    """
    Reset stale transcription jobs.
    
    Args:
        timeout_minutes: Minutes after which a CLAIMED job is considered stale
    """
    print(f"\n🔄 Cleaning up stale jobs (timeout: {timeout_minutes} minutes)...")
    count = reset_stale_jobs(timeout_minutes)
    print(f"✓ Cleanup complete: {count} job(s) reset")
    return count


if __name__ == "__main__":
    cleanup_stale_jobs()
