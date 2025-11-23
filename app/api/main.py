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
import hashlib
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.api.search_client import SearchClient
from app.api.enhanced_query_parser import enhanced_parser
from app.api.llm_service import llm_service

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

# Lazy initialization of search client (only when first search request arrives)
# This allows LLM features to work immediately while search loads in background
client = None
client_loading = False

async def get_search_client():
    """Lazily initialize search client on first use"""
    global client, client_loading
    
    if client is not None:
        return client
    
    if not client_loading:
        client_loading = True
        print("📦 Initializing Typesense search client...")
        client = SearchClient()
        print("✅ Typesense search client ready!")
    
    return client

# Search results cache (in-memory, with TTL)
# Structure: {cache_key: {"results": [...], "timestamp": float, "total": int}}
search_cache = {}
CACHE_TTL = 300  # 5 minutes

def get_cache_key(query: str, filters: Dict, excluded: list) -> str:
    """Generate cache key from search parameters"""
    cache_data = {
        "query": query,
        "filters": filters,
        "excluded": sorted(excluded) if excluded else []
    }
    return hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()

def get_cached_results(cache_key: str) -> Optional[Dict]:
    """Get cached results if valid"""
    if cache_key in search_cache:
        cached = search_cache[cache_key]
        age = time.time() - cached["timestamp"]
        if age < CACHE_TTL:
            print(f"✅ Cache HIT (age: {age:.1f}s)")
            return cached
        else:
            print(f"⚠️  Cache EXPIRED (age: {age:.1f}s)")
            del search_cache[cache_key]
    return None

def cache_results(cache_key: str, results: list, total: int):
    """Cache search results"""
    search_cache[cache_key] = {
        "results": results,
        "timestamp": time.time(),
        "total": total
    }
    print(f"💾 Cached {total} results (key: {cache_key[:8]}...)")

# Response Models
class SearchResponse(BaseModel):
    hits: List[Dict[str, Any]]
    found: int
    page: int
    limit: int
    total_pages: int
    query: str
    duration_ms: float
    llm_enabled: bool
    translated_query: Optional[str] = None
    detected_language: Optional[str] = None
    excluded_count: Optional[int] = None
    fallback_message: Optional[str] = None
    is_fallback: Optional[bool] = False

class AutocompleteResponse(BaseModel):
    suggestions: List[str]

class HealthResponse(BaseModel):
    status: str
    version: str
    search_engine: str
    llm_provider: str

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "search_engine": "Typesense",
        "llm_provider": llm_service.primary_provider
    }

