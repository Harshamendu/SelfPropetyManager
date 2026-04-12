---
name: add-backend-feature
description: Add a new backend domain (model, schema, service, router, migration)
---

# Add Backend Feature

Follow these steps exactly when adding a new backend domain:

## Steps

1. **Model** — Create `backend/app/models/{domain}.py`
   - UUID primary key with `default=uuid.uuid4`
   - `Mapped[type]` annotations for all columns
   - ForeignKey with `ondelete="CASCADE"` for parent relationships
   - `server_default=func.now()` for timestamps
   - `Optional[type]` for nullable fields

2. **Register model** — Add import to `backend/app/models/__init__.py`

3. **Schema** — Create `backend/app/schemas/{domain}.py`
   - `{Domain}Create` — required fields only
   - `{Domain}Update` — all fields optional
   - `{Domain}Response` — with `ConfigDict(from_attributes=True)`

4. **Service** — Create `backend/app/services/{domain}_service.py`
   - Async functions accepting `AsyncSession` as first param
   - Use SQLAlchemy `select()` with chained `.where()`

5. **Router** — Create `backend/app/routers/{domain}.py`
   - `APIRouter(tags=["{Domain}"])`
   - RESTful URLs: `GET /resources`, `POST /resources`, `PUT /resources/{id}`, `DELETE /resources/{id}`
   - Nested: `GET /parent/{id}/children`
   - Use `Depends(get_db)` and `Depends(require_user)` where needed
   - `response_model` on every endpoint
   - Proper status codes: 201 create, 204 delete

6. **Mount router** — Add to `backend/app/main.py`:
   ```python
   from app.routers import {domain}
   app.include_router({domain}.router, prefix="/api/v1")
   ```

7. **Migration** — Generate:
   ```bash
   docker-compose exec backend alembic revision --autogenerate -m "add {domain} table"
   ```

8. **Rebuild**:
   ```bash
   docker-compose build --no-cache backend && docker-compose up -d
   ```

9. **Verify** — Check migration ran in logs, test endpoints via curl or Swagger at `/docs`
