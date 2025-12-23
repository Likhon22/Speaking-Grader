"""
IELTS Speaking Grader MVP
A Streamlit application that simulates an IELTS speaking test with AI-powered grading.
"""

import time
import base64
import streamlit as st
from streamlit_mic_recorder import mic_recorder
from dotenv import load_dotenv

# Local imports
from data import IELTS_QUESTIONS
from config import CSS_STYLES
from services import text_to_speech, load_whisper_model, transcribe_audio, grade_submission
from components import display_results, render_progress_dots

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="IELTS Speaking Grader",
    page_icon="🎤",
    layout="centered"
)

# Apply CSS styles
st.markdown(CSS_STYLES, unsafe_allow_html=True)


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
        st.session_state.voice = "en-US-ChristopherNeural"
    
    # Load Whisper model
    with st.spinner("Loading speech recognition model..."):
        whisper_model = load_whisper_model()
    
    # ==================== START SCREEN ====================
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
    
    # ==================== TEST IN PROGRESS ====================
    elif st.session_state.test_started and not st.session_state.test_complete:
        current_q = st.session_state.current_question
        question = IELTS_QUESTIONS[current_q]
        
        # Progress Dots
        st.markdown(render_progress_dots(current_q, len(IELTS_QUESTIONS)), unsafe_allow_html=True)
        
        # Question display
        st.markdown(f"### Question {current_q + 1} of {len(IELTS_QUESTIONS)}")
        st.markdown(f"""
        <div class="question-card">
            <p style="font-size: 1.1rem; margin: 0;">{question}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Tip Card (Contextual Hint)
        tips = [
            "Focus on using transition words like 'then', 'after', and 'however'.",
            "Try to give specific examples to support your opinion."
        ]
        st.markdown(f"""
        <div class="tip-card">
            <span class="tip-icon">💡</span>
            <span class="tip-text">{tips[current_q]}</span>
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
                
                # Wait for audio to finish
                estimated_duration = len(question) / 13 
                time.sleep(estimated_duration)
                
                st.session_state.audio_played = True
                st.rerun()
        
        # Replay button
        if st.button("🔄 Replay Question"):
            st.session_state.replay_count += 1
            audio_bytes = text_to_speech(question, st.session_state.voice)
            audio_base64 = base64.b64encode(audio_bytes).decode()
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
            st.info("Please listen to the question first...")
            audio = None
        
        if audio:
            st.audio(audio['bytes'], format='audio/wav')
            
            # Transcribe
            with st.spinner("Transcribing your answer..."):
                transcript = transcribe_audio(audio['bytes'], whisper_model)
            
            # Validation: Check if transcript is empty or too short
            words = transcript.split()
            if not transcript or len(words) < 3:
                st.warning("⚠️ Original audio was too short or silent. Please try recording again with a fuller answer.")
                # Clear any previous answer for this question to prevent accidental submission
                if len(st.session_state.answers) > current_q:
                    st.session_state.answers[current_q] = ""
                # We don't show the submission buttons if the answer is invalid
                st.stop() 

            st.markdown("**Your transcribed answer:**")
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
    
    # ==================== RESULTS SCREEN ====================
    elif st.session_state.test_complete:
        st.markdown("### 📋 Your Responses")
        for i, (q, a) in enumerate(zip(IELTS_QUESTIONS, st.session_state.answers)):
            with st.expander(f"Question {i+1}: {q[:50]}..."):
                st.write(a)
        
        st.markdown("---")
        
        # Grade with Gemini - Animated Thinking
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown('<p class="thinking-text">🧠 Analyzing Fluency & Coherence...</p>', unsafe_allow_html=True)
        
        result = grade_submission(IELTS_QUESTIONS, st.session_state.answers)
        
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
