# RAG Pipeline

This guide explains how the Retrieval-Augmented Generation (RAG) pipeline works in Ollama PDF RAG.

## Overview

RAG combines the knowledge in your documents with the reasoning capabilities of language models. Here's the complete flow:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              RAG PIPELINE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  User Question                                                              │
│       │                                                                     │
│       ▼                                                                     │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │  Question   │────▶│   Multi-    │────▶│   Vector    │                   │
│  │ Classifier  │     │   Query     │     │   Search    │                   │
│  └─────────────┘     │  Generator  │     │  (ChromaDB) │                   │
│       │              └─────────────┘     └─────────────┘                   │
│       │                    │                    │                          │
│       │              ┌─────┴─────┐             │                          │
│       │              │ Query 1   │             │                          │
│       │              │ Query 2   │─────────────┼──▶ Relevant Chunks       │
│       │              │ Query 3   │             │                          │
│       │              └───────────┘             │                          │
│       │                                        │                          │
│       ▼                                        ▼                          │
│  ┌─────────────┐     ┌─────────────────────────────────────┐              │
│  │   Direct    │     │         Context Assembly            │              │
│  │    LLM      │     │  [Source: doc1.pdf] chunk content   │              │
│  │  Response   │     │  [Source: doc2.pdf] chunk content   │              │
│  └─────────────┘     │  [Source: doc1.pdf] chunk content   │              │
│       │              └─────────────────────────────────────┘              │
│       │                              │                                     │
│       │                              ▼                                     │
│       │              ┌─────────────────────────────────────┐              │
│       │              │           LLM Generation            │              │
│       │              │  - Chain-of-thought reasoning       │              │
│       │              │  - Source citation                  │              │
│       │              │  - Thinking mode (if supported)     │              │
│       │              └─────────────────────────────────────┘              │
│       │                              │                                     │
│       ▼                              ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐              │
│  │                    Final Response                        │              │
│  │  Answer text + Source citations + Reasoning steps        │              │
│  └─────────────────────────────────────────────────────────┘              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Step 1: Question Classification

Before processing, the system classifies the question:

```python
def needsDocumentContext(question: str) -> bool:
    document_keywords = [
        "document", "pdf", "file", "page", "section",
        "according to", "based on", "what does", "summarize",
        "the document", "the file", "uploaded", "in the"
    ]
    return any(keyword in question.lower() for keyword in document_keywords)
```

| Question | Classification | Action |
|----------|---------------|--------|
| "What does the document say about X?" | Document query | Use RAG |
| "What is machine learning?" | General query | Direct LLM |
| "Summarize the warranty terms" (no PDFs) | Document, no context | Show warning |

## Step 2: Multi-Query Generation

For document queries, we generate multiple search queries to improve retrieval:

```python
# Original question
"What are the security requirements?"

# Generated alternatives
1. "What security requirements are documented?"
2. "What security measures does the document mandate?"
3. "What are the security specifications mentioned?"
```

This overcomes limitations of single-query similarity search by exploring different phrasings.

**Implementation:**

```python
QUERY_PROMPT = PromptTemplate(
    input_variables=["question"],
    template="""You are an AI language model assistant. Generate 2
    different versions of the given user question to retrieve relevant 
    documents from a vector database.
    
    Original question: {question}"""
)

retriever = MultiQueryRetriever.from_llm(
    vector_db.as_retriever(search_kwargs={"k": 3}),
    llm,
    prompt=QUERY_PROMPT
)
```

## Step 3: Vector Search

Each generated query searches the ChromaDB vector database:

```
Query 1 ──▶ ChromaDB ──▶ [chunk_a, chunk_b, chunk_c]
Query 2 ──▶ ChromaDB ──▶ [chunk_a, chunk_d, chunk_e]
Query 3 ──▶ ChromaDB ──▶ [chunk_b, chunk_f, chunk_g]
                              │
                              ▼
                    Combined: [chunk_a, chunk_b, chunk_c,
                               chunk_d, chunk_e, chunk_f, chunk_g]
```

**Search Parameters:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| k | 3 | Chunks per query per PDF |
| Collection | Per-PDF | Each PDF has its own collection |
| Embeddings | nomic-embed-text | 768-dim vectors |

**Multi-PDF Search:**

When multiple PDFs are selected, we search each collection:

```python
for pdf in selected_pdfs:
    vector_db = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name=pdf.collection_name
    )
    docs = retriever.invoke(question)
    all_docs.extend(docs)
```

## Step 4: Context Assembly

Retrieved chunks are formatted with source labels:

```python
context_parts = []
for doc in all_docs[:10]:  # Top 10 chunks
    source = doc.metadata.get("pdf_name", "Unknown")
    context_parts.append(f"[Source: {source}]\n{doc.page_content}\n")

formatted_context = "\n---\n".join(context_parts)
```

**Example Context:**

