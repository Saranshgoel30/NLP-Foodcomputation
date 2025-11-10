"""
Main FastAPI Application for MMFOOD
Multilingual + Multimodal Food Knowledge Search
"""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
from structlog.stdlib import LoggerFactory

from .config import get_settings
from .models import (
    SearchRequest, SearchResponse, STTRequest, STTResponse,
    TranslateRequest, TranslateResponse, NLUParseRequest, NLUParseResponse,
    SPARQLBuildRequest, SPARQLBuildResponse, APIError, Recipe
)
from .graphdb_client import GraphDBClient
from .sparql_builder import build_sparql_query
from .nlu_parser import parse_query
from .ranking import rank_recipes
from .stt_adapter import get_stt_adapter
from .translation_adapter import get_translation_adapter

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Global instances
settings = get_settings()
graphdb_client = None
stt_adapter = None
translation_adapter = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown"""
    global graphdb_client, stt_adapter, translation_adapter
    
    # Startup
    logger.info("mmfood_api_starting", version="1.0.0")
    
    try:
        graphdb_client = GraphDBClient(settings)
        logger.info("graphdb_client_initialized")
    except Exception as e:
        logger.error("failed_to_init_graphdb", error=str(e))
    
    try:
        stt_adapter = get_stt_adapter(settings)
        logger.info("stt_adapter_initialized", provider=settings.stt_provider)
    except Exception as e:
        logger.warning("stt_adapter_init_failed", error=str(e))
    
    try:
        translation_adapter = get_translation_adapter(settings)
        logger.info("translation_adapter_initialized", provider=settings.translation_provider)
    except Exception as e:
        logger.warning("translation_adapter_init_failed", error=str(e))
    
    logger.info("mmfood_api_started")
    
    yield
    
    # Shutdown
    logger.info("mmfood_api_shutting_down")
    if graphdb_client:
        graphdb_client.close()
    logger.info("mmfood_api_stopped")


# Create FastAPI app
app = FastAPI(
    title="MMFOOD API",
    description="Multilingual + Multimodal Food Knowledge Search",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_timing(request: Request, call_next):
    """Add request timing to response headers"""
    start_time = time.time()
    response = await call_next(request)
    duration = (time.time() - start_time) * 1000  # ms
    response.headers["X-Process-Time"] = str(duration)
    logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        duration_ms=duration
    )
    return response


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=APIError(
            error="HTTPException",
            message=exc.detail,
            code=str(exc.status_code)
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(
        "unhandled_exception",
        error=str(exc),
        path=request.url.path,
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIError(
            error="InternalServerError",
            message="An unexpected error occurred",
            details=str(exc) if settings.api_reload else None
        ).model_dump()
    )


# Test endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "MMFOOD API", "status": "running"}


# Simple test search endpoint
@app.get("/test")
async def test():
    """Simple test endpoint"""
    return {"status": "ok", "message": "Backend is working!"}


# Minimal mock search endpoint for testing
@app.post("/search-test")
async def search_test(request: SearchRequest):
    """Mock search endpoint that returns empty results"""
    return SearchResponse(
        results=[],
        query=request.query,
        translatedQuery=None,
        count=0,
        durationMs=1.0
    )


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "graphdb": "connected" if graphdb_client else "unavailable",
        "stt": "available" if stt_adapter else "unavailable",
        "translation": "available" if translation_adapter else "unavailable"
    }


# NLU endpoint
@app.post("/nlu/parse", response_model=NLUParseResponse)
async def parse_nlu(request: NLUParseRequest):
    """
    Parse natural language query into structured constraints
    
    Example:
        Input: "give me Chinese chicken recipe under 30 minutes"
        Output: constraints with cuisine=['Chinese'], include=['chicken'], maxCookMinutes=30
    """
    try:
        constraints, confidence = parse_query(request.text, request.lang)
        
        return NLUParseResponse(
            constraints=constraints,
            confidence=confidence,
            originalText=request.text
        )
    except Exception as e:
        logger.error("nlu_parse_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"NLU parsing failed: {str(e)}"
        )


# SPARQL builder endpoint
@app.post("/sparql/build", response_model=SPARQLBuildResponse)
async def build_sparql(request: SPARQLBuildRequest):
    """
    Build SPARQL query from structured constraints
    
    Example:
        Input: constraints with include=['chicken'], exclude=['banana']
        Output: Complete SPARQL query string
    """
    try:
        sparql = build_sparql_query(
            request.constraints,
            limit=50,
            named_graph=settings.graphdb_named_graph
        )
        
        return SPARQLBuildResponse(
            sparql=sparql,
            params=None
        )
    except Exception as e:
        logger.error("sparql_build_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SPARQL build failed: {str(e)}"
        )


# Main search endpoint - Using Food Graph API
@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Production-ready search using Food Graph API with intelligent filtering
    Matches query against recipe names, ingredients, cuisine, and diet
    """
    start_time = time.time()
    
    try:
        query = request.query
        search_text = query.text.lower()
        
        print(f"🔍 SEARCH REQUEST: '{search_text}'", flush=True)
        logger.info("search_started", query=search_text, lang=query.lang)
        
        # Call the Food Graph API
        import httpx
        food_api_url = "http://16.170.211.162:8001/recipes"
        
        with httpx.Client(timeout=30.0) as client:
            # Fetch more recipes to ensure good matches after filtering
            response = client.get(food_api_url, params={"limit": 200})
            response.raise_for_status()
            api_recipes = response.json()
        
        logger.info("api_response_received", total_recipes=len(api_recipes))
        print(f"📡 Received {len(api_recipes)} recipes from Food Graph API", flush=True)
        
        # Intelligent filtering: match query against multiple fields
        matched_recipes = []
        
        for api_recipe in api_recipes:
            # Extract searchable text from recipe
            recipe_name = (api_recipe.get("name") or "").lower()
            cuisine = (api_recipe.get("cuisine") or "").lower()
            diet = (api_recipe.get("diet") or "").lower()
            course = (api_recipe.get("course") or "").lower()
            
            # Extract ingredient names from the structured data
            ingredient_text = ""
            ingredient_desc = api_recipe.get("ingredient_description", [])
            if isinstance(ingredient_desc, list):
                for section in ingredient_desc:
                    if isinstance(section, dict) and "items" in section:
                        items = section["items"]
                        if isinstance(items, dict):
                            ingredient_text += " " + " ".join(items.keys()).lower()
            
            # Combine all searchable text
            searchable = f"{recipe_name} {cuisine} {diet} {course} {ingredient_text}"
            
            # Check if query terms match (support multi-word queries)
            query_terms = search_text.split()
            if any(term in searchable for term in query_terms):
                matched_recipes.append(api_recipe)
            
            # Stop after finding enough matches
            if len(matched_recipes) >= 20:
                break
        
        logger.info("filtering_complete", matched=len(matched_recipes), searched=len(api_recipes))
        
        # Convert to Recipe model with full data mapping
        recipes = []
        for api_recipe in matched_recipes:
            try:
                # Parse ingredients into structured format
                ingredients_list = []
                ingredient_desc = api_recipe.get("ingredient_description", [])
                
                if isinstance(ingredient_desc, list):
                    for section in ingredient_desc:
                        if isinstance(section, dict):
                            heading = section.get("heading", "Ingredients")
                            items = section.get("items", {})
                            
                            if isinstance(items, dict):
                                for ing_name, ing_data in items.items():
                                    if isinstance(ing_data, dict):
                                        quantity = ing_data.get("quantity", "")
                                        unit = ing_data.get("unit", "")
                                        form = ing_data.get("form", "")
                                        notes = ing_data.get("notes", "")
                                        
                                        # Format ingredient string
                                        ing_str = f"{quantity} {unit} {ing_name}".strip()
                                        if form and form != "NA":
                                            ing_str += f" ({form})"
                                        if notes and notes != "NA":
                                            ing_str += f" - {notes}"
                                        
                                        ingredients_list.append(ing_str)
                
                # Parse instructions
                instructions_list = []
                instruction_desc = api_recipe.get("instruction_description", [])
                
                if isinstance(instruction_desc, list):
                    for section in instruction_desc:
                        if isinstance(section, dict):
                            steps = section.get("steps", [])
                            if isinstance(steps, list):
                                for step in steps:
                                    if isinstance(step, dict):
                                        step_text = step.get("step", "")
                                        if step_text:
                                            instructions_list.append(step_text)
                
                # Parse nutrition data - extract values and clean them
                nutrition_info = api_recipe.get("nutritional_info", {})
                nutrition_dict = None
                
                if isinstance(nutrition_info, dict) and nutrition_info:
                    # Helper to extract numeric value from strings like "120g" or "120 g" or "120"
                    def extract_number(value):
                        if value is None:
                            return None
                        if isinstance(value, (int, float)):
                            return float(value)
                        # Extract number from string
                        import re
                        if isinstance(value, str):
                            match = re.search(r'(\d+\.?\d*)', value)
                            if match:
                                return float(match.group(1))
                        return None
                    
                    nutrition_dict = {}
                    # Map API fields to our format and extract numeric values
                    if "Calories" in nutrition_info:
                        nutrition_dict["calories"] = extract_number(nutrition_info["Calories"])
                    if "Proteins" in nutrition_info:
                        nutrition_dict["protein"] = extract_number(nutrition_info["Proteins"])
                    if "Carbohydrates" in nutrition_info:
                        nutrition_dict["carbs"] = extract_number(nutrition_info["Carbohydrates"])
                    if "Dietary Fiber" in nutrition_info:
                        nutrition_dict["fiber"] = extract_number(nutrition_info["Dietary Fiber"])
                    if "Fats" in nutrition_info:
                        nutrition_dict["fat"] = extract_number(nutrition_info["Fats"])
                    if "Saturated Fats" in nutrition_info:
                        nutrition_dict["saturatedFat"] = extract_number(nutrition_info["Saturated Fats"])
                    if "Cholesterol" in nutrition_info:
                        nutrition_dict["cholesterol"] = extract_number(nutrition_info["Cholesterol"])
                    if "Sodium" in nutrition_info:
                        nutrition_dict["sodium"] = extract_number(nutrition_info["Sodium"])
                    
                    # Only include if we got at least some values
                    if not any(v is not None for v in nutrition_dict.values()):
                        nutrition_dict = None
                
                recipe = Recipe(
                    iri=api_recipe.get("uri", ""),
                    title=api_recipe.get("name", "Untitled Recipe"),
                    url=api_recipe.get("url"),
                    course=api_recipe.get("course"),
                    cuisine=api_recipe.get("cuisine"),
                    diet=api_recipe.get("diet"),
                    servings=api_recipe.get("servings"),
                    ingredients=ingredients_list if ingredients_list else None,
                    instructions=instructions_list if instructions_list else None,
                    difficulty=api_recipe.get("difficulty") if api_recipe.get("difficulty") != "NA" else None,
                    cookTime=api_recipe.get("cook_time"),
                    totalTime=api_recipe.get("total_time"),
                    prepTime=api_recipe.get("prep_time"),
                    nutrition=nutrition_dict
                )
                
                # Debug logging for first recipe
                if len(recipes) == 0:
                    print(f"✅ First Recipe Parsed:", flush=True)
                    print(f"   Title: {recipe.title}", flush=True)
                    print(f"   Ingredients: {len(recipe.ingredients) if recipe.ingredients else 0} items", flush=True)
                    print(f"   Instructions: {len(recipe.instructions) if recipe.instructions else 0} steps", flush=True)
                    print(f"   Nutrition: {recipe.nutrition}", flush=True)
                    print(f"   First ingredient: {recipe.ingredients[0] if recipe.ingredients else 'NONE'}", flush=True)
                    print(f"   First instruction: {recipe.instructions[0][:80] if recipe.instructions else 'NONE'}...", flush=True)
                    
                    logger.info("first_recipe_parsed", 
                               title=recipe.title,
                               has_ingredients=bool(recipe.ingredients),
                               ingredients_count=len(recipe.ingredients) if recipe.ingredients else 0,
                               has_instructions=bool(recipe.instructions),
                               instructions_count=len(recipe.instructions) if recipe.instructions else 0,
                               has_nutrition=bool(recipe.nutrition),
                               nutrition_keys=list(recipe.nutrition.keys()) if recipe.nutrition else []
                    )
                
                recipes.append(recipe)
                
            except Exception as e:
                logger.error("recipe_parse_error", error=str(e), recipe_name=api_recipe.get("name"))
                continue
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        logger.info("search_complete", results=len(recipes), duration_ms=duration_ms)
        
        return SearchResponse(
            results=recipes,
            query=query,
            translatedQuery=None,
            count=len(recipes),
            durationMs=duration_ms
        )
    
    except Exception as e:
        logger.error("search_failed", error=str(e))
        duration_ms = (time.time() - start_time) * 1000
        return SearchResponse(
            results=[],
            query=request.query,
            translatedQuery=None,
            count=0,
            durationMs=duration_ms
        )


