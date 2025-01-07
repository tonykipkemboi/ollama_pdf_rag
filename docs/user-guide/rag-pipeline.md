# RAG Pipeline

This guide explains the Retrieval Augmented Generation (RAG) pipeline used in Ollama PDF RAG.

## Overview

The RAG pipeline combines document retrieval with language model generation to provide accurate, context-aware responses:

1. Query Processing
2. Document Retrieval
3. Context Augmentation
4. Response Generation

## Components

### 1. Embeddings

- Uses Nomic's text embeddings
- Converts text chunks to vectors
- Enables semantic search

### 2. Vector Store

- ChromaDB for vector storage
- Efficient similarity search
- Persistent document storage

### 3. Retriever

- Multi-query retrieval
- Semantic search
- Context window management

### 4. Language Model

- Local Ollama models
- Context-aware responses
- Source attribution

## Pipeline Flow

1. **User Query**
   - Question is received
   - Query is processed

2. **Retrieval**
   - Similar chunks found
   - Context assembled

3. **Generation**
   - Context injected
   - Response generated
   - Sources tracked

## Performance Optimization

- Chunk size tuning
- Embedding quality
- Model selection
- Memory management

## Best Practices

1. **Query Formation**
   - Be specific
   - One question at a time
   - Clear language

2. **Model Selection**
   - Match to task
   - Consider resources
   - Balance speed/quality

3. **Context Management**
   - Monitor relevance
   - Adjust retrieval
   - Clean stale data 