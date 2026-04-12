# Self Property Manager

A full-stack web application for managing rental properties — track expenses, rental income, documents, contacts, reminders, and generate year-end reports. Built for landlords who manage multiple properties and want everything in one place.

---

## Features

- **Multi-Property Dashboard** — At-a-glance view of all properties with YTD rent collected, expenses, net income, lease status, and upcoming reminders
- **Expense Tracking** — Log expenses by category (HOA, mortgage, insurance, tax, maintenance, utilities, repairs). Supports recurring expenses with auto-generation
- **Rental Payment Tracking** — Record rent payments by tenant, track payment methods, and monitor collection by year
- **Document Management** — Upload and organize documents per property (leases, photos, insurance, tax records, inspections)
- **Contact Management** — Store tenants, contractors, agents, HOA contacts, and insurance providers per property
- **Reminders & Notifications** — Set due dates with email and in-app notifications. Supports recurring reminders
- **Year-End Excel Reports** — Export detailed reports with income and expense breakdowns by month and category per property
- **Legal Document Generation** — Generate DOCX documents from state-specific templates (e.g., Georgia landlord forms with O.C.G.A. references). Auto-fills property, tenant, and landlord info
- **Dark / Light Mode** — Full theme support with vibrant colors in dark mode
- **Multi-User Auth** — Email/password login with JWT. Admin and regular user roles
- **Backup & Restore** — Create, download, upload, and restore database backups from the UI
- **Config-Driven** — All ports, credentials, and paths driven from a single `.env` file

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Angular 19, Angular Material, SCSS |
| Backend | FastAPI (async), Python 3.11 |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (async) + asyncpg |
| Migrations | Alembic |
| Auth | JWT (python-jose) + bcrypt |
| Reports | openpyxl (Excel), python-docx (Word) |
| Templates | Jinja2 |
| Scheduler | APScheduler |
| Email | aiosmtplib |
| Deployment | Docker Compose + nginx |

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- ~2 GB free memory for containers

That's it. No need to install Python, Node, or PostgreSQL locally.

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Harshamendu/SelfPropetyManager.git
cd SelfPropetyManager
```

### 2. Create your environment file

```bash
cp .env.example .env
```

Edit `.env` and update at minimum:

```bash
# Change in production
DB_PASSWORD=your_secure_password
JWT_SECRET_KEY=your-random-secret-key

# Where uploaded documents are stored on your machine
DOCUMENT_HOST_PATH=/path/to/your/documents/folder

# Optional: change ports if defaults conflict
FRONTEND_PORT=80
BACKEND_PORT=8000
```

### 3. Start the application

```bash
docker-compose up --build -d
```

This will:
- Start PostgreSQL and wait for it to be healthy
- Start the backend, run database migrations automatically, and launch the API server
- Build the Angular frontend and serve it via nginx

### 4. Open the app

Go to **http://localhost** (or whatever port you set for `FRONTEND_PORT`).

### 5. Log in

A default admin account is created automatically:

| Field | Value |
|-------|-------|
| Email | `admin@propertymanager.com` |
| Password | `Admin@123` |

You can also register new user accounts from the login page.

---

## Configuration

All settings live in the `.env` file at the project root:

```bash
# ── Database ──────────────────────────────────
DB_USER=propmanager            # PostgreSQL username
DB_PASSWORD=propmanager        # PostgreSQL password
DB_NAME=propmanager            # Database name
DB_PORT=5432                   # PostgreSQL port on host

# ── Ports ─────────────────────────────────────
BACKEND_PORT=8000              # API server port
FRONTEND_PORT=80               # Web UI port

# ── Document Storage ──────────────────────────
DOCUMENT_HOST_PATH=/path/to/documents   # Host folder for uploaded files

# ── Auth ──────────────────────────────────────
JWT_SECRET_KEY=change-me       # JWT signing secret (use a long random string)

# ── Email Notifications (optional) ────────────
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your@gmail.com
SMTP_USE_TLS=true

