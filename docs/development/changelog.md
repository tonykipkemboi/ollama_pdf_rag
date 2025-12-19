# Changelog

All notable changes to Ollama PDF RAG are documented here.

## [v3.0.0] - 2025-12-19

### 🚀 Major Features

#### Next.js Frontend
- **Modern Chat UI** - Beautiful, responsive chat interface built with Next.js 16 and React 19
- **Real-time Streaming** - Live message streaming with Vercel AI SDK
- **Chat Persistence** - SQLite database for saving all conversations
- **PDF Selection** - Checkbox-based PDF selection before chatting
- **Question Classification** - Auto-detects if questions need document context
- **Model Selector** - Switch between Ollama models on the fly
- **Theme Support** - Dark/light mode toggle

#### FastAPI Backend
- **REST API** - Production-ready API with OpenAPI docs
- **PDF Management** - Upload, list, delete PDF endpoints
- **RAG Query** - Multi-PDF query with source attribution
- **Session Management** - Chat history per session
- **Health Monitoring** - Ollama connection status

#### Enhanced RAG
- **Multi-Query Retrieval** - Generates alternative queries for better recall
- **Thinking Models** - Support for qwen3, deepseek-r1 chain-of-thought
- **PDF Filtering** - Query specific PDFs, not all
- **Source Citations** - Every answer includes chunk sources

### 📖 Documentation
- **MkDocs Site** - Comprehensive documentation with Material theme
- **API Reference** - Full REST API documentation
- **Architecture Diagrams** - Visual pipeline explanations
- **Screenshots** - UI screenshots in docs

### 🔧 Infrastructure
- **GitHub Actions** - Updated CI for Python 3.10-3.12
- **Security Updates** - Patched Dependabot vulnerabilities
- **Improved Tests** - Mocked tests without Ollama dependency

### 💥 Breaking Changes
- Python 3.9 no longer supported (requires 3.10+)
- New FastAPI backend required on port 8001
- Database schema changes for chat persistence

---

## [v2.1.0] - 2024-01-07

### Added
- Comprehensive test suite with pytest
- GitHub Actions CI pipeline
- Pre-commit hooks for code quality
- Test coverage reporting
- Project restructuring with clean architecture
- New directory structure for better organization
- Sample PDFs in dedicated folder

### Changed
- Moved all source code to src/ directory
- Updated dependencies to latest compatible versions
- Improved README with testing documentation
- Added test status badge
- Reorganized PDF storage structure

### Fixed
- Dependency conflicts with pydantic
- ONNX runtime compatibility issues
- Test coverage configuration

---

## [v2.0] - 2023-11-05
- Major version release
- Improved RAG implementation
- Enhanced PDF processing

---

## [v1.0] - 2023-07-08
- Initial release
- Basic RAG functionality
- PDF processing capabilities
- Streamlit interface
- Jupyter notebook for experimentation

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| v3.0.0 | 2025-12-19 | Next.js UI, FastAPI, Enhanced RAG |
| v2.1.0 | 2024-01-07 | Test suite, CI/CD, restructuring |
| v2.0 | 2023-11-05 | Improved RAG, enhanced processing |
| v1.0 | 2023-07-08 | Initial release |

## Upgrade Guide

### From v2.x to v3.0.0

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
- Contains: chats, messages, users

The FastAPI backend uses:
- Location: `data/api.db`
- Contains: PDF metadata, chat sessions

### Breaking Changes in v3.0.0

- Python 3.9 is no longer supported
- Streamlit app now runs on port 8501
- New FastAPI backend required on port 8001
- New dependency: Node.js 18+ and pnpm

## Roadmap

### Upcoming Features

- [ ] Image extraction from PDFs
- [ ] OCR support for scanned documents  
- [ ] Multi-user authentication
- [ ] Document comparison mode
- [ ] Export chat history
- [ ] API key management
- [ ] Custom embedding models
- [ ] Batch PDF processing
