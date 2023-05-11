import strawberry
from graphql import GraphQLError
from motor.motor_asyncio import AsyncIOMotorDatabase
from strawberry.types import Info

from ..schemas.creator import CreatorSchema
from ..services.creator import get_creator_by_email, search_creators


@strawberry.type
class Query:
    @strawberry.field
    async def get_creator(self, info: Info, email: str) -> CreatorSchema:
        """
        Query to get creator by email. Example of the GraphQL document:

        ```graphql
        query {
            getCreator(email: "cool@email.com") {
                Id
                email
                username
                signedUp
                assets {
                    type
                    createdAt
                }
            }
        }
        ```

        Args:
            email (str): The email of the creator

        Returns:
            CreatorSchema: Data about creator and the related assets.
        """
        db: AsyncIOMotorDatabase = info.context["db"]

        creator = await get_creator_by_email(db, email)
        if not creator:
            raise GraphQLError(message="Creator does not exist.")

        return CreatorSchema(**creator)

    @strawberry.field
    async def search_creators(
        self,
        info: Info,
        search_text: str,
        page: int = 1,
        per_page: int = 10,
    ) -> list[CreatorSchema]:
        """
        Query to search creators based on the search text. Example of the GraphQL document:

        ```graphql
        query {
            searchCreators(searchText: "New Fancy Platform", page: 1, perPage: 10) {
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
            search_text (str): The text to search for in the creators' data.
            page (int): The page number of the search results.
            per_page (int): The number of search results per page.

        Returns:
            list[CreatorSchema]: A list of creators matching the search text along with their related assets.
        """
        db: AsyncIOMotorDatabase = info.context["db"]

        creators = await search_creators(db, search_text, page, per_page)

        return [CreatorSchema(**creator) for creator in creators]
