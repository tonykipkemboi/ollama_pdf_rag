"""Vector embeddings and database functionality."""
import logging
from typing import List
from pathlib import Path
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

logger = logging.getLogger(__name__)

class VectorStore:
    """Manages vector embeddings and database operations."""
    
    def __init__(self, embedding_model: str = "nomic-embed-text"):
        self.embeddings = OllamaEmbeddings(model=embedding_model)
        self.vector_db = None
    
    def create_vector_db(self, documents: List, collection_name: str = "local-rag") -> Chroma:
        """Create vector database from documents."""
        try:
            logger.info("Creating vector database")
            self.vector_db = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=collection_name
            )
            return self.vector_db
        except Exception as e:
            logger.error(f"Error creating vector database: {e}")
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