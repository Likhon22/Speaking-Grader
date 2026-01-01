"""
Async Text-to-Speech Service wrapper for FastAPI
Wraps the synchronous TTS service to work with async routes
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from services.tts_service import text_to_speech as sync_text_to_speech

# Thread pool for running sync operations
executor = ThreadPoolExecutor(max_workers=4)


async def text_to_speech_async(text: str, voice: str = "en-US-ChristopherNeural") -> bytes:
    """
    Async wrapper for text-to-speech conversion.

    Args:
        text: Text to convert to speech
        voice: Voice ID to use

    Returns:
        Audio bytes (MP3 format)
    """
    loop = asyncio.get_event_loop()
    audio_bytes = await loop.run_in_executor(
        executor,
        sync_text_to_speech,
        text,
        voice
    )
    return audio_bytes
