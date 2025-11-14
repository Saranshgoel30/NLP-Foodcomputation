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
from sparql_builder import build_sparql_query
from nlu_parser import parse_query
from ranking import rank_recipes
from stt_adapter import get_stt_adapter
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
        
        # Step 2: Parse query into constraints
        step2_start = time.time()
        constraints, confidence = parse_query(translated_text, 'en')
        logger.info("query_parsed", constraints=str(constraints), confidence=confidence, duration_ms=(time.time() - step2_start) * 1000)
        
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
        step3_start = time.time()
        sparql_query = build_sparql_query(
            constraints,
            limit=50,
            named_graph=settings.graphdb_named_graph
        )
        logger.info("sparql_built", query_length=len(sparql_query), duration_ms=(time.time() - step3_start) * 1000)
        logger.info("sparql_query", query=sparql_query[:500])  # Log first 500 chars
        
        # Step 4: Execute GraphDB query
        step4_start = time.time()
        if not graphdb_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="GraphDB client not available"
            )
        
        logger.info("graphdb_query_starting")
        recipes = graphdb_client.search_recipes(sparql_query)
        logger.info("graphdb_query_completed", recipe_count=len(recipes), duration_ms=(time.time() - step4_start) * 1000)
        
        # Step 5: Rank and filter results
        step5_start = time.time()
        ranked_recipes = rank_recipes(recipes, constraints)
        logger.info("ranking_completed", ranked_count=len(ranked_recipes), duration_ms=(time.time() - step5_start) * 1000)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        logger.info(
            "search_completed",
            query=original_text,
            results=len(ranked_recipes),
            duration_ms=duration_ms
        )
        
        # Debug: Check titles before returning
        if ranked_recipes:
            logger.info("sample_recipe_titles", 
                       first_title=ranked_recipes[0].title if ranked_recipes else "N/A",
                       first_iri=ranked_recipes[0].iri[:100] if ranked_recipes else "N/A")
        
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
