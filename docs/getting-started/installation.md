# Installation Guide

This guide walks you through setting up Ollama PDF RAG on your system.

## Prerequisites

Before installing, ensure you have:

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | Required for LangChain 1.0 |
| Node.js | 18+ | For Next.js frontend |
| pnpm | 9+ | Package manager for Node.js |
| Ollama | Latest | Local LLM server |
| Git | Any | For cloning the repo |

## Step 1: Install Ollama

### macOS / Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows

Download from [ollama.com/download](https://ollama.com/download/windows)

### Verify Installation

```bash
ollama --version
```

## Step 2: Pull Required Models

```bash
# Chat model (choose one or more)
ollama pull llama3.2          # Recommended - fast & capable
ollama pull qwen3:8b          # Great for thinking/reasoning
ollama pull mistral           # Alternative option

# Embedding model (required)
ollama pull nomic-embed-text
```

!!! tip "Model Selection"
    - **qwen3:8b** and **deepseek-r1** support "thinking mode" for chain-of-thought reasoning
    - **llama3.2** is fastest for general use
    - You can pull multiple models and switch between them in the UI

## Step 3: Clone the Repository

```bash
git clone https://github.com/tonykipkemboi/ollama_pdf_rag.git
cd ollama_pdf_rag
```

## Step 4: Python Environment Setup

### Using venv (Recommended)

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Using uv (Faster Alternative)

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create environment and install
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Step 5: Next.js Frontend Setup

```bash
cd web-ui

# Install dependencies
pnpm install

# Return to project root
cd ..
```

## Step 6: Verify Installation

### Start the Backend

```bash
python run_api.py
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete.
```

### Start the Frontend (New Terminal)

```bash
cd web-ui
pnpm dev
```

You should see:

```
▲ Next.js 16.0.10
- Local:        http://localhost:3000
```

### Test the App

1. Open [http://localhost:3000](http://localhost:3000)
2. You should see the PDF Chat interface
3. Upload a PDF using the 📎 button
4. Select it with the checkbox
5. Ask a question!

## Directory Structure

After installation, your directory should look like:

```
ollama_pdf_rag/
├── .venv/                 # Python virtual environment
├── data/
│   ├── pdfs/             # Uploaded PDFs
│   │   ├── sample/       # Sample PDFs
│   │   └── uploads/      # User uploads
│   ├── vectors/          # ChromaDB vector storage
│   └── api.db            # SQLite metadata
├── src/
│   ├── api/              # FastAPI backend
│   ├── app/              # Streamlit app
│   └── core/             # Core RAG logic
├── web-ui/               # Next.js frontend
│   ├── app/              # Next.js app router
│   ├── components/       # React components
│   └── data/
│       └── chat.db       # Chat history
├── requirements.txt      # Python dependencies
└── run_api.py           # Start FastAPI server
```

## Troubleshooting

### ONNX DLL Error (Windows)

```
DLL load failed while importing onnx_copy2py_export
```

**Solution:**

1. Install [Microsoft Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)
2. Restart your computer
3. Or try:
   ```bash
   pip uninstall onnxruntime onnxruntime-gpu
   pip install onnxruntime
   ```

### Port Already in Use

```
Address already in use: 8001
```

**Solution:**

```bash
# Find process using the port
lsof -i :8001

# Kill it
kill -9 <PID>
```

### Model Not Found

```
Model 'llama3.2' not found
```

**Solution:**

```bash
# Pull the model
ollama pull llama3.2

# Verify it's available
ollama list
```

### pnpm Not Found

```bash
# Install pnpm globally
npm install -g pnpm

# Or using corepack (Node.js 16.10+)
corepack enable
corepack prepare pnpm@latest --activate
```

### SQLite Errors

If you see database errors, delete the database files and restart:

```bash
rm -f data/api.db
rm -f web-ui/data/chat.db
```

## Next Steps

- Follow the [Quick Start Guide](quickstart.md) to use the app
- Read about [PDF Processing](../user-guide/pdf-processing.md)
- Learn the [RAG Pipeline](../user-guide/rag-pipeline.md)
- Check the [API Reference](../api/document.md)
