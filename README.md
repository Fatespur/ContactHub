# EE308FZ-AddressBook

Fuzhou University EE308FZ Software Engineering Pair Project — A modern, decoupled Address Book Web Application.

---

## 1. Project Overview

EE308FZ-AddressBook is a full-stack, decoupled contact management system designed for ease of use, data integrity, and responsive operation. The application provides contact lifecycle management (CRUD), multi-attribute contact details, group categorization, real-time search, favorite pinning, and bulk Excel (`.xlsx`) import and export.

---

## 2. Features

- **Contact Management (CRUD)**:
  - Create, view, update, and delete contacts.
  - Support for multiple phone numbers, email addresses, social accounts, and physical addresses per contact.
  - Primary contact flag designation (`is_primary`) per contact attribute type.
  - Full-replacement update semantics (`PUT`) ensuring data consistency.
- **Organization & Search**:
  - Real-time debounced keyword search across name, notes, phone numbers, and emails.
  - Group filtering with dynamic contact count badges.
  - Favorite pinning and filtering with dedicated toggle endpoint (`PATCH`).
  - Server-side and client-side pagination controls (10, 20, 50 items per page).
- **Excel Transfer (`.xlsx`)**:
  - Bulk export matching active filters into formatted Excel spreadsheets.
  - Bulk import with format validation, error reporting, and row-level transactional rollback.
  - Built-in standardized import template.
- **Modern User Experience**:
  - Responsive layout: Desktop (three columns), Tablet (drawer details), and Mobile-ready viewports.
  - Keyboard shortcuts (`Ctrl/Cmd + K` search, `Esc` modal dismiss).
  - Standalone Mock mode for client-only demonstrations, with zero-overhead toggle to live Flask backend.

---

## 3. Technology Stack

| Layer | Technologies |
| --- | --- |
| **Frontend** | Vue 3 (Composition API, `<script setup>`), Vite 7, Element Plus, Axios |
| **Backend** | Python 3.10+ (Flask 3.1), Native SQLite3, openpyxl, Flask-CORS, gunicorn |
| **Testing** | pytest, pytest-cov |
| **Deployment** | Render (Web Service + Static Site Blueprint) |

---

## 4. Project Structure

```text
EE308FZ-AddressBook/
├── backend/                  # Flask backend service
│   ├── app/                  # Application factory, database access, Excel handlers
│   │   ├── __init__.py       # App factory, routes, and validation
│   │   ├── db.py             # SQLite connection and query helpers
│   │   ├── excel.py          # openpyxl import and export handlers
│   │   └── schema.sql        # Database schema definitions
│   ├── instance/             # Local runtime SQLite database
│   ├── tests/                # Automated pytest test suites
│   ├── requirements.txt      # Production Python dependencies
│   ├── requirements-dev.txt  # Development & testing dependencies
│   ├── run.py                # Local development server entry
│   ├── wsgi.py               # Production WSGI entry point
│   └── README.md             # Backend setup and technical notes
├── frontend/                 # Vue 3 frontend application
│   ├── public/               # Static assets & import templates
│   ├── src/                  # Application source code
│   │   ├── api/              # API clients (request, contacts, mock)
│   │   ├── components/       # Reusable UI & contact components
│   │   ├── composables/      # Breakpoint & reactive utilities
│   │   ├── constants/        # System presets & options
│   │   ├── mock/             # Built-in demo datasets
│   │   ├── router/           # Vue Router definitions
│   │   ├── stores/           # Pinia/reactive state stores
│   │   ├── styles/           # CSS design tokens & overrides
│   │   ├── utils/            # Contact, download, & Excel helpers
│   │   └── views/            # ContactListView and SettingsView
│   ├── package.json          # Node.js dependencies and scripts
│   ├── vite.config.js        # Vite configuration and dev proxy
│   └── README.md             # Frontend setup and UI architecture
├── docs/                     # Project technical documentation
│   ├── API.md                # RESTful API specification contract
│   ├── CODING_STANDARDS.md   # Team collaboration and code standards
│   └── DEPLOY_RENDER.md      # Cloud deployment guide for Render
├── render.yaml               # Render Infrastructure as Code Blueprint
├── .gitignore                # Git ignore configuration
└── README.md                 # Main project documentation
```

