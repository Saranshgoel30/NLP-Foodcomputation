#  MMFOOD - Multilingual Food Search

**Typesense-Powered  10+ Languages  Lightning Fast**

A modern food ingredient search engine powered by Typesense with semantic understanding and multilingual support.

##  Key Features

###  **Intelligent Search**
- **Semantic Search**: Understands meaning, not just keywords
- **Keyword Search**: Lightning-fast exact matching  
- **Hybrid Search**: Best of both worlds with smart fusion
- **70ms** average latency

###  **Multilingual Support**
Search in 10+ Indian languages:
- English  हद  தமழ  ಕನನಡ  বল  اردو  മലയള  తలగ  ગજરત  ਪਜਬ

###  **Performance**
- **993** food ingredients indexed
- **70ms** average response time
- **92.3%** search success rate
- **100%** multilingual coverage

##  Architecture

```

   Next.js     Frontend (localhost:3000)
   Frontend  

       

   FastAPI     Backend (localhost:8000)
   Backend   

       

  Typesense    Vector Search (localhost:8108)
   Search       Semantic embeddings
   Multilingual support
```

##  Project Structure

```
NLP-Foodcomputation/
 frontend/              # Next.js application
    app/              # App router pages
    components/       # React components
    lib/              # API client
 app/api/              # FastAPI backend
    main.py          # API endpoints
    typesense_client.py  # Typesense integration
    translation_adapter.py
    config.py
    models.py
 scripts/              # Utility scripts
     index_food_ingredients.py
     test_search_performance.py
```

##  Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Typesense 26+ (running on localhost:8108)

### 1. Start Typesense

```bash
# Using Docker
docker run -p 8108:8108 -v/tmp/typesense-data:/data typesense/typesense:26.0 \
  --data-dir /data --api-key=xyz --enable-cors
```

### 2. Start Backend

```bash
cd app/api
pip install -r requirements.txt
python main.py
```

Backend will be available at http://localhost:8000

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at http://localhost:3000

##  Search Strategies

### 1. **Semantic Search** (Default)
```python
result = typesense_client.semantic_search("healthy breakfast foods")
```
Uses 768-dimensional embeddings for meaning-based search.

### 2. **Keyword Search**
```python
result = typesense_client.keyword_search("amaranth seeds")
```
Fast exact and fuzzy matching.

### 3. **Hybrid Search** (Recommended)
```python
result = typesense_client.hybrid_search("protein rich", semantic_weight=0.7)
```
Combines semantic + keyword with Reciprocal Rank Fusion.

##  Configuration

Edit `app/api/.env`:

```env
# Typesense
TYPESENSE_HOST=localhost
TYPESENSE_PORT=8108
TYPESENSE_API_KEY=xyz
TYPESENSE_ENABLED=true

# Search Strategy
SEARCH_STRATEGY=hybrid
HYBRID_SEMANTIC_WEIGHT=0.7

# Translation
TRANSLATION_PROVIDER=marianMT

# API
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

##  Performance Metrics

| Metric | Value |
|--------|-------|
| Average Latency | 70ms |
| Success Rate | 92.3% |
| Indexed Items | 993 ingredients |
| Languages | 10+ |
| Search Strategies | 3 (semantic/keyword/hybrid) |

##  Testing

```bash
# Test search performance
cd scripts
python test_search_performance.py

# Test API integration
python test_api_integration.py
```

##  API Documentation

### Search Endpoint
```http
POST /search
Content-Type: application/json

{
  "query": {
    "text": "healthy breakfast",
    "lang": "en"
  },
  "limit": 10
}
```

### Health Check
```http
GET /health

Response:
{
  "status": "healthy",
  "version": "2.0.0",
  "focus": "typesense",
  "typesense": "connected"
}
```

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

##  License

MIT License - see LICENSE file for details

##  Acknowledgments

- Typesense for blazing-fast vector search
- sentence-transformers for semantic embeddings
- FastAPI for the robust backend framework
- Next.js for the modern frontend

---

**Built with  for multilingual food discovery**
