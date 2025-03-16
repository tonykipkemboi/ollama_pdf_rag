import logging
from typing import List, Optional

import chromadb
from chromadb.config import Settings
from chromadb.errors import UniqueConstraintError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class VectorStore:
    """Manages vector database operations using the updated ChromaDB configuration."""

    def __init__(
        self, collection_name: str = "local-rag", persist_directory: str = "db/"
    ):
        self.collection_name = collection_name
        self.client = chromadb.Client(
            Settings(
                persist_directory=persist_directory,
                is_persistent=True,
                anonymized_telemetry=False,
            )
        )
        try:
            self.collection = self.client.create_collection(name=self.collection_name)
            logger.info(f"Created new collection '{self.collection_name}'")
        except UniqueConstraintError:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Using existing collection '{self.collection_name}'")

    def create_vector_db(
        self,
        documents: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
    ):
        try:
            logger.info("Adding documents to the vector database collection")
            if metadatas is None:
                metadatas = [{} for _ in documents]
            if ids is None:
                ids = [f"id_{i}" for i in range(len(documents))]
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
            return self.collection
        except Exception as e:
            logger.error(f"Error creating vector database: {e}")
            raise

    def delete_collection(self) -> None:
        try:
            logger.info(f"Deleting collection '{self.collection_name}'")
            self.client.delete_collection(name=self.collection_name)
            self.collection = None
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise
