# Cursor Rules — YouTube Transcription Migration to Local GPU Workers

## 1. Migration Goal

**REMOVE:** All server-side YouTube transcription using `youtube-transcript-api` or `SerpAPI`

**IMPLEMENT:** Pull-based job system where local GPU workers handle all transcription

**PRINCIPLE:** Server orchestrates, workers execute

---

## 2. What Must Be Deleted from Server

### Files/Functions to Remove or Refactor:
- `youtube_transcribe.py` - Delete all transcription logic
- Any imports of `youtube-transcript-api`
- Any SerpAPI transcription calls
- Functions like `transcribe_youtube_video()` that perform transcription
- Fallback logic that retries transcript APIs

### Anti-Patterns to Eliminate:
```python
# ❌ DELETE - Server must never do this
from youtube_transcript_api import YouTubeTranscriptApi
transcript = YouTubeTranscriptApi.get_transcript(video_id)

# ❌ DELETE - Server must never do this
serp_response = requests.get(serp_api_transcription_endpoint)
```

---

## 3. Architecture: Separation of Responsibilities

### Server Responsibilities (Orchestration Only)
1. Fetch AI news from RSS feeds
2. Fetch YouTube video metadata (titles, URLs, publish dates)
3. Rank all content by importance using Gemini AI
4. Select top N YouTube videos that need transcription
5. **Create transcription jobs** in database
6. Expose API endpoints for workers to pull jobs
7. Accept and store completed transcripts from workers
8. Summarize stored transcripts using Gemini AI
9. Generate and send email newsletters

### Worker Responsibilities (Execution Only)
1. Pull pending jobs from server API
2. Download YouTube audio using `yt-dlp`
3. Transcribe audio using `faster-whisper` with CUDA
4. Upload raw transcripts back to server
5. Clean up temporary files
6. Exit when complete

### Critical Rule:
**The server creates jobs. The worker pulls jobs. No pushing, no websockets, no continuous connections.**

---

## 4. Database Schema Changes

### Required Table: `transcription_jobs`

```sql
CREATE TABLE transcription_jobs (
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
    retry_count INTEGER DEFAULT 0,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

**Status Values:**
- `PENDING` - Job created, waiting for worker
- `CLAIMED` - Worker has pulled the job
- `COMPLETED` - Transcript uploaded successfully
- `FAILED` - Job failed after retries

### Required Table: `transcripts`

```sql
CREATE TABLE transcripts (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(255) UNIQUE NOT NULL,
    job_id VARCHAR(255),
    transcript TEXT NOT NULL,
    language VARCHAR(10),
    duration INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES transcription_jobs(job_id)
);
```

**Storage Rules:**
- Store raw, unmodified transcripts
- Never store summaries here
- Allow reprocessing from raw transcript
- Summarization happens separately on server

---

## 5. Server Code Changes (Step-by-Step)

### Step 1: Create Job Creation Function

```python
# NEW FILE: create_transcription_job.py

import uuid
from database import get_db_connection

