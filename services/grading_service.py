"""
Grading Service using Google Gemini API.
"""
import os
import json
import streamlit as st
from google import genai
from google.genai import types

# Local imports
from config import GEMINI_MODEL


# System prompt for IELTS grading
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


def grade_submission(questions: list, transcripts: list) -> dict:
    """Send questions and transcripts to Gemini for IELTS grading."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        st.error("⚠️ Please set your GEMINI_API_KEY in the .env file")
        return None
    
    client = genai.Client(api_key=api_key)
    
    # Build the combined Q&A text
    qa_text = ""
    for i, (q, t) in enumerate(zip(questions, transcripts), 1):
        qa_text += f"**Question {i}:** {q}\n**Student Answer {i}:** {t}\n\n"
    
    user_prompt = f"Please analyze the following student transcripts against the IELTS Speaking Band Descriptors (FC, LR, GRA, P).\n\n{qa_text}\n\nBased on this, generate a score for each criterion and a final overall Band Score. BE STRICT. BE DETAILED."

    try:
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
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Error calling Gemini API: {str(e)}")
        return None