---

## 5. Local Setup

### 5.1 Prerequisites

- Python `3.10+` (tested on 3.13)
- Node.js `20.19+` or `22.12+` (required by Vite 7)
- npm `10+`

---

### 5.2 Backend Setup

1. Open a terminal and navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```powershell
   # Windows PowerShell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
4. Start the backend development server:
   ```bash
   python run.py
   ```
   The backend service starts at `http://127.0.0.1:5000` with API prefix `/api/v1`. Database tables are initialized automatically on first startup.

---

### 5.3 Frontend Setup

1. Open a new terminal and navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start the frontend development server:
   ```bash
   npm run dev
   ```
   The frontend application is accessible at `http://localhost:5173`.

---

### 5.4 Connecting Frontend to Real Backend

By default, the frontend runs in **Mock mode** during local development (`npm run dev`) for standalone UI previewing.

To switch to the live Flask backend:

1. Create a `frontend/.env.local` file:
   ```ini
   VITE_USE_MOCK=false
   ```
2. Restart the frontend dev server (`npm run dev`).
3. Requests to `/api/v1/*` are automatically forwarded to `http://127.0.0.1:5000` via Vite's proxy.

---

## 6. Testing

### Backend Automated Tests

Run the full pytest suite from the `backend/` directory:

```powershell
# Windows PowerShell
New-Item -ItemType Directory -Path instance -Force | Out-Null
$testTemp = 'instance/pytest-' + [guid]::NewGuid().ToString('N')
.\.venv\Scripts\python -m pytest tests -q --basetemp=$testTemp

# Linux / macOS
pytest tests -q
```

All 60 automated tests (API CRUD, validation, error handling, Excel processing, deployment WSGI) execute against isolated in-memory or temporary SQLite databases.

### Frontend Production Build

Verify production bundle compilation from the `frontend/` directory:

```bash
npm run build
```

---

## 7. API Documentation

The complete RESTful API contract is specified in [docs/API.md](docs/API.md), covering:

- `GET /api/v1/contacts`: Paginated list query with search and filters.
- `GET /api/v1/contacts/{id}`: Detailed contact information.
- `POST /api/v1/contacts`: Contact creation.
- `PUT /api/v1/contacts/{id}`: Full contact replacement (requires all 8 editable fields).
- `DELETE /api/v1/contacts/{id}`: Contact deletion.
- `PATCH /api/v1/contacts/{id}/favorite`: Dedicated favorite status toggle.
- `GET /api/v1/contacts/export`: Filtered Excel binary download (`.xlsx`).
- `POST /api/v1/contacts/import`: Multipart Excel upload (`.xlsx`, max 10MB).

---

## 8. Known Limitations

- **Excel Round-Trip Delimiters**: Semicolon characters within unquoted single-line cells may be interpreted as item separators upon import. Primary flags default to the first entry if none are marked.
- **Group Statistics at Scale**: Group badge counters are aggregated client-side from the initial contact dataset (`page_size=100`). A future dedicated `/contacts/groups` endpoint will provide scalable aggregation.
- **Mobile Viewport Optimization**: Responsive styles accommodate screen widths down to 768px. Screens narrower than 768px utilize horizontal scroll navigation.

---

## 9. Team Collaboration & Git Workflow

This project is developed under a pair-programming workflow:

- **Branch Structure**:
  - `main`: Stable release branch.
  - `backend`: Backend development branch (Pull Request #1).
  - `frontend`: Frontend development branch (Pull Request #3).
- **Current Integration Status**:
  - Backend core APIs, database models, and Excel handlers implemented and verified on `backend`.
  - Frontend Vue 3 user interface, Element Plus components, and Mock/Real API clients implemented on `frontend`.
  - Code fixes, English comment standardization, and documentation alignment completed for pre-merge review.
