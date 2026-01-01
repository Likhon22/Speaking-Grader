# IELTS Speaking Grader - Mobile App API Documentation

**For Mobile Developers**

This document explains how to integrate the IELTS Speaking Grader backend API with your mobile application (Flutter, React Native, or Native iOS/Android).

---

## 🌐 API Server Information

**Base URL (Development):** `http://localhost:8000`  
**Base URL (Production):** `http://your-server-domain.com`

**Technology Stack:**

- FastAPI (Python backend)
- Whisper AI (Speech-to-Text)
- Google Gemini (AI Grading)
- Edge TTS (Text-to-Speech)

---

## 🎯 Complete User Flow

### Overview

```
1. User starts test → Select voice (male/female)
2. Question 1: Get audio → User records → Get transcript → Show to user
3. Question 2: Get audio → User records → Get transcript → Show to user
4. Submit both answers → Get AI grading results
```

### API Calls Sequence

```
GET  /api/test/start              (Step 1: Initialize test)
POST /api/tts/generate            (Step 2: Get question 1 audio)
POST /api/stt/transcribe          (Step 3: Transcribe answer 1)
POST /api/tts/generate            (Step 4: Get question 2 audio)
POST /api/stt/transcribe          (Step 5: Transcribe answer 2)
POST /api/grading/submit          (Step 6: Get AI scores)
```

---

## 📡 API Endpoints

### 1. Start Test Session

**Endpoint:** `GET /api/test/start`

**Purpose:** Initialize a new test session and get questions

**Parameters:**
| Name | Type | Required | Values | Default |
|------|------|----------|--------|---------|
| voice | query | No | `male` or `female` | `female` |

**Request Example:**

```http
GET /api/test/start?voice=female
```

**Response (200 OK):**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "questions": [
    {
      "id": 1,
      "text": "Describe a time when you helped someone",
      "tip": "Focus on using transition words like 'then', 'after', and 'however'."
    },
    {
      "id": 2,
      "text": "What is your opinion on social media?",
      "tip": "Try to give specific examples to support your opinion."
    }
  ],
  "voice_config": {
    "selected": "en-US-JennyNeural",
    "options": [
      {
        "id": "male",
        "name": "Male (Christopher)",
        "voice": "en-US-ChristopherNeural"
      },
      {
        "id": "female",
        "name": "Female (Jenny)",
        "voice": "en-US-JennyNeural"
      }
    ]
  }
}
```

**What to do with response:**

1. Save `session_id` - you'll need it for grading
2. Save `questions` array - these are the test questions
3. Save `voice_config.selected` - use this for TTS calls
4. Navigate to Question 1 screen

---

### 2. Generate Question Audio (Text-to-Speech)

**Endpoint:** `POST /api/tts/generate`

**Purpose:** Convert question text to speech audio

**Request Headers:**

```
Content-Type: application/json
```

**Request Body:**

```json
{
  "text": "Describe a time when you helped someone",
  "voice": "en-US-JennyNeural"
}
```

**Request Example (cURL):**

```bash
curl -X POST "http://localhost:8000/api/tts/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Describe a time when you helped someone",
    "voice": "en-US-JennyNeural"
  }' \
  --output question_audio.mp3
```

**Response:**

- **Content-Type:** `audio/mpeg`
- **Body:** MP3 audio file (binary bytes)
- **Size:** Typically 10-30 KB
- **Duration:** 3-8 seconds depending on text length

**What to do with response:**

1. Receive MP3 bytes
2. Load into your audio player
3. Play automatically or when user clicks play
4. User hears the question

**Mobile Code Example (Flutter):**

```dart
Future<Uint8List> getQuestionAudio(String questionText, String voice) async {
  final response = await http.post(
    Uri.parse('$baseUrl/api/tts/generate'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'text': questionText,
      'voice': voice,
    }),
  );

  if (response.statusCode == 200) {
    return response.bodyBytes; // MP3 audio
  } else {
    throw Exception('Failed to generate audio');
  }
}

// Play the audio
final audioBytes = await getQuestionAudio(question, selectedVoice);
await audioPlayer.play(BytesSource(audioBytes));
```

---

### 3. Transcribe User's Answer (Speech-to-Text)

**Endpoint:** `POST /api/stt/transcribe`

**Purpose:** Convert user's recorded audio to text

**Request Type:** `multipart/form-data`

**Form Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| audio_file | File | Yes | Audio file (WAV, MP3, M4A, WebM) |
| session_id | String | No | Session identifier for tracking |
| question_id | Integer | No | Question number (1 or 2) |

**Supported Audio Formats:**

- WAV (recommended)
- MP3
- M4A
- WebM

**File Size Limit:** 25 MB

**Request Example (cURL):**

```bash
curl -X POST "http://localhost:8000/api/stt/transcribe" \
  -F "audio_file=@user_recording.wav" \
  -F "session_id=550e8400-e29b-41d4-a716-446655440000" \
  -F "question_id=1"