# ── App ───────────────────────────────────────
CORS_ORIGINS=["http://localhost","http://localhost:4200"]
REMINDER_CHECK_INTERVAL_MINUTES=15
```

---

## Usage Guide

### Adding Your First Property

1. Log in and you'll see the **Dashboard** (empty at first)
2. Click **All Properties** in the sidebar, then click the **+** button
3. Fill in the property details — address, type, purchase info, and landlord info
4. Save. The property now appears in the sidebar and dashboard

### Managing Expenses

1. Click a property in the sidebar to open its detail page
2. Go to the **Expenses** tab
3. Click **+** to add an expense — select category, amount, date
4. For recurring expenses (e.g., monthly HOA), check **Recurring** and set the rule
5. Use the **Generate Recurring** button to auto-create entries for a month
6. Filter by category or sort by any column

### Recording Rental Payments

1. Open a property and go to the **Rental Payments** tab
2. Click **+** to record a payment — amount, date, payment method, period covered
3. Filter by year to see annual payment history

### Uploading Documents

1. Open a property and go to the **Documents** tab
2. Click **Upload** — drag and drop or browse for files
3. Select a category (lease, photo, insurance, tax, inspection, other)
4. Documents are stored at the path you set in `DOCUMENT_HOST_PATH`

### Managing Contacts

1. Open a property and go to the **Contacts** tab
2. Add tenants, contractors, agents, HOA contacts, or insurance providers
3. For tenants, fill in lease start/end dates and monthly rent — this powers the dashboard lease status

### Setting Reminders

1. Open a property and go to the **Reminders** tab
2. Create a reminder with a due date and type (lease renewal, maintenance, payment, etc.)
3. Enable **Email notification** and/or **In-app notification**
4. Recurring reminders auto-regenerate on the schedule you set
5. The notification bell in the top bar shows unread count

### Exporting Year-End Reports

1. Click **Reports** in the sidebar
2. Select a year and optionally a specific property
3. Click **Download Excel**
4. The report includes:
   - Monthly breakdown of every income and expense category
   - Annual totals per category
   - Net income calculations
   - Styled with color-coded headers (green = income, red = expense)

### Generating Legal Documents

1. Click **Document Templates** in the sidebar
2. Select a state from the dropdown (e.g., **GA - Georgia**)
3. Click **Load GA Templates** to seed state-specific legal templates
4. Click **Generate** on any template
5. Select a property — landlord, tenant, and rent info auto-fills
6. Review and edit variables, then click **Generate DOCX**
7. A Word document downloads with all fields filled in

### Dark / Light Mode

Click the sun/moon icon in the top bar to toggle between light and dark themes. Your preference is saved.

### Backup & Restore

1. Click **Backup & Recovery** in the sidebar
2. Click **Create Backup** to save the current database state
3. Download backups to your local machine
4. Upload or restore from a previous backup if needed

---

## Architecture

```
Browser
  │
  ▼
