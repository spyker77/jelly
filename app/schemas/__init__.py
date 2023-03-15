from typing import Optional

import strawberry


@strawberry.type
class AssetSchema:
    type: str
    creator: Optional["CreatorSchema"] = None


async def get_assets_for_creator(root) -> list[AssetSchema]:
    """Query to get assets for a particular creator. Example of the GraphQL document:

    ```graphql
    query {
        assets {
            type
            creator {
                username
                email
            }
        }
    }
    ```

    Returns:
        list[AssetSchema]: Data about assets of the creator.
    """
    # TODO: replace it with the actual query.
    assets = [
        AssetSchema(type="YouTube Shorts", creator=CreatorSchema(username="MiCrich", email="mi_crich@mail.com")),
        AssetSchema(type="Instagram Reels"),
        AssetSchema(type="TikTok Videos"),
    ]
    return assets


@strawberry.type
class CreatorSchema:
    username: str
    email: str
    assets: list[AssetSchema] = strawberry.field(resolver=get_assets_for_creator)


async def get_creators(root) -> list[CreatorSchema]:
    """Query to get all creators. Example of the GraphQL document:

    ```graphql
    query {
        creators {
            email
            username
            assets {
                type
            }
        }
    }
    ```

    Returns:
        list[CreatorSchema]:: Data about creators and the related assets.
    """
    # TODO: replace it with the actual query.
    creators = [
        CreatorSchema(username="MiCrich", email="mi_crich@mail.com"),
        CreatorSchema(username="LizShu", email="lizzy@mail.com"),
        CreatorSchema(username="MrBeast", email="beast@email.com"),
    ]
    return creators
