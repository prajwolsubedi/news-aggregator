# AI News Newsletter System

This repository contains both the frontend and backend for the AI News newsletter subscription system.

## Structure

- `frontend/` - Static HTML, CSS, and JavaScript files (hosted on GitHub Pages)

  - `index.html` - Subscription page
  - `about.html` - About page with project information
  - `css/` - Stylesheets
  - `js/` - JavaScript files for API integration
  - `assets/` - Media files (screenshots, videos)

- `backend/` - Backend API (deployed on Render)
  - Flask application with API endpoints
  - News fetching, ranking, and email sending
  - See `backend/README.md` for details

## Deployment

### Frontend

The frontend can be hosted on:

- GitHub Pages (recommended)
- Netlify
- Vercel
- Any static hosting service

### Backend

The backend is deployed on Render. See `backend/RENDER_SETUP_GUIDE.md` for deployment instructions.

## Configuration

### Frontend

The frontend connects to the backend API. Configure the API URL in `frontend/js/config.js` or by setting `window.API_BASE_URL` before the config script loads.

### Backend

See `backend/README.md` for environment variables and configuration details.

## GitHub Actions

The `.github/workflows/` directory contains workflows that trigger the backend pipeline on Render. These workflows use secrets configured in GitHub:

- `CRON_SECRET` - Secret token for authentication
- `RENDER_BASE_URL` - Backend API URL on Render

## Development

- Frontend: Edit files in `frontend/` directory
- Backend: Edit files in `backend/` directory
- Both are decoupled and can be deployed independently
