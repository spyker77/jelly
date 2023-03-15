from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


def test_graphql_path_works():
    response = client.get("/graphql")
    assert response.status_code == 200
