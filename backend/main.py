"""
FastAPI Backend for IELTS Speaking Grader
Main application entry point
"""
from backend.routes import test_routes, tts_routes, stt_routes, grading_routes
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routes

# Create FastAPI app
app = FastAPI(
    title="IELTS Speaking Grader API",
    description="REST API for IELTS speaking test with AI-powered grading",
    version="1.0.0"
)

# Configure CORS for mobile app access
app.add_middleware(
    CORSMiddleware,
    # In production, replace with specific mobile app origin
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(test_routes.router, prefix="/api/test",
                   tags=["Test Management"])
app.include_router(tts_routes.router, prefix="/api/tts",
                   tags=["Text-to-Speech"])
app.include_router(stt_routes.router, prefix="/api/stt",
                   tags=["Speech-to-Text"])
app.include_router(grading_routes.router,
                   prefix="/api/grading", tags=["Grading"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "IELTS Speaking Grader API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "services": {
            "whisper": "loaded",
            "gemini": "configured",
            "tts": "ready"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
