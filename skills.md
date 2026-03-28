# Self Property Manager - Project Skills & Standards

A modular full-stack property management application. This document serves as the definitive reference for architecture, conventions, and patterns used across the project.

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | Angular (standalone components) | 19+ |
| UI Framework | Angular Material + CDK | 19+ |
| Styling | SCSS with CSS custom properties | - |
| Backend | FastAPI (async) | 0.115+ |
| ORM | SQLAlchemy (async) + asyncpg | 2.0+ |
| Database | PostgreSQL | 16 |
| Migrations | Alembic | 1.14+ |
| Auth | JWT (python-jose) + bcrypt (passlib) | - |
| Scheduler | APScheduler | 3.10+ |
| Deployment | Docker Compose | 3.9 |
| Reverse Proxy | nginx | alpine |
| Language (Backend) | Python | 3.11 |
| Language (Frontend) | TypeScript | 5.6 |

---

## Architecture Overview

```
                 +-----------+
                 |  Browser  |
                 +-----+-----+
                       |
                 +-----v-----+
                 |   nginx    |  Port: FRONTEND_PORT (default 80)
                 |  (static)  |
                 +-----+-----+
                       |
            +----------+----------+
            |                     |
      /api/* proxy          /* SPA fallback
            |                (index.html)
      +-----v-----+
      |  FastAPI   |  Port: BACKEND_PORT (default 8000)
      |  (async)   |
      +-----+-----+
            |
      +-----v-----+
      | PostgreSQL |  Port: DB_PORT (default 5432)
      +-----------+
```

---

## Project Structure

```
SelfPropetyManager/
├── .env                          # Environment config (git-ignored)
├── .env.example                  # Template for .env
├── docker-compose.yml            # Service orchestration
├── CLAUDE.md                     # AI assistant instructions
├── skills.md                     # This file
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/             # Sequential migrations
│   ├── tests/
│   │   └── conftest.py
│   └── app/
│       ├── main.py               # App entry, CORS, router mounts, lifespan
│       ├── config.py             # Pydantic BaseSettings (reads .env)
│       ├── database.py           # Async engine, session factory, Base
│       ├── dependencies.py       # get_db, get_current_user, require_user
│       ├── models/               # SQLAlchemy ORM models (one per domain)
│       ├── schemas/              # Pydantic request/response (one per domain)
│       ├── routers/              # API endpoints (one per domain)
│       ├── services/             # Business logic (one per domain)
│       ├── tasks/                # APScheduler jobs
│       └── utils/                # Helpers (date, file)
│
└── frontend/
    ├── Dockerfile                # Multi-stage: node build -> nginx serve
    ├── nginx.conf                # API proxy + SPA fallback
    ├── package.json
    └── src/
        ├── styles.scss           # Global theme (CSS variables, Material overrides)
        ├── environments/         # Dev/prod API URLs
        └── app/
            ├── app.config.ts     # Providers (router, http, interceptors)
            ├── app.routes.ts     # Top-level routing with lazy loading
            ├── core/             # Singletons: services, guards, interceptors
            ├── shared/           # Reusable: components, pipes, directives
            ├── layout/           # Shell: sidebar, topbar, layout container
            └── features/         # Domain modules (one folder per feature)
```

---

## Backend Patterns

### Model Layer (`app/models/`)

Every domain entity gets its own file. All models inherit from `Base`.

```python
# app/models/expense.py
import uuid
from decimal import Decimal
from sqlalchemy import String, ForeignKey, Numeric, Date, Boolean, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    property_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"))
    category: Mapped[str] = mapped_column(String(100))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    # ... more fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

**Conventions:**
- UUID primary keys with `default=uuid.uuid4`
- `Mapped[type]` annotations for all columns
- `ForeignKey` with `ondelete="CASCADE"` for parent relationships
- `server_default=func.now()` for timestamps
- `Optional[type]` for nullable fields
- Decimal (`Numeric(12, 2)`) for monetary values

### Schema Layer (`app/schemas/`)

Each domain has Create, Update, Response schemas.

```python
# app/schemas/expense.py
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from uuid import UUID

class ExpenseCreate(BaseModel):
    category: str
    amount: Decimal
    description: str | None = None
    # ... required fields

class ExpenseUpdate(BaseModel):
    category: str | None = None
    amount: Decimal | None = None
    # ... all fields optional for partial updates

class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    category: str
    amount: Decimal
    # ... all fields including computed/timestamps
```

**Conventions:**
- `ConfigDict(from_attributes=True)` on Response schemas for ORM conversion
- Create schemas have required fields only
- Update schemas have all fields optional (used with `exclude_unset=True`)
- Use `str | None = None` for optional fields

### Router Layer (`app/routers/`)

Each router is a standalone `APIRouter` with tag grouping.

```python
# app/routers/expenses.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db

