import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_non_existent_path_returns_404_status_code():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response = await ac.get("/non-existent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_graphql_path_returns_200_status_code():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response = await ac.get("/graphql")
    assert response.status_code == 200
