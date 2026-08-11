from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.api.dependencies import build_generate_and_deliver_use_case
from src.infrastructure.api.v1.health import router as health_router
from src.infrastructure.api.v1.reports import router as reports_router
from src.infrastructure.config import settings
from src.infrastructure.scheduling.scheduler import create_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    scheduler = create_scheduler(
        job=lambda: build_generate_and_deliver_use_case().execute(),
        timezone=settings.scheduler_timezone,
    )
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown()


app = FastAPI(title="Harvest API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