router = APIRouter(tags=["Expenses"])

@router.get("/properties/{property_id}/expenses", response_model=list[ExpenseResponse])
async def list_expenses(
    property_id: UUID,
    year: int | None = None,
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    # ... query logic
```

**Conventions:**
- Resource-based URLs under `/api/v1`
- Nested resources: `/properties/{property_id}/expenses`
- Query params for filtering: `?year=2026&category=mortgage`
- All endpoints are `async`
- Dependency injection via `Depends(get_db)`, `Depends(require_user)`
- `response_model` on every endpoint
- Proper HTTP status codes: 201 for creation, 204 for deletion

### Service Layer (`app/services/`)

Business logic separated from routing.

```python
# app/services/expense_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def get_by_property(db: AsyncSession, property_id: UUID, year: int | None = None):
    stmt = select(Expense).where(Expense.property_id == property_id)
    if year:
        stmt = stmt.where(extract("year", Expense.date) == year)
    result = await db.execute(stmt)
    return result.scalars().all()
```

**Conventions:**
- Pure async functions (no class-based services)
- Accept `AsyncSession` as first parameter
- Build queries with SQLAlchemy `select()` + chained `.where()`
- Return ORM model instances (router converts via response_model)

### Dependency Injection (`app/dependencies.py`)

```python
from fastapi.security import HTTPBearer
security = HTTPBearer(auto_error=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def get_current_user(credentials = Depends(security), db = Depends(get_db)) -> User | None:
    # Decode JWT, lookup user, return or None

async def require_user(user = Depends(get_current_user)) -> User:
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
```

### Database Migrations (`alembic/`)

```bash
# Generate migration after model changes
alembic revision --autogenerate -m "add field to expenses"

# Apply migrations (done automatically on container start)
alembic upgrade head
```

**Conventions:**
- Migration IDs are short hex strings
- Descriptive messages: `add_landlord_info_to_properties`
- Include both `upgrade()` and `downgrade()` functions
- Data seeding done in migrations when appropriate (e.g., admin user)
- Container CMD runs `alembic upgrade head` before starting uvicorn

---

## Frontend Patterns

### Component Architecture

All components are **standalone** (no NgModules).

```typescript
// feature.component.ts
@Component({
  selector: 'app-feature',
  standalone: true,
  imports: [CommonModule, MatCardModule, ...],  // declare dependencies inline
  templateUrl: './feature.component.html',
  styleUrl: './feature.component.scss'
})
export class FeatureComponent implements OnInit {
  private service = inject(ServiceName);  // functional injection
  // ...
}
```

**Conventions:**
- `inject()` function over constructor injection
- `OnInit` for data loading
- Inline `imports` array on every component
- One component per file
- Template and styles in separate files (not inline, except login page)

### Feature Module Pattern

Each feature is a self-contained folder:

```
features/expenses/
├── models/
│   └── expense.model.ts        # Interfaces, types, constants
├── services/
│   └── expense.service.ts      # API calls via ApiService
├── expense-list/
│   ├── expense-list.component.ts
│   ├── expense-list.component.html
│   └── expense-list.component.scss
├── expense-form/
│   ├── expense-form.component.ts
│   ├── expense-form.component.html
│   └── expense-form.component.scss
└── expenses.routes.ts           # Lazy-loaded child routes
```

### Routing

```typescript
// app.routes.ts - top level
export const routes: Routes = [
  { path: 'login', loadComponent: () => import('...').then(m => m.LoginComponent) },
  {
    path: '',
    component: LayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: 'dashboard', loadComponent: () => import('...').then(m => m.DashboardComponent) },
      { path: 'properties', loadChildren: () => import('...').then(m => m.PROPERTIES_ROUTES) },
    ]
  }
];

// features/properties/properties.routes.ts - child routes
export const PROPERTIES_ROUTES: Routes = [
  { path: '', component: PropertyListComponent },
  { path: 'new', component: PropertyFormComponent },
  { path: ':id', component: PropertyDetailComponent },
  { path: ':id/edit', component: PropertyFormComponent },
];
```

**Conventions:**
- `loadComponent` / `loadChildren` for lazy loading
- `authGuard` on the layout route protects all children
- Feature routes exported as `FEATURE_ROUTES` constant

### Service Pattern

```typescript
// feature.service.ts
@Injectable({ providedIn: 'root' })
export class FeatureService {
  private api = inject(ApiService);

  getAll(): Observable<Feature[]> {
    return this.api.get<Feature[]>('/features');
  }

  getById(id: string): Observable<Feature> {
    return this.api.get<Feature>(`/features/${id}`);
  }