```
[Source: Security_Guide.pdf]
Authentication requirements include multi-factor authentication (MFA)
for all user accounts. Password policies must enforce...

---

[Source: Security_Guide.pdf]
Authorization uses role-based access control (RBAC) with the following
roles defined: Administrator, Manager, User, Guest...

---

[Source: Policy_Manual.pdf]
All security incidents must be reported within 24 hours using the
incident response form located in Appendix B...
```

## Step 5: LLM Generation

The formatted context and question are sent to the LLM:

### Standard Mode

```python
template = """Answer the question based ONLY on the following context.
Each section is marked with its source document.

Use chain-of-thought reasoning:
1. Identify relevant parts of the context
2. Analyze information from each source
3. Synthesize a comprehensive answer
4. Cite sources for each piece of information

Context:
{context}

Question: {question}

Think step-by-step and provide your answer with source citations:"""
```

### Thinking Mode (qwen3, deepseek-r1)

For models that support thinking, we use enhanced prompting:

```python
if supports_thinking:
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": cot_system_message},
            {"role": "user", "content": question}
        ],
        think=True,  # Enable thinking mode
        stream=False
    )
    
    # Capture thinking process
    if response.message.thinking:
        reasoning_steps.append(f"💡 Model's thinking: {response.message.thinking[:500]}")
```

## Step 6: Response Formatting

The final response includes:

```json
{
  "answer": "Based on the Security Guide, authentication requires...",
  "sources": [
    {"pdf_name": "Security_Guide.pdf", "pdf_id": "pdf_123", "chunk_index": 3},
    {"pdf_name": "Security_Guide.pdf", "pdf_id": "pdf_123", "chunk_index": 7},
    {"pdf_name": "Policy_Manual.pdf", "pdf_id": "pdf_456", "chunk_index": 2}
  ],
  "metadata": {
    "model_used": "qwen3:8b",
    "chunks_retrieved": 10,
    "pdfs_queried": 2,
    "reasoning_steps": [
      "📚 Searching across 2 PDF(s)",
      "🔍 Generating alternative queries...",
      "✅ Found 5 chunks in Security_Guide.pdf",
      "✅ Found 3 chunks in Policy_Manual.pdf",
      "💭 Generating answer...",
      "✨ Answer generated!"
    ]
  }
}
```

## Reasoning Steps

The pipeline logs progress for transparency:

| Step | Emoji | Description |
|------|-------|-------------|
| PDF Discovery | 📚 | Identifies selected PDFs |
| Model Init | 🤖 | Loads the LLM |
| Query Generation | 🔍 | Creates alternative queries |
| Retrieval | 📄 | Searches each PDF |
| Chunk Count | ✅ | Reports chunks found |
| Total | 📊 | Summarizes retrieval |
| Context | 🔗 | Shows chunks used |
| Generation | 💭 | LLM processing |
| Thinking | 🧠 | For thinking models |
| Chain-of-thought | 💡 | Model's reasoning |
| Complete | ✨ | Success |

## Configuration

### Chunk Settings

```python
DocumentProcessor(
    chunk_size=7500,    # Characters per chunk
    chunk_overlap=100   # Overlap between chunks
)
```

| Setting | Value | Rationale |
|---------|-------|-----------|
| chunk_size | 7500 | Balances context vs. precision |
| chunk_overlap | 100 | Preserves cross-boundary context |

### Retrieval Settings

```python
retriever = vector_db.as_retriever(
    search_kwargs={"k": 3}  # Top 3 chunks per query
)
```

### Model Settings

```python
# Thinking-enabled models
thinking_models = ['qwen3', 'deepseek-r1', 'qwen', 'deepseek']
```

## Performance Considerations

### Speed Optimization

| Factor | Impact | Solution |
|--------|--------|----------|
| Many PDFs | Slower | Select only needed PDFs |
| Large chunks | More tokens | Reduce chunk_size |
| Complex queries | Multiple LLM calls | Use faster models |

### Quality Optimization

| Factor | Impact | Solution |
|--------|--------|----------|
| Small chunks | Missing context | Increase chunk_size |
| Few results | Incomplete answers | Increase k value |
| Poor retrieval | Wrong chunks | Use thinking models |

## API Endpoint

```bash
POST /api/v1/query
Content-Type: application/json

{
  "question": "What are the security requirements?",
  "model": "qwen3:8b",
  "pdf_ids": ["pdf_123", "pdf_456"],
  "session_id": "optional-session-id"
}
```

**Response:**

```json
{
  "answer": "The security requirements include...",
  "sources": [...],
  "metadata": {...},
  "session_id": "generated-or-provided",
  "message_id": 42
}
```

## Troubleshooting

### "Found 0 relevant chunks"

- Check if PDFs are properly processed
- Verify embeddings were created
- Try rephrasing the question

### Slow Retrieval

- Reduce number of selected PDFs
- Use SSD storage for ChromaDB
- Check Ollama server performance

### Poor Quality Answers

- Use more specific questions
- Try thinking-enabled models
- Check if relevant chunks are being retrieved
