from datetime import datetime
from typing import Literal

from elasticsearch_dsl import Date, Document, Nested, Text

from .asset import Asset


class Creator(Document):
    username = Text(required=True)
    email = Text()
    signed_up = Date(default_timezone="UTC")
    assets = Nested(Asset)

    @classmethod
    def _matches(cls, hit) -> Literal[False]:
        return False

    class Index:
        name = "creator"

    def add_asset(self, type) -> None:
        self.assets.append(Asset(type=type, created_at=datetime.now()))

    def save(self, **kwargs):
        self.signed_up = datetime.now()
        return super().save(**kwargs)
