import asyncio

import pytest
from elasticsearch import NotFoundError
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import Settings, get_settings
from app.database.mongodb import get_db
from app.main import create_application
from app.models.creator import CreatorModel
from app.search_engine.elasticsearch import get_es

pytestmark = pytest.mark.asyncio


def get_settings_override() -> Settings:
    return Settings(mongodb_database="test_db")


overridden_settings = get_settings_override()


async def get_test_db() -> AsyncIOMotorDatabase:
    client = AsyncIOMotorClient(overridden_settings.mongodb_url)
    db = client[overridden_settings.mongodb_database]
    return db


app = create_application()
app.dependency_overrides[get_settings] = get_settings_override
app.dependency_overrides[get_db] = get_test_db


@pytest.fixture
async def test_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        yield ac


async def data_cleanup():
    async for es in get_es():
        db = await get_test_db()
        await db["creators"].drop()
        try:
            await es.indices.delete(index="creator")
        except NotFoundError:
            pass


@pytest.fixture(autouse=True)
def prepare_test_state():
    asyncio.run(data_cleanup())
    yield


@pytest.fixture
def test_creator_data(faker) -> dict[str, str]:
    return CreatorModel(username=faker.user_name(), email=faker.email()).dict()


async def add_test_creator(test_creator, test_client):
    test_email = test_creator["email"]
    test_username = test_creator["username"]
    mutation = f"""
    mutation {{
        addCreator(username: "{test_username}", email: "{test_email}") {{
            email
            assets {{
                type
                createdAt
            }}
        }}
    }}
    """
    await test_client.post("/graphql", json={"query": mutation})
    async for es in get_es():
        await es.indices.refresh(index="_all")
