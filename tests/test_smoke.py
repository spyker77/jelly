import pytest

pytestmark = pytest.mark.asyncio


async def test_graphql_path_returns_200_status_code(test_client):
    async for client in test_client:
        response = await client.get("/graphql")
        assert response.status_code == 200


async def test_non_existent_path_returns_404_status_code(test_client):
    async for client in test_client:
        response = await client.get("/non-existent")
        assert response.status_code == 404
