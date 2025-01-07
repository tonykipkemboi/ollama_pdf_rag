"""Test document processing functionality."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.core.document import DocumentProcessor
from langchain_core.documents import Document

@pytest.fixture
def processor():
    """Create a DocumentProcessor instance."""
    return DocumentProcessor()

@pytest.fixture
def test_pdf_path():
    """Get the test PDF path."""
    return Path("data/pdfs/sample/scammer-agent.pdf")

def test_init(processor):
    """Test initialization."""
    assert processor.chunk_size == 7500
    assert processor.chunk_overlap == 100

def test_init_custom_params():
    """Test initialization with custom parameters."""
    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=50)
    assert processor.chunk_size == 1000
    assert processor.chunk_overlap == 50

@patch('langchain_community.document_loaders.UnstructuredPDFLoader.load')
def test_load_pdf_file_not_found(mock_load):
    """Test loading non-existent PDF."""
    mock_load.side_effect = FileNotFoundError("File not found")
    processor = DocumentProcessor()
    with pytest.raises(FileNotFoundError):
        processor.load_pdf(Path("nonexistent.pdf"))

@pytest.mark.skipif(not Path("data/pdfs/sample/scammer-agent.pdf").exists(),
                    reason="Sample PDF not found")
def test_load_pdf_success(processor, test_pdf_path):
    """Test loading existing PDF."""
    documents = processor.load_pdf(test_pdf_path)
    assert len(documents) > 0
    assert hasattr(documents[0], 'page_content')

def test_split_documents(processor):
    """Test document splitting."""
    doc = Document(
        page_content="This is a test document " * 1000,
        metadata={"source": "test"}
    )
    documents = [doc]
    chunks = processor.split_documents(documents)
    assert len(chunks) > 1

def test_split_empty_document(processor):
    """Test splitting empty document."""
    doc = Document(page_content="", metadata={"source": "test"})
    documents = [doc]
    chunks = processor.split_documents(documents)
    # Empty documents may result in no chunks
    assert len(chunks) == 0 or (len(chunks) == 1 and chunks[0].page_content == "")

def test_split_large_document(processor):
    """Test splitting very large document."""
    large_text = "This is a test sentence. " * 10000
    doc = Document(page_content=large_text, metadata={"source": "test"})
    documents = [doc]
    chunks = processor.split_documents(documents)
    
    # Verify chunk sizes
    for chunk in chunks:
        assert len(chunk.page_content) <= processor.chunk_size

def test_metadata_preservation(processor):
    """Test metadata is preserved during splitting."""
    metadata = {"source": "test", "page": 1, "author": "Test Author"}
    doc = Document(
        page_content="This is a test document " * 1000,
        metadata=metadata
    )
    documents = [doc]
    chunks = processor.split_documents(documents)
    
    # Verify metadata in all chunks
    for chunk in chunks:
        assert chunk.metadata["source"] == metadata["source"]
        assert chunk.metadata["page"] == metadata["page"]
        assert chunk.metadata["author"] == metadata["author"]

def test_chunk_overlap():
    """Test chunk overlap is working correctly."""
    # Create a document with a repeating pattern to ensure overlap is detectable
    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 4  # Repeating pattern
    doc = Document(page_content=text, metadata={"source": "test"})
    
    # Use small chunk size to force multiple chunks
    processor = DocumentProcessor(chunk_size=20, chunk_overlap=10)
    chunks = processor.split_documents([doc])
    
    # Verify we got multiple chunks
    assert len(chunks) > 1
    
    # Verify overlap between consecutive chunks
    for i in range(len(chunks) - 1):
        current_chunk = chunks[i].page_content
        next_chunk = chunks[i + 1].page_content
        
        # Find any common substring of length >= chunk_overlap
        found_overlap = False
        for j in range(len(current_chunk) - processor.chunk_overlap + 1):
            substring = current_chunk[j:j + processor.chunk_overlap]
            if substring in next_chunk:
                found_overlap = True
                break
        
        assert found_overlap, f"No overlap found between chunks {i} and {i+1}" 