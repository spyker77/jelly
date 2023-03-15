from datetime import datetime

from elasticsearch_dsl import Date, InnerDoc, Text


class Asset(InnerDoc):
    type = Text(required=True)
    created_at = Date(default_timezone="UTC")

    def save(self, **kwargs):
        self.created_at = datetime.now()
        return super().save(**kwargs)
