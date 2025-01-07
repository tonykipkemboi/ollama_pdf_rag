# Quick Start Guide

This guide will help you get started with Ollama PDF RAG quickly.

## Prerequisites

Ensure you have:
- Completed the [installation](installation.md)
- Started the Ollama service
- Pulled the required models:
  ```bash
  ollama pull llama3.2
  ollama pull nomic-embed-text
  ```

## Starting the Application

1. Activate your virtual environment:
   ```bash
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Start the application:
   ```bash
   python run.py
   ```

3. Open your browser to `http://localhost:8501`

## Basic Usage

### 1. Upload a PDF

- Use the file uploader in the sidebar
- Or try the sample PDF provided

### 2. Select a Model

- Choose from your locally available Ollama models
- Default is `llama3.2`

### 3. Ask Questions

- Type your question in the chat input
- Press Enter or click Send
- Wait for the response

### 4. Adjust Display

- Use the zoom slider to adjust PDF visibility
- PDF pages are displayed on the right

### 5. Clean Up

- Use "Delete Collection" when switching documents
- This ensures clean context for new documents

## Example Usage

Here's a simple example workflow:

1. Upload a PDF about machine learning
2. Ask questions like:
   - "What are the main topics covered in this document?"
   - "Can you explain the concept of X mentioned on page Y?"
   - "Summarize the key findings"

## Tips

- Start with broad questions to understand document content
- Be specific when asking about particular sections
- Use follow-up questions for clarification
- Clear the context when switching documents

## Next Steps

- Read the [PDF Processing Guide](../user-guide/pdf-processing.md) for advanced usage
- Learn about the [RAG Pipeline](../user-guide/rag-pipeline.md)
- Explore the [Chat Interface](../user-guide/chat-interface.md) 