import strawberry
from graphql import GraphQLError
from motor.motor_asyncio import AsyncIOMotorDatabase
from strawberry.types import Info

from ..models.asset import AssetModel
from ..models.creator import CreatorModel
from ..schemas.asset import AssetSchema
from ..schemas.creator import CreatorSchema
from ..services.creator import create_creator, delete_creator_by_email, get_creator_by_email, update_creator_assets


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def add_creator(self, info: Info, username: str, email: str) -> CreatorSchema:
        """Mutation to add creator. Example of the GraphQL document:

        ```graphql
        mutation {
            addCreator(username: "CoolUser", email: "cool@email.com") {
                Id
                username
                email
                signedUp
                assets {
                    type
                    createdAt
                }
            }
        }
        ```

        Args:
            username (str): Username of the creator.
            email (str): The email of the creator.

        Returns:
            CreatorSchema: Data about the creator and related assets.
        """
        db: AsyncIOMotorDatabase = info.context["db"]

        creator = await get_creator_by_email(db, email)
        if creator:
            raise GraphQLError(message="Creator already exists.")

        new_creator = CreatorModel(username=username, email=email).dict(by_alias=True)
        result = await create_creator(db, new_creator)

        return CreatorSchema(**result)

    @strawberry.mutation
    async def add_asset_to_creator(self, info: Info, type: str, email: str) -> AssetSchema:
        """
        Mutation to add asset to the creator. Example of the GraphQL document:

        ```graphql
        mutation {
            addAssetToCreator(type: "New Fancy Platform", email: "cool@email.com") {
                type
                createdAt
            }
        }
        ```

        Args:
            type (str): Type of a new asset.
            email (str): The email of the creator.

        Returns:
            AssetSchema: Data about assets of the creator.
        """
        db: AsyncIOMotorDatabase = info.context["db"]

        creator = await get_creator_by_email(db, email)
        if not creator:
            raise GraphQLError(message="Creator does not exist.")

        new_asset = AssetModel(type=type).dict()
        creator_assets = creator.get("assets", [])
        creator_assets.append(new_asset)

        await update_creator_assets(db, email, creator_assets)

        return AssetSchema(**new_asset)

    @strawberry.mutation
    async def remove_asset_from_creator(self, info: Info, type: str, email: str) -> AssetSchema:
        """
        Mutation to remove an asset from the creator. Example of the GraphQL document:

        ```graphql
        mutation {
            removeAssetFromCreator(type: "New Fancy Platform", email: "cool@email.com") {
                type
                createdAt
            }
        }
        ```

        Args:
            type (str): Type of the asset to remove.
            email (str): The email of the creator.

        Returns:
            AssetSchema: Data about the removed asset.
        """
        db: AsyncIOMotorDatabase = info.context["db"]

        creator = await get_creator_by_email(db, email)
        if not creator:
            raise GraphQLError(message="Creator does not exist.")

        creator_assets = creator.get("assets", [])
        asset_to_remove = None

        for index, asset in enumerate(creator_assets):
            if asset["type"] == type:
                asset_to_remove = creator_assets.pop(index)
                break

        if asset_to_remove is None:
            raise GraphQLError(message="Asset does not exist.")

        await update_creator_assets(db, email, creator_assets)

        return AssetSchema(**asset_to_remove)

    @strawberry.mutation
    async def delete_creator(self, info: Info, email: str) -> CreatorSchema:
        """Mutation to delete creator. Example of the GraphQL document:

        ```graphql
        mutation {
            deleteCreator(email: "cool@email.com") {
                Id
                username
                email
                signedUp
                assets {
                    type
                    createdAt
                }
            }
        }
        ```

        Args:
            email (str): The email of the creator.

        Returns:
            CreatorSchema: Data about the creator that has just been deleted.
        """
        db: AsyncIOMotorDatabase = info.context["db"]

        creator = await get_creator_by_email(db, email)
        if not creator:
            raise GraphQLError(message="Creator does not exist.")

        deleted_creator = await delete_creator_by_email(db, email)

        return CreatorSchema(**deleted_creator)
