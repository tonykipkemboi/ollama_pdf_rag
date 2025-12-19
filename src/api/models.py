"""Pydantic models for API request/response schemas."""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class PDFUploadResponse(BaseModel):
    """Response model for PDF upload."""
    pdf_id: str
    name: str
    collection_name: str
    doc_count: int
    page_count: int
    upload_timestamp: datetime


class PDFListItem(BaseModel):
    """Model for PDF in list response."""
    pdf_id: str
    name: str
    collection_name: str
    upload_timestamp: datetime
    doc_count: int
    page_count: int
    is_sample: bool


class QueryRequest(BaseModel):
    """Request model for RAG query."""
    question: str
    model: str = "mistral:latest"
    pdf_ids: Optional[List[str]] = None
    session_id: Optional[str] = None


class SourceInfo(BaseModel):
    """Source information for retrieved documents."""
    pdf_name: str
    pdf_id: str
    chunk_index: int


class QueryResponse(BaseModel):
    """Response model for RAG query."""
    answer: str
    sources: List[SourceInfo]
    metadata: Dict[str, Any]
    session_id: str
    message_id: int


class ModelInfo(BaseModel):
    """Ollama model information."""
    name: str
    size: int
    modified_at: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    ollama_connected: bool
    chromadb_collections: int
    total_pdfs: int
