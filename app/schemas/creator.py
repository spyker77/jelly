from datetime import datetime

import strawberry

from ..schemas.asset import AssetSchema


@strawberry.type
class CreatorSchema:
    """
    A Strawberry GraphQL type representing a creator with their associated assets.
    """

    _id: str
    username: str
    email: str
    signed_up: datetime
    assets: list[AssetSchema]

    def __post_init__(self):
        """
        Converts the `assets` field from a list of dictionaries to a list of
        `AssetSchema` instances after the object is initialized. This step is
        necessary because the data passed to the constructor might not be
        instances of `AssetSchema` when creating the 'CreatorSchema' object.
        """
        self.assets = [AssetSchema(**asset) for asset in self.assets]

    @strawberry.field
    def assets_resolver(self, info) -> list[AssetSchema]:
        """
        Returns the list of `AssetSchema` instances associated with the creator.

        The assets_resolver field method is used in the GraphQL query to resolve
        the `assets` field of the `CreatorSchema` type. This field resolver
        method returns the already processed list of 'AssetSchema' instances,
        which was converted in the `__post_init__` method.
        """
        return self.assets
