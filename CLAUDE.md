# OWN Property Manager

## Project Overview
Full-stack property management application for managing rental properties in Georgia.

## Required Reading
- **@skills.md** — Complete architecture, patterns, conventions, theming, auth, naming rules. Read before making changes.

## Tech Stack
- **Frontend**: Angular 19+ (standalone components, Angular Material, SCSS)
- **Backend**: FastAPI (Python 3.11, async SQLAlchemy + asyncpg)
- **Database**: PostgreSQL 16
- **Auth**: JWT (python-jose + passlib/bcrypt), admin: `admin@propertymanager.com` / `Admin@123`
- **Deployment**: Docker Compose (all ports/credentials driven from `.env`)

---

## Workflow Rules (Best Practices)

### 1. Explore First, Then Plan, Then Code
- **Non-trivial tasks**: Read relevant files first. Create a plan. Then implement.
- **Trivial tasks** (typos, renames, log lines): Skip planning, just do it.
- Never modify code you haven't read.

### 2. Verify After Every Change
- Backend: Check `docker-compose logs --tail 20 backend` for errors after rebuild.
- Frontend: Rebuild with `--no-cache` and confirm in browser.
- API changes: Test with `curl` or Swagger at `localhost:8000/docs`.
- Run existing tests if available.

### 3. Keep Changes Minimal
- Fix what was asked. Don't refactor surrounding code.
- Don't add docstrings, comments, or type annotations to code you didn't change.
- Don't add error handling for scenarios that can't happen.
- Don't create abstractions for one-time operations.

### 4. Use Subagents for Research
- Deep codebase exploration: Use subagents to protect main context.
- Security review: Use the `security-reviewer` agent.
- Dark mode audit: Use the `dark-mode-checker` agent.

### 5. Context Management
- Use `/clear` between unrelated tasks.
- After two failed corrections, `/clear` and rewrite the prompt.
- When compacting, preserve the full list of modified files and build/test commands.

---

## Coding Standards

### Backend
- Each domain: model + schema + service + router (separate files)
- All endpoints are `async`. All queries use SQLAlchemy async session.
- UUID primary keys. Decimal for money. Timezone-aware timestamps.
- `response_model` on every endpoint. Proper HTTP status codes.
- Dependency injection: `Depends(get_db)`, `Depends(require_user)`
- Config from env only: `pydantic-settings` BaseSettings reads `.env`

### Frontend
- Standalone components only (no NgModules). Use `inject()` not constructor.
- Feature modules: `features/{name}/models/`, `services/`, `{name}-list/`, `{name}-form/`
- Services: `@Injectable({ providedIn: 'root' })`, return `Observable<T>`, use `ApiService`
- Lazy-loaded routes: `loadComponent` / `loadChildren`
- All SCSS colors via CSS variables: `var(--name)`. **Zero hardcoded hex in component SCSS.**
- Dark mode: vibrant saturated accents on dark backgrounds. Light mode: muted pastels.

### Naming
| Item | Backend | Frontend |
|------|---------|----------|
| Files | `snake_case.py` | `kebab-case.component.ts` |
| Classes | `PascalCase` | `PascalCase` |
| Functions | `snake_case` | `camelCase` |
| DB Tables | `plural_snake_case` | - |
| API URLs | `/kebab-case` | - |
| CSS vars | `--kebab-case` | `var(--kebab-case)` |

---

## Project Structure
```
backend/app/
├── main.py, config.py, database.py, dependencies.py
├── models/       # SQLAlchemy ORM (one per domain)
├── schemas/      # Pydantic Create/Update/Response (one per domain)
├── services/     # Business logic (one per domain)
├── routers/      # API endpoints (one per domain)
├── tasks/        # APScheduler background jobs
└── utils/        # Helpers (date, file)

frontend/src/app/
├── core/         # Singleton services, guards, interceptors
├── shared/       # Reusable components, pipes
├── layout/       # Sidebar, topbar, layout shell
└── features/     # Domain modules (components/services/models per feature)
```

## Commands
```bash
docker-compose up --build                              # Start all
docker-compose build --no-cache frontend && docker-compose up -d  # Rebuild frontend
docker-compose build --no-cache backend && docker-compose up -d   # Rebuild backend
docker-compose down                                    # Stop
docker-compose down -v                                 # Stop + reset DB
docker-compose logs --tail 30 backend                  # Check backend logs
```
- Ports in `.env`: FRONTEND_PORT=80, BACKEND_PORT=8000, DB_PORT=5432
- API prefix: `/api/v1`
- Swagger: `http://localhost:8000/docs`

## Document Storage
- Host: `/Users/harshavardhanreddymendu/Documents/PropertyManager`
- Container: `/data/documents`

## Skills (invoke with /skill-name)
- `/add-backend-feature` — Add new backend domain end-to-end
- `/add-frontend-feature` — Add new frontend feature module end-to-end
- `/fix-issue` — Diagnose and fix a bug with verification
- `/deploy` — Build, deploy, and verify all services

## Agents (use with "use a subagent to...")
- `security-reviewer` — Scan for SQL injection, auth bypass, secrets exposure, XSS
- `dark-mode-checker` — Find hardcoded colors in SCSS that break dark mode

## Common Gotchas
- **bcrypt**: Pin `bcrypt==4.2.1` in requirements.txt (passlib incompatible with 5.x)
- **Docker cache**: Always use `--no-cache` when code changes aren't reflected
- **NaN values**: API returns Decimal as string. Use `Number()` in TypeScript.
- **Pydantic errors**: `detail` can be string or array. Handle both in frontend.
- **Field names**: Backend uses `snake_case`, frontend must match exactly.
- **Python version**: Use 3.11, not 3.12 (Docker compatibility).
