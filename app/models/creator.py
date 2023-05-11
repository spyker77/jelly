from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field

from .asset import AssetModel


class CreatorModel(BaseModel):
    """
    A Pydantic model representing a creator with their associated assets.
    """

    _id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    username: str
    email: EmailStr
    signed_up: datetime = Field(default_factory=datetime.utcnow)
    assets: list[AssetModel] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
