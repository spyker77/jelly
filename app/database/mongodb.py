import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from ..config import get_settings

settings = get_settings()

logger = logging.getLogger("gunicorn.error")


client = AsyncIOMotorClient(settings.mongodb_url)


# async def get_db() -> AsyncIOMotorDatabase:
#     db = client[settings.mongodb_database]
#     try:
#         yield db
#     finally:
#         client.close()


async def get_db() -> AsyncIOMotorDatabase:
    db = client[settings.mongodb_database]
    return db