```

**Response (200 OK):**

```json
{
  "transcript": "I remember when I helped my neighbor move to a new apartment. It was last summer and the weather was very hot. First we packed all the boxes then we loaded them into the truck. After that we drove to her new apartment and finally we unloaded everything. It took about 6 hours but I felt really good helping her.",
  "word_count": 58,
  "duration": 95.5
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| transcript | String | Complete text transcription |
| word_count | Integer | Number of words spoken |
| duration | Float | Estimated duration in seconds |

**Error Response (400 Bad Request):**

```json
{
  "detail": "Recording too short or silent. Please speak more clearly."
}
```

**What to do with response:**

1. Display `transcript` to user for review
2. Save transcript for this question
3. Show word count and duration as metadata
4. Allow user to re-record if needed

**Mobile Code Example (Flutter):**

```dart
Future<Map<String, dynamic>> transcribeAudio(File audioFile, String sessionId, int questionId) async {
  var request = http.MultipartRequest(
    'POST',
    Uri.parse('$baseUrl/api/stt/transcribe'),
  );

  // Add audio file
  request.files.add(
    await http.MultipartFile.fromPath(
      'audio_file',
      audioFile.path,
    ),
  );

  // Add metadata
  request.fields['session_id'] = sessionId;
  request.fields['question_id'] = questionId.toString();

  var response = await request.send();
  var responseData = await response.stream.bytesToString();

  if (response.statusCode == 200) {
    return jsonDecode(responseData);
  } else {
    throw Exception('Transcription failed');
  }
}

// Usage
final result = await transcribeAudio(recordedFile, sessionId, 1);
print('Transcript: ${result['transcript']}');
print('Words: ${result['word_count']}');
```

---

### 4. Submit Test for Grading

**Endpoint:** `POST /api/grading/submit`

**Purpose:** Get AI-powered grading for both answers

**Request Headers:**

```
Content-Type: application/json
```

**Request Body:**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "answers": [
    {
      "question_id": 1,
      "question_text": "Describe a time when you helped someone",
      "transcript": "I remember when I helped my neighbor move to a new apartment. It was last summer and the weather was very hot. First we packed all the boxes then we loaded them into the truck. After that we drove to her new apartment and finally we unloaded everything. It took about 6 hours but I felt really good helping her."
    },
    {
      "question_id": 2,
      "question_text": "What is your opinion on social media?",
      "transcript": "In my opinion social media has both positive and negative effects. On one hand it helps people stay connected with friends and family. On the other hand it can be addictive and waste a lot of time. I think we should use it moderately."
    }
  ]
}
```

**Processing Time:** 15-30 seconds (calls Google Gemini AI)

**Response (200 OK):**

```json
{
  "overall_band": 6.5,
  "scores": {
    "fluency": 6.5,
    "lexical": 7.0,
    "grammar": 6.0,
    "pronunciation": 6.5
  },
  "positive_feedback": [
    "Good use of time markers: 'First', 'then', 'After that', 'finally'",
    "Clear narrative structure in Question 1",
    "Balanced argument in Question 2 with 'On one hand...On the other hand'"
  ],
  "critical_feedback": [
    "Limited vocabulary range - mostly common words",
    "Some run-on sentences without proper punctuation",
    "Could use more complex sentence structures"
  ],
  "language_errors": [
    {
      "original": "the weather was very hot",
      "corrected": "the weather was scorching / extremely hot",
      "explanation": "Use stronger adjectives for Band 7+. 'Very' is overused in IELTS.",
      "error_type": "Vocabulary"
    },
    {
      "original": "it can be addictive and waste a lot of time",
      "corrected": "it can be addictive and can waste a lot of time",
      "explanation": "Parallel structure requires 'can' before both verbs",
      "error_type": "Grammar"
    }
  ],
  "band_upgrade_tip": "Practice using subordinate clauses (although, whereas, despite) to create more complex sentences and aim for Band 7+",
  "detailed_result": {
    // Full raw response from Gemini (optional to use)
  }
}
```

**Response Fields Explanation:**

| Field                | Type          | Description                        |
| -------------------- | ------------- | ---------------------------------- |
| overall_band         | Float         | Final IELTS band score (0-9 scale) |
| scores.fluency       | Float         | Fluency & Coherence score          |
| scores.lexical       | Float         | Vocabulary range score             |
| scores.grammar       | Float         | Grammar accuracy score             |
| scores.pronunciation | Float         | Pronunciation score (inferred)     |
| positive_feedback    | Array[String] | What student did well              |
| critical_feedback    | Array[String] | Areas to improve                   |
| language_errors      | Array[Object] | Specific mistakes with corrections |
| band_upgrade_tip     | String        | How to reach next band level       |

**Error Response (500 Internal Server Error):**

```json
{
  "detail": "GEMINI_API_KEY not configured. Please set it in .env file"
}
```

**What to do with response:**

1. Display overall band score prominently
2. Show score breakdown as bars/charts
3. List positive feedback with checkmarks
4. List critical feedback with warning icons
5. Show language errors with corrections
6. Display upgrade tip at the bottom

**Mobile Code Example (Flutter):**

```dart
Future<Map<String, dynamic>> submitForGrading(
  String sessionId,
  List<Map<String, dynamic>> answers,
) async {
  final response = await http.post(
    Uri.parse('$baseUrl/api/grading/submit'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'session_id': sessionId,
      'answers': answers,
    }),
  );

  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    throw Exception('Grading failed');
  }
}

