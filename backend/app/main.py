import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (
    auth,
    backups,
    categories,
    contacts,
    document_gen,
    documents,
    expenses,
    notifications,
    properties,
    reminders,
    rental_payments,
    reports,
    users,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up")
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(properties.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(expenses.router, prefix="/api/v1")
app.include_router(rental_payments.router, prefix="/api/v1")
app.include_router(contacts.router, prefix="/api/v1")
app.include_router(reminders.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(document_gen.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(backups.router, prefix="/api/v1")


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
