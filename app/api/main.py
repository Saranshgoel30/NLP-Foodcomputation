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

from config import get_settings
from models import (
    SearchRequest, SearchResponse, STTRequest, STTResponse,
    TranslateRequest, TranslateResponse, NLUParseRequest, NLUParseResponse,
    SPARQLBuildRequest, SPARQLBuildResponse, APIError, Recipe
)
from graphdb_client import GraphDBClient
from translation_adapter import get_translation_adapter

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

# Import TypesenseClient with lazy loading
try:
    from typesense_client import TypesenseClient
    TYPESENSE_AVAILABLE = True
    logger.info("typesense_client_imported")
except Exception as e:
    TypesenseClient = None
    TYPESENSE_AVAILABLE = False
    logger.warning("typesense_import_failed", error=str(e))

# Global instances
settings = get_settings()
graphdb_client = None
typesense_client = None
stt_adapter = None
translation_adapter = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown"""
    global graphdb_client, typesense_client, stt_adapter, translation_adapter
    
    # Startup
    logger.info("mmfood_api_starting", version="1.0.0")
    
    try:
        graphdb_client = GraphDBClient(settings)
        logger.info("graphdb_client_initialized")
    except Exception as e:
        logger.error("failed_to_init_graphdb", error=str(e))
    
    # Initialize Typesense if enabled and available
    if settings.typesense_enabled and TYPESENSE_AVAILABLE and TypesenseClient:
        try:
            typesense_client = TypesenseClient(
                host=settings.typesense_host,
                port=settings.typesense_port,
                api_key=settings.typesense_api_key,
                collection_name='food_ingredients_v1',  # Using the indexed collection
                enable_redis=False  # Disable Redis for now
            )
            logger.info("typesense_client_initialized", 
                       strategy=settings.search_strategy,
                       collection='food_ingredients_v1')
        except Exception as e:
            logger.warning("typesense_init_failed", error=str(e))
            logger.info("falling_back_to_graphdb_only")
    
    # STT adapter not needed for current implementation
    # try:
    #     stt_adapter = get_stt_adapter(settings)
    #     logger.info("stt_adapter_initialized", provider=settings.stt_provider)
    # except Exception as e:
    #     logger.warning("stt_adapter_init_failed", error=str(e))
    
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


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "graphdb": "connected" if graphdb_client else "unavailable",
        "typesense": "connected" if typesense_client else ("disabled" if not settings.typesense_enabled else "unavailable"),
        "search_strategy": settings.search_strategy,
        "stt": "available" if stt_adapter else "unavailable",
        "translation": "available" if translation_adapter else "unavailable"
    }


# NLU and SPARQL endpoints - DEPRECATED (using Typesense now)
# @app.post("/nlu/parse", response_model=NLUParseResponse)
# async def parse_nlu(request: NLUParseRequest):
#     """
#     Parse natural language query into structured constraints
#     """
#     raise HTTPException(
#         status_code=status.HTTP_410_GONE,
#         detail="NLU endpoint deprecated. Use /search endpoint directly."
#     )

# @app.post("/sparql/build", response_model=SPARQLBuildResponse)
# async def build_sparql(request: SPARQLBuildRequest):
#     """
#     Build SPARQL query from structured constraints
#     """
#     raise HTTPException(
#         status_code=status.HTTP_410_GONE,
#         detail="SPARQL builder deprecated. Use /search endpoint with Typesense."
#     )


