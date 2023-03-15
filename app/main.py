import logging

from elasticsearch_dsl import connections
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import graphql

logger = logging.getLogger("uvicorn")


def create_application() -> FastAPI:
    application = FastAPI(
        title="Jelly",
        description="""A playground for FastAPI, GraphQL and Elasticsearch""",
        version="0.1.0",
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
    connections.create_connection(hosts=["http://elasticsearch:9200"])


@app.on_event("shutdown")
async def shutdown_event() -> None:
    logger.info("Shutting down...")
