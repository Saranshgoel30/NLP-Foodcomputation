# API Documentation

## Base URL

```
http://localhost:8000
```

## Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "graphdb": "connected",
  "stt": "available",
  "translation": "available"
}
```

---

### Search Recipes

```http
POST /search
```

**Request Body:**
```json
{
  "query": {
    "text": "Chinese chicken under 30 minutes",
    "lang": "en",
    "constraints": {
      "include": ["chicken"],
      "exclude": ["banana"],
      "cuisine": ["Chinese"],
      "diet": ["Non-Vegetarian"],
      "maxCookMinutes": 30,
      "course": ["Main Course"]
    }
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "iri": "http://example.org/recipe/123",
      "title": "Chinese Chicken Stir Fry",
      "cuisine": "Chinese",
      "diet": "Non-Vegetarian",
      "cookTime": "25 minutes",
      "ingredients": ["chicken", "soy sauce", "vegetables"],
      "instructions": "...",
      "score": 0.95
    }
  ],
  "query": {...},
  "translatedQuery": null,
  "count": 1,
  "durationMs": 234.5
}
```

---

### NLU Parse

```http
POST /nlu/parse
```

**Request Body:**
```json
{
  "text": "give me Jain dal without rajma",
  "lang": "en"
}
```

**Response:**
```json
{
  "constraints": {
    "include": ["dal"],
    "exclude": ["rajma"],
    "diet": ["Jain"]
  },
  "confidence": 0.85,
  "originalText": "give me Jain dal without rajma"
}
```

---

### Build SPARQL

```http
POST /sparql/build
```

**Request Body:**
```json
{
  "constraints": {
    "include": ["chicken"],
    "exclude": ["banana"],
    "maxCookMinutes": 30
  }
}
```

**Response:**
```json
{
  "sparql": "PREFIX fkg: <...> SELECT DISTINCT ... WHERE { ... }",
  "params": null
}
```

---

### Speech-to-Text

```http
POST /stt
```

**Request Body:**
```json
{
  "audio": "base64_encoded_audio_data",
  "format": "webm",
  "lang": "hi"
}
```

**Response:**
```json
{
  "transcript": "मुझे चीनी चिकन रेसिपी चाहिए",
  "confidence": 0.92,
  "lang": "hi"
}
```

---

### Translate

```http
POST /translate
```

**Request Body:**
```json
{
  "text": "मुझे चीनी चिकन रेसिपी चाहिए",
  "sourceLang": "hi",
  "targetLang": "en"
}
```

**Response:**
```json
{
  "translatedText": "I want Chinese chicken recipe",
  "sourceLang": "hi",
  "targetLang": "en"
}
```

---

## Error Responses

All endpoints return standard error format:

```json
{
  "error": "HTTPException",
  "message": "Detailed error message",
  "code": "400",
  "details": {...}
}
```

## Rate Limiting

- **Limit**: 60 requests per minute per IP
- **Header**: `X-RateLimit-Remaining`

## Response Headers

- `X-Process-Time`: Request processing time in milliseconds
- `X-RateLimit-Remaining`: Remaining requests in current window
