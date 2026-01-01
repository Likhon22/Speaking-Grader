"""
Speech-to-Text (STT) Routes
Transcribes user's audio recordings to text
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from backend.models.schemas import STTResponse
from services.stt_service import load_whisper_model, transcribe_audio

router = APIRouter()

# Load Whisper model once at startup
whisper_model = None


@router.on_event("startup")
async def load_model():
    """Load Whisper model on startup."""
    global whisper_model
    whisper_model = load_whisper_model()


@router.post("/transcribe")
async def transcribe_speech(
    audio_file: UploadFile = File(...,
                                  description="Audio file to transcribe (WAV, MP3, M4A)"),
    session_id: str = Form(None),
    question_id: int = Form(None)
) -> STTResponse:
    """
    Transcribe audio recording to text using Whisper.

    Args:
        audio_file: Uploaded audio file from user's recording
        session_id: Optional session identifier for tracking
        question_id: Optional question ID being answered

    Returns:
        Transcribed text with word count

    Example:
        POST /api/stt/transcribe
        Content-Type: multipart/form-data

        Form Data:
        - audio_file: [user_recording.wav]
        - session_id: "abc-123"
        - question_id: 1
    """
    global whisper_model

    # Validate file type
    allowed_types = ["audio/wav", "audio/mpeg",
                     "audio/mp4", "audio/x-m4a", "audio/webm"]
    if audio_file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )

    # Check file size (max 25MB)
    audio_bytes = await audio_file.read()
    if len(audio_bytes) > 25 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 25MB"
        )

    try:
        # Transcribe using Whisper
        transcript = transcribe_audio(audio_bytes, whisper_model)

        # Validate transcript
        words = transcript.split()
        word_count = len(words)

        if word_count < 3:
            raise HTTPException(
                status_code=400,
                detail="Recording too short or silent. Please speak more clearly."
            )

        # Calculate approximate duration (rough estimate)
        # Assuming 16kHz, 16-bit audio
        duration = len(audio_bytes) / (16000 * 2)

        return STTResponse(
            transcript=transcript,
            word_count=word_count,
            duration=round(duration, 2)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@router.get("/model-info")
async def get_model_info():
    """
    Get information about the loaded Whisper model.

    Returns:
        Model configuration and status
    """
    global whisper_model

    if whisper_model is None:
        return {
            "status": "not_loaded",
            "model": None
        }

    return {
        "status": "loaded",
        "model": "base",
        "languages": ["en"],
        "max_audio_length": "30 seconds recommended"
    }
