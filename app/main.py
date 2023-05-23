import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database.mongodb import close_db, get_db
from .routers import graphql
from .search_engine.elasticsearch import close_es, get_es
from .settings import get_settings

settings = get_settings()

logger = logging.getLogger("gunicorn.error")


def create_application() -> FastAPI:
    application = FastAPI(
        title="Jelly",
        description="""A playground for FastAPI, GraphQL and Elasticsearch""",
        version="0.2.0",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost", "https://localhost"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(graphql.router)
    return application


app = create_application()


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Starting up...")
    await get_db()
    await get_es()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    logger.info("Shutting down...")
    await close_db()
    await close_es()
