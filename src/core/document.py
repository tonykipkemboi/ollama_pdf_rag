import logging
from pathlib import Path
from typing import List
import fitz  # PyMuPDF
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class PDFLoader:
    """
    Loads PDF documents using PyMuPDF (fitz).
    """

    def load(self, file_path: Path) -> str:
        try:
            logger.info(f"Loading PDF from {file_path}")
            doc = fitz.open(str(file_path))
            full_text = []

            for page in doc:
                text = page.get_text()
                full_text.append(text)

            doc.close()
            return "\n".join(full_text)

        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            raise


class ChunkingStrategy(ABC):
    """
    Abstract base class for different document chunking strategies.
    """

    @abstractmethod
    def chunk_document(self, document_text: str) -> List[str]:
        pass


class ConstantLengthChunkStrategy(ChunkingStrategy):
    """
    A chunking strategy that splits text into fixed-size chunks
    with optional overlap.
    """

    def __init__(self, chunk_size: int = 200, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, document_text: str) -> List[str]:
        chunks = []
        start = 0

        while start < len(document_text):
            end = start + self.chunk_size
            chunk = document_text[start:end]
            chunks.append(chunk.strip())

            # Move the start pointer by (chunk_size - chunk_overlap)
            # to create overlapping chunks.
            start += self.chunk_size - self.chunk_overlap

        return chunks


class ParagraphChunkStrategy(ChunkingStrategy):
    """
    A chunking strategy that splits text by paragraphs.
    Assumes that paragraphs are separated by one or more blank lines.
    """

    def __init__(self, delimiter: str = "\n\n"):
        self.delimiter = delimiter

    def chunk_document(self, document_text: str) -> List[str]:
        paragraphs = document_text.split(self.delimiter)
        # Clean up whitespace
        return [para.strip() for para in paragraphs if para.strip()]


class DocumentProcessor:
    """
    Handles PDF document loading and processing using a specified chunking strategy.
    """

    def __init__(self, loader: PDFLoader, chunk_strategy: ChunkingStrategy):
        self.loader = loader
        self.chunk_strategy = chunk_strategy

    def load_pdf(self, file_path: Path) -> str:
        return self.loader.load(file_path)

    def split_documents(self, document_text: str) -> List[str]:
        return self.chunk_strategy.chunk_document(document_text)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Example 1: Use the constant length chunk strategy
    constant_chunk_strategy = ConstantLengthChunkStrategy(
        chunk_size=300, chunk_overlap=50
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

    # # Example 2: Use the paragraph-based chunk strategy
    # paragraph_chunk_strategy = ParagraphChunkStrategy()
    # processor_paragraphs = DocumentProcessor(
    #     loader=pdf_loader, chunk_strategy=paragraph_chunk_strategy
    # )
    #
    # paragraphs = processor_paragraphs.split_documents(document_text)
    # print(f"Number of paragraphs: {len(paragraphs)}")
    # for i, paragraph in enumerate(paragraphs):
    #     print(f"--- Paragraph {i+1} ---")
    #     print(paragraph)
    #     print("\n")
