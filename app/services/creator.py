from typing import Any

from bson import ObjectId
from fastapi import BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..search_engine.es_utils import (
    es_create_index,
    es_delete_document,
    es_index_document,
    es_search,
    es_update_document,
)


async def get_creator_by_email(db: AsyncIOMotorDatabase, email: str) -> dict[str, Any] | None:
    """
    Retrieve a creator from the database using their email address.

    Args:
        db (AsyncIOMotorDatabase): The database connection.
        email (str): The email of the creator.

    Returns:
        Optional[dict[str, Any]]: The creator data as a dictionary, or None if not found.
    """
    return await db["creators"].find_one({"email": email})


async def create_creator(
    db: AsyncIOMotorDatabase,
    creator: dict,
    background_tasks: BackgroundTasks,
) -> dict[str, Any]:
    """
    Create a new creator in the database and index them in Elasticsearch.

    Args:
        db (AsyncIOMotorDatabase): The database connection.
        creator (dict): The creator model instance to create.
        background_tasks: The FastAPI background tasks instance.

    Returns:
        dict[str, Any]: The result of the creator insertion.
    """
    await db["creators"].insert_one(creator)

    background_tasks.add_task(es_create_index, "creator")
    background_tasks.add_task(es_index_document, "creator", str(creator["_id"]), creator)

    return creator


async def update_creator_assets(
    db: AsyncIOMotorDatabase,
    email: str,
    assets: list,
    background_tasks: BackgroundTasks,
) -> None:
    """
    Update a creator's assets in the database and Elasticsearch.

    Args:
        db (AsyncIOMotorDatabase): The database connection.
        email (str): The email of the creator.
        assets (list): The updated list of assets for the creator.
        background_tasks: The FastAPI background tasks instance.

    Returns:
        None
    """
    await db["creators"].update_one({"email": email}, {"$set": {"assets": assets}})

    creator = await get_creator_by_email(db, email)
    background_tasks.add_task(es_update_document, "creator", str(creator["_id"]), {"assets": assets})


async def delete_creator_by_email(
    db: AsyncIOMotorDatabase,
    email: str,
    background_tasks: BackgroundTasks,
) -> dict[str, Any]:
    """
    Delete a creator from the database by their email and remove their index from Elasticsearch.

    Args:
        db (AsyncIOMotorDatabase): The database connection.
        email (str): The email of the creator.
        background_tasks: The FastAPI background tasks instance.

    Returns:
        dict[str, Any]: The deleted creator data as a dictionary.
    """
    creator = await get_creator_by_email(db, email)
    await db["creators"].delete_one({"email": email})

    background_tasks.add_task(es_delete_document, "creator", str(creator["_id"]))
    return creator


async def search_creators(
    db: AsyncIOMotorDatabase,
    search_text: str,
    page: int = 1,
    per_page: int = 10,
) -> list[dict[str, Any]]:
    """
    Search for creators in the database based on the provided search text, page, and per_page parameters.

    This function utilizes Elasticsearch to perform the search, then queries the database using the creator IDs
    returned from the search to retrieve the creator data.

    Args:
        db (AsyncIOMotorDatabase): The database connection.
        search_text (str): The text to search for in the creators' data.
        page (int, optional): The page number of the search results. Defaults to 1.
        per_page (int, optional): The number of search results per page. Defaults to 10.

    Returns:
        list[dict[str, Any]]: A list of dictionaries containing creator data that matches the search text.
    """
    response = await es_search("creator", search_text, page, per_page)
    creator_ids = [hit["_id"] for hit in response["hits"]["hits"]]
    creators = (
        await db["creators"].find({"_id": {"$in": [ObjectId(creator_id) for creator_id in creator_ids]}}).to_list(None)
    )

    return creators
