# 🍽️ Food Intelligence Platform

## AI-Powered Multilingual Recipe Discovery with Voice Search

**Next.js 14 • FastAPI • Typesense • DeepSeek AI • Whisper Speech-to-Text • 99 Languages • Lightning Fast**

A cutting-edge recipe search platform powered by advanced AI, semantic understanding, and natural language processing. Search recipes using text or voice in 99 languages with intelligent query understanding and smart filtering.

---

## 🌐 Live Demo

**Production URL**: http://43.205.136.103:3001

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://43.205.136.103:3001 | 3001 |
| Backend API | http://43.205.136.103:8001 | 8001 |
| API Documentation | http://43.205.136.103:8001/docs | 8001 |

### 🎤 Enabling Voice Search on Production

Voice search requires HTTPS or localhost due to browser security policies. To enable voice search on the production HTTP site, follow these steps:

#### For Google Chrome:
1. Open Chrome and navigate to: `chrome://flags/#unsafely-treat-insecure-origin-as-secure`
2. In the text box, add: `http://43.205.136.103:3001`
3. Change the dropdown from "Disabled" to **"Enabled"**
4. Click **"Relaunch"** to restart Chrome
5. Voice search will now work on the production site!

#### For Other Browsers:
- **Firefox**: Go to `about:config`, search for `media.getusermedia.insecure.enabled` and set to `true`
- **Edge**: Same as Chrome - use `edge://flags/#unsafely-treat-insecure-origin-as-secure`

> **Note**: For local development, voice search works automatically on `localhost:3000`.

---

## 📦 Input Data & Databases

### Recipe Database (`data/recipes.jsonl`)
- **9,668 recipes** with full metadata
- Fields: title, description, ingredients, instructions, cuisine, diet, course, prep_time, cook_time, image_url
- Source: Curated Indian & international recipe collection

### Ingredients Database (`data/ingredients.jsonl`)
- **4,217 ingredients** with aliases and substitutes
- Multilingual support (English, Hindi, regional languages)
- Used for smart ingredient matching and exclusion

### Query Templates (`data/queries.jsonl`)
- **10,000 search query templates**
- Used for autocomplete suggestions
- Covers common recipe search patterns

### Indexed Data (Typesense)
All data is indexed with **768-dimensional semantic embeddings** using the `paraphrase-multilingual-mpnet-base-v2` model for semantic search.

---

## 📤 Output Examples

### Search Query: "paneer without onion"

**Input:**
```json
{
  "query": "paneer without onion",
  "language": "English"
}
```

**LLM Processing Output:**
```json
{
  "base_query": "paneer",
  "include_ingredients": [],
  "exclude_ingredients": ["onion", "onions", "pyaaz", "kanda", "spring onion", "red onion", "white onion", "green onion", "shallots", "chopped onion", "sliced onion", "diced onion", "onion paste", "pearl onions", "pyaz", "onion cubes"],
  "tags": []
}
```

**Search Output:**
```json
{
  "found": 69,
  "total_pages": 4,
  "hits": [
    {
      "title": "Paneer Tikka Recipe",
      "cuisine": "North Indian",
      "diet": "Vegetarian",
      "prep_time": 20,
      "cook_time": 15
    },
    // ... 68 more results
  ]
}
```

### Multilingual Query: "प्याज़ के बिना दाल"

**Translation & Processing:**
```json
{
  "original_query": "प्याज़ के बिना दाल",
  "translated_query": "dal without onion",
  "detected_language": "Hindi",
  "base_query": "dal",
  "exclude_ingredients": ["onion", "pyaaz", "kanda", ...]
}
```

---

### 🎤 **Voice Search** (NEW!)
- **Speech-to-Text**: OpenAI Whisper API with 99 language support
- **Multilingual Recognition**: Speak in English, Hindi, Tamil, or any of 96+ languages
- **Real-time Transcription**: 1-2 second processing time
- **Smart Caching**: Reduced costs with intelligent cache system
- **Beautiful UI**: One-click recording with visual feedback

