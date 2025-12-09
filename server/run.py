"""Run the FastAPI server with uvicorn."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=3000,
        reload=True,
        log_level="info"
    )
