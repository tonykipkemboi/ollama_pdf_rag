# RAG Pipeline API

This page documents the RAG (Retrieval Augmented Generation) pipeline components.

## RAGPipeline

```python
class RAGPipeline:
    """Manages the RAG pipeline for document question-answering."""
    
    def __init__(self, model_name: str, embeddings: Embeddings):
        """Initialize RAG pipeline with model and embeddings."""
```

### Methods

#### create_vector_store
```python
def create_vector_store(self, documents: List[Document]) -> VectorStore:
    """Create a vector store from documents."""
```

Parameters:
- `documents`: List of processed documents

Returns:
- Initialized vector store

#### get_relevant_documents
```python
def get_relevant_documents(self, query: str) -> List[Document]:
    """Retrieve relevant documents for a query."""
```

Parameters:
- `query`: User question
- `k`: Number of documents to retrieve (default: 4)

Returns:
- List of relevant documents

#### generate_response
```python
def generate_response(self, query: str, context: List[Document]) -> str:
    """Generate response using LLM and context."""
```

Parameters:
- `query`: User question
- `context`: Retrieved documents

Returns:
- Generated response

## Usage Example

```python
# Initialize pipeline
pipeline = RAGPipeline(
    model_name="llama2",
    embeddings=NonicEmbeddings()
)

# Process query
docs = pipeline.get_relevant_documents("What is RAG?")
response = pipeline.generate_response(
    query="What is RAG?",
    context=docs
)
```

## Configuration

The pipeline can be configured with:

- Model selection
- Embedding type
- Retrieval parameters
- Response templates

## Performance Tuning

Optimize the pipeline by adjusting:

- Number of retrieved documents
- Context window size
- Temperature setting
- Response length 