### 🧠 **LLM-Powered Intelligence**
- **Smart Query Understanding**: DeepSeek AI + xAI Grok for intelligent interpretation
- **Context-Aware Translation**: Understands food terminology in multiple languages
- **Dietary Awareness**: Auto-detects Jain, vegan, gluten-free requirements
- **Ingredient Extraction**: Identifies exclusions ("without garlic", "बिना प्याज़")
- **Automatic Fallback**: Seamless degradation with rule-based backup

### 🔍 **Advanced Search**
- **Hybrid Semantic Search**: 50% text matching + 50% semantic similarity
- **Natural Language Queries**: "dal without garlic", "quick pasta under 20 minutes"
- **Smart Pagination**: Fetch all results across pages, cache for instant access
- **Intelligent Filtering**: Automatic exclusion of unwanted ingredients
- **Search Optimization**: Dish name extraction + filter application

### 🌍 **Multilingual Support**
Search in 99 languages including all Indian languages:
- English • हिंदी • தமிழ் • ಕನ್ನಡ • বাংলা • اردو • മലയാളം • తెలుగు • ગુજરાતી • ਪੰਜਾਬੀ
- Plus 89 more: Spanish, French, German, Chinese, Japanese, Korean, Arabic, Portuguese...

### 🎯 **Smart Features**
- **Pagination System**: Fetch all results, cache for 5 minutes, serve 20 per page
- **Cost Tracking**: Monitor LLM and Whisper API usage in real-time
- **Response Caching**: LLM cache (1 hour), Search cache (5 minutes)
- **Cross-Validation**: Compare DeepSeek vs Grok results for quality assurance
- **Beautiful UI**: Modern dark theme with responsive design

### 📊 **Performance**
- **9,600+** recipes indexed with semantic embeddings
- **70ms** average search response time
- **133+** results for complex queries (e.g., "dal without garlic")
- **99** languages with automatic detection
- **<2s** voice transcription processing

---

## 🚀 Quick Start

### Prerequisites
- **Docker Desktop** (running)
- **Python 3.10+**
- **Node.js 18+**
- **API Keys** (optional but recommended):
  - DeepSeek AI (for LLM features)
  - OpenAI (for Whisper voice search)
  - xAI Grok (optional, for cross-validation)

### 1. Clone & Install

```bash
# Clone repository
git clone https://github.com/Saranshgoel30/NLP-Foodcomputation.git
cd NLP-Foodcomputation

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Configure Environment Variables

```bash
# Copy example config
cp .env.example .env

# Edit .env and add your API keys:
# - DEEPSEEK_API_KEY (for LLM intelligence)
# - OPENAI_API_KEY (for Whisper voice search)
# - XAI_API_KEY (optional, for Grok cross-validation)
```

**Get API Keys:**
- **DeepSeek**: https://platform.deepseek.com ($0.14/$0.55 per 1M tokens)
- **OpenAI**: https://platform.openai.com (Whisper: $0.006/min, GPT fallback)
- **xAI Grok**: https://console.x.ai (optional, $5/$15 per 1M tokens)

**Note**: System works without API keys but with limited features (no LLM intelligence or voice search)

### 3. Start Typesense Search Engine

```bash
# Start via Docker Compose
docker compose up -d

# Verify running
curl http://localhost:8108/health
```

### 4. Index Recipe Data (First Time Only)

```bash
# Generate embeddings and index all recipes
python scripts/index_recipes.py

# This takes a few minutes - generates semantic embeddings for 9,600+ recipes
```

### 5. Start Backend API

```bash
# From project root
python run_api.py

# Backend runs on http://localhost:8000
# API docs: http://localhost:8000/docs
# Stats: http://localhost:8000/api/stats
```

### 6. Start Frontend

```bash
cd frontend
npm run dev

