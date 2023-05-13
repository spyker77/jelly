import pytest

from .conftest import add_test_creator

pytestmark = pytest.mark.asyncio


async def test_graphql_mutation_add_creator(test_creator_data, test_client):
    test_email = test_creator_data["email"]
    test_username = test_creator_data["username"]
    add_creator = f"""
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
        response = await client.post("/graphql", json={"query": add_creator})
        assert response.status_code == 200
        assert "errors" not in response.json()
        assert response.json()["data"]["addCreator"]["email"] == test_email


async def test_graphql_mutation_add_existing_creator(test_creator_data, test_client):
    test_email = test_creator_data["email"]
    test_username = test_creator_data["username"]
    add_creator = f"""
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
        await add_test_creator(test_creator_data, client)

        response = await client.post("/graphql", json={"query": add_creator})
        assert response.status_code == 200
        assert "errors" in response.json()
        assert response.json()["errors"][0]["message"] == "Creator already exists."


async def test_graphql_mutation_add_asset_to_creator(test_creator_data, test_client):
    test_email = test_creator_data["email"]
    test_type = "Test Type"
    add_asset_to_creator = f"""
    mutation {{
        addAssetToCreator(type: "{test_type}", email: "{test_email}") {{
            type
            createdAt
        }}
    }}
    """
    async for client in test_client:
        await add_test_creator(test_creator_data, client)

        response = await client.post("/graphql", json={"query": add_asset_to_creator})
        assert response.status_code == 200
        assert "errors" not in response.json()
        assert response.json()["data"]["addAssetToCreator"]["type"] == test_type


async def test_graphql_mutation_add_asset_to_non_existing_creator(test_client):
    test_email = "non_existing@example.com"
    test_type = "Test Type"
    add_asset_to_creator = f"""
    mutation {{
        addAssetToCreator(type: "{test_type}", email: "{test_email}") {{
            type
            createdAt
        }}
    }}
    """
    async for client in test_client:
        response = await client.post("/graphql", json={"query": add_asset_to_creator})
        assert response.status_code == 200
        assert "errors" in response.json()
        assert response.json()["errors"][0]["message"] == "Creator does not exist."


async def test_graphql_mutation_remove_asset_from_creator(test_creator_data, test_client):
    test_email = test_creator_data["email"]
    test_type = "Test Type"
    async for client in test_client:
        await add_test_creator(test_creator_data, client)

        add_asset_to_creator = f"""
        mutation {{
            addAssetToCreator(type: "{test_type}", email: "{test_email}") {{
                type
                createdAt
            }}
        }}
        """
        response = await client.post("/graphql", json={"query": add_asset_to_creator})
        assert response.status_code == 200
        assert "errors" not in response.json()

        remove_asset = f"""
        mutation {{
            removeAssetFromCreator(type: "{test_type}", email: "{test_email}") {{
                type
                createdAt
            }}
        }}
        """
        response = await client.post("/graphql", json={"query": remove_asset})
        assert response.status_code == 200
        assert "errors" not in response.json()
        assert response.json()["data"]["removeAssetFromCreator"]["type"] == test_type


async def test_graphql_mutation_remove_asset_from_non_existing_creator(test_client):
    test_email = "Test Type"
    test_type = "non_existing@example.com"
    remove_asset_from_creator = f"""
    mutation {{
        removeAssetFromCreator(type: "{test_type}", email: "{test_email}") {{
            type
            createdAt
        }}
    }}
    """
    async for client in test_client:
        response = await client.post("/graphql", json={"query": remove_asset_from_creator})
        assert response.status_code == 200
        assert "errors" in response.json()
        assert response.json()["errors"][0]["message"] == "Creator does not exist."


async def test_graphql_mutation_remove_non_existing_asset_from_creator(test_creator_data, test_client):
    test_email = test_creator_data["email"]
    test_type = "No Such Type"
    remove_asset_from_creator = f"""
    mutation {{
        removeAssetFromCreator(type: "{test_type}", email: "{test_email}") {{
            type
            createdAt
        }}
    }}
    """
    async for client in test_client:
        await add_test_creator(test_creator_data, client)

        response = await client.post("/graphql", json={"query": remove_asset_from_creator})
        assert response.status_code == 200
        assert "errors" in response.json()
        assert response.json()["errors"][0]["message"] == "Asset does not exist."


async def test_graphql_mutation_delete_creator(test_creator_data, test_client):
    test_email = test_creator_data["email"]
    delete_creator = f"""
    mutation {{
        deleteCreator(email: "{test_email}") {{
            email
        }}
    }}
    """
    async for client in test_client:
        await add_test_creator(test_creator_data, client)

        response = await client.post("/graphql", json={"query": delete_creator})
        assert response.status_code == 200
        assert "errors" not in response.json()
        assert response.json()["data"]["deleteCreator"]["email"] == test_email


async def test_graphql_mutation_delete_non_existing_creator(test_client):
    test_email = "non_existing@example.com"
    delete_creator = f"""
    mutation {{
        deleteCreator(email: "{test_email}") {{
            email
            assets {{
                type
                createdAt
            }}
        }}
    }}
    """
    async for client in test_client:
        response = await client.post("/graphql", json={"query": delete_creator})
        assert response.status_code == 200
        assert "errors" in response.json()
        assert response.json()["errors"][0]["message"] == "Creator does not exist."
