"""
FastAPI Backend for Food Intelligence Platform
Provides REST APIs for search, autocomplete, and suggestions
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
import os
import time

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.api.search_client import SearchClient
from app.api.query_parser import query_parser

app = FastAPI(
    title="Food Intelligence API",
    description="Semantic search API for recipes with natural language understanding",
    version="2.0.0"
)

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize search client
client = SearchClient()

# Response Models
class SearchResponse(BaseModel):
    hits: List[Dict[str, Any]]
    found: int
    query: str
    duration_ms: float

class AutocompleteResponse(BaseModel):
    suggestions: List[str]

class HealthResponse(BaseModel):
    status: str
    version: str
    search_engine: str

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "search_engine": "Typesense"
    }

@app.get("/api/search", response_model=SearchResponse)
async def search_recipes(
    q: str = Query(..., description="Natural language search query"),
    limit: int = Query(50, ge=1, le=250, description="Number of results"),
    cuisine: Optional[str] = Query(None, description="Filter by cuisine"),
    diet: Optional[str] = Query(None, description="Filter by diet"),
    course: Optional[str] = Query(None, description="Filter by course")
):
    """
    Search for recipes using natural language understanding
    
    Supports queries like:
    - "fali ki sabzi without tomatoes and onions"
    - "quick pasta under 20 minutes"
    - "chocolate cake no eggs"
    - "spicy chicken with garlic"
    
    - **q**: Natural language search query (required)
    - **limit**: Number of results to return (default: 50, max: 250)
    - **cuisine**: Filter by cuisine type
    - **diet**: Filter by diet type
    - **course**: Filter by course type
    """
    try:
        start = time.time()
        
        # Parse natural language query
        parsed = query_parser.parse(q)
        
        # Build filters from UI selections
        filters = {}
        if cuisine and cuisine != "All":
            filters['cuisine'] = cuisine
        if diet and diet != "All":
            filters['diet'] = diet
        if course and course != "All":
            filters['course'] = course
        
        # Use clean query for search with smart filtering
        results = client.search(
            parsed['clean_query'] or q,  # Fallback to original if cleaning fails
            limit=limit,
            filters=filters,
            excluded_ingredients=parsed['excluded_ingredients'],
            required_ingredients=parsed['required_ingredients'],
            time_constraint=parsed['time_constraint']
        )
        
        duration = (time.time() - start) * 1000  # Convert to ms
        
        return {
            "hits": results['hits'],
            "found": results['found'],
            "query": q,
            "duration_ms": round(duration, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/autocomplete", response_model=AutocompleteResponse)
async def autocomplete_query(
    q: str = Query(..., description="Partial query for autocomplete"),
    limit: int = Query(5, ge=1, le=10, description="Number of suggestions")
):
    """
    Get query suggestions for autocomplete
    
    - **q**: Partial search query
    - **limit**: Number of suggestions (default: 5, max: 10)
    """
    try:
        suggestions = client.autocomplete_query(q, limit=limit)
        return {
            "suggestions": [hit['document']['query'] for hit in suggestions]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Autocomplete failed: {str(e)}")

@app.get("/api/ingredient")
async def lookup_ingredient(
    q: str = Query(..., description="Ingredient to lookup"),
    limit: int = Query(3, ge=1, le=10, description="Number of results")
):
    """
    Lookup ingredient information and substitutes
    
    - **q**: Ingredient name
    - **limit**: Number of results (default: 3, max: 10)
    """
    try:
        results = client.autocomplete_ingredient(q, limit=limit)
        return {
            "results": [hit['document'] for hit in results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingredient lookup failed: {str(e)}")

@app.get("/api/stats")
async def get_stats():
    """Get platform statistics"""
    return {
        "total_recipes": "9600+",
        "cuisines": "15+",
        "diet_types": "7+",
        "search_type": "Semantic + Keyword Hybrid"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
