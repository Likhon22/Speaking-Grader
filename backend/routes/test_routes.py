"""
Test/Session Management Routes
Handles test session creation and management
"""
import uuid
from datetime import datetime
from typing import Dict
from fastapi import APIRouter, HTTPException

from backend.models.schemas import (
    TestStartRequest,
    TestStartResponse,
    Question,
    VoiceConfig,
    VoiceOption,
    SessionInfo
)
from data import IELTS_QUESTIONS

router = APIRouter()

# In-memory session storage (use Redis/Database in production)
sessions: Dict[str, dict] = {}

# Voice mapping
VOICE_MAP = {
    "male": "en-US-ChristopherNeural",
    "female": "en-US-JennyNeural",
    "other": "en-GB-SoniaNeural"  # British female voice as alternative
}


@router.get("/start")
async def start_test(voice: str = "female") -> TestStartResponse:
    """
    Start a new IELTS speaking test session.

    Args:
        voice: Voice preference (male, female, other)

    Returns:
        Session ID, questions, and voice configuration
    """
    # Generate unique session ID
    session_id = str(uuid.uuid4())

    # Map voice preference to actual voice ID
    voice_id = VOICE_MAP.get(voice.lower(), "en-US-JennyNeural")

    # Create session
    sessions[session_id] = {
        "session_id": session_id,
        "voice": voice_id,
        "current_question": 0,
        "answers": [],
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }

    # Prepare questions with IDs and tips
    questions = []
    tips = [
        "Focus on using transition words like 'then', 'after', and 'however'.",
        "Try to give specific examples to support your opinion."
    ]

    for idx, question_text in enumerate(IELTS_QUESTIONS):
        questions.append(Question(
            id=idx + 1,
            text=question_text,
            tip=tips[idx] if idx < len(
                tips) else "Speak clearly and naturally."
        ))

    # Prepare voice options
    voice_options = [
        VoiceOption(id="male", name="Male (Christopher)",
                    voice="en-US-ChristopherNeural"),
        VoiceOption(id="female", name="Female (Jenny)",
                    voice="en-US-JennyNeural"),
        VoiceOption(id="other", name="British (Sonia)",
                    voice="en-GB-SoniaNeural")
    ]

    voice_config = VoiceConfig(
        selected=voice_id,
        options=voice_options
    )

    return TestStartResponse(
        session_id=session_id,
        questions=questions,
        voice_config=voice_config
    )


@router.get("/session/{session_id}")
async def get_session(session_id: str) -> SessionInfo:
    """
    Get current session information.

    Args:
        session_id: Session identifier

    Returns:
        Current session status and progress
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]

    return SessionInfo(
        session_id=session["session_id"],
        current_question=session["current_question"],
        total_questions=len(IELTS_QUESTIONS),
        answers_completed=len(session["answers"]),
        voice=session["voice"],
        created_at=session["created_at"],
        status=session["status"]
    )


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session (cleanup).

    Args:
        session_id: Session identifier

    Returns:
        Success message
    """
    if session_id in sessions:
        del sessions[session_id]

    return {"message": "Session deleted successfully"}


@router.get("/questions")
async def get_questions():
    """
    Get all available IELTS questions.

    Returns:
        List of questions with tips
    """
    questions = []
    tips = [
        "Focus on using transition words like 'then', 'after', and 'however'.",
        "Try to give specific examples to support your opinion."
    ]

    for idx, question_text in enumerate(IELTS_QUESTIONS):
        questions.append(Question(
            id=idx + 1,
            text=question_text,
            tip=tips[idx] if idx < len(
                tips) else "Speak clearly and naturally."
        ))

    return {"questions": questions}
