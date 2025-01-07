# Document Processing API

This page documents the document processing components of Ollama PDF RAG.

## DocumentProcessor

```python
class DocumentProcessor:
    """Handles PDF document loading and processing."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize document processor with chunking parameters."""
```

### Methods

#### load_document
```python
def load_document(self, file_path: str) -> List[Document]:
    """Load a PDF document and return list of Document objects."""
```

Parameters:
- `file_path`: Path to the PDF file

Returns:
- List of Document objects

#### split_documents
```python
def split_documents(self, documents: List[Document]) -> List[Document]:
    """Split documents into chunks with overlap."""
```

Parameters:
- `documents`: List of Document objects

Returns:
- List of chunked Document objects

#### process_pdf
```python
def process_pdf(self, file_path: str) -> List[Document]:
    """Load and process a PDF file."""
```

Parameters:
- `file_path`: Path to the PDF file

Returns:
- List of processed Document chunks

## Usage Example

```python
# Initialize processor
processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)

# Process a PDF file
documents = processor.process_pdf("path/to/document.pdf")

# Access document content
for doc in documents:
    print(doc.page_content)
    print(doc.metadata)
```

## Configuration

The document processor can be configured with:

- `chunk_size`: Number of characters per chunk
- `chunk_overlap`: Number of overlapping characters
- `pdf_parser`: PDF parsing backend
- `encoding`: Text encoding

## Error Handling

The processor handles common errors:

- File not found
- Invalid PDF format
- Encoding issues
- Memory constraints 