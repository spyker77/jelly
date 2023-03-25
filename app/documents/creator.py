from datetime import datetime

from elasticsearch_dsl import Date, Document, Keyword, Nested, Text

from .asset import Asset


class Creator(Document):
    username = Text(fields={"keyword": Keyword()})
    email = Text(fields={"keyword": Keyword()}, required=True)
    signed_up = Date(default_timezone="UTC")
    assets = Nested(Asset)

    class Index:
        name = "creator"

    def add_asset(self, type) -> None:
        self.assets.append(Asset(type=type))
        self.save()

    def save(self, **kwargs):
        self.signed_up = datetime.now()
        return super().save(**kwargs)