# Frontend runs on http://localhost:3000
```

### 7. Start Searching! 🎉

Open http://localhost:3000 and try:
- **Text Search**: "dal without garlic", "jain recipes", "quick pasta"
- **Voice Search**: Click microphone button, speak naturally
- **Multilingual**: "pyaz ke bina sabzi", "பன்னீர் ரெசிபி"

---

## 🎤 Voice Search Guide

### Quick Start
1. Click the **blue microphone button** in search bar
2. Allow microphone permissions (first time only)
3. Speak your query: "I want dal without garlic"
4. Click mic again to stop recording
5. Watch it transcribe and search automatically!

### Supported Languages (99)
- **Indian**: English, Hindi, Tamil, Telugu, Bengali, Urdu, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Odia, Assamese
- **Global**: Spanish, French, German, Chinese, Japanese, Korean, Arabic, Portuguese, Russian, Italian, Dutch, Turkish, Vietnamese, Thai, and 75+ more

### Features
- **Automatic Language Detection**: No need to select language
- **Code-Switching Support**: Mix Hindi + English freely
- **Food Terminology**: Optimized for dish names and ingredients
- **Smart Caching**: Same query = instant transcription (no cost)
- **Cost Tracking**: Monitor usage at `/api/stats`

### Cost
- $0.006 per minute of audio (~$0.001 for 10 seconds)
- Average query: 5 seconds = $0.0005
- Monthly (1000 queries): ~$0.50
- With 50% cache hit: ~$0.25/month

**See**: `WHISPER_INTEGRATION_GUIDE.md` for detailed setup

---

## 🧠 LLM Intelligence Features

### What AI Powers:

**1. Query Understanding**
```
"jain recipes without tomatoes"
→ Detects: Jain dietary restriction
→ Auto-excludes: onion, garlic, potatoes, tomatoes
→ Returns: Filtered Jain-compliant recipes
```

**2. Multilingual Translation**
```
"pyaz aur lahsun ke bina sabzi"
→ Translates: "vegetables without onion and garlic"
→ Extracts exclusions: [onion, garlic]
→ Searches in English database
```

**3. Smart Filtering**
```
"dal without garlic"
→ Extracts dish: "dal"
→ Extracts exclusion: "garlic"
→ Strategy: Search "dal" → Filter garlic
→ Returns: 133 dal recipes without garlic
```

**4. Context Awareness**
```
"quick pasta under 20 minutes"
→ Understands: time constraint
→ Filters: total_time <= 20
→ Returns: Fast pasta recipes
```

### AI Provider Configuration

**Primary**: DeepSeek ($0.14/$0.55 per 1M tokens)
- Best cost/performance ratio
- Excellent multilingual support
- Food domain understanding

**Secondary**: xAI Grok ($5/$15 per 1M tokens)
- Cross-validation mode
- Quality assurance
- Automatic fallback

**Tertiary**: OpenAI GPT-4o-mini
- Final fallback option
- Stable and reliable

**Cost Tracking**: Visit `/api/stats` to monitor usage in real-time

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FOOD INTELLIGENCE PLATFORM                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   Next.js 14     │◄────►│   FastAPI        │◄────►│   Typesense      │
│   Frontend       │      │   Backend        │      │   Search Engine  │
│   (React/TS)     │      │   (Python)       │      │   (Vector DB)    │
└──────────────────┘      └──────────────────┘      └──────────────────┘
        │                          │                          │
        │                          ▼                          │
        │                  ┌──────────────┐                  │
        │                  │  LLM Service │                  │
        │                  ├──────────────┤                  │
        │                  │  DeepSeek    │                  │
        │                  │  xAI Grok    │                  │
        │                  │  OpenAI GPT  │                  │
        │                  └──────────────┘                  │
        │                          │                          │
        │                          ▼                          │
        │                  ┌──────────────┐                  │
        └─────────────────►│   Whisper    │                  │
                           │ Speech-to-Text│                  │
                           └──────────────┘                  │
                                                              │
                           ┌──────────────────────────────────┘
                           ▼
                    Semantic Embeddings
                    (paraphrase-multilingual-mpnet-base-v2)
```

### Tech Stack

**Frontend:**
- Next.js 14 (App Router)
- React 18 with TypeScript
- Tailwind CSS for styling
- Axios for API calls
- Lucide icons

**Backend:**
- FastAPI (async Python framework)
- Typesense Python client
- httpx for async LLM calls
- Sentence Transformers for embeddings
- PyTorch for ML models

**Search & AI:**
- Typesense 0.18.0 (vector search)
- DeepSeek AI (primary LLM)
- xAI Grok (secondary LLM)
- OpenAI Whisper (speech-to-text)
- OpenAI GPT-4o-mini (tertiary fallback)

