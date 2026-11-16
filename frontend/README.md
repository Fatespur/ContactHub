# AddressBook Frontend (Vue 3 + Element Plus)

Single-page web application for the AddressBook project, built with Vue 3, Vite, and Element Plus.

---

## 1. Getting Started

### Prerequisites

- Node.js `20.19+` or `22.12+` (required by Vite 7).
- npm `10+`.

### Local Run

```bash
cd frontend
npm install
npm run dev      # Local dev server at http://localhost:5173
npm run build    # Production build output to dist/
npm run preview  # Preview production build locally
```

---

## 2. Data Sources & Backend Integration

### Mock Mode vs. Real API

- **Development (`npm run dev`)**: Defaults to built-in **Mock data** (`src/mock/contacts.js`, 20 demo contact records) for standalone frontend development and UI demonstration. The mock implementation adheres strictly to the [API Contract](../docs/API.md), including pagination, search, group filtering, favorite toggling, and full PUT updates.
- **Production (`npm run build`)**: Automatically defaults to the **Real Backend** (`VITE_USE_MOCK=false`) when `VITE_USE_MOCK` is unset, preventing mock data from leaking into production deployments.

### Switching to the Real Backend

To connect the local frontend dev server to the live Flask backend:

1. Create a `frontend/.env.local` file:
   ```bash
   VITE_USE_MOCK=false
   ```
2. Start the Flask backend server on `http://127.0.0.1:5000` (see [Backend README](../backend/README.md)).
3. Start the frontend dev server:
   ```bash
   npm run dev
   ```
4. All API requests to `/api/v1/*` are proxied by `vite.config.js` to `http://127.0.0.1:5000`.

### Production Deployment Configuration

When deploying frontend and backend to separate domains (e.g., Render Static Site + Web Service):

1. Set the build-time environment variable:
   ```bash
   # frontend/.env.production.local
   VITE_API_BASE_URL=https://addressbook-api.onrender.com/api/v1
   ```
2. Ensure the backend configures `CORS_ORIGINS` to allow the frontend origin.
3. For full deployment instructions, see [Render Deployment Guide](../docs/DEPLOY_RENDER.md).

---

## 3. Implemented Features

- **Three-Column Responsive Layout**:
  - Desktop (>= 1280px): Persistent sidebar navigation, contact list table, and contact detail panel.
  - Medium / Laptop (1024px – 1279px): Detail view transitions into a smooth right-side slide-over drawer.
  - Tablet (768px – 1023px): Collapsible icon-rail sidebar and condensed 5-column table.
- **Contact List & Filtering**:
  - Real-time search with 300ms debounce across name, notes, phone, and email.
  - Group filtering with dynamic badge counts.
  - "Favorites only" quick filter.
  - Pagination (10, 20, 50 items per page).
  - Client-side column sorting by contact name on current page.
- **Contact Details**:
  - Avatar generator, favorite star toggle with optimistic UI updates and rollback on failure.
  - Full details for multiple phones, emails, social accounts, and physical addresses.
- **Create & Edit (Modal Form)**:
  - Dynamic rows for 4 contact sub-types (phones, emails, socials, addresses).
  - Strict mutual exclusion for primary (`is_primary`) flags within each sub-category.
  - Client-side validation matching backend constraints (phone regex without spaces, email format, address length <= 200).
  - Form dirty checking with exit confirmation to prevent accidental loss of edits.
  - Backend validation error mapping to individual fields and list item rows.
  - Full 8-field payload submission for strict PUT update contract.
- **Deletion**:
  - Single deletion with confirmation dialog.
  - Batch deletion (sequential deletion with progress).
- **Excel Import**:
  - Drag-and-drop or file picker, 10MB limit and `.xlsx` extension validation.
  - Upload progress indication and request abort (`AbortController`).
  - Import summary dialog displaying total rows, success count, failure count, and downloadable CSV error report.
  - Built-in template download (`contacts-import-template.xlsx`).
- **Excel Export**:
  - Export filtered contacts matching current search criteria.
  - Automatic filename extraction from `Content-Disposition` header.
- **Keyboard Shortcuts & Accessibility**:
  - `Ctrl + K` / `Cmd + K`: Focus search bar.
  - `Esc`: Close dialogs and drawers.
  - `Enter` on row: Open contact detail.
  - ARIA attributes and focus trap on modals.
- **Settings View**:
  - Data source status display, template download, keyboard shortcut cheat sheet, and project information.

---

## 4. Excel Import & Export Specifications

- **Import Template**: Located at `public/templates/contacts-import-template.xlsx` (8 columns + "Instructions" sheet), served at `/templates/contacts-import-template.xlsx`.
- **Mock Mode**:
  - Import simulates a 10-row import (8 successful, 2 failed) and appends 8 mock contacts to memory.
  - Export generates a mock CSV demo file with `_mock` in the filename.
- **Real Mode**:
  - Import submits `multipart/form-data` with field `file` to `POST /contacts/import` (60s timeout).
  - Export requests `GET /contacts/export` as a binary blob.
- **Post-Import Workflow**: Refreshes list and group counts, and automatically selects the newly imported record.

---

## 5. Known Limitations

- **Excel Round-Trip Ambiguity**: Consistent with the backend contract, multi-line cells and semicolon delimiters may split or merge values upon repeated export-import cycles. Primary flags default to the first entry if none are marked.
- **Group Statistics at Scale**: Group badge counts are computed client-side from a single query (`page_size=100`). If total contacts exceed 100, counts reflect the sampled dataset until a dedicated group aggregation endpoint is provided.
- **Client-Side Page Sorting**: Contact name sorting via Element Plus table header applies only to the current page, as the backend API does not currently expose sort query parameters.
- **Mobile Viewport (< 768px)**: Viewports narrower than 768px maintain a minimum 768px width with horizontal scrolling; dedicated mobile layout (< 768px) is not yet implemented.
