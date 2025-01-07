"""Test document processing functionality."""
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from src.core.document import DocumentProcessor
from src.app.main import extract_model_names
from langchain_core.documents import Document

class TestDocumentProcessor(unittest.TestCase):
    """Test cases for DocumentProcessor class."""
    
    def setUp(self):
        """Set up test cases."""
        self.processor = DocumentProcessor()
        self.test_pdf_path = Path("data/pdfs/sample/scammer-agent.pdf")
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.processor.chunk_size, 7500)
        self.assertEqual(self.processor.chunk_overlap, 100)
    
    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        processor = DocumentProcessor(chunk_size=1000, chunk_overlap=50)
        self.assertEqual(processor.chunk_size, 1000)
        self.assertEqual(processor.chunk_overlap, 50)
    
    @patch('langchain_community.document_loaders.UnstructuredPDFLoader.load')
    def test_load_pdf_file_not_found(self, mock_load):
        """Test loading non-existent PDF."""
        mock_load.side_effect = FileNotFoundError("File not found")
        with self.assertRaises(FileNotFoundError):
            self.processor.load_pdf(Path("nonexistent.pdf"))
    
    @unittest.skipIf(not Path("data/pdfs/sample/scammer-agent.pdf").exists(),
                    "Sample PDF not found")
    def test_load_pdf_success(self):
        """Test loading existing PDF."""
        documents = self.processor.load_pdf(self.test_pdf_path)
        self.assertGreater(len(documents), 0)
        self.assertTrue(hasattr(documents[0], 'page_content'))
    
    def test_split_documents(self):
        """Test document splitting."""
        doc = Document(
            page_content="This is a test document " * 1000,
            metadata={"source": "test"}
        )
        documents = [doc]
        chunks = self.processor.split_documents(documents)
        self.assertGreater(len(chunks), 1)
    
    def test_split_empty_document(self):
        """Test splitting empty document."""
        doc = Document(page_content="", metadata={"source": "test"})
        documents = [doc]
        chunks = self.processor.split_documents(documents)
        # Empty documents may result in no chunks
        self.assertTrue(len(chunks) == 0 or (len(chunks) == 1 and chunks[0].page_content == ""))
    
    def test_split_large_document(self):
        """Test splitting very large document."""
        large_text = "This is a test sentence. " * 10000
        doc = Document(page_content=large_text, metadata={"source": "test"})
        documents = [doc]
        chunks = self.processor.split_documents(documents)
        
        # Verify chunk sizes
        for chunk in chunks:
            self.assertLessEqual(len(chunk.page_content), self.processor.chunk_size)
    
    def test_metadata_preservation(self):
        """Test metadata is preserved during splitting."""
        metadata = {"source": "test", "page": 1, "author": "Test Author"}
        doc = Document(
            page_content="This is a test document " * 1000,
            metadata=metadata
        )
        documents = [doc]
        chunks = self.processor.split_documents(documents)
        
        # Verify metadata in all chunks
        for chunk in chunks:
            self.assertEqual(chunk.metadata["source"], metadata["source"])
            self.assertEqual(chunk.metadata["page"], metadata["page"])
            self.assertEqual(chunk.metadata["author"], metadata["author"])
    
    def test_chunk_overlap(self):
        """Test chunk overlap is working correctly."""
        # Create a document with a repeating pattern to ensure overlap is detectable
        text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 4  # Repeating pattern
        doc = Document(page_content=text, metadata={"source": "test"})
        
        # Use small chunk size to force multiple chunks
        processor = DocumentProcessor(chunk_size=20, chunk_overlap=10)
        chunks = processor.split_documents([doc])
        
        # Verify we got multiple chunks
        self.assertGreater(len(chunks), 1)
        
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
            
            self.assertTrue(found_overlap, f"No overlap found between chunks {i} and {i+1}")


class TestModelExtraction(unittest.TestCase):
    """Test cases for model name extraction."""
    
    def test_extract_model_names_empty(self):
        """Test extracting model names from empty response."""
        models_info = Mock()
        models_info.models = []
        result = extract_model_names(models_info)
        self.assertEqual(result, tuple())
    
    def test_extract_model_names_success(self):
        """Test successful model name extraction."""
        # Create mock Model objects
        mock_model1 = Mock()
        mock_model1.model = "model1:latest"
        mock_model2 = Mock()
        mock_model2.model = "model2:latest"
        
        # Create mock response
        models_info = Mock()
        models_info.models = [mock_model1, mock_model2]
        
        result = extract_model_names(models_info)
        self.assertEqual(result, ("model1:latest", "model2:latest"))
    
    def test_extract_model_names_invalid_format(self):
        """Test handling invalid response format."""
        models_info = {"invalid": "format"}
        result = extract_model_names(models_info)
        self.assertEqual(result, tuple())
    
    def test_extract_model_names_exception(self):
        """Test handling exceptions during extraction."""
        models_info = Mock()
        # Accessing .models will raise AttributeError
        del models_info.models
        result = extract_model_names(models_info)
        self.assertEqual(result, tuple()) 