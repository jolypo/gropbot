from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI

from app.config import settings
from app.telegram.bots import (
    start_all_bots,
    stop_all_bots,
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    applications = None

    try:

        applications = await start_all_bots()

        yield

    finally:

        await stop_all_bots(
            applications
        )


app = FastAPI(
    title="Saudi TASI AI Signal System",
    lifespan=lifespan,
)


@app.get("/health")
async def health():

    return {
        "status": "alive",

        "timestamp":
            datetime.now(timezone.utc).isoformat(),

        "database":
            "configured"
            if settings.database_url
            else "missing",

        "data_provider":
            "configured"
            if settings.sahmk_api_key
            else "not_configured",
    }
