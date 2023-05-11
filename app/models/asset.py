from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, Field


class AssetModel(BaseModel):
    """
    A Pydantic model representing an asset with its type and creation date.
    """

    type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
