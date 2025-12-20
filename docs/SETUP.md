# Setup Guide for Custom Domain

## Custom Domain: `ainews.prajwolsubedi.com.np`

## GitHub Pages Configuration

### 1. Set Custom Domain in GitHub

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Pages**
3. Under **Custom domain**, enter: `ainews.prajwolsubedi.com.np`
4. Check **Enforce HTTPS** (recommended)
5. Click **Save**

### 2. DNS Configuration

Add a CNAME record in your DNS provider (where `prajwolsubedi.com.np` is hosted):

```
Type: CNAME
Name: ainews
Value: your-username.github.io
TTL: 3600 (or default)
```

**Note**: Replace `your-username` with your actual GitHub username.

### 3. Wait for DNS Propagation

- DNS changes can take 24-48 hours to propagate
- GitHub will automatically detect when DNS is configured correctly
- You'll see a green checkmark in GitHub Pages settings when DNS is verified

## GitHub Secrets Configuration

✅ **No additional secrets needed!**

The workflow automatically uses your existing `RENDER_BASE_URL` secret for the frontend build. Make sure you have:

- `RENDER_BASE_URL` - Your Render backend URL (e.g., `https://ai-news-web-j6uy.onrender.com`)

This tells the frontend where to send API requests.

## Render Backend Configuration

In your Render dashboard, set the `FRONTEND_URL` environment variable:

1. Go to your Render service → **Environment** tab
2. Add/Update:
   - **Key**: `FRONTEND_URL`
   - **Value**: `https://ainews.prajwolsubedi.com.np`

This ensures unsubscribe links in emails point to your custom domain.

## Verification Checklist

- [ ] Custom domain set in GitHub Pages settings
- [ ] CNAME DNS record added
- [ ] DNS verified (green checkmark in GitHub)
- [x] `RENDER_BASE_URL` secret (already set - used for frontend build)
- [ ] `FRONTEND_URL` set in Render backend
- [ ] GitHub Actions workflow runs successfully
- [ ] Site accessible at `https://ainews.prajwolsubedi.com.np`

## Testing

1. Visit `https://ainews.prajwolsubedi.com.np`
2. Test subscription form
3. Check email for unsubscribe link
4. Verify unsubscribe link uses your custom domain
