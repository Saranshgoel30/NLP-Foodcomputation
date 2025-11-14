# 🚀 FoodKG Search - Multilingual Food Ingredient Search Engine# MMFOOD - Multilingual, Multimodal Food Knowledge Platform



**100x Faster • 10+ Languages • Semantic Understanding**[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

A revolutionary food ingredient search engine powered by Typesense vector search with support for multilingual queries across English, Hindi, Tamil, Kannada, and 10+ Indian languages.[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com)

[![Next.js 14](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)

![License](https://img.shields.io/badge/license-MIT-blue.svg)

![Python](https://img.shields.io/badge/python-3.10+-green.svg)A **production-ready**, enterprise-grade web application for searching recipes using natural language and voice input. Features multilingual support for 11 Indian languages, intelligent NLP parsing, and end-to-end voice search pipeline.

![Next.js](https://img.shields.io/badge/next.js-16.0-black.svg)

![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)## ✨ Key Features



## ✨ Features### 🎤 **Voice Search**

- **11 Language Support**: English, Hindi, Bengali, Telugu, Tamil, Marathi, Gujarati, Kannada, Malayalam, Odia, Punjabi

### 🧠 Intelligent Search- **Speech-to-Text**: OpenAI Whisper integration with auto language detection

- **Semantic Search**: Understands meaning, not just keywords- **Sub-2s Latency**: Fast transcription with CUDA acceleration support

- **Keyword Search**: Lightning-fast exact matching  - **Hands-free Search**: Complete voice-to-results pipeline

- **Hybrid Search**: Best of both worlds with RRF fusion

### 🧠 **Intelligent NLP**

### 🌍 Multilingual Support- **Natural Language Understanding**: Parse complex queries like "vegetarian paneer recipes without onion under 30 minutes"

Search in 10+ Indian languages natively:- **Constraint Extraction**: Automatically detect cuisine, diet, course, ingredients, time limits

- English • हिंदी • தமிழ் • ಕನ್ನಡ • বাংলা • اردو • മലയാളം • తెలుగు • ગુજરાતી • ਪੰਜਾਬੀ- **40+ Cuisines**: Punjabi, Bengali, South Indian, Chinese, Italian, and more

- **10+ Diets**: Vegetarian, Vegan, Jain, Halal, Gluten-free, etc.

### ⚡ Performance

- **70ms** average response time (100x faster than GraphDB)### 🌐 **Translation**

- **92.3%** search success rate- **Bidirectional**: Any language ↔ English

- **768-dim embeddings** for accurate semantic understanding- **Culinary Terms**: Preserves food-specific terminology (paneer, dal, biryani, ghee)

- **Auto Detection**: Smart language identification via Unicode analysis

### 🎨 Modern Features- **Graceful Fallback**: Works even if translation fails

- Real-time search with debouncing

- Voice input (speech-to-text)### 🔍 **Smart Search**

- Dark mode support- **9000+ Recipes**: Integrated with Food Graph API

- Smart filters (food groups, tags)- **Multi-field Matching**: Name, ingredients, cuisine, diet, course

- Multilingual ingredient cards- **100-500ms Latency**: Fast search with intelligent filtering

- Nutrition information display- **Dietary Constraints**: Jain, Vegan, Vegetarian, custom exclusions



## 🏗️ Architecture### 🔒 **Production Ready**

- **Rate Limiting**: Different limits per endpoint (60/30/10 req/min)

```- **Security Headers**: X-Frame-Options, CSP, XSS protection

┌─────────────────┐- **Request Tracing**: Unique IDs for distributed debugging

│  Next.js UI     │  ← Port 3000 (Real-time search, voice input)- **Health Checks**: Comprehensive dependency status monitoring

└────────┬────────┘- **API Documentation**: Interactive Swagger/OpenAPI docs

         │ REST API

┌────────▼────────┐## 🏗️ Architecture

│  FastAPI        │  ← Port 8000 (Search orchestration)

└────────┬────────┘```

         │/app

    ┌────┴────┐  /web            # Next.js 14 (TypeScript, App Router)

    │         │  /api            # FastAPI (Python) - NLU, SPARQL, Translation, STT

┌───▼──┐  ┌──▼───────┐  /workers        # Background jobs (STT, translation)

│Types │  │ GraphDB  │  /packages       # Shared types between web and API

│ense  │  │ (backup) │  /infra          # Docker, docker-compose, NGINX config

│:8108 │  └──────────┘```

└──────┘

```## 🚀 Quick Start



## 🚀 Quick Start### Prerequisites



### Prerequisites- Python 3.11+

- Node.js 20+

- Python 3.10+- Docker & Docker Compose (optional)

- Node.js 18+- Redis (for job queue)

- Docker (for Typesense)

### Local Development

### 1. Start Typesense Server

1. **Clone the repository**

```bash   ```bash

docker run -d -p 8108:8108 \   cd NLP-Foodcomputation

  -v typesense-data:/data \   ```

  typesense/typesense:0.25.1 \

  --data-dir /data \2. **Set up backend**

  --api-key=your_api_key \   ```bash

  --enable-cors   cd app/api

```   pip install -r requirements.txt

   cp .env.template .env

### 2. Start Backend   # Edit .env with your GraphDB credentials

   python main.py

```bash   ```

cd app/api

pip install -r requirements.txt3. **Set up frontend**

python main.py   ```bash

```   cd app/web

   npm install

Backend runs at: **http://localhost:8000**   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

   npm run dev

### 3. Start Frontend   ```



```bash4. **Access the application**

cd frontend   - Frontend: http://localhost:3000

npm install   - API: http://localhost:8000

npm run dev   - API Docs: http://localhost:8000/docs

```

### Docker Deployment

Frontend runs at: **http://localhost:3000**

```bash

### 4. Try It Out!cd app/infra

docker-compose up -d

Open http://localhost:3000 and search:```

- "Rice" (English)

- "दूध" (Milk in Hindi)Access via: http://localhost

- "தக்காளி" (Tomato in Tamil)

- Click the microphone for voice input!## 📖 Usage Examples



## 📁 Project Structure### 🔤 Text Search



``````bash

NLP-Foodcomputation/# Simple ingredient search

├── frontend/                    # Next.js UI"paneer recipes"

│   ├── app/

│   │   └── page.tsx            # Main search page# With dietary constraints

│   ├── components/             # React components"vegetarian chinese recipes"

│   │   ├── SearchResults.tsx

│   │   ├── IngredientCard.tsx# With exclusions

│   │   ├── SearchFilters.tsx"dal recipes without onion and garlic"

│   │   └── VoiceInput.tsx

│   ├── lib/# With time limits

│   │   └── api.ts              # API client"quick breakfast under 15 minutes"

│   └── types/

│       └── index.ts            # TypeScript definitions# Complex queries

│"Jain punjabi sabzi without potato under 30 minutes"

├── app/api/                     # FastAPI Backend```

│   ├── main.py                 # Main API with Typesense integration

│   ├── typesense_client.py     # Vector search client (1,044 lines)### 🎤 Voice Search

│   ├── graphdb_client.py       # GraphDB fallback

│   ├── translation_adapter.py  # Translation service#### English

│   ├── enrichment.py           # Data enrichment```

│   ├── middleware.py           # API middleware🎙️ "Find me chicken biryani recipes"

│   ├── models.py               # Pydantic models→ Returns: Biryani recipes with chicken

│   ├── config.py               # Configuration```

│   └── requirements.txt        # Python dependencies

│#### Hindi (हिंदी)

├── scripts/                     # Utility scripts```

│   ├── index_food_ingredients.py     # Index data from GraphDB🎙️ "मुझे पनीर टिक्का की रेसिपी चाहिए"

│   ├── test_search_performance.py    # Performance tests→ Translated: "I want paneer tikka recipe"

│   └── test_api_integration.py       # API integration tests→ Returns: Paneer tikka recipes

│```

├── docker-compose.typesense.yml # Typesense Docker config

├── test_results.json           # Performance test results#### Bengali (বাংলা)

├── .gitignore```

├── LICENSE🎙️ "আমি মাছের রেসিপি চাই মশলা ছাড়া"

└── README.md                   # This file→ Translated: "I want fish recipe without spices"

```→ Returns: Mild fish recipes

```

## 🔧 Configuration

#### Tamil (தமிழ்)

### Backend Configuration```

🎙️ "எனக்கு சைவ உணவு சமையல் குறிப்புகள் வேண்டும்"

Edit `app/api/.env`:→ Translated: "I want vegetarian food recipes"

→ Returns: Vegetarian recipes

```bash```

# Typesense

TYPESENSE_ENABLED=true### 🎯 API Usage

TYPESENSE_HOST=localhost

TYPESENSE_PORT=8108```bash

TYPESENSE_API_KEY=your_api_key# Text search

curl -X POST http://localhost:8080/search \

# Search Strategy  -H "Content-Type: application/json" \

SEARCH_STRATEGY=hybrid  # semantic, keyword, or hybrid  -d '{"query": {"text": "paneer tikka", "lang": "en"}}'

HYBRID_SEMANTIC_WEIGHT=0.7

# Voice search (with base64 audio)

# GraphDB (backup)curl -X POST http://localhost:8080/voice-search \

GRAPHDB_ENABLED=true  -H "Content-Type: application/json" \

GRAPHDB_URL=https://mmfood25-hackathon.tib.eu/sparql  -d '{"audio": "UklGRiQAAAB...", "format": "webm"}'

```

# Translation

### Frontend Configurationcurl -X POST http://localhost:8080/translate \

  -H "Content-Type: application/json" \

Create `frontend/.env.local`:  -d '{"text": "मुझे पनीर चाहिए", "sourceLang": "auto", "targetLang": "en"}'

```

```bash

NEXT_PUBLIC_API_URL=http://localhost:8000### 🎛️ Search Filters

```

- **Diet**: Vegetarian, Vegan, Jain, Non-Vegetarian, Halal, Gluten-free

## 📊 Performance Metrics- **Cuisine**: Indian, Chinese, Italian, Mexican, Thai, and 35+ more

- **Course**: Breakfast, Lunch, Dinner, Snack, Dessert, Appetizer

| Metric | Value | Comparison |- **Time**: Max cooking time or total preparation time

|--------|-------|------------|- **Inclusions**: Required ingredients

| Average Latency | **70ms** | 100x faster than GraphDB (7-13s) |- **Exclusions**: Ingredients to avoid

| Semantic Search | **70ms** | Understanding context |

| Keyword Search | **41ms** | Exact matching |## 🔧 Technology Stack

| Hybrid Search | **48ms** | Best of both |

| Success Rate | **92.3%** | 12/13 test queries passed |### Backend

| Multilingual | **100%** | All languages working |- FastAPI (Python 3.11), GraphDB (SPARQL), Whisper/Vosk (STT), MarianMT (Translation)



## 🧪 Testing### Frontend

- Next.js 14, TypeScript, Tailwind CSS, React Hook Form

### Run Performance Tests

## 📊 Performance

```bash

cd NLP-Foodcomputation- **p50 Response Time**: <800ms (typed queries, warm)

python scripts/test_search_performance.py- **SPARQL Query**: <200ms (GraphDB)

```- **Translation**: <100ms (local models)



### Run API Integration Tests## 🔒 Security



```bash- Environment-based configuration (no hardcoded secrets)

python scripts/test_api_integration.py- CORS, rate limiting, input validation

```- Request timeouts and circuit breakers



## 📦 Data---



### Indexed CollectionsBuilt for multilingual food enthusiasts 🍲

**food_ingredients_v1** (993 documents)
- English names + 10+ language translations
- 768-dimensional embeddings
- Metadata (food groups, tags, nutrition)

### Index New Data

```bash
python scripts/index_food_ingredients.py
```

## 🎯 API Endpoints

### Search
```
GET /search?text={query}&strategy={semantic|keyword|hybrid}
```

### Health Check
```
GET /health
```

### Documentation
```
GET /docs  # Swagger UI
GET /redoc  # ReDoc
```

## 🤝 Contributing

Contributions welcome! This project demonstrates:
- Modern vector search architecture
- Multilingual NLP techniques
- Real-time web applications
- Production-grade FastAPI backends
- Next.js best practices

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- **Typesense**: Vector search engine
- **GraphDB**: TIB mmfood25_hackathon repository
- **Sentence Transformers**: Multilingual embeddings
- **Next.js**: React framework
- **FastAPI**: Python web framework

## 📚 Documentation

- **PROJECT_COMPLETE.md**: Complete project overview
- **FRONTEND_README.md**: Detailed frontend documentation
- **app/api/requirements.txt**: Python dependencies
- **frontend/package.json**: Node.js dependencies

## 🌟 Key Technologies

- **Frontend**: Next.js 16, React, TypeScript, Tailwind CSS, Lucide Icons
- **Backend**: FastAPI, Python 3.10+, Pydantic
- **Search**: Typesense 0.25.1, Sentence Transformers
- **ML**: 768-dim multilingual embeddings (paraphrase-multilingual-mpnet-base-v2)
- **Database**: GraphDB (SPARQL endpoint)
- **DevOps**: Docker, Docker Compose

---

**Built with ❤️ for the future of food technology**

*Powered by Typesense • 768-dim embeddings • RRF fusion • 100x faster*

### 🚀 Ready to Use!

1. Start Typesense: `docker-compose -f docker-compose.typesense.yml up -d`
2. Start backend: `python app/api/main.py`
3. Start frontend: `npm run dev` (in frontend/)
4. Open: http://localhost:3000
5. **Search in any language!**
