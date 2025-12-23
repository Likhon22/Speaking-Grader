"""
Speech-to-Text Service using OpenAI Whisper.
"""
import os
import tempfile
import streamlit as st
import whisper


@st.cache_resource
def load_whisper_model():
    """Load Whisper model with caching."""
    return whisper.load_model("base")


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