def create_transcription_job(video_id, video_url, video_title, priority=0):
    """
    Creates a transcription job in the database.
    Server calls this instead of transcribing directly.
    """
    job_id = str(uuid.uuid4())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO transcription_jobs 
        (job_id, video_id, video_url, video_title, status, priority)
        VALUES (%s, %s, %s, %s, 'PENDING', %s)
        ON CONFLICT (job_id) DO NOTHING
    """, (job_id, video_id, video_url, video_title, priority))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return job_id
```

### Step 2: Replace Transcription Calls

```python
# OLD CODE (DELETE THIS):
transcript = transcribe_youtube_video(video_id)

# NEW CODE (USE THIS):
job_id = create_transcription_job(
    video_id=video_id,
    video_url=video_url,
    video_title=video_title,
    priority=1  # Higher priority for top news
)
```

### Step 3: Add Scheduled Preprocessing Task

This task runs **before workers start** (e.g., 8:00 AM if workers start at 8:30 AM)

```python
# MODIFY: run_pipeline.py or scheduler.py

def preprocess_and_create_jobs():
    """
    Runs before workers. Creates all transcription jobs.
    Workers will pull these jobs when they start.
    """
    print("Step 1: Fetching RSS news...")
    rss_news = fetch_rss_news()
    
    print("Step 2: Fetching YouTube videos...")
    youtube_videos = fetch_youtube_videos()
    
    print("Step 3: Ranking all content...")
    ranked_content = rank_all_news(rss_news + youtube_videos)
    
    print("Step 4: Selecting top YouTube videos...")
    top_videos = [item for item in ranked_content 
                  if item['source_type'] == 'youtube'][:10]
    
    print("Step 5: Creating transcription jobs...")
    for idx, video in enumerate(top_videos):
        create_transcription_job(
            video_id=video['video_id'],
            video_url=video['url'],
            video_title=video['title'],
            priority=idx  # Lower index = higher priority
        )
    
    print(f"Created {len(top_videos)} transcription jobs")
```

---

## 6. Server API Endpoints (Required)

### Endpoint 1: Worker Pulls Jobs

**Path:** `GET /api/get-videos`

**Purpose:** Worker calls this to get pending transcription jobs

**Server Logic:**
```python
# NEW FILE or ADD TO: app.py

from flask import Flask, jsonify, request
import datetime

@app.route('/api/get-videos', methods=['GET'])
def get_videos():
    """
    Returns pending transcription jobs and marks them as CLAIMED.
    Workers call this to get work.
    """
    worker_id = request.args.get('worker_id', 'unknown')
    limit = request.args.get('limit', 5, type=int)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Select pending jobs
    cursor.execute("""
        SELECT job_id, video_id, video_url, video_title, priority
        FROM transcription_jobs
        WHERE status = 'PENDING'
        ORDER BY priority ASC, created_at ASC
        LIMIT %s
        FOR UPDATE SKIP LOCKED
    """, (limit,))
    
    jobs = cursor.fetchall()
    
    # Mark as claimed
    if jobs:
        job_ids = [job[0] for job in jobs]
        cursor.execute("""
            UPDATE transcription_jobs
            SET status = 'CLAIMED', 
                claimed_at = %s,
                claimed_by = %s
            WHERE job_id = ANY(%s)
        """, (datetime.datetime.utcnow(), worker_id, job_ids))
        
        conn.commit()
    
    cursor.close()
    conn.close()
    
    # Format response
    jobs_list = [
        {
            "job_id": job[0],
            "video_id": job[1],
            "video_url": job[2],
            "video_title": job[3],
            "priority": job[4]
        }
        for job in jobs
    ]
    
    return jsonify({"jobs": jobs_list})
```

**Response Format:**
```json
{
  "jobs": [
    {
      "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "video_id": "dQw4w9WgXcQ",
      "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "video_title": "Example Video",
      "priority": 0
    }
  ]
}
```

### Endpoint 2: Worker Uploads Transcripts

**Path:** `POST /api/upload-all-transcripts`

**Purpose:** Worker calls this to submit completed transcripts

**Server Logic:**
```python
@app.route('/api/upload-all-transcripts', methods=['POST'])
def upload_all_transcripts():
    """
    Accepts batch transcript uploads from worker.
    Stores transcripts and marks jobs as COMPLETED.
    """
    data = request.json
    worker_id = data.get('worker_id', 'unknown')
    results = data.get('results', [])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    success_count = 0
    
    for result in results:
        job_id = result['job_id']
        video_id = result['video_id']
        transcript = result['transcript']
        language = result.get('language', 'en')
        duration = result.get('duration', 0)
        
        try:
            # Store transcript
            cursor.execute("""
                INSERT INTO transcripts 
                (video_id, job_id, transcript, language, duration)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (video_id) 
                DO UPDATE SET transcript = EXCLUDED.transcript
            """, (video_id, job_id, transcript, language, duration))
            
            # Mark job as completed
            cursor.execute("""
                UPDATE transcription_jobs
                SET status = 'COMPLETED',
                    completed_at = %s
                WHERE job_id = %s
            """, (datetime.datetime.utcnow(), job_id))
            
            success_count += 1
            
        except Exception as e:
            print(f"Error processing job {job_id}: {e}")
            cursor.execute("""
                UPDATE transcription_jobs
                SET status = 'FAILED',
                    error_message = %s
                WHERE job_id = %s
            """, (str(e), job_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({
        "success": True,
        "processed": success_count,
        "total": len(results)
    })
```

**Request Format:**
```json
{
  "worker_id": "local-gpu-worker",
  "results": [
    {
      "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "video_id": "dQw4w9WgXcQ",
      "language": "en",
      "duration": 900,
      "transcript": "This is the full raw transcript text..."
    }
  ]
}
```

---

## 7. Worker Implementation (Local GPU)

**Worker does NOT run continuously. It runs once and exits.**

### Worker Flow:
```
1. Start worker (via OS scheduler at 8:30 AM)
2. Call GET /api/get-videos
3. For each job:
   - Download audio (yt-dlp)
   - Transcribe (faster-whisper with CUDA)
   - Add to results batch
4. POST all results to /api/upload-all-transcripts
5. Clean up temp files
6. Exit
```

### Worker Pseudo-Code:
```python
# WORKER FILE: worker.py (runs on local GPU machine)

import requests
import yt_dlp
from faster_whisper import WhisperModel

SERVER_URL = "http://your-server.com"

def main():
    # Pull jobs
    response = requests.get(f"{SERVER_URL}/api/get-videos?worker_id=local-gpu&limit=10")
    jobs = response.json()['jobs']
    
    if not jobs:
        print("No jobs available")
        return
    
    # Load Whisper model (CUDA)
    model = WhisperModel("large-v3", device="cuda", compute_type="float16")
    
    results = []
    
    for job in jobs:
        try:
            # Download audio
            audio_path = download_audio(job['video_url'])
            
            # Transcribe
            segments, info = model.transcribe(audio_path)
            transcript = " ".join([seg.text for seg in segments])
            
            results.append({
                "job_id": job['job_id'],
                "video_id": job['video_id'],
                "language": info.language,
                "duration": int(info.duration),
                "transcript": transcript
            })
            
            # Clean up
            os.remove(audio_path)
            
        except Exception as e:
            print(f"Error processing {job['video_id']}: {e}")
    
    # Upload all results
    if results:
        requests.post(
            f"{SERVER_URL}/api/upload-all-transcripts",
            json={"worker_id": "local-gpu", "results": results}
        )
    
    print(f"Completed {len(results)} transcriptions")

if __name__ == "__main__":
    main()
```

---

## 8. Summarization (Server Only)

**Summarization happens AFTER transcripts are stored.**

```python
# NEW OR MODIFY: summarize_transcripts.py

def summarize_all_transcripts():
    """
    Runs after workers complete. Summarizes stored transcripts.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get transcripts without summaries
    cursor.execute("""
        SELECT video_id, transcript 
        FROM transcripts 
        WHERE summary IS NULL OR summary = ''
    """)
    
    transcripts = cursor.fetchall()
    
    for video_id, transcript in transcripts:
        summary = summarize_with_gemini(transcript)
        
        cursor.execute("""
            UPDATE transcripts 
            SET summary = %s 
            WHERE video_id = %s
        """, (summary, video_id))
    
    conn.commit()
    cursor.close()
    conn.close()
