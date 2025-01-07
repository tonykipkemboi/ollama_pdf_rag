# PDF Processing

This guide explains how the PDF processing works in Ollama PDF RAG.

## Document Loading

The application uses LangChain's PDF loader to read and process PDF documents. Here's how it works:

1. Upload a PDF through the Streamlit interface
2. The PDF is loaded and parsed into text
3. Text is split into manageable chunks
4. Chunks are processed for better context retention

## Chunking Strategy

Documents are split using the following parameters:

- Chunk size: 1000 characters (configurable)
- Chunk overlap: 200 characters (configurable)
- Split by: Character

This ensures:
- Manageable chunk sizes for the model
- Sufficient context overlap
- Preservation of document structure

## Text Processing

The text processing pipeline includes:

1. **Extraction**: Converting PDF to raw text
2. **Cleaning**: Removing artifacts and formatting
3. **Splitting**: Creating overlapping chunks
4. **Indexing**: Preparing for vector storage

## Configuration

You can adjust processing parameters in the application:

```python
chunk_size = 1000  # Characters per chunk
chunk_overlap = 200  # Overlap between chunks
```

## Best Practices

1. **Document Quality**
   - Use searchable PDFs
   - Ensure good scan quality
   - Check text extraction quality

2. **Chunk Size**
   - Larger for detailed context
   - Smaller for precise answers
   - Balance based on model capacity

3. **Memory Management**
   - Monitor RAM usage
   - Adjust chunk size if needed
   - Clean up collections regularly 