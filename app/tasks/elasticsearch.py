from elasticsearch import AsyncElasticsearch

from ..search_engine.manager import ElasticsearchManager


async def es_create_index(ctx, index_name: str):
    """
    Create an index in Elasticsearch.

    Args:
        index_name (str): The name of the index to create.
    """
    es: AsyncElasticsearch = ctx["es"]
    await ElasticsearchManager(es).create_index(index_name=index_name)


async def es_index_document(ctx, index_name: str, doc_id: str, doc: dict):
    """
    Index a document in Elasticsearch.

    Args:
        index_name (str): The name of the index to which the document will be indexed.
        doc_id (str): The ID of the document.
        doc (dict): The document to index.
    """
    es: AsyncElasticsearch = ctx["es"]
    await ElasticsearchManager(es).index_document(index_name=index_name, doc_id=doc_id, doc=doc)


async def es_update_document(ctx, index_name: str, doc_id: str, doc: dict):
    """
    Update a document in Elasticsearch.

    Args:
        index_name (str): The name of the index where the document is located.
        doc_id (str): The ID of the document.
        doc (dict): The updated document.
    """
    es: AsyncElasticsearch = ctx["es"]
    await ElasticsearchManager(es).update_document(index_name=index_name, doc_id=doc_id, doc=doc)


async def es_delete_document(ctx, index_name: str, doc_id: str):
    """
    Delete a document from Elasticsearch.

    Args:
        index_name (str): The name of the index where the document is located.
        doc_id (str): The ID of the document to delete.
    """
    es: AsyncElasticsearch = ctx["es"]
    await ElasticsearchManager(es).delete_document(index_name=index_name, doc_id=doc_id)
