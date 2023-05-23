from elasticsearch import AsyncElasticsearch

from ..settings import get_settings

settings = get_settings()

es_client = None


async def get_es() -> AsyncElasticsearch:
    global es_client
    if es_client is None:
        es_client = AsyncElasticsearch(hosts=[settings.elasticsearch_url])
    return es_client


async def close_es():
    global es_client
    if es_client is not None:
        await es_client.close()
        es_client = None
