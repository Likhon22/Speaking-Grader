"""
Grading Routes
Handles AI-powered grading using Google Gemini
"""
import os
import json
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from google import genai
from google.genai import types

from backend.models.schemas import (
    GradingRequest,
    GradingResponse,
    ScoreBreakdown,
    LanguageError
)
from config.settings import GEMINI_MODEL

router = APIRouter()


# System prompt for IELTS grading (same as in grading_service.py)
SYSTEM_INSTRUCTION = """You are an EXPERT IELTS Speaking Examiner with 20+ years of experience. Your task is to provide a highly detailed, evidence-based evaluation of the student's speaking performance.

CRITICAL INSTRUCTION: You must justify every score with SPECIFIC EXAMPLES (quotes) from the student's transcript. Do not give generic advice.

***SCORING CRITERIA Breakdown:***

1.  **Fluency & Coherence (FC):**
    *   Do they speak at a normal length? Are there long pauses?
    *   Do they use discourse markers (e.g., "However", "On the other hand") effectively?
    *   *Evidence required:* Quote where they hesitated or used good linking words.

2.  **Lexical Resource (LR):**
    *   Do they use a wide range of vocabulary? Is it precise?
    *   Do they use idioms or collocations?
    *   *Evidence required:* Quote specific good/bad vocabulary choices.

3.  **Grammatical Range & Accuracy (GRA):**
    *   Do they use a mix of simple and complex sentences?
    *   Are there frequent errors? Do errors cause confusion?
    *   *Evidence required:* Quote specific grammatical errors and suggest the correct form.

4.  **Pronunciation (P):**
    *   (Inferred from transcript context): Are there garbled words suggesting mispronunciation?
    *   *Note:* Be lenient here as you are grading a transcript, but penalize if the STT output is incomprehensible due to mumbling.

    **FEEDBACK INSTRUCTIONS:**
*   **POSITIVE_FEEDBACK:** Must be specific.
*   **CRITICAL_FEEDBACK:** Must be actionable.
*   **LANGUAGE_ERRORS:**
    *   `explanation`: Briefly explain WHY it is wrong or better (e.g., "'Immediately' is more natural than 'very fast' in this context").
    *   `error_type`: Use categories like "Vocabulary", "Grammar", "Pronunciation", "Fluency".
*   **BAND_UPGRADE_TIP:** Give a specific exercise."""


# Schema for structured JSON output
GRADE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "FINAL_OVERALL_BAND_SCORE": {"type": "NUMBER"},
        "SCORE_BREAKDOWN": {
            "type": "OBJECT",
            "properties": {
                "Fluency_Coherence": {"type": "NUMBER"},
                "Lexical_Resource": {"type": "NUMBER"},
                "Grammatical_Range_Accuracy": {"type": "NUMBER"},
                "Pronunciation": {"type": "NUMBER"}
            }
        },
        "POSITIVE_FEEDBACK": {"type": "STRING"},
        "CRITICAL_FEEDBACK": {"type": "STRING"},
        "LANGUAGE_ERRORS": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "error_type": {"type": "STRING"},
                    "original_phrase": {"type": "STRING"},
                    "correction": {"type": "STRING"},
                    "explanation": {"type": "STRING"}
                }
            }
        },
        "BAND_UPGRADE_TIP": {"type": "STRING"}
    },
    "required": ["FINAL_OVERALL_BAND_SCORE", "SCORE_BREAKDOWN", "POSITIVE_FEEDBACK", "CRITICAL_FEEDBACK", "LANGUAGE_ERRORS", "BAND_UPGRADE_TIP"]
}


def parse_feedback(feedback_text: str) -> List[str]:
    """Parse feedback string into list of points."""
    # Split by bullet points or newlines
    points = []
    for line in feedback_text.split('\n'):
        line = line.strip()
        # Remove bullet points
        line = line.lstrip('•-*').strip()
        if line and len(line) > 10:  # Meaningful feedback
            points.append(line)
    return points if points else [feedback_text]


