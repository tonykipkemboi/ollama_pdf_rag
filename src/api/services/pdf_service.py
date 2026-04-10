"""PDF processing service."""
import os
from datetime import datetime
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import List, Optional
from fastapi import HTTPException, UploadFile
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

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Strip directory components from a filename to prevent path traversal.

        Handles both POSIX (``/``) and Windows (``\\``) separators regardless
        of the host OS.

        Args:
            filename: Raw filename (potentially from user input)

        Returns:
            Basename only, with all directory components removed

        Raises:
            HTTPException: If the resulting basename is empty
        """
        # Use PureWindowsPath to split on both / and \ on any platform,
        # then take only the final component.
        sanitized = PureWindowsPath(filename).name
        # Defence-in-depth: also run through PurePosixPath
        sanitized = PurePosixPath(sanitized).name
        if not sanitized or sanitized in (".", ".."):
            raise HTTPException(
                status_code=400,
                detail="Invalid filename"
            )
        return sanitized

    def _safe_file_path(self, filename: str) -> Path:
        """Build a file path guaranteed to be within self.storage_dir.

        Args:
            filename: Already-sanitized filename

        Returns:
            Resolved Path within self.storage_dir

        Raises:
            HTTPException: If the resolved path escapes the storage directory
        """
        file_path = (self.storage_dir / filename).resolve()
        storage_resolved = self.storage_dir.resolve()
        if not file_path.is_relative_to(storage_resolved) or file_path == storage_resolved:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename"
            )
        return file_path

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
        # Sanitize filename to prevent path traversal (CWE-22)
        safe_filename = self._sanitize_filename(file.filename)

        # Generate unique ID
        pdf_id = self._generate_pdf_id(safe_filename)

        # Save file — build path from sanitized name and verify containment
        file_path = self._safe_file_path(f"{pdf_id}_{safe_filename}")
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
                "pdf_name": safe_filename,
                "chunk_index": i,
                "source_file": safe_filename
            })

        # Create vector DB collection
        collection_name = f"pdf_{abs(hash(safe_filename + pdf_id))}"
        vector_db = self.vector_store.create_vector_db(
            documents=chunks,
            collection_name=collection_name
        )

        # Store metadata in database
        pdf_metadata = PDFMetadata(
            pdf_id=pdf_id,
            name=safe_filename,
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

        # Delete file if it exists — verify path is within storage dir first
        if pdf.file_path:
            file_path = Path(pdf.file_path).resolve()
            storage_resolved = self.storage_dir.resolve()
            if not (file_path.is_relative_to(storage_resolved) and file_path != storage_resolved):
                raise HTTPException(status_code=400, detail="Invalid file path")
            if file_path.exists():
                os.remove(file_path)

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
