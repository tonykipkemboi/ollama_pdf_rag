"""Vector embeddings and database functionality."""
import logging
from typing import List
from pathlib import Path
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

logger = logging.getLogger(__name__)

class VectorStore:
    """Manages vector embeddings and database operations."""

    def __init__(self, embedding_model: str = "nomic-embed-text", persist_directory: str = "data/vectors"):
        self.embeddings = OllamaEmbeddings(model=embedding_model)
        self.persist_directory = persist_directory
        self.vector_db = None
        # Ensure persist directory exists
        Path(persist_directory).mkdir(parents=True, exist_ok=True)

    def create_vector_db(self, documents: List, collection_name: str = "local-rag") -> Chroma:
        """Create vector database from documents with persistence."""
        try:
            logger.info(f"Creating vector database with collection: {collection_name}")
            logger.info(f"Persisting to: {self.persist_directory}")
            logger.info(f"Number of documents: {len(documents)}")

            self.vector_db = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=collection_name,
                persist_directory=self.persist_directory
            )

            logger.info(f"✅ Vector database created successfully with {len(documents)} documents")
            return self.vector_db
        except Exception as e:
            logger.error(f"❌ Error creating vector database: {e}")
            raise
    
    def delete_collection(self) -> None:
        """Delete vector database collection."""
        if self.vector_db:
            try:
                logger.info("Deleting vector database collection")
                self.vector_db.delete_collection()
                self.vector_db = None
            except Exception as e:
                logger.error(f"Error deleting collection: {e}")
                raise 