@router.post("/submit")
async def submit_for_grading(request: GradingRequest) -> GradingResponse:
    """
    Grade submitted answers using Google Gemini AI.

    Args:
        request: Contains session_id and list of answers with transcripts

    Returns:
        Detailed grading with scores and feedback

    Example:
        POST /api/grading/submit
        {
            "session_id": "abc-123",
            "answers": [
                {
                    "question_id": 1,
                    "question_text": "Describe a time when...",
                    "transcript": "I remember when I helped..."
                },
                {
                    "question_id": 2,
                    "question_text": "What is your opinion...",
                    "transcript": "In my opinion..."
                }
            ]
        }
    """
    # Validate API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY not configured. Please set it in .env file"
        )

    # Validate answers
    if not request.answers or len(request.answers) == 0:
        raise HTTPException(
            status_code=400,
            detail="No answers provided for grading"
        )

    try:
        # Build Q&A text for Gemini
        qa_text = ""
        for answer in request.answers:
            qa_text += f"**Question {answer.question_id}:** {answer.question_text}\n"
            qa_text += f"**Student Answer {answer.question_id}:** {answer.transcript}\n\n"

        user_prompt = (
            f"Please analyze the following student transcripts against the IELTS Speaking Band Descriptors (FC, LR, GRA, P).\n\n"
            f"{qa_text}\n\n"
            f"Based on this, generate a score for each criterion and a final overall Band Score. BE STRICT. BE DETAILED."
        )

        # Call Gemini API
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.3,
                response_mime_type="application/json",
                response_schema=GRADE_SCHEMA
            )
        )

        # Parse response
        result = json.loads(response.text)

        # Extract scores
        scores = ScoreBreakdown(
            fluency=result["SCORE_BREAKDOWN"]["Fluency_Coherence"],
            lexical=result["SCORE_BREAKDOWN"]["Lexical_Resource"],
            grammar=result["SCORE_BREAKDOWN"]["Grammatical_Range_Accuracy"],
            pronunciation=result["SCORE_BREAKDOWN"]["Pronunciation"]
        )

        # Parse feedback into lists
        positive_feedback = parse_feedback(result.get("POSITIVE_FEEDBACK", ""))
        critical_feedback = parse_feedback(result.get("CRITICAL_FEEDBACK", ""))

        # Parse language errors
        language_errors = []
        for error in result.get("LANGUAGE_ERRORS", []):
            language_errors.append(LanguageError(
                original=error.get("original_phrase", ""),
                corrected=error.get("correction", ""),
                explanation=error.get("explanation", ""),
                error_type=error.get("error_type", "General")
            ))

        return GradingResponse(
            overall_band=result["FINAL_OVERALL_BAND_SCORE"],
            scores=scores,
            positive_feedback=positive_feedback,
            critical_feedback=critical_feedback,
            language_errors=language_errors,
            band_upgrade_tip=result.get("BAND_UPGRADE_TIP", ""),
            detailed_result=result  # Include full result for reference
        )

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse Gemini response: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Grading failed: {str(e)}"
        )


@router.get("/criteria")
async def get_grading_criteria():
    """
    Get IELTS speaking grading criteria information.

    Returns:
        Detailed explanation of each criterion
    """
    return {
        "criteria": [
            {
                "name": "Fluency & Coherence",
                "key": "fluency",
                "description": "Ability to speak smoothly without hesitation, with logical organization",
                "band_9": "Speaks fluently with only rare repetition or self-correction"
            },
            {
                "name": "Lexical Resource",
                "key": "lexical",
                "description": "Range and accuracy of vocabulary used",
                "band_9": "Uses vocabulary with full flexibility and precision in all topics"
            },
            {
                "name": "Grammatical Range & Accuracy",
                "key": "grammar",
                "description": "Variety and correctness of grammatical structures",
                "band_9": "Uses a full range of structures naturally and appropriately"
            },
            {
                "name": "Pronunciation",
                "key": "pronunciation",
                "description": "Clarity and naturalness of speech",
                "band_9": "Uses a full range of pronunciation features with precision"
            }
        ],
        "band_scale": {
            "9": "Expert",
            "8": "Very Good",
            "7": "Good",
            "6": "Competent",
            "5": "Modest",
            "4": "Limited",
            "3": "Extremely Limited"
        }
    }
