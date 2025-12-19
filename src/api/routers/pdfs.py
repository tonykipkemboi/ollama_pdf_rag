"""PDF management endpoints."""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..dependencies import get_db, get_pdf_service
from ..models import PDFUploadResponse, PDFListItem
from ..services.pdf_service import PDFService

router = APIRouter(prefix="/api/v1/pdfs", tags=["pdfs"])


@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """Upload and process a PDF file."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    pdf_metadata = await pdf_service.upload_and_process(file, db)

    return PDFUploadResponse(
        pdf_id=pdf_metadata.pdf_id,
        name=pdf_metadata.name,
        collection_name=pdf_metadata.collection_name,
        doc_count=pdf_metadata.doc_count,
        page_count=pdf_metadata.page_count,
        upload_timestamp=pdf_metadata.upload_timestamp
    )


@router.get("", response_model=List[PDFListItem])
def list_pdfs(
    db: Session = Depends(get_db),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """List all uploaded PDFs."""
    pdfs = pdf_service.list_pdfs(db)
    return [
        PDFListItem(
            pdf_id=pdf.pdf_id,
            name=pdf.name,
            collection_name=pdf.collection_name,
            upload_timestamp=pdf.upload_timestamp,
            doc_count=pdf.doc_count,
            page_count=pdf.page_count,
            is_sample=pdf.is_sample
        )
        for pdf in pdfs
    ]


@router.delete("/{pdf_id}")
def delete_pdf(
    pdf_id: str,
    db: Session = Depends(get_db),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """Delete a PDF and its vector collection."""
    success = pdf_service.delete_pdf(pdf_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="PDF not found")
    return {"message": "PDF deleted successfully"}
