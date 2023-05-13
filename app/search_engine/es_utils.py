from graphql import GraphQLError

from ..search_engine.elasticsearch import get_es


def _prepare_mongo_doc_for_es(doc: dict) -> dict:
    """
    Prepare a MongoDB document for indexing in Elasticsearch.

    Args:
        doc: The MongoDB document.

    Returns:
        dict: The prepared document.
    """
    if "_id" not in doc:
        return doc

    prepared_doc = doc.copy()
    prepared_doc["mongo_id"] = str(prepared_doc.pop("_id"))
    return prepared_doc


async def es_create_index(index_name: str):
    """
    Create an index in Elasticsearch.

    Args:
        index_name (str): The name of the index to create.
    """
    async for es in get_es():
        await es.indices.create(index=index_name)


async def es_index_document(index_name: str, doc_id: str, doc):
    """
    Index a document in Elasticsearch.

    Args:
        index_name (str): The name of the index to which the document will be indexed.
        doc_id (str): The ID of the document.
        doc: The document to index.
    """
    prepared_doc = _prepare_mongo_doc_for_es(doc)
    async for es in get_es():
        await es.index(index=index_name, id=doc_id, document=prepared_doc)


async def es_update_document(index_name: str, doc_id: str, doc):
    """
    Update a document in Elasticsearch.

    Args:
        index_name (str): The name of the index where the document is located.
        doc_id (str): The ID of the document.
        doc: The updated document.
    """
    prepared_doc = _prepare_mongo_doc_for_es(doc)
    async for es in get_es():
        await es.update(index=index_name, id=doc_id, doc=prepared_doc)


async def es_delete_document(index_name: str, doc_id: str):
    """
    Delete a document from Elasticsearch.

    Args:
        index_name (str): The name of the index where the document is located.
        doc_id (str): The ID of the document to delete.
    """
    async for es in get_es():
        await es.delete(index=index_name, id=doc_id)


async def es_search(index_name: str, search_text: str, page: int, per_page: int) -> dict:
    """
    Search for documents in a specified Elasticsearch index using the given search text and pagination parameters.

    Args:
        index_name (str): The name of the Elasticsearch index to search in.
        search_text (str): The text to search for in the index.
        page (int): The page number of the search results.
        per_page (int): The number of search results per page.

    Returns:
        dict: A dictionary containing the search results metadata and the actual results as a list of dictionaries.
    """
    if page < 1:
        raise GraphQLError(message="Page must be greater than or equal to 1.")
    if per_page < 1:
        raise GraphQLError(message="Per page must be greater than or equal to 1.")

    async for es in get_es():
        return await es.search(
            index=index_name,
            query={"bool": {"must": {"query_string": {"query": search_text}}}},
            from_=(page - 1) * per_page,
            size=per_page,
        )
