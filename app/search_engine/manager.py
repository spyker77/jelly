import logging

from elasticsearch import AsyncElasticsearch, ConnectionError, RequestError
from graphql import GraphQLError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger("gunicorn.error")


class ElasticsearchManager:
    """
    A class that encapsulates Elasticsearch operations like creating an index,
    indexing a document, updating a document, deleting a document, and searching.
    """

    def __init__(self, es: AsyncElasticsearch):
        self.es = es

    @staticmethod
    def _prepare_mongo_doc_for_es(doc: dict) -> dict:
        """
        Prepare a MongoDB document for indexing in Elasticsearch.

        Args:
            doc (dict): The MongoDB document.

        Returns:
            dict: The prepared document.
        """
        if "_id" not in doc:
            return doc

        prepared_doc = doc.copy()
        prepared_doc["mongo_id"] = str(prepared_doc.pop("_id"))
        return prepared_doc

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(ConnectionError),
    )
    async def create_index(self, index_name: str):
        """
        Create an index in Elasticsearch.

        Args:
            index_name (str): The name of the index to create.
        """
        if not await self.es.indices.exists(index=index_name):
            try:
                await self.es.indices.create(index=index_name)
            except RequestError as e:
                if "resource_already_exists_exception" in str(e):  # due to a race condition
                    logger.warning(f"Index {index_name} already exists, skipping.")
                    pass
                else:
                    raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(ConnectionError),
    )
    async def index_document(self, index_name: str, doc_id: str, doc: dict):
        """
        Index a document in Elasticsearch.

        Args:
            index_name (str): The name of the index to which the document will be indexed.
            doc_id (str): The ID of the document.
            doc (dict): The document to index.
        """
        prepared_doc = self._prepare_mongo_doc_for_es(doc)
        await self.es.index(index=index_name, id=doc_id, document=prepared_doc)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(ConnectionError),
    )
    async def update_document(self, index_name: str, doc_id: str, doc: dict):
        """
        Update a document in Elasticsearch.

        Args:
            index_name (str): The name of the index where the document is located.
            doc_id (str): The ID of the document.
            doc (dict): The updated document.
        """
        prepared_doc = self._prepare_mongo_doc_for_es(doc)
        await self.es.update(index=index_name, id=doc_id, doc=prepared_doc)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(ConnectionError),
    )
    async def delete_document(self, index_name: str, doc_id: str):
        """
        Delete a document from Elasticsearch.

        Args:
            index_name (str): The name of the index where the document is located.
            doc_id (str): The ID of the document to delete.
        """
        await self.es.delete(index=index_name, id=doc_id)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(ConnectionError),
    )
    async def search(self, index_name: str, search_text: str, page: int, per_page: int) -> dict:
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

        result = await self.es.search(
            index=index_name,
            query={"bool": {"must": {"query_string": {"query": search_text}}}},
            from_=(page - 1) * per_page,
            size=per_page,
        )

        return result