**Infrastructure:**
- Docker & Docker Compose
- Environment-based config
- CORS-enabled APIs

---

## 📁 Project Structure

```
NLP-Foodcomputation/
├── app/api/                      # Backend FastAPI application
│   ├── main.py                   # Main API endpoints
│   ├── llm_service.py            # LLM integration (DeepSeek, Grok, GPT)
│   ├── llm_config.py             # LLM configuration & prompts
│   ├── whisper_service.py        # Speech-to-text service
│   ├── search_client.py          # Typesense client
│   ├── enhanced_query_parser.py  # Query understanding & parsing
│   └── translation_helper.py     # Language detection & translation
├── frontend/                     # Next.js frontend
│   ├── app/                      # App router
│   │   ├── page.tsx              # Main search page
│   │   └── layout.tsx            # Root layout
│   ├── components/               # React components
│   │   ├── SearchBar.tsx         # Search input with voice
│   │   ├── VoiceInput.tsx        # Microphone button
│   │   ├── RecipeCard.tsx        # Recipe display
│   │   └── FilterSidebar.tsx     # Filters
│   └── package.json
├── scripts/                      # Utility scripts
│   ├── index_recipes.py          # Index data to Typesense
│   ├── index_ingredients.py      # Index ingredients
│   └── test_*.py                 # Test scripts
├── data/                         # Recipe datasets
│   ├── recipes.jsonl             # 9,600+ recipes
│   ├── ingredients.jsonl         # Ingredient database
│   └── queries.jsonl             # Test queries
├── docker-compose.yml            # Typesense container
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
└── README.md                     # This file
```

---

## 🔍 Search Strategies

### 1. Hybrid Semantic Search (Current Implementation)
- **50% Text Matching** + **50% Semantic Similarity**
- Best balance of accuracy and relevance
- Handles typos and synonyms
- Fast response time (~70ms)

### 2. Dish Extraction + Filtering (Smart Mode)
```
Query: "dal without garlic"
→ Extract dish: "dal"
→ Extract exclusions: ["garlic", "lahsun", "lasun", "garlic paste", "garlic powder"]
→ Strategy: Search "dal" → Filter out garlic variants
→ Result: 133 recipes
```

### 3. Multilingual Translation
```
Query: "pyaz ke bina sabzi"
→ Detect language: Hindi
→ Translate: "vegetables without onion"
→ Search with exclusions
→ Return: Filtered results
```

---

## 📡 API Documentation

### Core Endpoints

#### Health Check
```bash
GET /
Response: {
  "status": "healthy",
  "version": "1.0.0",
  "search_engine": "Typesense",
  "llm_provider": "deepseek"
}
```

#### Search Recipes
```bash
GET /api/search?q=dal+without+garlic&page=1&limit=20

Response: {
  "hits": [...],
  "found": 133,
  "page": 1,
  "limit": 20,
  "total_pages": 7,
  "query": "dal without garlic",
  "translated_query": "lentils without garlic",
  "detected_language": "en",
  "excluded_count": 12
}
```

#### Voice Transcription
```bash
POST /api/transcribe
Content-Type: multipart/form-data
Body: audio file (mp3, wav, webm, m4a)

Response: {
  "status": "success",
  "transcription": "I want dal without garlic",
  "detected_language": "en",
  "duration_minutes": 0.08,
  "cost_usd": 0.00048,
  "processing_time_seconds": 1.5,
  "cached": false
}
```

#### Platform Statistics
```bash
GET /api/stats

Response: {
  "platform": {...},
  "search_cache": {...},
  "llm": {
    "enabled": true,
    "primary_provider": "deepseek",
    "total_requests": 245,
    "total_cost_usd": 0.0823,
    "avg_cost_per_request": 0.000336
  },
  "whisper": {
    "enabled": true,
    "total_transcriptions": 45,
    "total_cost_usd": 0.0192,
    "avg_cost_per_transcription": 0.000427
  }
}
```

Full API docs: http://localhost:8000/docs

---

## ⚙️ Configuration

### Environment Variables