// Usage
final answers = [
  {
    'question_id': 1,
    'question_text': questions[0]['text'],
    'transcript': transcript1,
  },
  {
    'question_id': 2,
    'question_text': questions[1]['text'],
    'transcript': transcript2,
  },
];

final gradingResult = await submitForGrading(sessionId, answers);
print('Band Score: ${gradingResult['overall_band']}');
```

---

## 🔄 Complete Workflow Example

### Step-by-Step Mobile App Implementation

```dart
class IELTSTestFlow {
  String baseUrl = 'http://your-server.com';
  String sessionId;
  List<Map<String, dynamic>> questions;
  String selectedVoice;
  List<String> transcripts = [];

  // Step 1: Start test
  Future<void> startTest(String voicePreference) async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/test/start?voice=$voicePreference'),
    );

    final data = jsonDecode(response.body);
    sessionId = data['session_id'];
    questions = List<Map<String, dynamic>>.from(data['questions']);
    selectedVoice = data['voice_config']['selected'];
  }

  // Step 2: Get question audio
  Future<Uint8List> getQuestionAudio(int questionIndex) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/tts/generate'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'text': questions[questionIndex]['text'],
        'voice': selectedVoice,
      }),
    );

    return response.bodyBytes;
  }

  // Step 3: Transcribe user's answer
  Future<String> transcribeAnswer(File audioFile, int questionId) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/api/stt/transcribe'),
    );

    request.files.add(
      await http.MultipartFile.fromPath('audio_file', audioFile.path),
    );
    request.fields['session_id'] = sessionId;
    request.fields['question_id'] = questionId.toString();

    var response = await request.send();
    var responseData = await response.stream.bytesToString();
    var result = jsonDecode(responseData);

    return result['transcript'];
  }

  // Step 4: Submit for grading
  Future<Map<String, dynamic>> submitTest() async {
    final answers = List.generate(questions.length, (index) => {
      'question_id': questions[index]['id'],
      'question_text': questions[index]['text'],
      'transcript': transcripts[index],
    });

    final response = await http.post(
      Uri.parse('$baseUrl/api/grading/submit'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'session_id': sessionId,
        'answers': answers,
      }),
    );

    return jsonDecode(response.body);
  }
}

// Usage in your app
final testFlow = IELTSTestFlow();

// 1. Start
await testFlow.startTest('female');

// 2. Question 1
final q1Audio = await testFlow.getQuestionAudio(0);
await audioPlayer.play(BytesSource(q1Audio));
// ... user records answer ...
final transcript1 = await testFlow.transcribeAnswer(recordedFile1, 1);
testFlow.transcripts.add(transcript1);

// 3. Question 2
final q2Audio = await testFlow.getQuestionAudio(1);
await audioPlayer.play(BytesSource(q2Audio));
// ... user records answer ...
final transcript2 = await testFlow.transcribeAnswer(recordedFile2, 2);
testFlow.transcripts.add(transcript2);

