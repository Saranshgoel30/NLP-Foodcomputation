# MMFOOD - Multilingual, Multimodal Food Knowledge Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)

A **production-ready**, enterprise-grade web application for searching recipes using natural language and voice input. Features multilingual support for 11 Indian languages, intelligent NLP parsing, and end-to-end voice search pipeline.

## ✨ Key Features

### 🎤 **Voice Search**
- **11 Language Support**: English, Hindi, Bengali, Telugu, Tamil, Marathi, Gujarati, Kannada, Malayalam, Odia, Punjabi
- **Speech-to-Text**: OpenAI Whisper integration with auto language detection
- **Sub-2s Latency**: Fast transcription with CUDA acceleration support
- **Hands-free Search**: Complete voice-to-results pipeline

### 🧠 **Intelligent NLP**
- **Natural Language Understanding**: Parse complex queries like "vegetarian paneer recipes without onion under 30 minutes"
- **Constraint Extraction**: Automatically detect cuisine, diet, course, ingredients, time limits
- **40+ Cuisines**: Punjabi, Bengali, South Indian, Chinese, Italian, and more
- **10+ Diets**: Vegetarian, Vegan, Jain, Halal, Gluten-free, etc.

### 🌐 **Translation**
- **Bidirectional**: Any language ↔ English
- **Culinary Terms**: Preserves food-specific terminology (paneer, dal, biryani, ghee)
- **Auto Detection**: Smart language identification via Unicode analysis
- **Graceful Fallback**: Works even if translation fails

### 🔍 **Smart Search**
- **9000+ Recipes**: Integrated with Food Graph API
- **Multi-field Matching**: Name, ingredients, cuisine, diet, course
- **100-500ms Latency**: Fast search with intelligent filtering
- **Dietary Constraints**: Jain, Vegan, Vegetarian, custom exclusions

### 🔒 **Production Ready**
- **Rate Limiting**: Different limits per endpoint (60/30/10 req/min)
- **Security Headers**: X-Frame-Options, CSP, XSS protection
- **Request Tracing**: Unique IDs for distributed debugging
- **Health Checks**: Comprehensive dependency status monitoring
- **API Documentation**: Interactive Swagger/OpenAPI docs

## 🏗️ Architecture

```
/app
  /web            # Next.js 14 (TypeScript, App Router)
  /api            # FastAPI (Python) - NLU, SPARQL, Translation, STT
  /workers        # Background jobs (STT, translation)
  /packages       # Shared types between web and API
  /infra          # Docker, docker-compose, NGINX config
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional)
- Redis (for job queue)

### Local Development

1. **Clone the repository**
   ```bash
   cd NLP-Foodcomputation
   ```

2. **Set up backend**
   ```bash
   cd app/api
   pip install -r requirements.txt
   cp .env.template .env
   # Edit .env with your GraphDB credentials
   python main.py
   ```

3. **Set up frontend**
   ```bash
   cd app/web
   npm install
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Docker Deployment

```bash
cd app/infra
docker-compose up -d
```

Access via: http://localhost

## 📖 Usage Examples

### 🔤 Text Search

```bash
# Simple ingredient search
"paneer recipes"

# With dietary constraints
"vegetarian chinese recipes"

# With exclusions
"dal recipes without onion and garlic"

# With time limits
"quick breakfast under 15 minutes"

# Complex queries
"Jain punjabi sabzi without potato under 30 minutes"
```

### 🎤 Voice Search

#### English
```
🎙️ "Find me chicken biryani recipes"
→ Returns: Biryani recipes with chicken
```

#### Hindi (हिंदी)
```
🎙️ "मुझे पनीर टिक्का की रेसिपी चाहिए"
→ Translated: "I want paneer tikka recipe"
→ Returns: Paneer tikka recipes
```

#### Bengali (বাংলা)
```
🎙️ "আমি মাছের রেসিপি চাই মশলা ছাড়া"
→ Translated: "I want fish recipe without spices"
→ Returns: Mild fish recipes
```

#### Tamil (தமிழ்)
```
🎙️ "எனக்கு சைவ உணவு சமையல் குறிப்புகள் வேண்டும்"
→ Translated: "I want vegetarian food recipes"
→ Returns: Vegetarian recipes
```

### 🎯 API Usage

```bash
# Text search
curl -X POST http://localhost:8080/search \
  -H "Content-Type: application/json" \
  -d '{"query": {"text": "paneer tikka", "lang": "en"}}'

# Voice search (with base64 audio)
curl -X POST http://localhost:8080/voice-search \
  -H "Content-Type: application/json" \
  -d '{"audio": "UklGRiQAAAB...", "format": "webm"}'

# Translation
curl -X POST http://localhost:8080/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "मुझे पनीर चाहिए", "sourceLang": "auto", "targetLang": "en"}'
```

### 🎛️ Search Filters

- **Diet**: Vegetarian, Vegan, Jain, Non-Vegetarian, Halal, Gluten-free
- **Cuisine**: Indian, Chinese, Italian, Mexican, Thai, and 35+ more
- **Course**: Breakfast, Lunch, Dinner, Snack, Dessert, Appetizer
- **Time**: Max cooking time or total preparation time
- **Inclusions**: Required ingredients
- **Exclusions**: Ingredients to avoid

## 🔧 Technology Stack

### Backend
- FastAPI (Python 3.11), GraphDB (SPARQL), Whisper/Vosk (STT), MarianMT (Translation)

### Frontend
- Next.js 14, TypeScript, Tailwind CSS, React Hook Form

## 📊 Performance

- **p50 Response Time**: <800ms (typed queries, warm)
- **SPARQL Query**: <200ms (GraphDB)
- **Translation**: <100ms (local models)

## 🔒 Security

- Environment-based configuration (no hardcoded secrets)
- CORS, rate limiting, input validation
- Request timeouts and circuit breakers

---

Built for multilingual food enthusiasts 🍲