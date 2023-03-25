import logging
from time import sleep

from elasticsearch.exceptions import ConnectionError, RequestError
from elasticsearch_dsl import connections
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .documents.creator import Creator
from .routers import graphql

logger = logging.getLogger("gunicorn.error")


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


async def setup_elasticsearch():
    documents = {Creator}
    for document in documents:
        while True:
            try:
                document.init()
                break
            except ConnectionError:
                wait_seconds = 5
                sleep(wait_seconds)
                logger.info(
                    f"Wait {wait_seconds} seconds and try again to establish a new connection to Elasticsearch."
                )
            except RequestError:
                # Resource already exists.
                break


app = create_application()


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Starting up...")
    connections.create_connection(hosts=["http://elasticsearch:9200"])
    await setup_elasticsearch()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    logger.info("Shutting down...")