# Main search endpoint
@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Complete search pipeline: NLU → SPARQL → GraphDB → Rank → Response
    
    Supports multilingual queries with translation
    """
    start_time = time.time()
    
    try:
        query = request.query
        original_text = query.text
        original_lang = query.lang
        
        logger.info("search_started", query=original_text, lang=original_lang)
        
        # Step 1: Translate to English if needed
        step1_start = time.time()
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
                    detected_lang=detected_lang,
                    duration_ms=(time.time() - step1_start) * 1000
                )
            except Exception as e:
                logger.warning("translation_failed", error=str(e))
        else:
            logger.info("translation_skipped", duration_ms=(time.time() - step1_start) * 1000)
        
        # Step 2: Simple constraints (parse_query not needed for Typesense)
        step2_start = time.time()
        # constraints, confidence = parse_query(translated_text, 'en')
        # For now, use empty constraints
        from models import SearchConstraints
        constraints = SearchConstraints() if not query.constraints else query.constraints
        confidence = 1.0
        logger.info("constraints_ready", duration_ms=(time.time() - step2_start) * 1000)
        
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
        
        # Step 3: Choose search strategy
        step3_start = time.time()
        recipes = []
        
        if settings.search_strategy == 'typesense' and typesense_client:
            # Pure Typesense semantic search
            logger.info("using_typesense_search")
            
            # Build filter string for Typesense
            filter_parts = []
            if constraints.cuisine:
                filter_parts.append(f"cuisine:={constraints.cuisine}")
            if constraints.diet:
                filter_parts.append(f"diet:={constraints.diet}")
            filter_str = ' && '.join(filter_parts) if filter_parts else None
            
            # Perform search
            result = typesense_client.semantic_search(
                translated_text,
                limit=50,
                filters=filter_str
            )
            
            # Convert Typesense results to Recipe objects
            recipes = []
            for hit in result.get('hits', []):
                doc = hit['document']
                recipes.append(Recipe(
                    iri=doc.get('id', ''),
                    title=doc.get('name', ''),
                    cuisine=doc.get('cuisine'),
                    diet=doc.get('diet'),
                    course=doc.get('course'),
                    ingredients=doc.get('ingredients', []) if isinstance(doc.get('ingredients'), list) else [],
                    instructions=doc.get('description')
                ))
            
            logger.info("typesense_search_completed", recipe_count=len(recipes), duration_ms=(time.time() - step3_start) * 1000)
            
        elif settings.search_strategy == 'hybrid' and typesense_client:
            # Hybrid: Typesense semantic + keyword
            logger.info("using_hybrid_search", semantic_weight=settings.hybrid_semantic_weight)
            
            # Build filter string
            filter_parts = []
            if constraints.cuisine:
                filter_parts.append(f"cuisine:={constraints.cuisine}")
            if constraints.diet:
                filter_parts.append(f"diet:={constraints.diet}")
            filter_str = ' && '.join(filter_parts) if filter_parts else None
            
            # Perform hybrid search
            result = typesense_client.hybrid_search(
                translated_text,
                limit=50,
                semantic_weight=settings.hybrid_semantic_weight,
                filters=filter_str
            )
            
            # Convert Typesense results to Recipe objects
            recipes = []
            for hit in result.get('hits', []):
                doc = hit['document']
                recipes.append(Recipe(
                    iri=doc.get('id', ''),
                    title=doc.get('name', ''),
                    cuisine=doc.get('cuisine'),
                    diet=doc.get('diet'),
                    course=doc.get('course'),
                    ingredients=doc.get('ingredients', []) if isinstance(doc.get('ingredients'), list) else [],
                    instructions=doc.get('description')
                ))
            
            logger.info("hybrid_search_completed", recipe_count=len(recipes), duration_ms=(time.time() - step3_start) * 1000)
            
        else:
            # Default: Use GraphDB or Typesense
            logger.info("using_default_search")
            
            if typesense_client:
                # Fall back to Typesense semantic search
                result = typesense_client.semantic_search(translated_text, limit=50)
                for hit in result.get('hits', []):
                    doc = hit['document']
                    recipes.append(Recipe(
                        iri=doc.get('id', ''),
                        title=doc.get('name', ''),
                        cuisine=doc.get('cuisine'),
                        diet=doc.get('diet'),
                        course=doc.get('course'),
                        ingredients=doc.get('ingredients', []) if isinstance(doc.get('ingredients'), list) else [],
                        instructions=doc.get('description')
                    ))
                logger.info("fallback_search_completed", recipe_count=len(recipes))
            else:
                # No search available
                logger.warning("no_search_backend_available")
                recipes = []
        
        # Step 4: Results already ranked by Typesense
        step4_start = time.time()
        # Hybrid/semantic search already ranked
        ranked_recipes = recipes
        logger.info("results_ready", count=len(recipes), duration_ms=(time.time() - step4_start) * 1000)
        
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


# STT endpoint - DEPRECATED
# @app.post("/stt", response_model=STTResponse)
# async def speech_to_text(request: STTRequest):
#     """
#     Convert audio to text using Whisper/Vosk
#     """
#     raise HTTPException(
#         status_code=status.HTTP_410_GONE,
#         detail="STT endpoint deprecated. Frontend should implement speech recognition directly."
#     )


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
        reload=False,  # Disabled due to ML library loading issues
        log_level=settings.log_level.lower()
    )
