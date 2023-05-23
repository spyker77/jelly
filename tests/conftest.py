import pytest
from elasticsearch import AsyncElasticsearch, NotFoundError
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.database.mongodb import get_db
from app.main import create_application
from app.models.creator import CreatorModel
from app.search_engine.elasticsearch import get_es
from app.settings import get_settings

pytestmark = pytest.mark.asyncio

settings = get_settings()


async def get_test_db() -> AsyncIOMotorDatabase:
    mongo_client = AsyncIOMotorClient(settings.mongodb_url)
    return mongo_client[settings.mongodb_database]


async def get_test_es() -> AsyncElasticsearch:
    es_client = AsyncElasticsearch(hosts=[settings.elasticsearch_url])
    return es_client


app = create_application()
app.dependency_overrides[get_db] = get_test_db
app.dependency_overrides[get_es] = get_test_es


async def data_cleanup(db: AsyncIOMotorDatabase, es: AsyncElasticsearch):
    try:
        await es.indices.delete(index="creator")
    except NotFoundError:
        pass
    finally:
        await db["creators"].drop()


@pytest.fixture(autouse=True)
async def prepare_test_state():
    test_db = await get_test_db()
    test_es = await get_test_es()
    await data_cleanup(test_db, test_es)
    yield
    await test_db.close()
    await test_es.close()


@pytest.fixture
async def test_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        yield ac


@pytest.fixture
def test_creator_data(faker) -> dict[str, str]:
    return CreatorModel(username=faker.user_name(), email=faker.email()).dict()


@pytest.fixture
async def add_test_creator(test_creator_data, test_client):
    test_email = test_creator_data["email"]
    test_username = test_creator_data["username"]
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
    async for client in test_client:
        await client.post("/graphql", json={"query": mutation})