```

---

## 9. Updated Daily Schedule

```
8:00 AM - Server preprocessing
  - Fetch RSS news
  - Fetch YouTube metadata
  - Rank content
  - Create transcription jobs

8:30 AM - Worker starts (OS scheduler: cron/Task Scheduler)
  - Pull jobs
  - Transcribe videos
  - Upload transcripts
  - Exit

9:00 AM - Server post-processing
  - Summarize transcripts
  - Generate newsletter
  - Send emails
```

---

## 10. Forbidden Patterns (Never Violate)

### ❌ Server Must Never:
- Import `youtube-transcript-api`
- Call `YouTubeTranscriptApi.get_transcript()`
- Use SerpAPI for transcription
- Download or process audio files
- Run transcription models
- Push jobs to workers
- Keep websocket connections to workers

### ❌ Worker Must Never:
- Store data in its own database
- Use LLMs for summarization
- Serve HTTP endpoints (it's a client, not a server)
- Run continuously
- Process jobs it didn't pull from the server

---

## 11. Error Handling Rules

### Job Timeout
- If a job stays `CLAIMED` for > 30 minutes, reset to `PENDING`
- Implement cleanup task on server

```python
def reset_stale_jobs():
    """Run every 30 minutes to reset stuck jobs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE transcription_jobs
        SET status = 'PENDING', claimed_at = NULL, claimed_by = NULL
        WHERE status = 'CLAIMED' 
        AND claimed_at < NOW() - INTERVAL '30 minutes'
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
```

### Worker Failure
- If worker crashes, jobs remain `CLAIMED`
- Cleanup task will reset them
- Worker must be idempotent (safe to retry)

### Duplicate Prevention
- Use `ON CONFLICT` clauses in SQL
- Check job status before processing

---

## 12. Validation Checklist

Before considering migration complete, verify:

- [ ] No `youtube-transcript-api` imports on server
- [ ] No transcription code in server files
- [ ] `transcription_jobs` table exists
- [ ] `transcripts` table exists
- [ ] Server creates jobs instead of transcribing
- [ ] `/api/get-videos` endpoint implemented
- [ ] `/api/upload-all-transcripts` endpoint implemented
- [ ] Worker pulls jobs (not pushed to)
- [ ] Worker uploads transcripts
- [ ] Summarization uses stored transcripts only
- [ ] Daily schedule updated (preprocessing before workers)
- [ ] Cleanup task for stale jobs implemented

---

## 13. Final Mental Model

```
Server prepares jobs → Worker pulls → Worker transcribes → Worker uploads → Server summarizes
```

**No shortcuts. No mixed responsibilities. No server-side transcription.**

This is the only correct architecture.