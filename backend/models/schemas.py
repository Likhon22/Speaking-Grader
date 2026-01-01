"""
Pydantic models for request/response validation
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ==================== Voice Configuration ====================
class VoiceOption(BaseModel):
    """Available voice option."""
    id: str
    name: str
    voice: str


class VoiceConfig(BaseModel):
    """Voice configuration."""
    selected: str
    options: List[VoiceOption]


# ==================== Question Models ====================
class Question(BaseModel):
    """IELTS question."""
    id: int
    text: str
    tip: str


# ==================== Test/Session Models ====================
class TestStartRequest(BaseModel):
    """Request to start a new test."""
    voice: Optional[str] = "female"  # male, female, other


class TestStartResponse(BaseModel):
    """Response when starting a new test."""
    session_id: str
    questions: List[Question]
    voice_config: VoiceConfig


# ==================== TTS Models ====================
class TTSRequest(BaseModel):
    """Request to generate speech from text."""
    text: str = Field(..., description="Text to convert to speech")
    voice: str = Field(default="en-US-JennyNeural",
                       description="Voice ID to use")


# ==================== STT Models ====================
class STTResponse(BaseModel):
    """Response from speech-to-text transcription."""
    transcript: str
    word_count: int
    duration: Optional[float] = None


# ==================== Grading Models ====================
class AnswerSubmission(BaseModel):
    """Single answer submission."""
    question_id: int
    question_text: str
    transcript: str


class GradingRequest(BaseModel):
    """Request to grade submitted answers."""
    session_id: str
    answers: List[AnswerSubmission]


class LanguageError(BaseModel):
    """Individual language error."""
    original: str
    corrected: str
    explanation: str
    error_type: str


class ScoreBreakdown(BaseModel):
    """Individual scores for each criterion."""
    fluency: float
    lexical: float
    grammar: float
    pronunciation: float


class GradingResponse(BaseModel):
    """Response from grading service."""
    overall_band: float
    scores: ScoreBreakdown
    positive_feedback: List[str]
    critical_feedback: List[str]
    language_errors: List[LanguageError]
    band_upgrade_tip: str
    detailed_result: Optional[Dict[str, Any]] = None


# ==================== Session Models ====================
class SessionInfo(BaseModel):
    """Session information."""
    session_id: str
    current_question: int
    total_questions: int
    answers_completed: int
    voice: str
    created_at: str
    status: str  # active, completed


# ==================== Error Models ====================
class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
    code: Optional[int] = None
