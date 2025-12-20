# AI News Backend

This directory contains the backend API for the AI News newsletter system, designed to be deployed on Render.

## Structure

- `app.py` - Flask application with API endpoints
- `core/` - Core modules (database, models, utils)
- `news/` - News fetching modules (RSS, YouTube)
- `ranking/` - News ranking with AI
- `transcription/` - Video transcription job management
- `email_templates.py` - Email template generation
- `send_email.py` - Email sending via Resend API
- `run_pipeline.py` - Main pipeline orchestration
- `preprocess_jobs.py` - Preprocessing and job creation
- `requirements.txt` - Python dependencies
- `render.yaml` - Render deployment configuration
- `Procfile` - Process definition for Render

## API Endpoints

- `GET /` - API information
- `POST /api/subscribe` - Subscribe to newsletter
- `GET /unsubscribe/<token>` - Unsubscribe from newsletter
- `POST /internal/run-preprocess` - Trigger preprocessing (protected)
- `POST /internal/run-pipeline` - Trigger main pipeline (protected)
- `GET /api/get-videos` - Worker endpoint for transcription jobs
- `POST /api/upload-all-transcripts` - Worker endpoint for transcript uploads

## Deployment

Deploy to Render using the `render.yaml` configuration file. See `RENDER_SETUP_GUIDE.md` for detailed instructions.

## Environment Variables

Required environment variables:

- `MONGO_URI` or `DATABASE_URL` - Database connection string
- `RESEND_API_KEY` - Resend API key for email sending
- `SENDER_EMAIL` - Email address for sending newsletters
- `FRONTEND_URL` - Frontend URL (GitHub Pages) for unsubscribe links (e.g., `https://username.github.io/repo-name`)
- `BASE_URL` - Backend URL (fallback for unsubscribe links if FRONTEND_URL not set)
- `CRON_SECRET` - Secret token for internal endpoints
- `SECRET_KEY` - Flask secret key
- `GEMINI_API_KEY` - Google Gemini API key for AI ranking
- `YOUTUBE_API_KEY` - YouTube API key for video fetching

## Scheduled Jobs

The backend is triggered by GitHub Actions workflows (in the frontend repository):

- 08:30 NPT - Preprocessing job
- 09:00 NPT - Main pipeline (newsletter generation and sending)
