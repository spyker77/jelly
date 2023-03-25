import strawberry

from app.schemas.asset import AssetSchema


@strawberry.type
class CreatorSchema:
    username: str
    email: str
    signed_up: str | None
    assets: list[AssetSchema]
