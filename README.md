# Food Intelligence Platform (NLP-Foodcomputation)#  MMFOOD - Multilingual Food Search



This project is a semantic search engine for recipes, built with Typesense and Sentence Transformers.**Typesense-Powered  10+ Languages  Lightning Fast**

It replicates the core functionality of the `food-intelligence-platform` using a Python-first approach.

A modern food ingredient search engine powered by Typesense with semantic understanding and multilingual support.

## Prerequisites

##  Key Features

- Docker Desktop (must be running)

- Python 3.10+###  **Intelligent Search**

- **Semantic Search**: Understands meaning, not just keywords

## Setup- **Keyword Search**: Lightning-fast exact matching  

- **Hybrid Search**: Best of both worlds with smart fusion

1. **Install Dependencies**- **70ms** average latency

   ```bash

   pip install -r requirements.txt###  **Multilingual Support**

   pip install streamlitSearch in 10+ Indian languages:

   ```- English  हद  தமழ  ಕನನಡ  বল  اردو  മലയള  తలగ  ગજરત  ਪਜਬ



2. **Start Typesense**###  **Performance**

   ```bash- **993** food ingredients indexed

   docker compose up -d- **70ms** average response time

   ```- **92.3%** search success rate

- **100%** multilingual coverage

3. **Index Data**

   The recipe data is located in `data/updated_recipes.jsonl`.##  Architecture

   Run the indexer to generate embeddings and populate Typesense:

   ```bash```

   python scripts/index_recipes.py

   ```   Next.js     Frontend (localhost:3000)

   *Note: This process takes a few minutes as it generates embeddings for ~9600 recipes.*   Frontend  



## Usage       



### Web Interface (Streamlit)   FastAPI     Backend (localhost:8000)

Run the interactive search UI:   Backend   

```bash

python -m streamlit run app/ui.py       

```

  Typesense    Vector Search (localhost:8108)

### CLI Search   Search       Semantic embeddings

Run a quick search from the terminal:   Multilingual support

```bash```

python scripts/search.py "healthy breakfast with oats"

```##  Project Structure



## Architecture```

NLP-Foodcomputation/

- **Database**: Typesense (Vector Search) frontend/              # Next.js application

- **Embeddings**: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`    app/              # App router pages

- **Backend**: Python (`app/api/search_client.py`)    components/       # React components

- **Frontend**: Streamlit (`app/ui.py`)    lib/              # API client

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
