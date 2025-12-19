"""Run the FastAPI server."""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