  create(data: FeatureCreate): Observable<Feature> {
    return this.api.post<Feature>('/features', data);
  }

  update(id: string, data: Partial<FeatureCreate>): Observable<Feature> {
    return this.api.put<Feature>(`/features/${id}`, data);
  }

  delete(id: string): Observable<void> {
    return this.api.delete<void>(`/features/${id}`);
  }
}
```

**Conventions:**
- All services are `providedIn: 'root'` singletons
- Use `ApiService` wrapper (not raw `HttpClient`)
- Return `Observable<T>` (subscribe in components)
- Stateless: no internal caching (except auth/notification/theme)
- `BehaviorSubject` for shared reactive state (auth user, theme, unread count)

### Core ApiService

```typescript
@Injectable({ providedIn: 'root' })
export class ApiService {
  private baseUrl = environment.apiUrl;

  get<T>(path: string): Observable<T>;
  post<T>(path: string, body: any): Observable<T>;
  put<T>(path: string, body: any): Observable<T>;
  delete<T>(path: string): Observable<T>;
  upload(path: string, formData: FormData): Observable<any>;
  postBlob(path: string, body: any): Observable<Blob>;
  downloadBlob(path: string): Observable<Blob>;
}
```

### Interceptors

```typescript
// Functional interceptors (Angular 19 style)
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  // Adds Bearer token from localStorage
  // Catches 401 on non-auth URLs -> logout
};

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  // Logs errors, distinguishes client vs server errors
  // Re-throws for component handling
};

// Registered in app.config.ts
provideHttpClient(withInterceptors([authInterceptor, errorInterceptor]))
```

### Model Interfaces

```typescript
// Always define: full entity, create input, and constants
export interface Feature {
  id: string;
  name: string;
  created_at: string;
}

export interface FeatureCreate {
  name: string;
}

export const FEATURE_TYPES = ['type_a', 'type_b', 'type_c'] as const;
```

---

## Theming System

### CSS Variables (defined in `styles.scss`)

Two theme classes on `<body>`: `light-theme` and `dark-theme`.

| Variable | Purpose |
|----------|---------|
| `--bg-primary` | Page background |
| `--bg-card` | Card/panel background |
| `--bg-sidebar` | Sidebar background |
| `--bg-input` | Input field background |
| `--bg-surface` | Elevated surface background |
| `--text-primary` | Main text |
| `--text-secondary` | Supporting text |
| `--text-muted` | Disabled/hint text |
| `--border-color` | Dividers, borders |
| `--hover-bg` | Row/item hover state |
| `--accent-primary` | Primary accent (blue) |
| `--accent-green` | Success/income |
| `--accent-red` | Error/expense |
| `--accent-orange` | Warning/overdue |
| `--stat-income-bg/text` | Income stat cards |
| `--stat-expense-bg/text` | Expense stat cards |
| `--stat-reminder-bg/text` | Reminder/warning cards |
| `--lease-active-bg/text` | Active lease badge |
| `--badge-*-bg/text` | Status badges (pending, completed, etc.) |

**Rules:**
- Never use hardcoded hex colors in component SCSS
- Always use `var(--variable-name)` for any color
- Dark mode uses vibrant, saturated colors on dark backgrounds
- Light mode uses muted, pastel backgrounds with dark text

### ThemeService

```typescript
// Toggle: themeService.toggle()
// Set:    themeService.setTheme('dark')
// Read:   themeService.isDark
// Persists to localStorage, applies class to document.body
```

---

## Authentication System

### Flow

```
1. User submits email/password
2. POST /api/v1/auth/login -> returns { access_token, user }
3. Token stored in localStorage ('auth_token')
4. authInterceptor adds "Authorization: Bearer <token>" to all requests
5. authGuard checks token exists before allowing route access
6. 401 response on non-auth URLs -> auto logout
```

### Roles

| Field | Purpose |
|-------|---------|
| `is_active` | Account enabled/disabled |
| `is_admin` | Full access (admin panel, user management) |

### Default Admin

| Field | Value |
|-------|-------|
| Email | `admin@propertymanager.com` |
| Password | `Admin@123` |
| Role | Admin |

---

## Configuration Management

### Single `.env` file drives everything

```bash
# Database
DB_USER=propmanager
DB_PASSWORD=propmanager
DB_NAME=propmanager
DB_PORT=5432

# Ports
BACKEND_PORT=8000
FRONTEND_PORT=80

# Storage
DOCUMENT_HOST_PATH=/path/to/documents

# Auth
JWT_SECRET_KEY=change-me-in-production

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...

