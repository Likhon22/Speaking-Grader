"""
Text-to-Speech (TTS) Routes
Converts question text to speech audio
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend.models.schemas import TTSRequest
from backend.utils.async_tts import text_to_speech_async

router = APIRouter()


@router.post("/generate")
async def generate_speech(request: TTSRequest):
    """
    Convert text to speech using edge-tts.

    Args:
        request: Contains text and voice preference

    Returns:
        MP3 audio file as bytes

    Example:
        POST /api/tts/generate
        {
            "text": "Describe a time when you helped someone",
            "voice": "en-US-JennyNeural"
        }
    """
    try:
        # Use async TTS service
        audio_bytes = await text_to_speech_async(request.text, request.voice)

        # Return audio as MP3
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=question.mp3",
                "Cache-Control": "public, max-age=3600"  # Cache for 1 hour
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate speech: {str(e)}"
        )


@router.get("/voices")
async def get_available_voices():
    """
    Get list of available voices.

    Returns:
        List of voice options with metadata
    """
    voices = [
        {
            "id": "en-US-ChristopherNeural",
            "name": "Christopher (US Male)",
            "language": "en-US",
            "gender": "male",
            "recommended": True
        },
        {
            "id": "en-US-JennyNeural",
            "name": "Jenny (US Female)",
            "language": "en-US",
            "gender": "female",
            "recommended": True
        },
        {
            "id": "en-GB-SoniaNeural",
            "name": "Sonia (UK Female)",
            "language": "en-GB",
            "gender": "female",
            "recommended": False
        },
        {
            "id": "en-GB-RyanNeural",
            "name": "Ryan (UK Male)",
            "language": "en-GB",
            "gender": "male",
            "recommended": False
        },
        {
            "id": "en-AU-NatashaNeural",
            "name": "Natasha (AU Female)",
            "language": "en-AU",
            "gender": "female",
            "recommended": False
        }
    ]

    return {"voices": voices}
