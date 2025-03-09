import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple

import fitz  # PyMuPDF
from models import Chunk, ChunkType

logger = logging.getLogger(__name__)


def get_page_for_offset(offset: int, page_starts: List[Tuple[int, int]]) -> int:
    """
    Determines the page number for a given character offset based on the
    list of (page_number, start_offset) pairs.
    """
    page_for_chunk = None
    for page_num, start_offset in page_starts:
        if offset >= start_offset:
            page_for_chunk = page_num
        else:
            break
    return page_for_chunk if page_for_chunk is not None else 0


class PDFLoader:
    """
    Loads PDF documents using PyMuPDF (fitz) and returns the full text along
    with a list of (page_number, start_offset) pairs.
    """

    def load(self, file_path: Path) -> Tuple[str, List[Tuple[int, int]]]:
        try:
            logger.info(f"Loading PDF from {file_path}")
            doc = fitz.open(str(file_path))
            full_text = ""
            page_starts: List[Tuple[int, int]] = []
            current_offset = 0

            for page in doc:
                text = page.get_text()
                page_starts.append((page.number, current_offset))
                full_text += text
                current_offset += len(text)

            doc.close()
            return full_text, page_starts

        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            raise


class ChunkingStrategy(ABC):
    """
    Abstract base class for different document chunking strategies.
    The chunk_document method returns a list of Chunk objects.
    """

    @abstractmethod
    def chunk_document(
        self, document_text: str, pdf_name: str, page_starts: List[Tuple[int, int]]
    ) -> List[Chunk]:
        pass


class ConstantLengthChunkStrategy(ChunkingStrategy):
    """
    Splits text into fixed-size chunks with optional overlap.
    """

    def __init__(self, chunk_size: int = 200, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self, document_text: str, pdf_name: str, page_starts: List[Tuple[int, int]]
    ) -> List[Chunk]:
        chunks = []
        start = 0
        chunk_index = 1

        while start < len(document_text):
            end = start + self.chunk_size
            text_chunk = document_text[start:end].strip()
            pdf_page = get_page_for_offset(start, page_starts)
            chunk = Chunk(
                id=f"{pdf_name}-{chunk_index}",
                pdf_name=pdf_name,
                pdf_page=pdf_page,
                section_name=None,  # TODO: Implement section detection
                subsection_name=None,  # TODO: Implement subsection detection
                chunk_type=ChunkType.TEXT,
                text=text_chunk,
            )
            chunks.append(chunk)
            chunk_index += 1
            # Advance the start pointer to create overlapping chunks.
            start += self.chunk_size - self.chunk_overlap

        return chunks


class ParagraphChunkStrategy(ChunkingStrategy):
    """
    Splits text by paragraphs.
    Assumes paragraphs are separated by one or more blank lines.
    """

    def __init__(self, delimiter: str = "\n\n"):
        self.delimiter = delimiter

    def chunk_document(
        self, document_text: str, pdf_name: str, page_starts: List[Tuple[int, int]]
    ) -> List[Chunk]:
        raw_paragraphs = document_text.split(self.delimiter)
        chunks = []
        current_offset = 0
        chunk_index = 1

        for para in raw_paragraphs:
            para = para.strip()
            if not para:
                continue
            # Find the offset of this paragraph starting from the current_offset.
            offset = document_text.find(para, current_offset)
            if offset == -1:
                offset = current_offset
            current_offset = offset + len(para)
            pdf_page = get_page_for_offset(offset, page_starts)
            chunk = Chunk(
                id=f"{pdf_name}-{chunk_index}",
                pdf_name=pdf_name,
                pdf_page=pdf_page,
                section_name=None,
                subsection_name=None,
                chunk_type=ChunkType.TEXT,
                text=para,
            )
            chunks.append(chunk)
            chunk_index += 1

        return chunks


class AdvancedParagraphChunkStrategy(ChunkingStrategy):
    """
    Future implementation:
    1. Isolate tables and image captions as individual chunks.
    2. Label each chunk accordingly.
    3. Split remaining text into paragraphs, with further splitting if too long.
    4. Experiment with overlaps and bulletpoints.
    """

    def chunk_document(
        self, document_text: str, pdf_name: str, page_starts: List[Tuple[int, int]]
    ) -> List[Chunk]:
        # Implementation can be added later.
        pass


class LayoutPDFReaderChunkingStrategy(ChunkingStrategy):
    """
    Future implementation using intelligent layout-aware chunking.
    """

    def chunk_document(
        self, document_text: str, pdf_name: str, page_starts: List[Tuple[int, int]]
    ) -> List[Chunk]:
        # Implementation can be added later.
        pass


class CLAREDIChunkingStrategy(ChunkingStrategy):
    """
    Future implementation for Context Length Aware Ranked Elided Document Injection.
    """

    def chunk_document(
        self, document_text: str, pdf_name: str, page_starts: List[Tuple[int, int]]
    ) -> List[Chunk]:
        # Implementation can be added later.
        pass


class DocumentProcessor:
    """
    Loads and processes a PDF using a specified chunking strategy.
    """

    def __init__(self, loader: PDFLoader, chunk_strategy: ChunkingStrategy):
        self.loader = loader
        self.chunk_strategy = chunk_strategy

    def load_pdf(self, file_path: Path) -> Tuple[str, List[Tuple[int, int]]]:
        return self.loader.load(file_path)

    def process_pdf(self, file_path: Path) -> List[Chunk]:
        """
        Loads the PDF, splits the text into chunks using the chunking strategy,
        and returns a list of Chunk objects with the proper page numbers.
        """
        document_text, page_starts = self.load_pdf(file_path)
        pdf_name = file_path.name
        return self.chunk_strategy.chunk_document(document_text, pdf_name, page_starts)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pdf_loader = PDFLoader()

    pdf_path = Path("../../data/pdfs/CV.pdf")

    # Example 1: Using the constant length chunk strategy
    constant_chunk_strategy = ConstantLengthChunkStrategy(
        chunk_size=300, chunk_overlap=50
    )
    processor_constant = DocumentProcessor(
        loader=pdf_loader, chunk_strategy=constant_chunk_strategy
    )

    constant_chunks = processor_constant.process_pdf(pdf_path)
    print(f"Number of chunks (constant strategy): {len(constant_chunks)}")
    for i, chunk in enumerate(constant_chunks):
        print(f"--- Chunk {i+1} ---")
        print(chunk)
        print("\n")

    # Example 2: Using the paragraph-based chunk strategy
    paragraph_chunk_strategy = ParagraphChunkStrategy(delimiter="\n\n")
    processor_paragraph = DocumentProcessor(
        loader=pdf_loader, chunk_strategy=paragraph_chunk_strategy
    )

    paragraph_chunks = processor_paragraph.process_pdf(pdf_path)
    print(f"Number of chunks (paragraph strategy): {len(paragraph_chunks)}")
    for i, chunk in enumerate(paragraph_chunks):
        print(f"--- Chunk {i+1} ---")
        print(chunk)
        print("\n")
