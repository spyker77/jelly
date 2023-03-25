import strawberry

from app.documents.creator import Creator
from app.schemas.asset import AssetSchema
from app.schemas.creator import CreatorSchema


@strawberry.type
class Query:
    @strawberry.field(name="creator")
    async def get_creator(self, email: str) -> list[CreatorSchema]:
        """Query to get creator. Example of the GraphQL document:

        ```graphql
        query {
            creator(email: "cool@email.com") {
                email
                username
                signedUp
                assets {
                    type
                }
            }
        }
        ```

        Returns:
            list[CreatorSchema]:: Data about creator and the related assets.
        """
        response = Creator.search().query("match", email=email).execute()
        creators = [
            CreatorSchema(
                username=hit["_source"]["username"],
                email=hit["_source"]["email"],
                signed_up=hit["_source"]["signed_up"],
                assets=hit["_source"]["assets"] if "assets" in hit["_source"] else [],
            )
            for hit in response.hits.hits
        ]
        return creators

    @strawberry.field(name="creatorAssets")
    async def get_assets_for_creator(self, email: str) -> list[AssetSchema]:
        """Query to get assets for a particular creator. Example of the GraphQL document:

        ```graphql
        query {
            creatorAssets(email: "cool@email.com") {
                type
            }
        }
        ```

        Returns:
            list[AssetSchema]: Data about assets of the creator.
        """
        response = Creator.search().query("match", email=email).execute()
        assets = [AssetSchema(type=asset["type"]) for hit in response.hits.hits for asset in hit["_source"]["assets"]]
        return assets