# OLD SEARCH CODE BELOW - TO BE REMOVED
@app.post("/search-old", response_model=SearchResponse)
async def search_old(request: SearchRequest):
    """OLD search using GraphDB - keeping for reference"""
    start_time = time.time()
    
    try:
        query = request.query
        original_text = query.text
        original_lang = query.lang
        
        # Step 1: Translate to English if needed
        translated_text = original_text
        if original_lang != 'en' and translation_adapter:
            try:
                translated_text, detected_lang = translation_adapter.translate(
                    original_text,
                    original_lang,
                    'en'
                )
                logger.info(
                    "query_translated",
                    original=original_text,
                    translated=translated_text,
                    detected_lang=detected_lang
                )
            except Exception as e:
                logger.warning("translation_failed", error=str(e))
        
        # Step 2: Parse query into constraints
        try:
            constraints, confidence = parse_query(translated_text, 'en')
        except Exception as e:
            logger.error("nlu_parsing_failed", error=str(e))
            # Create empty constraints if parsing fails
            from .models import QueryConstraints
            constraints = QueryConstraints()
            confidence = 0.0
        
        # Override with explicit constraints if provided
        if query.constraints:
            if query.constraints.include:
                constraints.include = query.constraints.include
            if query.constraints.exclude:
                constraints.exclude = query.constraints.exclude
            if query.constraints.cuisine:
                constraints.cuisine = query.constraints.cuisine
            if query.constraints.diet:
                constraints.diet = query.constraints.diet
            if query.constraints.maxCookMinutes:
                constraints.maxCookMinutes = query.constraints.maxCookMinutes
            if query.constraints.maxTotalMinutes:
                constraints.maxTotalMinutes = query.constraints.maxTotalMinutes
            if query.constraints.course:
                constraints.course = query.constraints.course
            if query.constraints.keywords:
                constraints.keywords = query.constraints.keywords
        
        # Step 3: Build SPARQL query
        sparql_query = build_sparql_query(
            constraints,
            limit=50,
            named_graph=settings.graphdb_named_graph
        )
        
        # Step 4: Execute GraphDB query
        recipes = []
        try:
            if not graphdb_client:
                logger.warning("graphdb_client_not_available")
                recipes = []
            else:
                recipes = graphdb_client.search_recipes(sparql_query)
        except Exception as graphdb_error:
            logger.error("graphdb_query_failed", error=str(graphdb_error))
            # Return empty list if GraphDB fails - will use mock data on frontend
            recipes = []
        
        # Step 5: Rank and filter results
        ranked_recipes = rank_recipes(recipes, constraints) if recipes else []
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        logger.info(
            "search_completed",
            query=original_text,
            results=len(ranked_recipes),
            duration_ms=duration_ms
        )
        
        return SearchResponse(
            results=ranked_recipes,
            query=query,
            translatedQuery=translated_text if translated_text != original_text else None,
            count=len(ranked_recipes),
            durationMs=duration_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("search_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


# STT endpoint
@app.post("/stt", response_model=STTResponse)
async def speech_to_text(request: STTRequest):
    """
    Convert audio to text using Whisper/Vosk
    
    Supports multiple Indian languages
    """
    if not stt_adapter:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="STT service not available"
        )
    
    try:
        transcript, confidence, detected_lang = stt_adapter.transcribe(
            request.audio,
            request.format or 'webm'
        )
        
        logger.info(
            "stt_completed",
            transcript_length=len(transcript),
            confidence=confidence,
            lang=detected_lang
        )
        
        return STTResponse(
            transcript=transcript,
            confidence=confidence,
            lang=detected_lang
        )
        
    except Exception as e:
        logger.error("stt_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech-to-text failed: {str(e)}"
        )


# Translation endpoint
@app.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """
    Translate text between languages
    
    Supports Indic languages with culinary terminology preservation
    """
    if not translation_adapter:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Translation service not available"
        )
    
    try:
        translated_text, detected_source = translation_adapter.translate(
            request.text,
            request.sourceLang,
            request.targetLang
        )
        
        logger.info(
            "translation_completed",
            source_lang=detected_source,
            target_lang=request.targetLang,
            original_length=len(request.text),
            translated_length=len(translated_text)
        )
        
        return TranslateResponse(
            translatedText=translated_text,
            sourceLang=detected_source,
            targetLang=request.targetLang
        )
        
    except Exception as e:
        logger.error("translation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )
