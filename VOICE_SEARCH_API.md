# Voice Search & Translation API Documentation

## 🎯 Overview

Production-grade multilingual voice search system for recipe discovery. Supports 11 Indian languages with end-to-end AI pipeline integration.

---

## 📡 API Endpoints

### 1. Speech-to-Text (STT)

**POST** `/stt`

Convert audio recordings to text using OpenAI Whisper model.

#### Supported Languages
- **English** (en)
- **Hindi** (hi) - हिंदी
- **Bengali** (bn) - বাংলা
- **Telugu** (te) - తెలుగు
- **Marathi** (mr) - मराठी
- **Tamil** (ta) - தமிழ்
- **Gujarati** (gu) - ગુજરાતી
- **Kannada** (kn) - ಕನ್ನಡ
- **Malayalam** (ml) - മലയാളം
- **Odia** (or) - ଓଡ଼ିଆ
- **Punjabi** (pa) - ਪੰਜਾਬੀ

#### Audio Requirements
- **Formats**: webm, wav, mp3, ogg, m4a
- **Max Size**: 25MB
- **Encoding**: Base64

#### Request
```json
{
  "audio": "UklGRiQAAABXQVZFZm10IBAAAAABAAEA...",
  "format": "webm"
}
```

#### Response
```json
{
  "transcript": "मुझे पनीर टिक्का की रेसिपी चाहिए",
  "confidence": 0.95,
  "detectedLanguage": "hi"
}
```

#### Error Codes
- `400 Bad Request`: Invalid audio data, empty audio, or file too large
- `503 Service Unavailable`: Whisper model not loaded
- `500 Internal Server Error`: Transcription failed

---

### 2. Translation

**POST** `/translate`

Translate text between English and Indian languages with culinary term preservation.

#### Features
- **Auto Language Detection**: Set `sourceLang: "auto"`
- **Bidirectional**: Any language ↔ English
- **Culinary Terms**: Preserves food-specific terminology (paneer, dal, biryani, etc.)

#### Request
```json
{
  "text": "मुझे पनीर टिक्का की रेसिपी चाहिए",
  "sourceLang": "auto",
  "targetLang": "en"
}
```

#### Response
```json
{
  "translatedText": "I want paneer tikka recipe",
  "detectedSourceLang": "hi",
  "confidence": 0.92
}
```

#### Culinary Term Preservation
The system maintains accurate translations for:
- **Ingredients**: paneer, dal, ghee, atta, besan
- **Dishes**: biryani, tikka, korma, samosa
- **Techniques**: tadka, dum, tandoor

---

### 3. Voice Search (Complete Pipeline)

**POST** `/voice-search`

End-to-end voice search combining STT → Translation → NLP → Recipe Search.

#### Pipeline Flow
```
Audio Input
    ↓ [Whisper STT]
Native Language Text (e.g., Hindi)
    ↓ [Translation]
English Text
    ↓ [NLP Parser]
Structured Constraints
    ↓ [Recipe Search]
Matching Recipes
```

#### Request
```json
{
  "audio": "UklGRiQAAABXQVZFZm10IBAAAAABAAEA...",
  "format": "webm"
}
```

#### Response
Same as `/search` endpoint, with additional metadata:
```json
{
  "results": [...],
  "query": {
    "text": "I want paneer tikka recipe under 30 minutes",
    "lang": "en",
    "constraints": {
      "include": ["paneer", "tikka"],
      "maxCookMinutes": 30
    }
  },
  "translatedQuery": "मुझे 30 मिनट में पनीर टिक्का बनाने की रेसिपी चाहिए",
  "count": 12,
  "durationMs": 3420.5
}
```

#### Performance
- **STT**: ~500-1500ms (depends on audio length)
- **Translation**: ~50-200ms
- **NLP Parsing**: ~5-20ms
- **Search**: ~100-500ms
- **Total**: ~700-2200ms typical

---

## 🔧 Technical Implementation

### Whisper Model Configuration

```python
# Default: base model (74M params)
# Available models: tiny, base, small, medium, large
model = whisper.load_model("base")

# Auto language detection
result = model.transcribe(
    audio_path,
    language=None,  # Auto-detect
    task='transcribe'
)
```

### Translation Strategy

1. **Script Detection**: Identify language by Unicode range
2. **Culinary Terms**: Apply food-specific translation table
3. **Fallback**: Return original text if translation fails

### Error Handling