```bash
# LLM APIs
DEEPSEEK_API_KEY=sk-xxx                    # Primary LLM
XAI_API_KEY=xai-xxx                        # Secondary LLM (optional)
OPENAI_API_KEY=sk-proj-xxx                 # Whisper + GPT fallback

# Typesense
TYPESENSE_HOST=localhost
TYPESENSE_PORT=8108
TYPESENSE_PROTOCOL=http
TYPESENSE_API_KEY=xyz

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000

# Feature Flags
ENABLE_LLM_PARSING=true
ENABLE_LLM_COMPARISON=true                 # Compare DeepSeek vs Grok
```

### Frontend Configuration

```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🧪 Testing

### Quick API Test
```bash
python test_api_quick.py
```

### Whisper Integration Test
```bash
python test_whisper.py
```

### Manual Testing
```bash
# Health check
curl http://localhost:8000/

# Search test
curl "http://localhost:8000/api/search?q=dal+without+garlic"

# Stats
curl http://localhost:8000/api/stats

# Clear caches
curl -X POST http://localhost:8000/api/cache/clear
```

---

## 📊 Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **Recipes Indexed** | 9,600+ | Semantic embeddings generated |
| **Search Latency** | ~70ms | Hybrid semantic search |
| **Languages Supported** | 99 | Voice + text search |
| **Search Accuracy** | 95%+ | With LLM intelligence |
| **Voice Processing** | 1-2s | Whisper transcription |
| **Cache Hit Rate** | 40-60% | LLM + Search caching |
| **Cost per Search** | $0.0003-0.0008 | DeepSeek + caching |
| **Cost per Voice Query** | $0.0005 | 5 seconds audio |

---

## 💰 Cost Breakdown

### Monthly Cost Estimates (1000 searches)

**With LLM Intelligence:**
- DeepSeek API: ~$0.30-0.40
- Whisper (if 50% voice): ~$0.25
- **Total: ~$0.55-0.65/month**

**With Caching (50% hit rate):**
- DeepSeek: ~$0.15-0.20
- Whisper: ~$0.13
- **Total: ~$0.28-0.33/month**

**Enterprise Scale (100k searches/month):**
- ~$28-33/month with caching
- ~$55-65/month without caching

**Note**: xAI Grok cross-validation adds ~2x cost but only in comparison mode (optional).

---

## 🚀 Deployment

### Current Production Deployment

The platform is deployed on **AWS Lightsail** (16GB RAM, 4 vCPU):

```
Server: 43.205.136.103
├── nlp-frontend (Port 3001) - Next.js Frontend
├── nlp-backend (Port 8001) - FastAPI Backend  
└── nlp-typesense (Port 8108 internal) - Typesense Search Engine
```

**Deployment Commands:**
```bash
# SSH into server
ssh -i aws-key.pem bitnami@43.205.136.103

# View running containers
sg docker -c 'docker ps'

# View logs
sg docker -c 'docker logs nlp-backend --tail 100'
sg docker -c 'docker logs nlp-frontend --tail 100'

# Restart services
cd ~/NLP-Foodcomputation
sg docker -c 'docker compose restart'
```

### Production Checklist
- [ ] Set production API keys in `.env`
- [ ] Update CORS origins for production domain
- [ ] Enable HTTPS for APIs
- [ ] Set up monitoring (see `/api/stats`)
- [ ] Configure rate limiting
- [ ] Set up error tracking
- [ ] Backup Typesense data volume
- [ ] Test voice search on mobile devices
- [ ] Monitor LLM costs daily

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f
```

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Total Recipes Indexed** | 9,668 |
| **Total Ingredients** | 4,217 |
| **Query Templates** | 10,000 |
| **Languages Supported** | 99 |
| **Average Search Time** | ~70ms |
| **Deployment Storage** | ~33 GB |

---

## 👥 Authors

- **Saransh Goel** - Ashoka University Capstone Project
- **Aarya Toshniwal** - Ashoka University Capstone Project

---

## 📧 Contact

For questions about this project:
- GitHub: [@Saranshgoel30](https://github.com/Saranshgoel30)
- Repository: [NLP-Foodcomputation](https://github.com/Saranshgoel30/NLP-Foodcomputation)
