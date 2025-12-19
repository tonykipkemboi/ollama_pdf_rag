# Changelog

All notable changes to Ollama PDF RAG are documented here.

## [Unreleased]

### Added
- **Next.js Frontend** - Modern React-based chat interface
  - Real-time message streaming with AI SDK
  - Chat history persistence with SQLite
  - PDF selection with checkboxes before chatting
  - Question classification (RAG vs general chat)
  - Model selector with live Ollama model detection
  - Dark/light theme support
  - Mobile-responsive design

- **FastAPI Backend** - Production-ready REST API
  - PDF upload and processing endpoints
  - RAG query endpoint with multi-PDF support
  - Model listing and health check endpoints
  - Session-based chat history
  - Swagger/ReDoc documentation

- **Enhanced RAG Pipeline**
  - Multi-query retrieval for better results
  - Support for thinking models (qwen3, deepseek-r1)
  - Chain-of-thought reasoning with reasoning steps
  - Source attribution for all answers
  - PDF-specific filtering

- **PDF Selection UX**
  - Checkbox-based selection in sidebar
  - "All/None" quick selection buttons
  - Selection persists across page reloads
  - Warning when no PDFs selected for document queries

- **Question Classification**
  - Auto-detects if question needs document context
  - General chat mode (no RAG) for non-document questions
  - Clear warning for document questions without PDFs

### Changed
- Updated Python requirement to 3.10+ (LangChain 1.0 requirement)
- CI workflow now tests Python 3.10, 3.11, 3.12
- Removed Ollama model downloads from CI (uses mocks)
- Upgraded all GitHub Actions to v4/v5

### Fixed
- Fixed vector DB persistence in ChromaDB
- Fixed streaming response format for AI SDK
- Fixed CI failures due to disk space (removed model downloads)
- Fixed deprecated `actions/upload-artifact@v3`

### Security
- Updated `next-auth` to 5.0.0-beta.30 (email misdelivery fix)
- Updated `@playwright/test` to 1.57.0
- Updated `protobuf` to >=5.29.5 (DoS fix)
- Added pnpm overrides for transitive vulnerabilities

---

## [1.0.0] - 2024-12-01

### Added
- Initial release
- Streamlit chat interface
- LangChain RAG implementation
- PDF processing with UnstructuredPDFLoader
- ChromaDB vector storage
- Multi-query retriever
- Ollama LLM integration
- Jupyter notebooks for experimentation
- MkDocs documentation site
- GitHub Actions CI/CD
- pytest test suite

### Technical Stack
- Python 3.9+
- Streamlit 1.40.0
- LangChain 1.0.0
- ChromaDB 0.4.22
- Ollama (local LLM)

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| Unreleased | - | Next.js UI, FastAPI, Enhanced RAG |
| 1.0.0 | 2024-12-01 | Initial release with Streamlit |

## Upgrade Guide

### From 1.0.0 to Unreleased

1. **Python Version**: Upgrade to Python 3.10+
   ```bash
   python --version  # Should be 3.10+
   ```

2. **Install New Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Next.js Frontend**:
   ```bash
   cd web-ui
   pnpm install
   ```

4. **Start Services**:
   ```bash
   # Option 1: Use start script
   ./start_all.sh
   
   # Option 2: Manual
   python run_api.py &  # Terminal 1
   cd web-ui && pnpm dev  # Terminal 2
   ```

5. **Access New UI**: Open http://localhost:3000

## Migration Notes

### Database Changes

The Next.js UI uses a separate SQLite database for chat history:
- Location: `web-ui/data/chat.db`
- Contains: chats, messages, users, votes

The FastAPI backend uses:
- Location: `data/api.db`
- Contains: PDF metadata, chat sessions

### Breaking Changes

- Python 3.9 is no longer supported
- Streamlit app now runs on port 8501 (was default)
- New FastAPI backend required on port 8001

## Roadmap

### Planned Features

- [ ] Image extraction from PDFs
- [ ] OCR support for scanned documents
- [ ] Multi-user authentication
- [ ] Document comparison mode
- [ ] Export chat history
- [ ] API key management
- [ ] Custom embedding models
- [ ] Batch PDF processing
