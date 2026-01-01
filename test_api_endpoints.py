"""
API Testing Script
Tests all endpoints to ensure they're working correctly
"""
import requests
import json
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health check endpoint."""
    print("1️⃣ Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
    return response.status_code == 200


def test_start_test():
    """Test starting a new test."""
    print("2️⃣ Testing start test...")
    response = requests.get(f"{BASE_URL}/api/test/start?voice=female")
    print(f"   Status: {response.status_code}")
    data = response.json()
    session_id = data.get("session_id")
    print(f"   Session ID: {session_id}")
    print(f"   Questions: {len(data.get('questions', []))}\n")
    return session_id if response.status_code == 200 else None


def test_tts(text="Hello, this is a test"):
    """Test text-to-speech generation."""
    print("3️⃣ Testing TTS (Text-to-Speech)...")
    response = requests.post(
        f"{BASE_URL}/api/tts/generate",
        json={
            "text": text,
            "voice": "en-US-JennyNeural"
        }
    )
    print(f"   Status: {response.status_code}")
    print(f"   Audio size: {len(response.content)} bytes")

    # Save audio file
    if response.status_code == 200:
        with open("test_audio.mp3", "wb") as f:
            f.write(response.content)
        print(f"   ✅ Audio saved to test_audio.mp3\n")
        return True
    return False


def test_get_voices():
    """Test getting available voices."""
    print("4️⃣ Testing get voices...")
    response = requests.get(f"{BASE_URL}/api/tts/voices")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        voices = response.json().get("voices", [])
        print(f"   Available voices: {len(voices)}")
        for voice in voices[:3]:
            print(f"      - {voice['name']}")
    print()
    return response.status_code == 200


def test_stt():
    """Test speech-to-text (requires audio file)."""
    print("5️⃣ Testing STT (Speech-to-Text)...")

    # Check if test audio exists
    if not os.path.exists("test_audio.mp3"):
        print("   ⚠️ Skipping - no test audio file\n")
        return True

    files = {
        'audio_file': ('test.mp3', open('test_audio.mp3', 'rb'), 'audio/mpeg')
    }
    data = {
        'session_id': 'test-session',
        'question_id': 1
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/stt/transcribe",
            files=files,
            data=data
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Transcript: {result.get('transcript', '')}")
            print(f"   Word count: {result.get('word_count', 0)}\n")
            return True
        else:
            print(f"   Error: {response.text}\n")
            return False
    except Exception as e:
        print(f"   ⚠️ Error: {str(e)}\n")
        return False


def test_grading():
    """Test grading submission."""
    print("6️⃣ Testing grading...")

    # Check if GEMINI_API_KEY is set
    from dotenv import load_dotenv
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "your_api_key_here":
        print("   ⚠️ Skipping - GEMINI_API_KEY not configured\n")
        return True

    payload = {
        "session_id": "test-session",
        "answers": [
            {
                "question_id": 1,
                "question_text": "Describe a time when you helped someone",
                "transcript": "I remember when I helped my neighbor move to a new apartment. First, we packed all the boxes. Then we loaded them into the truck. It took about 6 hours."
            }
        ]
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/grading/submit",
            json=payload,
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Overall Band: {result.get('overall_band')}")
            print(f"   Scores: {result.get('scores')}\n")
            return True
        else:
            print(f"   Error: {response.text}\n")
            return False
    except Exception as e:
        print(f"   ⚠️ Error: {str(e)}\n")
        return False


def test_session_info(session_id):
    """Test getting session info."""
    if not session_id:
        print("7️⃣ Skipping session info test - no session ID\n")
        return True

    print("7️⃣ Testing get session info...")
    response = requests.get(f"{BASE_URL}/api/test/session/{session_id}")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Current question: {data.get('current_question')}")
        print(f"   Answers completed: {data.get('answers_completed')}\n")
        return True
    return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 IELTS Speaking Grader API - Test Suite")
    print("=" * 60)
    print()

    # Check if server is running
    try:
        requests.get(BASE_URL, timeout=2)
    except:
        print("❌ Server not running!")
        print(f"   Please start the server first:")
        print(f"   python run_api.py\n")
        return

    results = []

    # Run tests
    results.append(("Health Check", test_health()))

    session_id = test_start_test()
    results.append(("Start Test", session_id is not None))

    results.append(("TTS Generate", test_tts()))
    results.append(("Get Voices", test_get_voices()))
    results.append(("STT Transcribe", test_stt()))
    results.append(("Grading", test_grading()))
    results.append(("Session Info", test_session_info(session_id)))

    # Summary
    print("=" * 60)
    print("📊 Test Summary")
    print("=" * 60)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)

    print()
    print(f"Results: {passed_count}/{total_count} tests passed")
    print("=" * 60)


if __name__ == "__main__":
    main()