nginx (port 80)
  ├── /* ──────► Angular SPA (static files)
  └── /api/* ──► FastAPI (port 8000)
                    │
                    ▼
                PostgreSQL (port 5432)
```

- **nginx** serves the compiled Angular app and proxies `/api/` requests to the backend
- **FastAPI** handles all business logic, authentication, and database operations
- **PostgreSQL** stores all data with UUID primary keys and timezone-aware timestamps
- **Alembic** migrations run automatically when the backend container starts
- **APScheduler** runs in the background to check for due reminders and send notifications

---

## Project Structure

```
SelfPropertyManager/
├── .env.example                    # Environment template
├── docker-compose.yml              # All services
├── CLAUDE.md                       # AI assistant instructions
├── skills.md                       # Full architecture reference
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/versions/           # Database migrations
│   └── app/
│       ├── main.py                 # FastAPI app + router mounts
│       ├── config.py               # Settings from .env
│       ├── database.py             # Async engine + session
│       ├── dependencies.py         # Auth + DB dependencies
│       ├── models/                 # ORM models (one per domain)
│       ├── schemas/                # Pydantic schemas (one per domain)
│       ├── services/               # Business logic (one per domain)
│       ├── routers/                # API endpoints (one per domain)
│       ├── tasks/                  # Background scheduler jobs
│       └── utils/                  # Helper functions
│
├── frontend/
│   ├── Dockerfile                  # Multi-stage: build + nginx
│   ├── nginx.conf                  # Reverse proxy config
│   ├── package.json
│   └── src/
│       ├── styles.scss             # Global theme (CSS variables)
│       ├── environments/           # Dev/prod API URLs
│       └── app/
│           ├── core/               # Auth, API, theme, notification services
│           ├── shared/             # Reusable components and pipes
│           ├── layout/             # Sidebar, topbar, shell
│           └── features/           # Feature modules
│               ├── auth/           # Login/register
│               ├── dashboard/      # Property summary cards
│               ├── properties/     # CRUD + detail with tabs
│               ├── expenses/       # Expense tracking
│               ├── rental-payments/# Payment records
│               ├── documents/      # File upload/download
│               ├── contacts/       # Contact management
│               ├── reminders/      # Reminder CRUD
│               ├── reports/        # Year-end Excel export
│               ├── document-gen/   # Template-based DOCX generation
│               ├── categories/     # Expense/income categories
│               └── backups/        # DB backup/restore
│
└── scripts/
    ├── backup-db.sh                # CLI database backup
    └── restore-db.sh               # CLI database restore
```

---

## API Documentation

With the backend running, visit **http://localhost:8000/docs** for interactive Swagger documentation of all endpoints.

Key endpoint groups:

| Prefix | Description |
|--------|-------------|
| `/api/v1/auth` | Register, login, current user |
| `/api/v1/properties` | Property CRUD + summaries |
| `/api/v1/properties/{id}/expenses` | Expenses per property |
| `/api/v1/properties/{id}/rental-payments` | Payments per property |
| `/api/v1/properties/{id}/documents` | Document upload/download |
| `/api/v1/contacts` | Contact management |
| `/api/v1/reminders` | Reminder CRUD + completion |
| `/api/v1/notifications` | In-app notification feed |
| `/api/v1/reports/year-end/{year}` | Excel report download |
| `/api/v1/document-templates` | Template CRUD + DOCX generation |
| `/api/v1/categories` | Expense/income categories |
| `/api/v1/backups` | Backup create/restore/download |
| `/api/health` | Health check |

---

## Common Operations

### Rebuild after code changes

```bash
# Frontend changes
docker-compose build --no-cache frontend && docker-compose up -d

# Backend changes
docker-compose build --no-cache backend && docker-compose up -d

# Everything
docker-compose build --no-cache && docker-compose up -d
```

### View logs

```bash
docker-compose logs --tail 50 backend     # Backend logs
docker-compose logs --tail 50 frontend    # Frontend/nginx logs
docker-compose logs -f backend            # Follow logs in real time
```

### Stop the application

```bash
docker-compose down          # Stop all containers
docker-compose down -v       # Stop and DELETE all data (fresh start)
```

### Change ports

Edit `.env`:
```bash
FRONTEND_PORT=3000    # UI at http://localhost:3000
BACKEND_PORT=9000     # API at http://localhost:9000
```
Then restart: `docker-compose up -d`

### Database backup via CLI

```bash
./scripts/backup-db.sh              # Create backup
./scripts/restore-db.sh             # Restore latest backup
./scripts/restore-db.sh backup.sql  # Restore specific file
```

---

## Development (without Docker)

If you prefer running services directly for faster iteration:

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://propmanager:propmanager@localhost:5432/propmanager"
export SYNC_DATABASE_URL="postgresql://propmanager:propmanager@localhost:5432/propmanager"

# Run migrations
alembic upgrade head

# Start server with hot reload
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
ng serve    # Starts dev server at http://localhost:4200
```

In dev mode, the frontend calls `http://localhost:8000/api/v1` directly (no nginx proxy needed).

---

## Email Notifications Setup

To enable email reminders:

1. Create a [Google App Password](https://myaccount.google.com/apppasswords) (or use your SMTP provider)
2. Update `.env`:
   ```bash
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your@gmail.com
   SMTP_PASSWORD=your_16_char_app_password
   SMTP_FROM_EMAIL=your@gmail.com
   SMTP_USE_TLS=true
   ```
3. Restart: `docker-compose up -d`
4. The scheduler checks for due reminders every 15 minutes (configurable via `REMINDER_CHECK_INTERVAL_MINUTES`)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Frontend shows old code after changes | Rebuild with `docker-compose build --no-cache frontend && docker-compose up -d` |
| Backend won't start | Check logs: `docker-compose logs backend`. Common: migration error or missing env var |
| "Invalid email or password" on login | Default admin: `admin@propertymanager.com` / `Admin@123`. Or register a new account. |
| Port already in use | Change `FRONTEND_PORT` or `BACKEND_PORT` in `.env` and restart |
| Document uploads fail | Ensure `DOCUMENT_HOST_PATH` in `.env` points to an existing folder with write permissions |
| NaN showing in totals | Known fix applied. If reappears, ensure `Number()` coercion on Decimal values from API |
| Dark mode colors look wrong | All SCSS must use `var(--name)` CSS variables. Run dark-mode-checker agent to audit |
| Database needs fresh start | `docker-compose down -v && docker-compose up -d` (deletes all data) |

---

## License

This is a personal project for managing rental properties. Not licensed for redistribution.
