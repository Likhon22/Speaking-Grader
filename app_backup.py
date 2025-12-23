"""
IELTS Speaking Grader MVP
A Streamlit application that simulates an IELTS speaking test with AI-powered grading.
"""

import time
import os
import json
import base64
import tempfile
import streamlit as st
from streamlit_mic_recorder import mic_recorder
from streamlit_mic_recorder import mic_recorder
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
    /* --- MOBILE APP SIMULATION --- */
    
    /* 1. Global Background (The "Desk") */
    .stApp {
        background-color: #263238; /* Dark background to make phone pop */
        background-image: radial-gradient(#37474F 1px, transparent 1px);
        background-size: 20px 20px;
    }

    /* 2. The Phone Frame */
    .block-container {
        max-width: 390px !important;
        width: 390px !important;
        background-color: #E0F2F1;
        padding: 2rem 1.5rem 2rem 1.5rem !important;
        margin: auto;
        border: 12px solid #111;
        border-radius: 40px;
        box-shadow: 0 0 0 2px #333, 20px 20px 50px rgba(0,0,0,0.5);
        height: 800px !important; /* Fixed Height */
        overflow-y: auto !important; /* Internal Scroll */
        color: #37474F !important;
    }

    /* Hide scrollbar to resemble a real phone */
    .block-container::-webkit-scrollbar {
        display: none;
    }
    .block-container {
        -ms-overflow-style: none;
        scrollbar-width: none;
    }
    
    /* Ensure all headers inside the phone are also dark */
    .block-container h1, .block-container h2, .block-container h3, .block-container p, .block-container li {
        color: #37474F !important;
    }

    /* 3. Hide Streamlit Elements */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    /* 4. Custom Components */
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
        color: #004D40;
    }
    
    .question-card {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,196,180, 0.15);
        text-align: center;
        margin: 1rem 0;
        border: 1px solid #B2DFDB;
    }
    
    /* Score Cards */
    .score-card {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        color: #333;
    }
    
    /* Buttons - Minty Style */
    .stButton > button {
        background: linear-gradient(135deg, #00C853 0%, #009688 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 30px;
        font-weight: bold;
        width: 100%;
        box-shadow: 0 4px 10px rgba(0, 200, 83, 0.3);
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 15px rgba(0, 200, 83, 0.4);
    }
    
    /* Record Button Simulation (The Mic Recorder is harder to style cleanly, but we try) */
    
    /* Bottom Nav Bar (Fake) */
    .bottom-nav {
        display: flex;
        justify-content: space-around;
        align-items: center;
        background: white;
        padding: 15px 0;
        border-radius: 0 0 25px 25px; /* Clip to phone bottom */
        margin-top: 30px;
        border-top: 1px solid #eee;
    }
    .nav-item {
        text-align: center;
        font-size: 0.8rem;
        color: #90A4AE;
        cursor: pointer;
    }
    .nav-item.active {
        color: #009688;
        font-weight: bold;
    }
    .nav-icon {
        font-size: 1.5rem;
        display: block;
        margin-bottom: 4px;
    }

    /* Mint UI Specifics */
    .progress-bg { background: #B2DFDB; }
    .skill-card { border: 1px solid #E0F2F1; }
    
    /* Expanders - Force Styling */
    .streamlit-expanderHeader, div[data-testid="stExpander"] details summary {
        background-color: white !important;
        color: #37474F !important;
        border-radius: 10px;
        border: 1px solid #B2DFDB;
    }
    
    .streamlit-expanderHeader:hover, div[data-testid="stExpander"] details summary:hover {
        color: #009688 !important;
    }
    
    .streamlit-expanderContent, div[data-testid="stExpander"] details {
        background-color: white !important;
        color: #37474F !important;
    }
    
    /* Donut Chart Fixes */
    .donut-chart { 
        width: 180px; 
        height: 180px;
        position: relative;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        /* Ensure background doesn't bleed */
        z-index: 1;
    }
    .donut-inner { 
        width: 140px; 
        height: 140px; 
        background-color: white !important;
        border-radius: 50%;
        position: absolute; /* Force it to overlay */
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 10; /* High z-index to stay on top */
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 10px rgba(0,0,0,0.05); /* Shadow to separate layers */
    }
    .overall-score { font-size: 3.5rem; }
    
    /* Progress Dots */
    .progress-dots {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 1rem;
    }
    .dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: #B2DFDB;
        transition: all 0.3s ease;
    }
    .dot.active {
        background-color: #009688;
        transform: scale(1.3);
    }
    .dot.completed {
        background-color: #00C853;
    }
    
    /* Thinking Animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    .thinking-text {
        animation: pulse 1.5s infinite;
        font-size: 1.2rem;
        color: #009688;
        text-align: center;
    }
    
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_whisper_model():
    """Load Whisper model with caching."""
    return whisper.load_model("base")


import asyncio
import edge_tts

# ... (other imports remain, but remove gTTS)

# ... (rest of code)

def text_to_speech(text: str, voice: str = "en-US-ChristopherNeural") -> bytes:
    """Convert text to speech using edge-tts (async) -> run synchronously."""
    # Create a temporary file to store the audio
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        tmp_file_path = tmp_file.name

    async def _generate_audio():
        communicate = edge_tts.Communicate(text, voice)  # Use selected voice
        await communicate.save(tmp_file_path)

    # Run the async function
    asyncio.run(_generate_audio())

    # Read the file back into bytes & cleanup
    with open(tmp_file_path, "rb") as f:
        audio_bytes = f.read()
    
    os.unlink(tmp_file_path)
    return audio_bytes


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
    
    system_instruction = """You are an EXPERT IELTS Speaking Examiner with 20+ years of experience. Your task is to provide a highly detailed, evidence-based evaluation of the student's speaking performance.

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

    user_prompt = f"Please analyze the following student transcripts against the IELTS Speaking Band Descriptors (FC, LR, GRA, P).\n\n{qa_text}\n\nBased on this, generate a score for each criterion and a final overall Band Score. BE STRICT. BE DETAILED."

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
                        "correction": {"type": "STRING"},
                        "explanation": {"type": "STRING"}
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
    """Display the grading results with the premium Minty UI."""
    if not result:
        return
    
    try:
        overall_score = float(result['FINAL_OVERALL_BAND_SCORE'])
        overall_percent = (overall_score / 9.0) * 100
    except:
        overall_score = 0.0
        overall_percent = 0
    
    # Determine status based on score
    if overall_score >= 8.0:
        status_label = "✨ Excellent work!"
        status_color = "#00C853"  # Green
        status_bg = "#E8F5E9"
    elif overall_score >= 6.5:
        status_label = "🌟 Very Good!"
        status_color = "#2962FF"  # Blue
        status_bg = "#E3F2FD"
    elif overall_score >= 5.0:
        status_label = "👍 Good Effort"
        status_color = "#FFAB00"  # Orange
        status_bg = "#FFF8E1"
    elif overall_score >= 4.0:
        status_label = "📚 Getting There"
        status_color = "#FF9100"  # Deep Orange
        status_bg = "#FFF3E0"
    elif overall_score >= 3.0:
        status_label = "🌱 Foundation Building"
        status_color = "#FF3D00"  # Red
        status_bg = "#FFEBEE"
    else:
        status_label = "💪 Don't Give Up!"
        status_color = "#D50000"  # Dark Red
        status_bg = "#FFEBEE"
    
    scores = result['SCORE_BREAKDOWN']
    
    # --- Overall Score Section ---
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0;">
        <div class="donut-chart" style="background: conic-gradient({status_color} var(--p), #E0F2F1 0); --p: {overall_percent}%;">
            <div class="donut-inner">
                <div class="overall-score" style="color: {status_color};">{overall_score}</div>
                <div class="overall-label">Band Score</div>
            </div>
        </div>
        <div style="margin-top: 20px;">
            <span style="background: {status_bg}; color: {status_color}; padding: 8px 20px; border-radius: 20px; font-weight: bold; font-size: 1.1rem;">
                {status_label}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Skills Breakdown")
    
    # --- Skills Grid ---
    col1, col2 = st.columns(2)
    
    metrics = [
        ("Pronunciation", scores.get('Pronunciation', 0)),
        ("Grammar", scores.get('Grammatical_Range_Accuracy', 0)),
        ("Vocabulary", scores.get('Lexical_Resource', 0)),
        ("Fluency", scores.get('Fluency_Coherence', 0)),
    ]
    
    for i, (label, score) in enumerate(metrics):
        try:
            score = float(score)
            percent = (score / 9.0) * 100
            color = "#00C853" if score >= 7 else "#FFAB00" if score >= 5 else "#FF3D00"
        except:
            score = 0
            percent = 0
            color = "#ddd"

        col = col1 if i % 2 == 0 else col2
        with col:
            st.markdown(f"""
            <div class="skill-card">
                <div class="skill-score" style="color: {color};">{score}</div>
                <div class="skill-label">{label}</div>
                <div class="progress-bg">
                    <div class="progress-fill" style="width: {percent}%; background: {color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    # --- Suggestions Section ---
    st.markdown("### 💡 Suggestions")
    
    # Filter for suggestions (Language Errors)
    errors = result.get('LANGUAGE_ERRORS', [])
    if errors:
        for err in errors:
            type_label = err.get('error_type', 'Tip')
            # Choose icon based on type
            icon_class = "icon-purple" if "Pronunciation" in type_label else "icon-yellow"
            icon_symbol = "✨" if "Pronunciation" in type_label else "⚠️"
            
            explanation = err.get('explanation', "Here is a better way to say it.")
            
            st.markdown(f"""
            <div class="suggestion-card">
                <div class="suggestion-header">
                    <div class="icon-box {icon_class}">{icon_symbol}</div>
                    <div style="font-weight: bold; color: #37474F;">{type_label}</div>
                </div>
                <div style="margin-bottom: 5px;">
                    <span style="color: #78909C;">You said:</span> 
                    <span style="color: #37474F; font-weight: 500;">"{err.get('original_phrase', '')}"</span>
                </div>
                <div style="margin-bottom: 10px;">
                    <span style="color: #00C853; font-weight: bold;">Better:</span> 
                    <span style="color: #2E7D32; font-weight: 600;">"{err.get('correction', '')}"</span>
                </div>
                <div class="correction-box">
                    <div style="display: flex; gap: 10px;">
                        <span>💡</span>
                        <span style="color: #455A64; font-size: 0.95rem;">{explanation}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No specific errors found! Great job.")
        
    # --- Detailed Report Expander ---
    with st.expander("📄 View Detailed Transcript Analysis"):
        st.markdown("### 📝 Full Transcript & Notes")
        st.write(result.get('POSITIVE_FEEDBACK'))
        st.write(result.get('CRITICAL_FEEDBACK'))
        st.markdown("---")
        st.write(result.get('BAND_UPGRADE_TIP'))




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
    if 'replay_count' not in st.session_state:
        st.session_state.replay_count = 0
    if 'voice' not in st.session_state:
        st.session_state.voice = "en-US-ChristopherNeural"  # Default Male
    
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
        
        # Voice Selection
        st.markdown("---")
        st.markdown("##### 🔊 Examiner Voice")
        voice_choice = st.radio(
            "Select voice:",
            ["👨 Male (Christopher)", "👩 Female (Jenny)"],
            horizontal=True,
            label_visibility="collapsed"
        )
        if "Male" in voice_choice:
            st.session_state.voice = "en-US-ChristopherNeural"
        else:
            st.session_state.voice = "en-US-JennyNeural"
    
    # Test in progress
    elif st.session_state.test_started and not st.session_state.test_complete:
        current_q = st.session_state.current_question
        question = IELTS_QUESTIONS[current_q]
        
        # Progress Dots
        dots_html = '<div class="progress-dots">'
        for i in range(len(IELTS_QUESTIONS)):
            if i < current_q:
                dots_html += '<div class="dot completed"></div>'
            elif i == current_q:
                dots_html += '<div class="dot active"></div>'
            else:
                dots_html += '<div class="dot"></div>'
        dots_html += '</div>'
        st.markdown(dots_html, unsafe_allow_html=True)
        
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
                audio_bytes = text_to_speech(question, st.session_state.voice)
                audio_base64 = base64.b64encode(audio_bytes).decode()
                st.markdown(f"""
                <audio autoplay>
                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                </audio>
                """, unsafe_allow_html=True)
                
                # ESTIMATE AUDIO DURATION: Avg speaking rate ~15 chars/sec
                estimated_duration = len(question) / 13 
                time.sleep(estimated_duration) # Wait while audio plays
                
                st.session_state.audio_played = True
                st.rerun() # Rerun to show the recorder
        
        # Replay button
        if st.button("🔄 Replay Question"):
            st.session_state.replay_count += 1
            audio_bytes = text_to_speech(question)
            audio_base64 = base64.b64encode(audio_bytes).decode()
            # unique key ensures re-render
            st.markdown(f"""
            <audio autoplay key={st.session_state.replay_count}>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🎙️ Record Your Answer")
        
        # Microphone recorder (Only show if audio has played)
        if st.session_state.audio_played:
            audio = mic_recorder(
                start_prompt="⏺️ Start Recording",
                stop_prompt="⏹️ Stop Recording",
                just_once=False,
                use_container_width=True,
                key=f"recorder_{current_q}"
            )
        else:
            st.info(" Please listen to the question first...")
            audio = None
        
        if audio:
            st.audio(audio['bytes'], format='audio/wav')
            
            # Transcribe and show
            with st.spinner("Transcribing your answer..."):
                transcript = transcribe_audio(audio['bytes'], whisper_model)
            
            st.markdown("**Your transcribed answer:**")
            
            # Scrollable Transcript Box (Fixed Height)
            with st.container(height=150):
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
        
        # Grade with Gemini - Animated Thinking
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown('<p class="thinking-text">� Analyzing Fluency & Coherence...</p>', unsafe_allow_html=True)
        
        # Run grading (this takes time)
        result = grade_submission(IELTS_QUESTIONS, st.session_state.answers)
        
        # Clear thinking animation
        thinking_placeholder.empty()
        
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
