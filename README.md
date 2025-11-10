# MMFOOD - Multilingual, Multimodal Food Knowledge App

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready, multilingual + multimodal web application for searching recipes from a Food Knowledge Graph using natural language (typed or spoken), with support for Indian languages, precision filtering, and fast response times.

## 🌟 Features

- **Multilingual Support**: Search in English, Hindi, Marathi, Tamil, Telugu, Bengali, Gujarati, Kannada, Malayalam
- **Voice Input**: Speech-to-text with Whisper/Vosk for hands-free searching
- **Precision Filtering**: Aggressive false-positive reduction with strict SPARQL queries
- **Dietary Constraints**: Support for Jain, Vegan, Vegetarian, and custom exclusions
- **Time-based Search**: Filter by cooking time and total preparation time
- **Colloquial Queries**: Understands natural language like "Jain dal without rajma under 30 minutes"
- **Mobile-First UI**: Responsive design with accessibility support
- **Fast Performance**: <800ms p50 response time for typed queries

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

### Text Search

```
"Chinese chicken recipe under 30 minutes"
"Jain dal makhani without rajma"
"brown rice recipes"
"no onion no garlic sabzi"
```

### Voice Search

1. Click the microphone button
2. Speak your query in any supported language
3. Query is transcribed, translated (if needed), and executed

### Filters

- **Diet**: Vegetarian, Vegan, Jain, Non-Vegetarian
- **Cuisine**: Indian, Chinese, Italian, etc.
- **Course**: Breakfast, Lunch, Dinner, Snack
- **Time**: Max cooking/total time
- **Exclusions**: Ingredients to avoid (comma-separated)

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