// 4. Submit
final results = await testFlow.submitTest();
// Display results screen
```

---

## ⚙️ Configuration

### Voice Options

Only **2 voices** are available:

| Voice ID                  | Name        | Gender | Accent   |
| ------------------------- | ----------- | ------ | -------- |
| `en-US-ChristopherNeural` | Christopher | Male   | American |
| `en-US-JennyNeural`       | Jenny       | Female | American |

**Usage:**

- User selects "male" or "female" in app
- Pass to `/api/test/start?voice=female`
- Use returned `voice_config.selected` for all TTS calls

### Audio Requirements

**For Recording (Upload to STT):**

- **Format:** WAV, MP3, M4A, or WebM
- **Max Size:** 25 MB
- **Recommended:** WAV, 16kHz, mono
- **Min Duration:** At least 3 words spoken

**From TTS (Download):**

- **Format:** MP3
- **Size:** 10-30 KB typical
- **Duration:** 3-8 seconds per question

---

## 🚨 Error Handling

### Common Errors

**1. Invalid Audio File (STT)**

```json
{
  "detail": "Invalid file type. Allowed: audio/wav, audio/mpeg, audio/mp4, audio/x-m4a, audio/webm"
}
```

**Solution:** Check file format before upload

**2. Recording Too Short (STT)**

```json
{
  "detail": "Recording too short or silent. Please speak more clearly."
}
```

**Solution:** Show user message to speak longer (minimum 3 words)

**3. File Too Large (STT)**

```json
{
  "detail": "File too large. Maximum size is 25MB"
}
```

**Solution:** Compress audio or reduce recording duration

**4. Gemini API Not Configured (Grading)**

```json
{
  "detail": "GEMINI_API_KEY not configured. Please set it in .env file"
}
```

**Solution:** Contact backend administrator

**5. Server Error (Any endpoint)**

```json
{
  "detail": "Transcription failed: [error details]"
}
```

**Solution:** Show error to user, allow retry

### Recommended Error Handling

```dart
try {
  final result = await transcribeAudio(file, sessionId, 1);
  // Success
} on SocketException {
  // No internet connection
  showError('No internet connection. Please check your network.');
} on TimeoutException {
  // Request timeout
  showError('Request timed out. Please try again.');
} on HttpException catch (e) {
  // HTTP error
  if (e.message.contains('400')) {
    showError('Audio file is invalid or too short.');
  } else if (e.message.contains('500')) {
    showError('Server error. Please try again later.');
  }
} catch (e) {
  // Other errors
  showError('Something went wrong: ${e.toString()}');
}
```

---

## 📊 Performance Guidelines

### Expected Response Times

| Endpoint              | Typical Time  | Notes                   |
| --------------------- | ------------- | ----------------------- |
| `/api/test/start`     | 100-300ms     | Fast, just returns data |
| `/api/tts/generate`   | 2-4 seconds   | Generates audio         |
| `/api/stt/transcribe` | 5-10 seconds  | Depends on audio length |
| `/api/grading/submit` | 15-30 seconds | Calls external AI API   |

### Optimization Tips

1. **Cache question audio** - Don't request same question audio twice
2. **Show loading indicators** - Especially for grading (takes 20-30s)
3. **Validate locally first** - Check file size/format before upload
4. **Handle timeouts** - Set 60s timeout for grading endpoint
5. **Offline mode** - Save recordings locally, upload when online

---

## 🔐 Security Notes

### API Security

- **No authentication required** for MVP
- All endpoints are public
- No user login/registration

### Data Privacy

- Audio files are **not stored** on server (deleted after transcription)
- Transcripts are sent to Google Gemini for grading
- Sessions are temporary (not persisted to database)

### Production Recommendations

- Add HTTPS/TLS encryption
- Implement rate limiting
- Add API key authentication
- Add user accounts and session management

---

## 🐛 Testing

### Health Check

Always verify server is running:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "services": {
    "whisper": "loaded",
    "gemini": "configured",
    "tts": "ready"
  }
}
```

### Quick Test

```bash
# 1. Start test
curl "http://localhost:8000/api/test/start?voice=female"

# 2. Generate audio
curl -X POST "http://localhost:8000/api/tts/generate" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello test","voice":"en-US-JennyNeural"}' \
  --output test.mp3

# 3. Check if audio plays
```

---

## 📞 Support

### Backend Server Information

**Start Server:**

```bash
python run_api.py
```

**Server Logs:** Check `api_server.log` for errors

**Documentation:** http://localhost:8000/docs (Swagger UI)

### Common Issues

**Issue:** Server not responding
**Solution:** Check if server is running, verify port 8000 is open

**Issue:** Transcription fails
**Solution:** Whisper model may not be loaded, restart server

**Issue:** Grading returns 500 error
**Solution:** Check GEMINI_API_KEY is set in backend `.env` file

---

## 📝 Summary Checklist

For mobile developers implementing this API:

- [ ] Understand the 6-step workflow
- [ ] Implement session start (GET /api/test/start)
- [ ] Implement TTS audio playback (POST /api/tts/generate)
- [ ] Implement audio recording on device
- [ ] Implement STT upload (POST /api/stt/transcribe)
- [ ] Implement grading submission (POST /api/grading/submit)
- [ ] Handle all error cases
- [ ] Add loading indicators (especially 20-30s for grading)
- [ ] Test with real audio recordings
- [ ] Implement retry mechanisms

---

**API Version:** 1.0.0  
**Last Updated:** January 1, 2026  
**Contact:** Backend Team
