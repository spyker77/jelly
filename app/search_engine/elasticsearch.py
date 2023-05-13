from elasticsearch import AsyncElasticsearch

from ..config import get_settings

settings = get_settings()


async def get_es() -> AsyncElasticsearch:
    async with AsyncElasticsearch(hosts=[settings.elasticsearch_url]) as client:
        yield client
