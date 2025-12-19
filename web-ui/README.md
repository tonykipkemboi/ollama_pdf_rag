# 📄 PDF Chat - Ollama RAG Frontend

A modern Next.js frontend for chatting with your PDF documents locally using Ollama.

## Features

- 🔒 **100% Local** - All processing happens on your machine
- 📄 **PDF Management** - Upload, view, and manage your PDF documents
- 💬 **AI Chat** - Ask questions about your documents using local LLMs
- 🧠 **Multi-Query RAG** - Intelligent retrieval with source citations
- 🎨 **Modern UI** - Built with Next.js 16, Tailwind CSS, and shadcn/ui
- 🌙 **Dark Mode** - Full dark/light theme support

## Prerequisites

- Node.js 18+
- pnpm
- [Ollama](https://ollama.ai) running locally with models:
  - `llama3.2` (or another chat model)
  - `nomic-embed-text` (for embeddings)
- FastAPI backend running on port 8001

## Running Locally

1. Install dependencies:
```bash
pnpm install
```

2. Set up the database:
```bash
pnpm db:migrate
```

3. Start the development server:
```bash
pnpm dev
```

The app will be available at [http://localhost:3000](http://localhost:3000).

## Architecture

This frontend connects to the FastAPI backend (`run_api.py`) for:
- PDF upload and processing
- RAG queries with Ollama
- Model management

## Tech Stack

- [Next.js 16](https://nextjs.org) with App Router
- [AI SDK](https://ai-sdk.dev) for streaming responses
- [shadcn/ui](https://ui.shadcn.com) components
- [Tailwind CSS](https://tailwindcss.com) for styling
- [Drizzle ORM](https://orm.drizzle.team) for local SQLite database
