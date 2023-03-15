import strawberry
from strawberry.fastapi import GraphQLRouter

from .mutation import Mutation
from .query import Query

schema = strawberry.Schema(query=Query, mutation=Mutation)

router = GraphQLRouter(schema, path="/graphql")
