import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from ..settings import get_settings

settings = get_settings()

logger = logging.getLogger("gunicorn.error")

mongo_client = None


async def get_db() -> AsyncIOMotorDatabase:
    global mongo_client
    if mongo_client is None:
        mongo_client = AsyncIOMotorClient(settings.mongodb_url)
    return mongo_client[settings.mongodb_database]


async def close_db():
    global mongo_client
    if mongo_client is not None:
        mongo_client.close()
        mongo_client = None
