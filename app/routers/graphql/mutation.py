import strawberry
from elasticsearch_dsl import Search

from app.documents.creator import Creator
from app.schemas import AssetSchema, CreatorSchema


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
        instance = Creator(username=username, email=email)
        instance.save()
        return CreatorSchema(username=instance.username, email=instance.email)

    @strawberry.mutation
    async def add_asset_to_creator(self, type: str, email: str) -> AssetSchema:
        """Mutation to add asset to the creator. Example of the GraphQL document:

        ```graphql
        mutation {
            addAssetToCreator(type: "New Fancy Platform", email: "cool@email.com") {
                type
                creator {
                    username
                    email
                }
            }
        }
        ```

        Args:
            type (str): Type of a new asset.
            email (str): Email of the creator.

        Returns:
            AssetSchema: Data about the creator and related assets.
        """

        query = Search(index="creator").query("match", email=email)
        response = query.execute()

        if creator := Creator.get(id=response[0].meta.id):
            creator.add_asset(type=type)

        return AssetSchema(type=type, creator=creator)

    @strawberry.mutation
    async def delete_creator(self, email: str) -> CreatorSchema:
        """Mutation to delete creator. Example of the GraphQL document:

        ```graphql
        mutation {
            deleteCreator(email: "cool@email.com") {
                username
                email
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

        query = Search(index="creator").query("match", email=email)
        response = query.execute()

        if creator := Creator.get(id=response[0].meta.id):
            creator.delete()

        return CreatorSchema(username=response[0].username, email=response[0].email)
