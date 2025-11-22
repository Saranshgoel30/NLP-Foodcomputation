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
from app.api.query_expansion import query_expander

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
        
        # STAGE 0.5: REVOLUTIONARY Query Expansion (find MORE relevant results!)
        print(f"\n🚀 Stage 0.5: Query Expansion")
        expansion_result = await query_expander.expand_query(
            search_query,
            context={
                "excluded_ingredients": parsed.get('excluded_ingredients', []),
                "cuisine": parsed.get('cuisine_type'),
                "dietary": parsed.get('dietary_preferences', [])
            }
        )
        
        expanded_queries = expansion_result.get('expanded_queries', [])
        search_strategy = expansion_result.get('search_strategy', 'parallel')
        
        # Collect results from all expanded queries
        all_results = {}  # Dict to deduplicate by recipe ID
        
        # STAGE 1: Exhaustive multi-query search (optimized for maximum recall)
        print(f"\n🔍 Stage 1: Multi-query exhaustive search")
        print(f"   Strategy: {search_strategy}")
        print(f"   Queries: {len(expanded_queries)} variants")
        
        try:
            # Execute all expanded queries
            for i, exp_query in enumerate(expanded_queries[:5], 1):  # Limit to top 5 for performance
                query_text = exp_query.get('query', '')
                weight = exp_query.get('weight', 1.0)
                
                print(f"   Query {i}/{min(len(expanded_queries), 5)}: '{query_text}' (weight: {weight})")
                
                try:
                    query_results = search_client.search(
                        query_text,
                        limit=250,  # Always fetch maximum for best coverage
                        filters=filters,
                        excluded_ingredients=[],  # Don't filter yet - let LLM do smart filtering
                        required_ingredients=[],  # Don't filter yet - let LLM do smart filtering
                        time_constraint=parsed.get('cooking_time')
                    )
                    
                    # Deduplicate and weight results
                    for hit in query_results.get('hits', []):
                        recipe_id = hit.get('document', {}).get('id') or hit.get('document', {}).get('name', '')
                        
                        if recipe_id not in all_results:
                            # First time seeing this recipe
                            if 'document' not in hit:
                                hit['document'] = {}
                            hit['document']['_query_weight'] = weight
                            hit['document']['_found_by'] = query_text
                            all_results[recipe_id] = hit
                        else:
                            # Recipe seen before, boost weight if this query has higher weight
                            existing_weight = all_results[recipe_id]['document'].get('_query_weight', 0)
                            if weight > existing_weight:
                                all_results[recipe_id]['document']['_query_weight'] = weight
                                all_results[recipe_id]['document']['_found_by'] = query_text
                    
                    print(f"      → Found {len(query_results.get('hits', []))} recipes")
                    
                except Exception as e:
                    print(f"      ❌ Query failed: {str(e)}")
                    continue
            
            # Convert dict back to list and sort by combined score
            results_list = list(all_results.values())
            
            # Sort by: query_weight * typesense_score
            for hit in results_list:
                typesense_score = hit.get('text_match', 0)
                query_weight = hit.get('document', {}).get('_query_weight', 1.0)
                hit['_combined_score'] = typesense_score * query_weight
            
            results_list.sort(key=lambda x: x.get('_combined_score', 0), reverse=True)
            
            results = {
                'hits': results_list,
                'found': len(results_list)
            }
            
            print(f"\n✅ Stage 1 complete: Found {len(results_list)} UNIQUE recipes across {min(len(expanded_queries), 5)} queries")
            print(f"   Deduplication: {sum(len(all_results) for _ in expanded_queries[:5])} total → {len(results_list)} unique")
                
        except Exception as e:
            print(f"❌ Search error: {str(e)}")
            import traceback
            traceback.print_exc()
            results = {'hits': [], 'found': 0}
        
        # STAGE 2: Light LLM-powered filtering (only for CRITICAL constraints)
        excluded_ingredients = parsed.get('excluded_ingredients', [])
        required_ingredients = parsed.get('required_ingredients', [])
        dietary_preferences = parsed.get('dietary_preferences', [])
        
        # Only apply LLM filtering if there are CRITICAL exclusions (allergies, dietary restrictions)
        has_critical_constraints = bool(excluded_ingredients)
        
        if has_critical_constraints and results.get('hits') and len(results.get('hits', [])) > 10:
            print(f"🤖 Stage 2: Light LLM filtering (critical constraints only)")
            print(f"   Excluded: {excluded_ingredients}")
            print(f"   Note: Required ingredients and dietary preferences used for ranking, not filtering")
            
            try:
                # ONLY filter for excluded ingredients - be lenient with everything else
                filtered_results = await smart_filter.filter_recipes_smart(
                    results['hits'],
                    original_query=q,
                    excluded_ingredients=excluded_ingredients,
                    required_ingredients=[],  # Don't filter by required - use for ranking only
                    dietary_preferences=[]  # Don't filter by dietary - use for ranking only
                )
                
                # Combine results: perfect first, then good, then possible
                # Be MORE inclusive - accept good and possible matches
                final_hits = (
                    filtered_results['perfect_matches'] +
                    filtered_results['good_matches'] +
                    filtered_results['possible_matches']  # Include possible matches too!
                )[:limit]
                
                final_found = len(final_hits)
                excluded_count = len(filtered_results.get('excluded', []))
                print(f"✅ Stage 2 complete: {final_found} matches (excluded {excluded_count} recipes with allergens)")
            except Exception as e:
                print(f"❌ Smart filtering error: {str(e)}")
                import traceback
                traceback.print_exc()
                final_hits = results.get('hits', [])[:limit]
                final_found = len(final_hits)
                excluded_count = 0
        else:
            # No critical filtering needed - return all results!
            print(f"✅ No critical constraints - returning all {len(results.get('hits', []))} results")
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
