import strawberry
from elasticsearch_dsl import Q

from app.documents.creator import Creator
from app.schemas.asset import AssetSchema
from app.schemas.creator import CreatorSchema


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def add_creator(self, username: str, email: str) -> CreatorSchema:
        """Mutation to add creator. Example of the GraphQL document:

        ```graphql
        mutation {
            addCreator(username: "CoolUser", email: "cool@email.com") {
                username
                email
                signedUp
                assets {
                    type
                }
            }
        }
        ```

        Args:
            username (str): Username of the creator.
            email (str): Email of the creator.

        Returns:
            CreatorSchema: Data about the creator and related assets.
        """
        query = Q("bool", must=[Q("match", username=username), Q("match", email=email)])
        response = Creator.search().query(query).execute()

        if response.hits.total.value > 0:
            raise Exception("Creator already exists.")

        instance = Creator(username=username, email=email)
        instance.save()

        return CreatorSchema(
            username=instance.username,
            email=instance.email,
            signed_up=instance.signed_up,
            assets=instance.assets,
        )

    @strawberry.mutation
    async def add_asset_to_creator(self, type: str, email: str) -> AssetSchema:
        """Mutation to add asset to the creator. Example of the GraphQL document:

        ```graphql
        mutation {
            addAssetToCreator(type: "New Fancy Platform", email: "cool@email.com") {
                type
            }
        }
        ```

        Args:
            type (str): Type of a new asset.
            email (str): Email of the creator.

        Returns:
            AssetSchema: Data about the creator and related assets.
        """
        response = Creator.search().query("match", email=email).execute()

        creator = Creator.get(id=response[0].meta.id)
        if not creator:
            raise Exception("Creator does not exist.")

        creator.add_asset(type=type)

        return AssetSchema(type=type)

    @strawberry.mutation
    async def delete_creator(self, email: str) -> CreatorSchema:
        """Mutation to delete creator. Example of the GraphQL document:

        ```graphql
        mutation {
            deleteCreator(email: "cool@email.com") {
                username
                email
                signedUp
                assets {
                    type
                }
            }
        }
        ```

        Args:
            email (str): Email of the creator.

        Returns:
            CreatorSchema: Data about the creator that has just been deleted.
        """
        response = Creator.search().query("match", email=email).execute()

        creator = Creator.get(id=response[0].meta.id)
        if not creator:
            raise Exception("Creator does not exist.")

        creator.delete()

        return CreatorSchema(
            username=creator.username,
            email=creator.email,
            signed_up=creator.signed_up,
            assets=creator.assets,
        )
