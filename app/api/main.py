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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.api.search_client import SearchClient
from app.api.query_parser import QueryParser
from app.api.enhanced_query_parser import enhanced_parser
from app.api.smart_recipe_filter import smart_filter

# Initialize both parsers - enhanced uses LLM, original is fallback
query_parser = QueryParser()  # Keep for backward compatibility

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
    Search for recipes using LLM-powered natural language understanding
    
    Supports queries like:
    - "fali ki sabzi without tomatoes and onions"
    - "quick pasta under 20 minutes"
    - "chocolate cake no eggs"
    - "spicy chicken with garlic"
    - "jain recipes" (auto-excludes onion, garlic)
    - Multilingual queries in Hindi/Regional languages
    
    - **q**: Natural language search query (required)
    - **limit**: Number of results to return (default: 50, max: 250)
    - **cuisine**: Filter by cuisine type
    - **diet**: Filter by diet type
    - **course**: Filter by course type
    """
    try:
        start = time.time()
        
        # Step 1: Translate to English if needed (ALWAYS translate non-English first)
        translated_query = await enhanced_parser.translate_to_english(q)
        print(f"\n🌍 Translation Step:")
        print(f"  Original Query: {q}")
        print(f"  Translated to English: {translated_query}")
        
        # Step 2: Use enhanced LLM-powered parser on translated query
        parsed = await enhanced_parser.parse_query(translated_query)
        
        # Debug logging
        print(f"\n🔍 LLM-Enhanced Query Analysis:")
        print(f"  Original: {q}")
        print(f"  English Translation: {translated_query}")
        print(f"  Method: {parsed.get('parsing_method', 'Unknown')}")
        print(f"  Language: {parsed.get('language_detected', 'Unknown')}")
        print(f"  Dish: {parsed.get('dish_name', 'N/A')}")
        print(f"  Excluded: {parsed.get('excluded_ingredients', [])}")
        print(f"  Required: {parsed.get('required_ingredients', [])}")
        print(f"  Dietary: {parsed.get('dietary_preferences', [])}")
        print(f"  Time: {parsed.get('cooking_time', 'N/A')}")
        print(f"  Cuisine: {parsed.get('cuisine_type', 'N/A')}\n")
        
        # Build filters from UI selections and parsed data
        filters = {}
        if cuisine and cuisine != "All":
            filters['cuisine'] = cuisine
        elif parsed.get('cuisine_type'):
            # Use LLM-detected cuisine if not specified
            filters['cuisine'] = parsed['cuisine_type']
            
        if diet and diet != "All":
            filters['diet'] = diet
        elif parsed.get('dietary_preferences'):
            # Use LLM-detected dietary preferences
            filters['diet'] = parsed['dietary_preferences'][0]
            
        if course and course != "All":
            filters['course'] = course
        
        # Use the English translated query for better search results
        search_query = translated_query
        
        # Get search client (lazy loads on first use)
        search_client = await get_search_client()
        
        # STAGE 1: Get broad search results (semantic search)
        # Get more results than requested for better filtering
        broad_limit = min(limit * 3, 150)  # Get 3x results for filtering
        
        print(f"🔍 Stage 1: Semantic search for '{search_query}' (getting {broad_limit} results)")
        
        try:
            results = search_client.search(
                search_query,
                limit=broad_limit,
                filters=filters,
                excluded_ingredients=[],  # Don't filter yet - let LLM do smart filtering
                required_ingredients=[],  # Don't filter yet - let LLM do smart filtering
                time_constraint=parsed.get('cooking_time')
            )
            
            # Validate results structure
            if not isinstance(results, dict) or 'hits' not in results:
                print(f"❌ Invalid results structure: {type(results)}")
                results = {'hits': [], 'found': 0}
                
        except Exception as e:
            print(f"❌ Search error: {str(e)}")
            import traceback
            traceback.print_exc()
            results = {'hits': [], 'found': 0}
        
        # STAGE 2: Smart LLM-powered filtering
        excluded_ingredients = parsed.get('excluded_ingredients', [])
        required_ingredients = parsed.get('required_ingredients', [])
        dietary_preferences = parsed.get('dietary_preferences', [])
        
        if (excluded_ingredients or required_ingredients or dietary_preferences) and results.get('hits'):
            print(f"🤖 Stage 2: LLM smart filtering")
            print(f"   Excluded: {excluded_ingredients}")
            print(f"   Required: {required_ingredients}")
            print(f"   Dietary: {dietary_preferences}")
            
            try:
                filtered_results = await smart_filter.filter_recipes_smart(
                    results['hits'],
                    original_query=q,
                    excluded_ingredients=excluded_ingredients,
                    required_ingredients=required_ingredients,
                    dietary_preferences=dietary_preferences
                )
                
                # Combine results: perfect first, then good, then possible
                final_hits = (
                    filtered_results['perfect_matches'] +
                    filtered_results['good_matches'] +
                    filtered_results['possible_matches']
                )[:limit]
            except Exception as e:
                print(f"❌ Smart filtering error: {str(e)}")
                import traceback
                traceback.print_exc()
                final_hits = results.get('hits', [])[:limit]
                final_found = len(final_hits)
                excluded_count = 0
            else:
                final_found = len(final_hits)
                excluded_count = len(filtered_results.get('excluded', []))
                print(f"✅ Stage 2 complete: {final_found} matches (excluded {excluded_count} recipes)")
        else:
            # No filtering needed
            final_hits = results.get('hits', [])[:limit]
            final_found = len(final_hits)
            excluded_count = 0
        
        duration = (time.time() - start) * 1000  # Convert to ms
        
        # Return with translation info for UI display
        return {
            "hits": final_hits,
            "found": final_found,
            "query": q,
            "translated_query": translated_query if translated_query != q else None,
            "detected_language": parsed.get('language_detected'),
            "llm_enabled": enhanced_parser.use_llm,
            "excluded_count": excluded_count if excluded_count > 0 else None,
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
        
        return {
            "query": q,
            "analysis": parsed,
            "ingredients": ingredients,
            "parser_stats": enhanced_parser.get_stats()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/stats")
async def get_stats():
    """Get platform statistics including LLM status"""
    parser_stats = enhanced_parser.get_stats()
    
    return {
        "total_recipes": "9600+",
        "cuisines": "15+",
        "diet_types": "7+",
        "search_type": "LLM-Enhanced Semantic Search",
        "llm_enabled": parser_stats["llm_enabled"],
        "llm_provider": parser_stats["llm_stats"]["provider"] if parser_stats["llm_enabled"] else "None",
        "llm_model": parser_stats["llm_stats"]["model"] if parser_stats["llm_enabled"] else "N/A"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
