# Backend - EE308FZ-AddressBook

RESTful API backend service built with Python Flask, native `sqlite3`, Flask-CORS, and openpyxl, providing contact CRUD, search and filtering, pagination, favorite pinning, and Excel `.xlsx` import and export.

---

## 1. Quick Start

Run from the `backend/` directory (Python 3.10+ required):

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python run.py

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python run.py
```

The service runs at `http://127.0.0.1:5000` with the API prefix `/api/v1`. Database tables are created automatically on first run and stored at `backend/instance/address_book.sqlite3`. Data persists across server restarts. CORS allows requests from `http://localhost:5173`.

Vite dev proxy forwards `/api` requests to `http://127.0.0.1:5000` while preserving the request path; the frontend uses `/api/v1/...` relative endpoints. See [API Contract](../docs/API.md) for full configuration details.

---

## 2. Production Deployment

When deploying to Linux or cloud platforms (e.g. Render Web Service):

- Set the service root directory to `backend`.
- Build command: `pip install -r requirements.txt`.
- Start command: `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 1 --threads 4`.

**Environment Variables**:
- `DATABASE`: Path to the SQLite database file (e.g., `/var/data/address_book.sqlite3` on a persistent disk mount). Parent directories are created automatically.
- `CORS_ORIGINS`: Comma-separated list of allowed frontend origins (e.g., `https://addressbook-web.onrender.com`). Defaults to local development origins if omitted.

To ensure data persistence across container redeployments, attach a persistent storage disk. See [Render Deployment Guide](../docs/DEPLOY_RENDER.md).

---

## 3. Running Automated Tests

Tests execute against isolated, temporary SQLite databases without affecting development data:

```powershell
# Windows PowerShell
New-Item -ItemType Directory -Path instance -Force | Out-Null
$testTemp = 'instance/pytest-' + [guid]::NewGuid().ToString('N')
.\.venv\Scripts\python -m pytest tests -q --basetemp=$testTemp

# Linux / macOS
pytest tests -q
```

Specifying a project-internal temporary directory avoids permission restrictions on Windows system temporary directories.

---

## 4. API Contract & Validation Rules

- **PUT Full Update Contract**: The `PUT /api/v1/contacts/{id}` endpoint requires all 8 editable fields (`name`, `group`, `is_favorite`, `notes`, `phones`, `emails`, `social_accounts`, `addresses`). Omitting any editable field returns `400 VALIDATION_ERROR` and performs no database write. To clear optional fields, explicitly pass `null` (for `group` and `notes`) or `[]` (for list fields).
- **Phone Number Format**: Phone numbers are validated against `^[0-9+()\-]+$`. Whitespace characters are disallowed.

---

## 5. Excel Import and Export Specifications

- **Export (`GET /api/v1/contacts/export`)**: Filters contacts by `keyword`, `group`, and `is_favorite`, ignoring pagination. Returns a `.xlsx` binary spreadsheet.
- **Import (`POST /api/v1/contacts/import`)**: Accepts a `.xlsx` file upload up to 10 MB via the `file` multipart field. The first worksheet must contain the fixed 8-column header defined in the contract. Empty rows are skipped; validation errors are aggregated in the response; repeated imports insert new records.
- **Transaction Safety**: Each contact row and its sub-entries are committed in a dedicated transaction. Internal database errors return HTTP 500, rollback the current row, and abort further processing; previously committed rows remain preserved. Invalid file formats or size overruns return `400 INVALID_FILE`.
- **Formula Handling**: Formula-like text in exports is sanitized to plain strings. During import, actual formula cells are rejected per-row to protect against formula injection.

---

## 6. Known Limitations (Excel Round-Trip)

Consistent with the frozen API contract, no artificial escape markers or hidden columns are introduced:

- Standard contact attributes, multiple entries, favorite flags, and single primary flags are preserved. New record IDs and timestamps are generated upon import.
- When all primary flags in a category are false, import assigns `is_primary=true` to the first entry. If multiple entries are marked primary, only the first is retained.
- In cells without line breaks, semicolons act as delimiters (e.g. an address `Campus;Building A` splits into two addresses). Inside multi-line cells, semicolons within an item line are preserved.
- Line breaks inside a cell delimit items. Colons distinguish labels/platforms from values, and trailing `*` marks primary items. Colons within values (e.g. HTTPS URLs) are preserved.
- Empty strings and nulls cannot be distinguished in empty Excel cells. Text exceeding Excel's 32,767 character cell limit or containing XML control characters causes export to return HTTP 400 to prevent silent truncation.

Consequently, the current format cannot guarantee lossless round-trips for arbitrary valid API payloads. Eliminating these ambiguities would require a coordinated update to the API contract.