All endpoints include:
- ✅ Input validation with detailed error messages
- ✅ Graceful degradation (translation failures don't break search)
- ✅ Structured logging for debugging
- ✅ Retry logic for transient failures

---

## 📊 Usage Examples

### Example 1: Hindi Voice Search
```bash
# User speaks: "मुझे जल्दी बनने वाली पनीर की रेसिपी बताओ"
# (Give me quick paneer recipes)

POST /voice-search
{
  "audio": "<base64_audio>",
  "format": "webm"
}

# Response:
# - Detected: Hindi
# - Translated: "give me quick paneer recipes"
# - Parsed: include=[paneer], maxCookMinutes=30
# - Results: 15 paneer recipes under 30 minutes
```

### Example 2: Bengali Voice Search
```bash
# User speaks: "আমি মাছের রেসিপি চাই মশলা ছাড়া"
# (I want fish recipe without spices)

POST /voice-search
{
  "audio": "<base64_audio>",
  "format": "webm"
}

# Response:
# - Detected: Bengali
# - Translated: "I want fish recipe without spices"
# - Parsed: include=[fish], exclude=[spices]
# - Results: Mild fish recipes
```

### Example 3: Tamil Vegetarian Search
```bash
# User speaks: "எனக்கு சைவ உணவு சமையல் குறிப்புகள் வேண்டும்"
# (I want vegetarian food recipes)

POST /voice-search
{
  "audio": "<base64_audio>",
  "format": "webm"
}

# Response:
# - Detected: Tamil
# - Translated: "I want vegetarian food recipes"
# - Parsed: diet=[Vegetarian]
# - Results: 200+ vegetarian recipes
```

---

## 🚀 Frontend Integration

### 1. Record Audio
```typescript
const mediaRecorder = new MediaRecorder(stream, {
  mimeType: 'audio/webm'
});

const chunks: Blob[] = [];
mediaRecorder.ondataavailable = (e) => chunks.push(e.data);

mediaRecorder.onstop = async () => {
  const audioBlob = new Blob(chunks, { type: 'audio/webm' });
  const base64Audio = await blobToBase64(audioBlob);
  
  // Call voice search API
  const response = await fetch('/api/voice-search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      audio: base64Audio,
      format: 'webm'
    })
  });
  
  const results = await response.json();
  displayRecipes(results);
};
```

### 2. Display Transcription
```typescript
// Show what user said
<div className="transcription">
  <p className="original">"{data.translatedQuery}"</p>
  <p className="translated">→ "{data.query.text}"</p>
</div>
```

### 3. Show Detected Constraints
```typescript
// Visual pills for detected constraints
{data.query.constraints?.diet && (
  <Badge variant="success">
    <Leaf className="w-3 h-3" />
    {data.query.constraints.diet.join(', ')}
  </Badge>
)}

{data.query.constraints?.maxCookMinutes && (
  <Badge variant="info">
    <Clock className="w-3 h-3" />
    Under {data.query.constraints.maxCookMinutes}min
  </Badge>
)}
```

---

## 🔒 Security & Privacy

### Audio Data
- ✅ **Not stored**: Audio is transcribed and immediately discarded
- ✅ **In-memory processing**: Temporary files deleted after use
- ✅ **Size limits**: 25MB max to prevent abuse

### API Rate Limiting
- ⚠️ **TODO**: Implement rate limiting (100 requests/minute/IP)
- ⚠️ **TODO**: Add API key authentication for production

---

## 📈 Monitoring & Logging

All endpoints log structured data:

```json
{
  "event": "voice_search_complete",
  "total_duration_ms": 2150.5,
  "stt_ms": 1420.3,
  "translation_ms": 85.2,
  "nlp_ms": 12.8,
  "search_ms": 632.2,
  "results_count": 15,
  "original_language": "hi",
  "translated": true
}
```

### Key Metrics to Monitor
1. **STT Latency**: Should be < 2000ms
2. **Translation Accuracy**: Monitor user feedback
3. **NLP Confidence**: Track average confidence scores
4. **Error Rates**: < 1% transcription failures
5. **Language Distribution**: Track which languages users speak

---

## 🐛 Troubleshooting

### Issue: "Whisper model not loaded"
**Solution**: 
```bash
pip install openai-whisper
# Model downloads automatically on first use (~140MB for base)
```

### Issue: "Audio transcription failed"
**Causes**:
- Corrupted audio file
- Unsupported format
- Audio too long (>25MB)

**Solution**: Check audio format and size

### Issue: "Translation service unavailable"
**Behavior**: System gracefully degrades, uses original text for search

**Solution**: Check translation_adapter initialization in logs

---

## 🎓 Best Practices

1. **Microphone Quality**: Use noise-cancelling microphones for better accuracy
2. **Audio Duration**: Keep recordings under 30 seconds for best results
3. **Language Consistency**: Let Whisper auto-detect language instead of forcing
4. **Error Handling**: Always show user-friendly messages on failures
5. **Loading States**: Show visual feedback during processing (2-3 seconds)

---

## 📝 Next Steps

- [ ] Add caching for repeated phrases
- [ ] Implement real-time streaming transcription
- [ ] Support code-mixed queries (Hinglish: "paneer recipes under 30 min")
- [ ] Add pronunciation variations handling
- [ ] Implement confidence-based retry prompts

---

*Last Updated: November 11, 2025*
*Backend Version: 1.0.0*
*Whisper Model: base (multilingual)*
