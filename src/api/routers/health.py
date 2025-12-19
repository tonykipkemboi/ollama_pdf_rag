"""Health check endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import ollama

from ..dependencies import get_db
from ..models import HealthResponse
from ..database import PDFMetadata

router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Check API health."""

    # Check Ollama connection
    ollama_connected = False
    try:
        ollama.list()
        ollama_connected = True
    except:
        pass

    # Check ChromaDB collections
    from pathlib import Path
    vector_dir = Path("data/vectors")
    collection_count = len([d for d in vector_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]) if vector_dir.exists() else 0

    # Check total PDFs
    total_pdfs = db.query(PDFMetadata).count()

    return HealthResponse(
        status="healthy" if ollama_connected else "degraded",
        ollama_connected=ollama_connected,
        chromadb_collections=collection_count,
        total_pdfs=total_pdfs
    )
