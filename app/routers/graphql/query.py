import strawberry

from app.schemas import AssetSchema, CreatorSchema, get_assets_for_creator, get_creators


@strawberry.type
class Query:
    creators: list[CreatorSchema] = strawberry.field(resolver=get_creators)
    assets: list[AssetSchema] = strawberry.field(resolver=get_assets_for_creator)
