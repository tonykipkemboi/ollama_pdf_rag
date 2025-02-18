import json
import logging
from pathlib import Path
from typing import List, Optional

import chromadb
from chromadb.config import Settings
from chromadb.errors import UniqueConstraintError
from document import ConstantLengthChunkStrategy, DocumentProcessor, PDFLoader

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


if __name__ == "__main__":
    # --- Load PDF and create chunks ---
    constant_chunk_strategy = ConstantLengthChunkStrategy(
        chunk_size=500, chunk_overlap=100
    )
    pdf_loader = PDFLoader()
    processor = DocumentProcessor(
        loader=pdf_loader, chunk_strategy=constant_chunk_strategy
    )

    pdf_path = Path("../../data/pdfs/sample/CV.pdf")
    document_text = processor.load_pdf(pdf_path)
    chunks = processor.split_documents(document_text)

    print(f"Number of chunks (constant strategy): {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i+1} ---")
        print(chunk)
        print("\n")

    # --- Initialize the vector store and add the PDF chunks ---
    vector_store = VectorStore(collection_name="local-rag")

    # Use the chunks (list of strings) as the documents.
    metadatas = [{"source": f"chunk_{i+1}"} for i in range(len(chunks))]
    ids = [f"id_{i+1}" for i in range(len(chunks))]
    vector_store.create_vector_db(documents=chunks, metadatas=metadatas, ids=ids)

    # --- Run a query against the collection ---
    query = "What algorithm was used to develop a set of optimised parsers?"
    results = vector_store.collection.query(
        query_texts=[query],
        n_results=3,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    print("Query Results:")
    print(json.dumps(results, indent=4))

    vector_store.delete_collection()
