"""PDF processing service."""
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session

from ...core.document import DocumentProcessor
from ...core.embeddings import VectorStore
from ..database import PDFMetadata
from ..config import settings


class PDFService:
    """Service for PDF operations."""

    def __init__(self):
        """Initialize PDF service."""
        self.doc_processor = DocumentProcessor(chunk_size=7500, chunk_overlap=100)
        self.vector_store = VectorStore(
            embedding_model="nomic-embed-text",
            persist_directory=settings.VECTOR_DB_DIR
        )
        self.storage_dir = Path(settings.PDF_STORAGE_DIR)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    async def upload_and_process(
        self,
        file: UploadFile,
        db: Session
    ) -> PDFMetadata:
        """Upload and process a PDF file.

        Args:
            file: Uploaded PDF file
            db: Database session

        Returns:
            PDFMetadata: Metadata for the processed PDF
        """
        # Generate unique ID
        pdf_id = self._generate_pdf_id(file.filename)

        # Save file
        file_path = self.storage_dir / f"{pdf_id}_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Process PDF
        documents = self.doc_processor.load_pdf(file_path)
        chunks = self.doc_processor.split_documents(documents)

        # Add metadata to chunks
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "pdf_id": pdf_id,
                "pdf_name": file.filename,
                "chunk_index": i,
                "source_file": file.filename
            })

        # Create vector DB collection
        collection_name = f"pdf_{abs(hash(file.filename + pdf_id))}"
        vector_db = self.vector_store.create_vector_db(
            documents=chunks,
            collection_name=collection_name
        )

        # Store metadata in database
        pdf_metadata = PDFMetadata(
            pdf_id=pdf_id,
            name=file.filename,
            collection_name=collection_name,
            upload_timestamp=datetime.now(),
            doc_count=len(chunks),
            page_count=len(documents),
            is_sample=False,
            file_path=str(file_path)
        )
        db.add(pdf_metadata)
        db.commit()
        db.refresh(pdf_metadata)

        return pdf_metadata

    def list_pdfs(self, db: Session) -> List[PDFMetadata]:
        """List all PDFs.

        Args:
            db: Database session

        Returns:
            List of PDF metadata
        """
        return db.query(PDFMetadata).all()

    def get_pdf(self, pdf_id: str, db: Session) -> Optional[PDFMetadata]:
        """Get single PDF metadata.

        Args:
            pdf_id: PDF identifier
            db: Database session

        Returns:
            PDF metadata or None
        """
        return db.query(PDFMetadata).filter(PDFMetadata.pdf_id == pdf_id).first()

    def delete_pdf(self, pdf_id: str, db: Session) -> bool:
        """Delete PDF and its collection.

        Args:
            pdf_id: PDF identifier
            db: Database session

        Returns:
            True if deleted successfully, False otherwise
        """
        pdf = self.get_pdf(pdf_id, db)
        if not pdf:
            return False

        # Delete vector collection
        try:
            from langchain_chroma import Chroma
        except ImportError:
            from langchain_community.vectorstores import Chroma
        from langchain_ollama import OllamaEmbeddings

        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        vector_db = Chroma(
            persist_directory=settings.VECTOR_DB_DIR,
            embedding_function=embeddings,
            collection_name=pdf.collection_name
        )
        vector_db.delete_collection()

        # Delete file if it exists
        if pdf.file_path and os.path.exists(pdf.file_path):
            os.remove(pdf.file_path)

        # Delete metadata from database
        db.delete(pdf)
        db.commit()

        return True

    def _generate_pdf_id(self, filename: str) -> str:
        """Generate unique PDF ID.

        Args:
            filename: Original filename

        Returns:
            Unique PDF identifier
        """
        timestamp = datetime.now().isoformat()
        return f"pdf_{abs(hash(filename + timestamp))}"
