#!/bin/bash

echo "=================================="
echo "Starting Ollama PDF RAG Services"
echo "=================================="
echo ""

# Start FastAPI backend
echo "🚀 Starting FastAPI backend (port 8001)..."
python3 run_api.py &
FASTAPI_PID=$!
echo "   FastAPI PID: $FASTAPI_PID"
echo ""

# Wait for FastAPI to start
sleep 5

# Start Next.js frontend
echo "🎨 Starting Next.js frontend (port 3000)..."
cd web-ui && pnpm dev &
NEXTJS_PID=$!
echo "   Next.js PID: $NEXTJS_PID"
cd ..
echo ""

# Start Streamlit admin (optional)
echo "🔧 Starting Streamlit admin (port 8501)..."
python3 run.py &
STREAMLIT_PID=$!
echo "   Streamlit PID: $STREAMLIT_PID"
echo ""

echo "=================================="
echo "All services started!"
echo "=================================="
echo ""
echo "📡 Service URLs:"
echo "   • FastAPI Backend:  http://localhost:8001"
echo "   • Next.js Frontend: http://localhost:3000"
echo "   • Streamlit Admin:  http://localhost:8501"
echo ""
echo "📚 API Documentation:"
echo "   • FastAPI Docs:     http://localhost:8001/docs"
echo "   • Health Check:     http://localhost:8001/api/v1/health"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
wait
