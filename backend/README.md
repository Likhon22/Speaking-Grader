# IELTS Speaking Grader - FastAPI Backend

REST API backend for IELTS Speaking Grader mobile application.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create/update `.env` file:

```
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 3. Run the API Server

```bash
# Development mode with auto-reload
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Or use the run script
python run_api.py
```

### 4. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📋 API Endpoints

### Test Management

- `GET /api/test/start?voice=female` - Start new test session
- `GET /api/test/session/{session_id}` - Get session info
- `GET /api/test/questions` - Get all questions
- `DELETE /api/test/session/{session_id}` - Delete session

### Text-to-Speech (TTS)

- `POST /api/tts/generate` - Generate question audio
- `GET /api/tts/voices` - List available voices

### Speech-to-Text (STT)

- `POST /api/stt/transcribe` - Transcribe user's audio
- `GET /api/stt/model-info` - Get Whisper model info

### Grading

- `POST /api/grading/submit` - Submit answers for AI grading
- `GET /api/grading/criteria` - Get IELTS criteria info

---

## 🔄 Complete Workflow Example

### 1. Start Test

```bash
curl -X GET "http://localhost:8000/api/test/start?voice=female"
```

**Response:**

```json
{
  "session_id": "abc-123-def",
  "questions": [
    {
      "id": 1,
      "text": "Describe a time when you helped someone",
      "tip": "Focus on using transition words..."
    }
  ],
  "voice_config": {
    "selected": "en-US-JennyNeural",
    "options": [...]
  }
}
```

### 2. Generate Question Audio (TTS)

```bash
curl -X POST "http://localhost:8000/api/tts/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Describe a time when you helped someone",
    "voice": "en-US-JennyNeural"
  }' \
  --output question.mp3
```

Returns: MP3 audio file

### 3. Transcribe User Answer (STT)

```bash
curl -X POST "http://localhost:8000/api/stt/transcribe" \
  -F "audio_file=@user_recording.wav" \
  -F "session_id=abc-123-def" \
  -F "question_id=1"
```

**Response:**

```json
{
  "transcript": "I remember when I helped my neighbor move...",
  "word_count": 58,
  "duration": 135.5
}
```

### 4. Submit for Grading

```bash
curl -X POST "http://localhost:8000/api/grading/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123-def",
    "answers": [
      {
        "question_id": 1,
        "question_text": "Describe a time when...",
        "transcript": "I remember when I helped..."
      }
    ]
  }'
```

**Response:**

```json
{
  "overall_band": 6.5,
  "scores": {
    "fluency": 6.0,
    "lexical": 7.0,
    "grammar": 6.5,
    "pronunciation": 6.0
  },
  "positive_feedback": ["Good use of time markers"],
  "critical_feedback": ["Limited vocabulary range"],
  "language_errors": [...],
  "band_upgrade_tip": "Practice complex sentences"
}
```

---

## 📱 Mobile App Integration

### Flutter Example

```dart
// Start test
final response = await http.get(
  Uri.parse('http://your-server:8000/api/test/start?voice=female')
);

// Get question audio
final audioResponse = await http.post(
  Uri.parse('http://your-server:8000/api/tts/generate'),
  body: jsonEncode({
    'text': questionText,
    'voice': 'en-US-JennyNeural'
  })
);
Uint8List audioBytes = audioResponse.bodyBytes;

// Transcribe user recording
var request = http.MultipartRequest(
  'POST',
  Uri.parse('http://your-server:8000/api/stt/transcribe')
);
request.files.add(
  await http.MultipartFile.fromPath('audio_file', audioFile.path)
);
```

---

## 🐳 Docker Deployment

```bash
# Build image
docker build -t ielts-grader-api .

# Run container
docker run -p 8000:8000 --env-file .env ielts-grader-api
```

---

## 🔧 Configuration

### Voice Options

- `male` → `en-US-ChristopherNeural`
- `female` → `en-US-JennyNeural`
- `other` → `en-GB-SoniaNeural`

### File Limits

- Max audio file size: 25MB
- Supported formats: WAV, MP3, M4A, WebM

### Models

- **Whisper**: `base` model (faster, good accuracy)
- **Gemini**: Configured via `GEMINI_API_KEY`

---

## 📊 Project Structure

```
backend/
├── main.py              # FastAPI app entry
├── models/
│   └── schemas.py       # Pydantic models
└── routes/
    ├── test_routes.py   # Session management
    ├── tts_routes.py    # Text-to-speech
    ├── stt_routes.py    # Speech-to-text
    └── grading_routes.py # AI grading

services/                # Existing services (reused)
├── tts_service.py
├── stt_service.py
└── grading_service.py
```

---

## 🔐 Security Notes

- Set proper CORS origins in production (not `*`)
- Add authentication middleware for user management
- Use HTTPS in production
- Validate file uploads thoroughly
- Rate limit API endpoints

---

## 🐛 Troubleshooting

### Whisper model not loading

```bash
# Manually download model
python -c "import whisper; whisper.load_model('base')"
```

### CORS errors from mobile app

Update `backend/main.py`:

```python
allow_origins=["https://your-app-domain.com"]
```

### Port already in use

```bash
# Use different port
uvicorn backend.main:app --port 8001
```
