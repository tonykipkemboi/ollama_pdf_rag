# REST API Reference

The FastAPI backend provides a REST API for PDF management and RAG queries.

**Base URL:** `http://localhost:8001`

## Interactive Documentation

FastAPI provides automatic interactive API docs:

- **Swagger UI:** [http://localhost:8001/docs](http://localhost:8001/docs)
- **ReDoc:** [http://localhost:8001/redoc](http://localhost:8001/redoc)

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/models` | List available models |
| GET | `/api/v1/pdfs` | List uploaded PDFs |
| POST | `/api/v1/pdfs/upload` | Upload a PDF |
| DELETE | `/api/v1/pdfs/{pdf_id}` | Delete a PDF |
| POST | `/api/v1/query` | RAG query |
| GET | `/api/v1/sessions/{session_id}/messages` | Get chat history |

---

## Health Check

### `GET /health`

Check if the API is running and Ollama is accessible.

**Response:**

```json
{
  "status": "healthy",
  "ollama_status": "connected",
  "models_available": 3
}
```

---

## Models

### `GET /api/v1/models`

List available Ollama chat models.

**Response:**

```json
[
  {
    "name": "qwen3:8b",
    "size": 4932501234,
    "modified_at": "2024-12-19T10:00:00Z",
    "is_chat_model": true
  },
  {
    "name": "llama3.2",
    "size": 2019234567,
    "modified_at": "2024-12-18T15:00:00Z",
    "is_chat_model": true
  }
]
```

**Notes:**
- Only returns chat-capable models (excludes embedding models)
- Size is in bytes
- Filters out models without chat templates

---

## PDF Management

### `GET /api/v1/pdfs`

List all uploaded PDFs.

**Response:**

```json
[
  {
    "pdf_id": "pdf_4122871031772577363",
    "name": "Security_Guide.pdf",
    "collection_name": "pdf_4122871031772577363",
    "upload_timestamp": "2024-12-19T18:00:00Z",
    "doc_count": 45,
    "page_count": 12,
    "is_sample": false
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| pdf_id | string | Unique identifier |
| name | string | Original filename |
| collection_name | string | ChromaDB collection name |
| upload_timestamp | datetime | When uploaded |
| doc_count | integer | Number of chunks |
| page_count | integer | Original page count |
| is_sample | boolean | Is a sample PDF |

---

### `POST /api/v1/pdfs/upload`

Upload and process a PDF file.

**Request:**

```bash
curl -X POST "http://localhost:8001/api/v1/pdfs/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

**Response:**

```json
{
  "pdf_id": "pdf_4122871031772577363",
  "name": "document.pdf",
  "collection_name": "pdf_4122871031772577363",
  "doc_count": 23,
  "page_count": 8,
  "upload_timestamp": "2024-12-19T18:30:00Z"
}
```

**Errors:**

| Status | Description |
|--------|-------------|
| 400 | Not a PDF file |
| 500 | Processing failed |

**Processing Steps:**
1. Save file to disk
2. Extract text with UnstructuredPDFLoader
3. Split into chunks (7500 chars, 100 overlap)
4. Generate embeddings (nomic-embed-text)
5. Store in ChromaDB
6. Save metadata to SQLite

---

### `DELETE /api/v1/pdfs/{pdf_id}`

Delete a PDF and its vectors.

**Request:**

```bash
curl -X DELETE "http://localhost:8001/api/v1/pdfs/pdf_4122871031772577363"
```

**Response:**

```json
{
  "message": "PDF deleted successfully"
}
```

**Errors:**

| Status | Description |
|--------|-------------|
| 404 | PDF not found |

**Deletes:**
- PDF file from disk
- Vector collection from ChromaDB
- Metadata from SQLite

---

## RAG Query

### `POST /api/v1/query`

Query documents using RAG.

**Request:**

```json
{
  "question": "What are the security requirements?",
  "model": "qwen3:8b",
  "pdf_ids": ["pdf_123", "pdf_456"],
  "session_id": "optional-session-id"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| question | string | Yes | User's question |
| model | string | Yes | Ollama model name |
| pdf_ids | array | No | PDFs to search (null = all) |
| session_id | string | No | Chat session ID |

**Response:**

```json
{
  "answer": "Based on the documents, the security requirements include...",
  "sources": [
    {
      "pdf_name": "Security_Guide.pdf",
      "pdf_id": "pdf_123",
      "chunk_index": 3
    },
    {
      "pdf_name": "Security_Guide.pdf",
      "pdf_id": "pdf_123",
      "chunk_index": 7
    }
  ],
  "metadata": {
    "model_used": "qwen3:8b",
    "chunks_retrieved": 10,
    "pdfs_queried": 2,
    "reasoning_steps": [
      "📚 Searching across 2 PDF(s): Security_Guide.pdf, Policy.pdf",
      "🤖 Using model: qwen3:8b",
      "🔍 Generating alternative search queries...",
      "📄 Retrieving from: Security_Guide.pdf",
      "✅ Found 5 relevant chunks in Security_Guide.pdf",
      "📄 Retrieving from: Policy.pdf",
      "✅ Found 3 relevant chunks in Policy.pdf",
      "📊 Total chunks retrieved: 8",
      "🔗 Using top 8 chunks for context",
      "💭 Generating answer with source citations...",
      "🧠 Using thinking-enabled model for deeper reasoning...",
      "✨ Answer generated successfully!"
    ]
  },
  "session_id": "e4b444b3-7adb-4da3-aefb-e2b745c7719c",
  "message_id": 42
}
```

| Field | Type | Description |
|-------|------|-------------|
| answer | string | Generated response |
| sources | array | Source chunks used |
| metadata | object | Processing details |
| session_id | string | Chat session ID |
| message_id | integer | Database message ID |

**Errors:**

| Status | Description |
|--------|-------------|
| 404 | Model not found |
| 500 | Query failed |

---

## Chat History

### `GET /api/v1/sessions/{session_id}/messages`

Get chat history for a session.

**Request:**

```bash
curl "http://localhost:8001/api/v1/sessions/e4b444b3-7adb/messages"
```

**Response:**

```json
[
  {
    "message_id": 41,
    "role": "user",
    "content": "What are the security requirements?",
    "sources": null,
    "timestamp": "2024-12-19T18:30:00Z"
  },
  {
    "message_id": 42,
    "role": "assistant",
    "content": "Based on the documents...",
    "sources": [
      {"pdf_name": "Security_Guide.pdf", "chunk_index": 3}
    ],
    "timestamp": "2024-12-19T18:30:15Z"
  }
]
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad request (invalid input) |
| 404 | Resource not found |
| 500 | Internal server error |

---

## Usage Examples

### Python

```python
import requests

# Upload PDF
with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8001/api/v1/pdfs/upload",
        files={"file": f}
    )
pdf_id = response.json()["pdf_id"]

# Query
response = requests.post(
    "http://localhost:8001/api/v1/query",
    json={
        "question": "What is this about?",
        "model": "llama3.2",
        "pdf_ids": [pdf_id]
    }
)
print(response.json()["answer"])
```

### JavaScript

```javascript
// Upload PDF
const formData = new FormData();
formData.append('file', pdfFile);

const uploadRes = await fetch('http://localhost:8001/api/v1/pdfs/upload', {
  method: 'POST',
  body: formData
});
const { pdf_id } = await uploadRes.json();

// Query
const queryRes = await fetch('http://localhost:8001/api/v1/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: 'What is this about?',
    model: 'llama3.2',
    pdf_ids: [pdf_id]
  })
});
const { answer } = await queryRes.json();
```

### cURL

```bash
# Upload
curl -X POST "http://localhost:8001/api/v1/pdfs/upload" \
  -F "file=@document.pdf"

# Query
curl -X POST "http://localhost:8001/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is this about?","model":"llama3.2"}'
```
