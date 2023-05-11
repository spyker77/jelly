from datetime import datetime

import strawberry


@strawberry.type
class AssetSchema:
    """
    A Strawberry GraphQL type representing an asset with its type and creation date.
    """

    type: str
    created_at: datetime
