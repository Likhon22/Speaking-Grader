"""
IELTS Speaking Grader MVP
A Streamlit application that simulates an IELTS speaking test with AI-powered grading.
"""

import os
import json
import tempfile
import base64
from io import BytesIO

import streamlit as st
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
from dotenv import load_dotenv
import whisper
from google import genai
from google.genai import types

from data import IELTS_QUESTIONS

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="IELTS Speaking Grader",
    page_icon="🎤",
    layout="centered"
)

# Custom CSS for premium look
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .question-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        color: #333333;
    }
    .score-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin: 0.5rem 0;
    }
    .score-breakdown {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .feedback-positive {
        background: linear-gradient(135deg, #a8e6cf 0%, #88d8b0 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: #155724;
    }
    .feedback-critical {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: #856404;
    }
    .error-card {
        background: #fff5f5;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.3rem 0;
        border-left: 4px solid #e74c3c;
        color: #721c24;
    }
    .tip-card {
        background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #333;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: bold;
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_whisper_model():
    """Load Whisper model with caching."""
    return whisper.load_model("base")


def text_to_speech(text: str) -> bytes:
    """Convert text to speech using gTTS and return audio bytes."""
    tts = gTTS(text=text, lang='en', slow=False)
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer.read()


def transcribe_audio(audio_bytes: bytes, model) -> str:
    """Transcribe audio bytes using Whisper."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_file.write(audio_bytes)
        tmp_file_path = tmp_file.name
    
    try:
        result = model.transcribe(tmp_file_path)
        return result["text"].strip()
    finally:
        os.unlink(tmp_file_path)


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
    
    system_instruction = """You are an official IELTS Speaking Examiner with deep knowledge of the official Band Descriptors (Band 1-9). Your task is to evaluate the student's spoken answers (provided as transcripts) based on the four main criteria.

***IELTS BAND SCORING CRITERIA (Context for your grading):***
1. **Fluency & Coherence (FC):** How smoothly and clearly the answer flows. Consider speech rate, hesitation, repetition, self-correction, and logical organization.
2. **Lexical Resource (LR):** Use of vocabulary and paraphrasing. Consider range, appropriateness, flexibility, and ability to discuss topics with precision.
3. **Grammatical Range & Accuracy (GRA):** Variety and correctness of grammar. Consider range of structures, accuracy, and control of complex sentences.
4. **Pronunciation (P):** How easily the speech is understood. Note: Since you only have a transcript, infer pronunciation issues only from highly confusing or garbled-looking STT output, but focus mainly on the other three criteria.

You must assign a Band Score (5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, or 9.0) for each of the four criteria and then calculate a FINAL OVERALL BAND SCORE.

Be strict but fair. Base your scoring on the actual content and quality of the responses."""

    user_prompt = f"Please analyze the following student transcripts against the IELTS Speaking Band Descriptors (FC, LR, GRA, P).\n\n{qa_text}\n\nBased on this, generate a score for each criterion and a final overall Band Score."

    # Define the schema strictly
    grade_schema = {
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
                        "correction": {"type": "STRING"}
                    }
                }
            },
            "BAND_UPGRADE_TIP": {"type": "STRING"}
        },
        "required": ["FINAL_OVERALL_BAND_SCORE", "SCORE_BREAKDOWN", "POSITIVE_FEEDBACK", "CRITICAL_FEEDBACK", "LANGUAGE_ERRORS", "BAND_UPGRADE_TIP"]
    }

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3,
                response_mime_type="application/json",
                response_schema=grade_schema
            )
        )
        
        # Parse JSON directly
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Error calling Gemini API: {str(e)}")
        return None


def display_results(result: dict):
    """Display the grading results with nice formatting."""
    if not result:
        return
    
    # Overall Score
    st.markdown(f"""
    <div class="score-card">
        <h1 style="margin:0; font-size: 3rem;">Band {result['FINAL_OVERALL_BAND_SCORE']}</h1>
        <p style="margin:0; font-size: 1.2rem;">Overall Band Score</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Score Breakdown
    st.markdown("### 📊 Score Breakdown")
    scores = result['SCORE_BREAKDOWN']
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Fluency & Coherence", scores['Fluency_Coherence'])
        st.metric("Grammatical Range & Accuracy", scores['Grammatical_Range_Accuracy'])
    with col2:
        st.metric("Lexical Resource", scores['Lexical_Resource'])
        st.metric("Pronunciation", scores['Pronunciation'])
    
    # Feedback
    st.markdown("### 💬 Feedback")
    
    st.markdown(f"""
    <div class="feedback-positive">
        <strong>✅ Strength:</strong> {result['POSITIVE_FEEDBACK']}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="feedback-critical">
        <strong>⚠️ Area for Improvement:</strong> {result['CRITICAL_FEEDBACK']}
    </div>
    """, unsafe_allow_html=True)
    
    # Language Errors
    if result.get('LANGUAGE_ERRORS'):
        st.markdown("### 🔍 Language Errors")
        for error in result['LANGUAGE_ERRORS']:
            st.markdown(f"""
            <div class="error-card">
                <strong>{error['error_type']}</strong><br>
                ❌ "{error['original_phrase']}" → ✅ "{error['correction']}"
            </div>
            """, unsafe_allow_html=True)
    
    # Band Upgrade Tip
    st.markdown(f"""
    <div class="tip-card">
        <strong>🚀 How to Improve:</strong><br>
        {result['BAND_UPGRADE_TIP']}
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main application logic."""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎤 IELTS Speaking Grader</h1>
        <p>Practice your speaking skills with AI-powered feedback</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'test_started' not in st.session_state:
        st.session_state.test_started = False
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'answers' not in st.session_state:
        st.session_state.answers = []
    if 'test_complete' not in st.session_state:
        st.session_state.test_complete = False
    if 'audio_played' not in st.session_state:
        st.session_state.audio_played = False
    
    # Load Whisper model
    with st.spinner("Loading speech recognition model..."):
        whisper_model = load_whisper_model()
    
    # Start screen
    if not st.session_state.test_started:
        st.markdown("""
        ### 📝 Instructions
        1. Click **Start Test** to begin
        2. Listen to each question (played via audio)
        3. Record your spoken answer
        4. Complete both questions to receive your score
        
        **Tip:** Speak clearly and aim for 1-2 minutes per answer.
        """)
        
        if st.button("🚀 Start Test", use_container_width=True):
            st.session_state.test_started = True
            st.session_state.audio_played = False
            st.rerun()
    
    # Test in progress
    elif st.session_state.test_started and not st.session_state.test_complete:
        current_q = st.session_state.current_question
        question = IELTS_QUESTIONS[current_q]
        
        # Question display
        st.markdown(f"### Question {current_q + 1} of {len(IELTS_QUESTIONS)}")
        st.markdown(f"""
        <div class="question-card">
            <p style="font-size: 1.1rem; margin: 0;">{question}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Play question audio
        if not st.session_state.audio_played:
            with st.spinner("🔊 Playing question..."):
                audio_bytes = text_to_speech(question)
                audio_base64 = base64.b64encode(audio_bytes).decode()
                st.markdown(f"""
                <audio autoplay>
                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                </audio>
                """, unsafe_allow_html=True)
                st.session_state.audio_played = True
        
        # Replay button
        if st.button("🔄 Replay Question"):
            audio_bytes = text_to_speech(question)
            audio_base64 = base64.b64encode(audio_bytes).decode()
            st.markdown(f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🎙️ Record Your Answer")
        
        # Microphone recorder
        audio = mic_recorder(
            start_prompt="⏺️ Start Recording",
            stop_prompt="⏹️ Stop Recording",
            just_once=False,
            use_container_width=True,
            key=f"recorder_{current_q}"
        )
        
        if audio:
            st.audio(audio['bytes'], format='audio/wav')
            
            # Transcribe and show
            with st.spinner("Transcribing your answer..."):
                transcript = transcribe_audio(audio['bytes'], whisper_model)
            
            st.markdown("**Your transcribed answer:**")
            st.info(transcript)
            
            # Store answer
            if len(st.session_state.answers) <= current_q:
                st.session_state.answers.append(transcript)
            else:
                st.session_state.answers[current_q] = transcript
            
            # Next question or submit
            col1, col2 = st.columns(2)
            
            if current_q < len(IELTS_QUESTIONS) - 1:
                with col1:
                    if st.button("➡️ Next Question", use_container_width=True):
                        st.session_state.current_question += 1
                        st.session_state.audio_played = False
                        st.rerun()
            else:
                with col1:
                    if st.button("✅ Submit Test", use_container_width=True):
                        st.session_state.test_complete = True
                        st.rerun()
    
    # Results screen
    elif st.session_state.test_complete:
        st.markdown("### 📋 Your Responses")
        for i, (q, a) in enumerate(zip(IELTS_QUESTIONS, st.session_state.answers)):
            with st.expander(f"Question {i+1}: {q[:50]}..."):
                st.write(a)
        
        st.markdown("---")
        
        # Grade with Gemini
        with st.spinner("🤖 AI is grading your responses..."):
            result = grade_submission(IELTS_QUESTIONS, st.session_state.answers)
        
        if result:
            display_results(result)
        
        st.markdown("---")
        
        # Restart option
        if st.button("🔄 Take Test Again", use_container_width=True):
            st.session_state.test_started = False
            st.session_state.current_question = 0
            st.session_state.answers = []
            st.session_state.test_complete = False
            st.session_state.audio_played = False
            st.rerun()


if __name__ == "__main__":
    main()
