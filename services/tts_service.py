"""
Text-to-Speech Service using Edge TTS.
"""
import os
import asyncio
import tempfile
import edge_tts


def text_to_speech(text: str, voice: str = "en-US-ChristopherNeural") -> bytes:
    """Convert text to speech using edge-tts (async) -> run synchronously."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        tmp_file_path = tmp_file.name

    async def _generate_audio():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(tmp_file_path)

    asyncio.run(_generate_audio())

    with open(tmp_file_path, "rb") as f:
        audio_bytes = f.read()
    
    os.unlink(tmp_file_path)
    return audio_bytes
