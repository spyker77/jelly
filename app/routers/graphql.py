from typing import Any

import strawberry
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from strawberry.fastapi import GraphQLRouter

from ..database.mongodb import get_db
from ..graphql.mutation import Mutation
from ..graphql.query import Query


async def get_context(db: AsyncIOMotorDatabase = Depends(get_db)) -> dict[str, Any]:
    return {"db": db}


schema = strawberry.Schema(query=Query, mutation=Mutation)

router = GraphQLRouter(schema, path="/graphql", context_getter=get_context)
