"""
Simple script to run the FastAPI backend server
"""
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting IELTS Speaking Grader API...")
    print("📍 Server: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("🔧 Health: http://localhost:8000/health")
    print("\nPress CTRL+C to stop\n")

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