@app.get("/api/search", response_model=SearchResponse)
async def search_recipes(
    q: str = Query(..., description="Natural language search query"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    page: int = Query(1, ge=1, description="Page number"),
    cuisine: Optional[str] = Query(None, description="Filter by cuisine"),
    diet: Optional[str] = Query(None, description="Filter by diet"),
    course: Optional[str] = Query(None, description="Filter by course")
):
    """
    Search for recipes using LLM-powered natural language understanding
    
    Supports queries like:
    - "fali ki sabzi without tomatoes and onions"
    - "quick pasta under 20 minutes"
    - "chocolate cake no eggs"
    - "spicy chicken with garlic"
    - "jain recipes" (auto-excludes onion, garlic)
    - Multilingual queries in Hindi/Regional languages
    
    - **q**: Natural language search query (required)
    - **limit**: Results per page (default: 20, max: 100)
    - **page**: Page number (default: 1)
    - **cuisine**: Filter by cuisine type
    - **diet**: Filter by diet type
    - **course**: Filter by course type
    """
    try:
        start = time.time()
        
        # Step 1: Translate to English if needed
        translated_query = await enhanced_parser.translate_to_english(q)
        print(f"\n🌍 Translation Step:")
        print(f"  Original Query: {q}")
        print(f"  Translated to English: {translated_query}")
        
        # Step 2: Use LLM to extract dietary restrictions and exclusions
        parsed = await enhanced_parser.parse_query(translated_query)
        
        # Debug logging
        print(f"\n🔍 Query Analysis:")
        print(f"  Original: {q}")
        print(f"  Translated: {translated_query}")
        print(f"  Dish: {parsed.get('dish_name', 'N/A')}")
        print(f"  Excluded: {parsed.get('excluded_ingredients', [])}")
        print(f"  Dietary: {parsed.get('dietary_preferences', [])}")
        
        # Build filters
        filters = {}
        if cuisine and cuisine != "All":
            filters['cuisine'] = cuisine
        if diet and diet != "All":
            filters['diet'] = diet
        if course and course != "All":
            filters['course'] = course
        
        # Get search client
        search_client = await get_search_client()
        
        # Extract constraints
        excluded_ingredients = parsed.get('excluded_ingredients', [])
        
        # CRITICAL FIX: If user is searching "X without Y", search for X, then filter Y
        # Don't search for "X without Y" literally!
        dish_name = parsed.get('dish_name', '')
        if dish_name and excluded_ingredients:
            # User wants a specific dish without certain ingredients
            # Search for the dish, then apply exclusions
            search_query = dish_name
            print(f"  🎯 Optimized: Searching '{dish_name}' then filtering out {excluded_ingredients}")
        else:
            # Use translated query as-is
            search_query = translated_query
        
        # Generate cache key
        cache_key = get_cache_key(search_query, filters, excluded_ingredients)
        
        # Try cache first
        cached = get_cached_results(cache_key)
        
        if cached:
            # Serve from cache (instant!)
            all_hits = cached["results"]
            total_found = cached["total"]
            excluded_count = 0  # Already filtered
        else:
            # FETCH ALL RESULTS by iterating through Typesense pages
            print(f"\n🔍 Semantic Search (fetching ALL results): '{search_query}'")
            
            all_hits = []
            typesense_page = 1
            per_page = 250  # Typesense max
            max_pages = 40  # Safety: max 10,000 results (40 * 250)
            
            while typesense_page <= max_pages:
                # Modify search_client to accept page parameter
                results = search_client.search(
                    search_query,
                    limit=per_page,
                    filters=filters,
                    excluded_ingredients=excluded_ingredients,
                    required_ingredients=[],
                    time_constraint=parsed.get('cooking_time'),
                    page=typesense_page  # Pass page to search_client
                )
                
                hits = results.get('hits', [])
                if not hits:
                    break  # No more results
                
                all_hits.extend(hits)
                
                print(f"   📄 Fetched Typesense page {typesense_page}: {len(hits)} recipes (total: {len(all_hits)})")
                
                # If we got less than per_page, we've reached the end
                if len(hits) < per_page:
                    break
                
                typesense_page += 1
            
            total_found = len(all_hits)
            excluded_count = results.get('excluded_count', 0) if excluded_ingredients else 0
            
            print(f"✅ Found: {total_found} total recipes across {typesense_page} Typesense pages")
            if excluded_count > 0:
                print(f"   Excluded: {excluded_count} recipes")
            
            # Cache the results
            cache_results(cache_key, all_hits, total_found)
        
        # Apply pagination to cached/fetched results
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        final_hits = all_hits[start_idx:end_idx]
        
        print(f"📄 API Page {page}: Showing {len(final_hits)} recipes ({start_idx+1}-{min(end_idx, total_found)} of {total_found})")
        
        duration = (time.time() - start) * 1000
        total_pages = (total_found + limit - 1) // limit  # Ceiling division
        
        # Return results with pagination info
        return {
            "hits": final_hits,
            "found": total_found,  # Total results across all pages
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "query": q,
            "translated_query": translated_query if translated_query != q else None,
            "detected_language": parsed.get('language_detected'),
            "llm_enabled": enhanced_parser.use_llm,
            "excluded_count": excluded_count if excluded_count > 0 else None,
            "fallback_message": None,
            "is_fallback": False,
            "duration_ms": round(duration, 2)
        }
    except Exception as e:
        print(f"❌ Search error: {str(e)}")
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
        search_client = await get_search_client()
        suggestions = search_client.autocomplete_query(q, limit=limit)
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
        search_client = await get_search_client()
        results = search_client.autocomplete_ingredient(q, limit=limit)
        return {
            "results": [hit['document'] for hit in results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingredient lookup failed: {str(e)}")

@app.get("/api/translate")
async def translate_text(
    text: str = Query(..., description="Text to translate"),
    target_lang: str = Query("English", description="Target language")
):
    """
    Translate recipe-related text with food context preservation
    
    - **text**: Text to translate
    - **target_lang**: Target language (English, Hindi, etc.)
    """
    try:
        translated = await enhanced_parser.translate_from_english(text, target_lang)
        return {
            "original": text,
            "translated": translated,
            "target_language": target_lang
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@app.get("/api/analyze")
async def analyze_query(
    q: str = Query(..., description="Query to analyze")
):
    """
    Analyze query and extract detailed information
    
    Returns structured analysis including:
    - Intent detection
    - Ingredient extraction (included/excluded/implied)
    - Dietary preferences
    - Language detection
    - Translation
    
    - **q**: Query to analyze
    """
    try:
        # Get comprehensive analysis
        parsed = await enhanced_parser.parse_query(q)
        ingredients = await enhanced_parser.extract_smart_ingredients(q)
        
        # Translate if needed
        translated_query = await enhanced_parser.translate_to_english(q)
        
        return {
            "original_query": q,
            "translated_query": translated_query if translated_query != q else None,
            "parsed": parsed,
            "ingredients": ingredients,
            "parser_stats": enhanced_parser.get_stats()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/compare")
async def compare_llm_providers(
    q: str = Query(..., description="Query to compare across providers")
):
    """
    Compare LLM providers (DeepSeek vs Grok) on same query
    
    Only works if multiple providers are configured.
    Returns comparison data showing how each LLM interpreted the query.
    """
    try:
        if len(llm_service.all_providers) < 2:
            raise HTTPException(
                status_code=400, 
                detail="Need at least 2 LLM providers for comparison. Configure DEEPSEEK_API_KEY and XAI_API_KEY in .env"
            )
        
        # Parse with comparison enabled
        result = await llm_service.understand_query(q, enable_comparison=True)
        
        return {
            "query": q,
            "result": result,
            "comparison": result.get("_comparison"),
            "providers": [p.value for p in llm_service.all_providers]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

@app.get("/api/cache/clear")
async def clear_search_cache():
    """Clear the search results cache"""
    global search_cache
    cache_size = len(search_cache)
    search_cache.clear()
    return {
        "status": "success",
        "message": f"Cleared {cache_size} cached search results",
        "cache_size": 0
    }

@app.get("/api/cache/stats")
async def get_cache_stats():
    """Get search cache statistics"""
    return {
        "cache_size": len(search_cache),
        "cache_ttl_seconds": CACHE_TTL,
        "cached_queries": [
            {
                "key": key[:8] + "...",
                "results_count": entry["total"],
                "age_seconds": round(time.time() - entry["timestamp"], 1)
            }
            for key, entry in search_cache.items()
        ]
    }

@app.get("/api/stats")
async def get_stats():
    """Get platform statistics including LLM performance"""
    parser_stats = enhanced_parser.get_stats()
    llm_stats = llm_service.get_stats()
    
    return {
        "platform": {
            "total_recipes": "9600+",
            "cuisines": "15+",
            "diet_types": "7+",
            "search_type": "LLM-Enhanced Semantic Search",
        },
        "search_cache": {
            "cached_queries": len(search_cache),
            "ttl_seconds": CACHE_TTL
        },
        "llm": {
            "enabled": llm_stats["primary_provider"] != "none",
            "primary_provider": llm_stats["primary_provider"],
            "available_providers": llm_stats["available_providers"],
            "total_requests": llm_stats["request_count"],
            "total_cost_usd": llm_stats["total_cost_usd"],
            "avg_cost_per_request": llm_stats["avg_cost_per_request"],
            "cache_size": llm_stats["cache_size"],
            "comparison_enabled": llm_stats["comparison_enabled"]
        },
        "parser": parser_stats
    }

@app.post("/api/cache/clear")
async def clear_cache():
    """Clear LLM response cache (for testing/debugging)"""
    try:
        llm_service.clear_cache()
        return {"status": "success", "message": "Cache cleared", "timestamp": time.time()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache clear failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*80)
    print("🚀 FOOD INTELLIGENCE PLATFORM v3.0.0")
    print("="*80)
    print("\n📡 Starting API Server...")
    print("   Docs: http://localhost:8000/docs")
    print("   Health: http://localhost:8000/")
    print("   Stats: http://localhost:8000/api/stats")
    print("\n⏳ Loading services...\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
