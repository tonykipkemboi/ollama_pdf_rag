# Embeddings API

This page documents the text embedding components used for semantic search.

## NomicEmbeddings

```python
class NomicEmbeddings:
    """Manages text embeddings using Nomic's embedding model."""
    
    def __init__(self, model_name: str = "nomic-embed-text"):
        """Initialize embeddings with model name."""
```

### Methods

#### embed_documents
```python
def embed_documents(self, texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts."""
```

Parameters:
- `texts`: List of text strings

Returns:
- List of embedding vectors

#### embed_query
```python
def embed_query(self, text: str) -> List[float]:
    """Generate embedding for a single query text."""
```

Parameters:
- `text`: Query text

Returns:
- Embedding vector

## Usage Example

```python
# Initialize embeddings
embeddings = NomicEmbeddings()

# Embed documents
docs = ["First document", "Second document"]
doc_embeddings = embeddings.embed_documents(docs)

# Embed query
query = "Sample query"
query_embedding = embeddings.embed_query(query)
```

## Configuration

Configure embeddings with:

- Model selection
- Batch size
- Normalization
- Caching options

## Performance

Optimization options:

- Batch processing
- GPU acceleration
- Caching
- Dimensionality

## Best Practices

1. **Text Preparation**
   - Clean input text
   - Handle special characters
   - Normalize length

2. **Resource Management**
   - Batch similar lengths
   - Monitor memory usage
   - Cache frequent queries

3. **Quality Control**
   - Validate embeddings
   - Check dimensions
   - Monitor similarity scores
``` 