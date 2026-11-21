# Deploying to Render (Full-Stack Deployment Guide)

This guide covers deploying the ContactHub application (Python Flask + SQLite backend, Vue 3 + Vite frontend) to [Render](https://render.com). It includes local verification results, two deployment methods (Dashboard Manual and Blueprint Infrastructure as Code), data persistence trade-offs, and troubleshooting procedures.

- Repository: <https://github.com/Fatespur/ContactHub>

---

## 0. Local Verification Summary

Before cloud deployment, full local integration and tests have been verified:

| Verification Item | Command | Result |
| --- | --- | --- |
| Backend Unit & Integration Tests | `pytest tests -q` | **Passed (60 passed)** |
| Backend Smoke Tests (26 scenarios: CORS, CRUD, pagination, search, favorites, validation, 404/405, Excel import/export) | Execute against running `run.py` | **PASS** |
| Production WSGI Entry (`wsgi:app`) | Simulated binding to `0.0.0.0:$PORT` | **PASS (200 / 201, CORS headers verified)** |
| Frontend Production Build | `npm run build` | **PASS** (artifacts in `frontend/dist/`) |
| Frontend Dev Server Proxy | `npm run dev` + `GET /api/v1/contacts` | **PASS (200 via Vite proxy)** |
| Frontend Production Build + Real Backend (Cross-Origin) | Static hosting of `dist/`, accessed via browser | **PASS (List, details, group stats loaded from SQLite)** |

---

## 1. Prerequisites and Repository Setup

To deploy on Render, both frontend and backend directories must be present on the target branch (typically `main` once PR #1 and PR #3 are merged).

Verify that the following essential files are present in the repository:

- [ ] `backend/requirements.txt`, `backend/wsgi.py`, `backend/app/`, `backend/app/schema.sql`
- [ ] `frontend/package.json`, `frontend/package-lock.json`, `frontend/vite.config.js`, `frontend/src/`
- [ ] `frontend/public/templates/contacts-import-template.xlsx` (tracked in git via `.gitignore` whitelist)
- [ ] `render.yaml` in repository root (required for Blueprint deployment)

> Note: Local dependency directories such as `backend/.venv/`, `frontend/node_modules/`, `frontend/dist/`, and `backend/instance/` are ignored in `.gitignore` and must not be committed.

---

## 2. Deployment Architecture

```
Browser Client
  │ https://contacthub-web.onrender.com        (Static Site, CDN)
  │     └─ axios baseURL = https://contacthub-api.onrender.com/api/v1
  ▼
https://contacthub-api.onrender.com             (Web Service, Python + gunicorn)
  │     └─ Flask app (/api/v1/...), Flask-CORS allows frontend origin via CORS_ORIGINS
  ▼
SQLite file: backend/instance/address_book.sqlite3 (ephemeral by default; persistent if Disk attached)
```

Because frontend and backend run on distinct domains, cross-origin communication is configured as follows:

1. **Backend**: `CORS_ORIGINS` environment variable specifies allowed frontend origins (comma-separated).
2. **Frontend**: `VITE_API_BASE_URL` injects the backend base URL at build time (defaults to same-origin `/api/v1` when unset).

---

## 3. Method A: Dashboard Manual Setup (Recommended)

### 3.1 Create Backend Web Service

In Render Dashboard -> **New +** -> **Web Service** -> Select the `ContactHub` repository.

| Field | Value |
| --- | --- |
| Name | `contacthub-api` |
| Language / Runtime | `Python 3` |
| Region | `Singapore` (or nearest region) |
| Branch | `main` |
| **Root Directory** | `backend` *(Critical: allows locating `requirements.txt`)* |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn -b 0.0.0.0:$PORT --workers 1 --threads 4 wsgi:app` |
| Instance Type | `Free` |
| Health Check Path (Advanced) | `/api/v1/contacts` |

Under **Environment Variables**, add:

| Key | Value |
| --- | --- |
| `PYTHON_VERSION` | `3.13.4` |
| `CORS_ORIGINS` | Start with `*` (temporary), then restrict to frontend domain in step 3.3 |

Click **Create Web Service**. Wait until logs display `Booting worker` and status transitions to **Live**.

Verification:
```bash
curl https://contacthub-api.onrender.com/api/v1/contacts
# Expected response: {"code":200,"data":{"items":[],"page":1,"page_size":10,"total":0},"message":"success"}
```

> Note: Free tier instances spin down after 15 minutes of inactivity. The initial cold start may take 30-60 seconds, which is normal behavior.

### 3.2 Create Frontend Static Site

In Render Dashboard -> **New +** -> **Static Site** -> Select the same repository.

| Field | Value |
| --- | --- |
| Name | `contacthub-web` |
| Branch | `main` |
| **Root Directory** | `frontend` *(Critical)* |
| Build Command | `npm install && npm run build` |
| **Publish Directory** | `dist` |

Under **Environment Variables**, add:

| Key | Value |
| --- | --- |
| `NODE_VERSION` | `22.12.0` (Vite 7 requires Node >= 20.19 or 22.12) |
| `VITE_USE_MOCK` | `false` (ensures production builds connect to live API) |
| `VITE_API_BASE_URL` | `https://contacthub-api.onrender.com/api/v1` (replace with actual backend URL from step 3.1, no trailing slash) |

Under **Redirects / Rewrites** (in Settings or Advanced during creation), add a single rule for SPA routing:

| Source | Destination | Action |
| --- | --- | --- |
| `/*` | `/index.html` | `Rewrite` |

> Note: `VITE_*` variables are evaluated at **build time**. After updating environment variables, trigger **Manual Deploy -> Clear build cache & deploy**.

### 3.3 Restrict Backend CORS Configuration

Update the backend `CORS_ORIGINS` variable from `*` to the exact frontend domain:

```
https://contacthub-web.onrender.com
```

Save changes; Render will redeploy the service automatically.

### 3.4 Verification

Navigate to `https://contacthub-web.onrender.com` and run through the verification checklist below.

---

## 4. Method B: Blueprint Infrastructure as Code (`render.yaml`)

A root `render.yaml` is provided to deploy both services simultaneously:

1. Render Dashboard -> **New +** -> **Blueprint** -> Select repository (`main` branch).
2. Render parses `contacthub-api` and `contacthub-web`.
3. Fill in `VITE_API_BASE_URL` when prompted (or leave blank and set after deployment).
4. Click **Apply** and wait for both services to enter the **Live** state.
5. In the frontend service settings, supply `VITE_API_BASE_URL` and redeploy using "Clear build cache & deploy".

To validate Blueprint syntax locally (requires [Render CLI](https://render.com/docs/cli)):

```bash
render blueprints validate render.yaml
```

---

## 5. Post-Deployment Verification Checklist

- [ ] `GET https://contacthub-api.onrender.com/api/v1/contacts` returns JSON (status 200).
- [ ] Home page loads: contact table is initially empty or displays previously imported data (not the 20 mock records).
- [ ] Create Contact: new contact appears in list and persists upon page refresh within the same container lifecycle.
- [ ] Edit, Delete, and Favorite toggle (`PATCH`) function as expected.
- [ ] Search, group filtering, and pagination operate normally.
- [ ] Excel Export: downloads `.xlsx` readable by Microsoft Excel / LibreOffice / WPS.
- [ ] Excel Import: download template, populate sample rows, upload file, and confirm success summary.
- [ ] Browser DevTools -> Network: API requests target the backend domain with `access-control-allow-origin` headers.
- [ ] Direct navigation or refresh on `https://contacthub-web.onrender.com/settings` returns HTTP 200 (SPA rewrite functioning).

---

## 6. Data Persistence: Free Tier vs. Persistent Disk

| Feature | Free Instance (Default) | Paid Instance + Persistent Disk |
| --- | --- | --- |
| Storage Location | Container ephemeral filesystem (`backend/instance/address_book.sqlite3`) | Persistent mount (`/var/data/address_book.sqlite3`) |
| Data Survival | Reset on redeployment or restart | Preserved across restarts and redeployments |
| Cold Start | Spins down after 15 min idle; 30-60s cold start | Starter plan does not spin down |
| Cost | Free (750 instance hours / month) | Starter tier (~$7/mo) + Disk ($0.25/GB/mo) |

**For course evaluation and demo**: The free tier is sufficient. Sample data can be re-imported via Excel before demonstration.

### 6.1 Public Demo Safety & Non-Authenticated Boundary Notice

> [!CAUTION]
> **Essential Safety Notice for Public Deployments:**
> 1. **Prefer Client-Side Mock Mode for Public Showcase**: For public demos or resume portfolios, it is strongly recommended to set VITE_USE_MOCK=true on the frontend. This runs all CRUD interactions entirely in frontend memory, eliminating backend abuse risks and data privacy exposure.
> 2. **CORS is Not Authorization or Access Control**: Cross-Origin Resource Sharing (CORS) is strictly a browser-enforced security policy. It provides **zero protection against non-browser tools** (such as curl, Postman, automated scrapers). Setting CORS_ORIGINS must never be cited as evidence of authentication or access security.
> 3. **Unauthenticated CRUD Boundary**: The backend provides open, unauthenticated REST APIs designed for academic demonstrations and internal integration. **Never deploy a live public backend containing real personal data** (names, real phone numbers, or private addresses). If deploying a live backend for demonstration, use strictly synthetic/sample data and inform visitors of its public, unauthenticated state.

**For persistent production storage**:
1. Upgrade backend **Settings -> Instance Type** to `Starter`.
2. In **Disks -> Add Disk**: Name `contacthub-data`, Mount Path `/var/data`, Size `1 GB`.
3. In **Environment Variables**: Add `DATABASE=/var/data/address_book.sqlite3`.
4. Trigger redeployment via **Manual Deploy**.

---

## 7. Troubleshooting & FAQ

| Symptom | Probable Cause | Remediation |
| --- | --- | --- |
| Logs show `Failed to bind to $PORT` | Start command does not bind to `0.0.0.0:$PORT` | Ensure start command is `gunicorn -b 0.0.0.0:$PORT --workers 1 --threads 4 wsgi:app` |
| `ModuleNotFoundError: No module named 'app'` | Root Directory not set to `backend` | Set Root Directory to `backend` in Web Service settings |
| Initial request slow / 502 timeout | Free tier spinning up from sleep | Retry request after 30 seconds; upgrade to Starter for zero sleep |
| Browser console `blocked by CORS policy` | `CORS_ORIGINS` does not match frontend origin | Set `CORS_ORIGINS` to exact frontend domain (no trailing slash) |
| Page displays 20 mock records | `VITE_USE_MOCK` is not `false` or cache not cleared | Set `VITE_USE_MOCK=false`, trigger "Clear build cache & deploy" |
| API requests return 404 | `VITE_API_BASE_URL` unset, falling back to static host | Set `VITE_API_BASE_URL=https://<api-domain>/api/v1` and rebuild |
| Refreshing `/settings` returns 404 | Missing SPA rewrite rule | Add Rewrite rule `/* -> /index.html` |
| Template download returns 404 | Template missing from build output | Verify `frontend/public/templates/contacts-import-template.xlsx` is tracked |
| Import returns `400 INVALID_FILE` | Header mismatch or non-`.xlsx` format | Use official repository template with exact 8 columns |
| Data missing after restart | Ephemeral storage on Free tier | Normal on free tier; see Section 6 for persistent disk setup |

---

## 8. Deployment-Specific Configuration Summary

| File | Change | Purpose |
| --- | --- | --- |
| `backend/wsgi.py` | Exposes `app = create_app()` | Production WSGI entry point for gunicorn |
| `backend/app/__init__.py` | Supports `DATABASE` and `CORS_ORIGINS` environment variables | Configurable runtime paths and CORS permissions |
| `backend/requirements.txt` | Includes `gunicorn` | Production HTTP WSGI server on Linux containers |
| `frontend/src/api/request.js` | Uses `VITE_API_BASE_URL || '/api/v1'` | Dynamic routing between local proxy and remote API |
| `frontend/src/api/contacts.js` | Defaults to real backend in production builds | Prevents mock data in production |
| `frontend/.env.example` | Documents `VITE_API_BASE_URL` and `VITE_USE_MOCK` | Configuration template for local and remote setups |
| `.gitignore` | Whitelists `frontend/public/templates/*.xlsx` | Ensures import templates are committed |
| `render.yaml` | Blueprint specification | One-click dual-service deployment |
| `docs/DEPLOY_RENDER.md` | Deployment guide | Complete instructions and troubleshooting |

