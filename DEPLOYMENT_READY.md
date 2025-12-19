# ✅ Deployment Readiness Checklist

## Pre-Deployment Verification

### ✅ Code Files

- [x] `app.py` - Flask app with internal endpoints (`/internal/run-preprocess`, `/internal/run-pipeline`)
- [x] `app.py` - Token verification uses `CRON_SECRET` and `X-Cron-Token` header
- [x] `render.yaml` - Configured for web service only (no worker)
- [x] `render.yaml` - Includes `CRON_SECRET` environment variable
- [x] `requirements.txt` - All dependencies listed (APScheduler removed - not needed)
- [x] `Procfile` - Only web service (worker removed - using GitHub Actions)

### ✅ GitHub Actions Workflows

- [x] `.github/workflows/trigger-preprocess.yml` - Runs at 02:45 UTC (08:30 NPT)
- [x] `.github/workflows/trigger-pipeline.yml` - Runs at 03:15 UTC (09:00 NPT)
- [x] Both workflows use `X-Cron-Token` header
- [x] Both workflows use `CRON_SECRET` and `RENDER_BASE_URL` secrets

### ✅ Security

- [x] Internal endpoints protected with token authentication
- [x] Token stored as `CRON_SECRET` in environment variables
- [x] `SECRET_KEY` validation for production
- [x] No hardcoded secrets in code

### ✅ Configuration

- [x] `render.yaml` - Valid YAML structure
- [x] `.gitignore` - Excludes sensitive files
- [x] No linter errors

## Required Environment Variables

### Render Dashboard

Set these in your web service:

```
GEMINI_API_KEY=your_gemini_api_key
YOUTUBE_API_KEY=your_youtube_api_key
SERP_API_KEY=your_serp_api_key
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_gmail_app_password
BASE_URL=https://ai-news-web.onrender.com
CRON_SECRET=your_random_secret_token_here
```

Auto-set by Render:

- `DATABASE_URL` - From PostgreSQL database
- `SECRET_KEY` - Auto-generated
- `FLASK_ENV` - Set to `production`
- `SMTP_SERVER` - Set to `smtp.gmail.com`
- `SMTP_PORT` - Set to `587`

### GitHub Secrets

Set these in: Repository → Settings → Secrets → Actions

```
CRON_SECRET=your_random_secret_token_here (SAME as Render)
RENDER_BASE_URL=https://ai-news-web.onrender.com
```

## Deployment Steps

1. **Generate Secret Token**

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Push Code to GitHub**

   ```bash
   git add .
   git commit -m "Production ready - GitHub Actions scheduler"
   git push origin main
   ```

3. **Deploy on Render**

   - Go to Render Dashboard
   - New → Blueprint
   - Connect GitHub repository
   - Render auto-detects `render.yaml`
   - Set all environment variables (including `CRON_SECRET`)

4. **Configure GitHub Secrets**

   - Repository → Settings → Secrets → Actions
   - Add `CRON_SECRET` (same token as Render)
   - Add `RENDER_BASE_URL` (your Render URL)

5. **Verify**
   - Web service is running
   - Test subscription form
   - Check GitHub Actions workflows exist
   - Test endpoints manually (see below)

## Manual Testing

Test the endpoints after deployment:

```bash
# Replace YOUR_TOKEN and YOUR_URL
curl -X POST \
  -H "X-Cron-Token: YOUR_TOKEN" \
  https://YOUR_URL.onrender.com/internal/run-preprocess

curl -X POST \
  -H "X-Cron-Token: YOUR_TOKEN" \
  https://YOUR_URL.onrender.com/internal/run-pipeline
```

## Architecture Summary

```
GitHub Actions (Scheduler)
├── trigger-preprocess.yml (02:45 UTC = 08:30 NPT)
│   └── POST /internal/run-preprocess
│       └── Calls preprocess_and_create_jobs()
│           └── Uses in-memory data (ephemeral filesystem compatible)
│
└── trigger-pipeline.yml (03:15 UTC = 09:00 NPT)
    └── POST /internal/run-pipeline
        └── Calls run_pipeline.main()
```

## ✅ Everything is Ready!

Your project is production-ready. All components are configured correctly:

- ✅ GitHub Actions workflows created
- ✅ Flask endpoints protected with token
- ✅ Render configuration valid
- ✅ Documentation updated
- ✅ No linter errors

**You can now deploy!** 🚀