# App
CORS_ORIGINS=["http://localhost","http://localhost:4200"]
REMINDER_CHECK_INTERVAL_MINUTES=15
```

**How it flows:**
1. `.env` is read by `docker-compose.yml` for variable substitution
2. `docker-compose.yml` passes vars to containers via `env_file` and `environment`
3. Backend `config.py` uses `pydantic-settings` to read env vars automatically
4. Frontend uses `environments/environment.ts` for API URL (build-time)

---

## Docker Operations

```bash
# Start all services
docker-compose up -d

# Rebuild after code changes
docker-compose build --no-cache frontend   # Frontend changes
docker-compose build --no-cache backend    # Backend changes
docker-compose up -d                       # Restart with new images

# View logs
docker-compose logs --tail 50 backend
docker-compose logs -f frontend

# Stop
docker-compose down

# Reset database (destructive)
docker-compose down -v   # Removes pgdata volume
docker-compose up -d     # Fresh start with migrations
```

---

## Adding a New Feature (Checklist)

### Backend

1. **Model**: Create `app/models/feature.py` with SQLAlchemy model
2. **Register model**: Add import to `app/models/__init__.py`
3. **Schema**: Create `app/schemas/feature.py` with Create/Update/Response
4. **Service**: Create `app/services/feature_service.py` with CRUD functions
5. **Router**: Create `app/routers/feature.py` with API endpoints
6. **Mount router**: Add `app.include_router(feature.router, prefix="/api/v1")` in `main.py`
7. **Migration**: Run `alembic revision --autogenerate -m "add feature table"`
8. **Rebuild**: `docker-compose build --no-cache backend && docker-compose up -d`

### Frontend

1. **Model**: Create `features/feature/models/feature.model.ts`
2. **Service**: Create `features/feature/services/feature.service.ts`
3. **Components**: Create list/form/detail components in `features/feature/`
4. **Routes**: Create `features/feature/feature.routes.ts`
5. **Register routes**: Add lazy-loaded child in `app.routes.ts`
6. **Sidebar link**: Add navigation item in `layout/sidebar/`
7. **Rebuild**: `docker-compose build --no-cache frontend && docker-compose up -d`

---

## Naming Conventions

| Item | Backend (Python) | Frontend (TypeScript) |
|------|-----------------|----------------------|
| Files | `snake_case.py` | `kebab-case.component.ts` |
| Classes | `PascalCase` | `PascalCase` |
| Functions | `snake_case` | `camelCase` |
| Variables | `snake_case` | `camelCase` |
| DB Tables | `plural_snake_case` | - |
| API URLs | `/kebab-case` | - |
| CSS Classes | `.kebab-case` | `.kebab-case` |
| CSS Variables | `--kebab-case` | `var(--kebab-case)` |
| Constants | `UPPER_SNAKE_CASE` | `UPPER_SNAKE_CASE` |
| Interfaces | - | `PascalCase` (no `I` prefix) |

---

## API URL Patterns

| Pattern | Example | Purpose |
|---------|---------|---------|
| `GET /resources` | `GET /properties` | List all |
| `GET /resources/:id` | `GET /properties/abc-123` | Get one |
| `POST /resources` | `POST /properties` | Create |
| `PUT /resources/:id` | `PUT /properties/abc-123` | Full update |
| `PATCH /resources/:id` | `PATCH /expenses/abc-123` | Partial update |
| `DELETE /resources/:id` | `DELETE /properties/abc-123` | Delete |
| `GET /parent/:id/children` | `GET /properties/abc-123/expenses` | Nested list |
| `GET /resources?filter=val` | `GET /expenses?year=2026&category=hoa` | Filtered list |

---

## Error Handling

### Backend
- `HTTPException` with appropriate status codes
- Pydantic validation returns `422` with `detail` as array of error objects
- Auth failures return `401` with `detail` as string

### Frontend
- `errorInterceptor` logs all HTTP errors
- `authInterceptor` catches `401` on non-auth URLs and triggers logout
- Components handle errors in `subscribe({ error: ... })` callbacks
- Extract error messages: check if `detail` is string or array

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Standalone components (no NgModules) | Angular 19 best practice, simpler dependency management |
| Functional interceptors/guards | Angular 19 pattern, lighter than class-based |
| Async SQLAlchemy + asyncpg | Non-blocking DB operations, better concurrency |
| UUID primary keys | Globally unique, no sequential ID leakage |
| CSS variables for theming | Runtime theme switching without rebuild |
| Pydantic BaseSettings | Type-safe config with .env file auto-loading |
| Alembic in container CMD | Migrations always run on deploy, zero manual steps |
| nginx SPA fallback | Client-side routing works on page refresh |
| Service layer separation | Routers stay thin, business logic is testable |
| BehaviorSubject for shared state | Simple reactive state without NgRx overhead |
