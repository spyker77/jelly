import pytest

pytestmark = pytest.mark.asyncio


async def test_graphql_query_get_creator(add_test_creator, test_creator_data, test_client):
    await add_test_creator
    test_email = test_creator_data["email"]
    get_creator = f"""
        {{
            getCreator(email: "{test_email}") {{
                email
                assets {{
                    type
                    createdAt
                }}
            }}
        }}
    """
    async for client in test_client:
        response = await client.post("/graphql", json={"query": get_creator})
        assert response.status_code == 200
        assert "errors" not in response.json()
        assert response.json()["data"]["getCreator"]["email"] == test_email


async def test_graphql_query_get_creator_assets(add_test_creator, test_creator_data, test_client):
    await add_test_creator
    test_email = test_creator_data["email"]
    test_type = "Test Type"
    async for client in test_client:
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

        get_creator = f"""
            {{
                getCreator(email: "{test_email}") {{
                    email
                    assets {{
                        type
                        createdAt
                    }}
                }}
            }}
        """
        response = await client.post("/graphql", json={"query": get_creator})
        assert response.status_code == 200
        assert "errors" not in response.json()
        assert response.json()["data"]["getCreator"]["assets"][0]["type"] == test_type


async def test_graphql_query_get_non_existing_creator(test_client):
    test_email = "non_existing@example.com"
    get_creator = f"""
    query {{
        getCreator(email: "{test_email}") {{
            email
            assets {{
                type
                createdAt
            }}
        }}
    }}
    """
    async for client in test_client:
        response = await client.post("/graphql", json={"query": get_creator})
        assert response.status_code == 200
        assert "errors" in response.json()
        assert response.json()["errors"][0]["message"] == "Creator does not exist."


async def test_graphql_query_search_creators(add_test_creator, test_creator_data, test_client):
    await add_test_creator
    test_email = test_creator_data["email"]
    search_creators = f"""
    {{
        searchCreators(searchText: "{test_email}", page: 1, perPage: 10) {{
            email
            assets {{
                type
                createdAt
            }}
        }}
    }}
    """
    async for client in test_client:
        response = await client.post("/graphql", json={"query": search_creators})
        assert response.status_code == 200
        assert "errors" not in response.json()
        assert len(response.json()["data"]["searchCreators"]) == 1
        assert response.json()["data"]["searchCreators"][0]["email"] == test_email


@pytest.mark.parametrize(
    "page, per_page, expected_error",
    [
        (0, 10, "Page must be greater than or equal to 1."),
        (1, 0, "Per page must be greater than or equal to 1."),
    ],
)
async def test_graphql_query_search_creators_with_page_errors(
    add_test_creator,
    test_creator_data,
    test_client,
    page,
    per_page,
    expected_error,
):
    await add_test_creator
    test_email = test_creator_data["email"]
    search_creators = f"""
    {{
        searchCreators(searchText: "{test_email}", page: {page}, perPage: {per_page}) {{
            email
            assets {{
                type
                createdAt
            }}
        }}
    }}
    """
    async for client in test_client:
        response = await client.post("/graphql", json={"query": search_creators})
        assert response.status_code == 200
        assert "errors" in response.json()
        assert response.json()["errors"][0]["message"] == expected_error
