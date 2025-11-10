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
    SPARQLBuildRequest, SPARQLBuildResponse, APIError, Recipe, UserQuery
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


# Create FastAPI app with enhanced metadata
app = FastAPI(
    title="MMFOOD API",
    description="""
    ## Multilingual + Multimodal Food Knowledge Search
    
    A production-ready API for searching recipes using natural language and voice input.
    
    ### Features
    - 🎤 **Speech-to-Text**: 11 Indian languages + English
    - 🌐 **Translation**: Bidirectional translation with culinary term preservation
    - 🧠 **NLP**: Intelligent query parsing with constraint extraction
    - 🔍 **Search**: 9000+ recipes from Food Graph API
    - 🎙️ **Voice Search**: End-to-end pipeline (STT → Translation → NLP → Search)
    
    ### Rate Limits
    - General endpoints: 60 requests/minute
    - Search endpoint: 30 requests/minute
    - STT/Voice endpoints: 10 requests/minute
    """,
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "MMFOOD Team",
        "url": "https://github.com/Saranshgoel30/NLP-Foodcomputation",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Import middleware
from .middleware import (
    rate_limit_middleware,
    security_headers_middleware,
    request_id_middleware
)

# CORS middleware (applied first, innermost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
)


# Custom middleware (applied in reverse order - last added runs first)
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID for tracing"""
    return await request_id_middleware(request, call_next)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to responses"""
    return await security_headers_middleware(request, call_next)


@app.middleware("http")
async def apply_rate_limiting(request: Request, call_next):
    """Apply rate limiting based on endpoint"""
    return await rate_limit_middleware(request, call_next)


@app.middleware("http")
async def add_timing(request: Request, call_next):
    """Add request timing to response headers"""
    start_time = time.time()
    response = await call_next(request)
    duration = (time.time() - start_time) * 1000  # ms
    response.headers["X-Process-Time"] = f"{duration:.2f}"
    logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        duration_ms=round(duration, 2),
        status_code=response.status_code
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
@app.get("/", tags=["System"])
async def root():
    """
    **API Root**
    
    Welcome endpoint showing API status and links to documentation.
    """
    return {
        "message": "MMFOOD API - Multilingual Multimodal Food Knowledge Search",
        "status": "running",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }


# Simple test endpoint
@app.get("/test", tags=["System"])
async def test():
    """Simple connectivity test"""
    return {"status": "ok", "message": "Backend is working!", "timestamp": time.time()}


# Minimal mock search endpoint for testing
@app.post("/search-test", tags=["System"])
async def search_test(request: SearchRequest):
    """Mock search endpoint that returns empty results (for frontend testing)"""
    return SearchResponse(
        results=[],
        query=request.query,
        translatedQuery=None,
        count=0,
        durationMs=1.0
    )


# Metrics endpoint for monitoring
@app.get("/metrics", tags=["System"])
async def metrics():
    """
    **System Metrics**
    
    Returns performance metrics and usage statistics.
    Useful for monitoring dashboards and alerting.
    
    **Metrics include:**
    - Request counts by endpoint
    - Rate limit statistics
    - Average response times
    - Error rates
    """
    from .middleware import rate_limiters
    
    metrics_data = {
        "timestamp": time.time(),
        "rate_limiters": {},
        "system": {
            "stt_available": stt_adapter is not None,
            "translation_available": translation_adapter is not None,
            "graphdb_available": graphdb_client is not None
        }
    }
    
    # Get rate limiter statistics
    for name, limiter in rate_limiters.items():
        metrics_data["rate_limiters"][name] = {
            "rate": limiter.rate,
            "per_seconds": limiter.per,
            "active_clients": len(limiter.allowance)
        }
    
    return metrics_data


# Health check with detailed status
@app.get("/health", tags=["System"])
async def health_check():
    """
    **Comprehensive health check**
    
    Returns system status and dependency health.
    Use this for monitoring and load balancer health checks.
    
    **Response includes:**
    - Overall status (healthy/degraded/unhealthy)
    - Service version
    - Dependency status (GraphDB, STT, Translation, Food Graph API)
    - Uptime
    - Response times for dependencies
    """
    import httpx
    
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time(),
        "dependencies": {}
    }
    
    # Check GraphDB
    try:
        if graphdb_client:
            # Try a simple SPARQL query
            test_query = "SELECT ?s WHERE { ?s ?p ?o } LIMIT 1"
            start = time.time()
            result = graphdb_client.execute_query(test_query)
            duration = (time.time() - start) * 1000
            
            health_status["dependencies"]["graphdb"] = {
                "status": "connected" if result else "degraded",
                "response_time_ms": round(duration, 2),
                "url": settings.graphdb_url
            }
        else:
            health_status["dependencies"]["graphdb"] = {
                "status": "unavailable",
                "error": "Client not initialized"
            }
    except Exception as e:
        health_status["dependencies"]["graphdb"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check Food Graph API
    try:
        start = time.time()
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{settings.food_graph_api_url}/recipes", params={"limit": 1})
            duration = (time.time() - start) * 1000
            
            health_status["dependencies"]["food_graph_api"] = {
                "status": "connected" if response.status_code == 200 else "degraded",
                "response_time_ms": round(duration, 2),
                "url": settings.food_graph_api_url
            }
    except Exception as e:
        health_status["dependencies"]["food_graph_api"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check STT
    health_status["dependencies"]["stt"] = {
        "status": "available" if stt_adapter else "unavailable",
        "provider": settings.stt_provider if stt_adapter else None,
        "model": settings.stt_model_name if stt_adapter else None
    }
    
    # Check Translation
    health_status["dependencies"]["translation"] = {
        "status": "available" if translation_adapter else "unavailable",
        "provider": settings.translation_provider if translation_adapter else None
    }
    
    # Determine overall status
    dep_statuses = [dep.get("status") for dep in health_status["dependencies"].values()]
    if "error" in dep_statuses or "unavailable" in dep_statuses:
        health_status["status"] = "degraded"
    
    # If critical services are down, mark as unhealthy
    if health_status["dependencies"].get("food_graph_api", {}).get("status") == "error":
        health_status["status"] = "unhealthy"
    
    return health_status


# ============================================================================
# SPEECH-TO-TEXT ENDPOINT
# ============================================================================

@app.post("/stt", response_model=STTResponse, tags=["Speech & Translation"])
async def speech_to_text(request: STTRequest):
    """
    Convert speech audio to text using Whisper
    
    **Supports Indian Languages:**
    - Hindi (hi), Bengali (bn), Telugu (te), Marathi (mr)
    - Tamil (ta), Gujarati (gu), Kannada (kn), Malayalam (ml)
    - Odia (or), Punjabi (pa), English (en)
    
    **Audio Requirements:**
    - Format: webm, wav, mp3, ogg, m4a
    - Max size: 25MB
    - Encoding: Base64
    
    **Example Request:**
    ```json
    {
        "audio": "base64_encoded_audio_data",
        "format": "webm"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "transcript": "मुझे पनीर टिक्का की रेसिपी चाहिए",
        "confidence": 0.95,
        "detectedLanguage": "hi"
    }
    ```
    """
    if not stt_adapter:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Speech-to-text service is not available. Whisper model may not be loaded."
        )
    
    start_time = time.time()
    
    try:
        # Validate request
        if not request.audio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Audio data is required"
            )
        
        # Log request (without full audio data)
        audio_size = len(request.audio) if request.audio else 0
        logger.info(
            "stt_request_received",
            audio_size_bytes=audio_size,
            format=request.format
        )
        
        # Transcribe audio
        transcript, confidence, detected_lang = stt_adapter.transcribe(
            audio_base64=request.audio,
            format=request.format
        )
        
        duration_ms = (time.time() - start_time) * 1000
        
        logger.info(
            "stt_completed",
            transcript_length=len(transcript),
            confidence=f"{confidence:.2%}",
            detected_language=detected_lang,
            duration_ms=f"{duration_ms:.0f}"
        )
        
        return STTResponse(
            transcript=transcript,
            confidence=confidence,
            detectedLanguage=detected_lang
        )
        
    except ValueError as e:
        # Validation errors (bad input)
        logger.warning("stt_validation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        # Service errors (transcription failed)
        logger.error("stt_service_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )
    except Exception as e:
        # Unexpected errors
        logger.error("stt_unexpected_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during transcription"
        )


# ============================================================================
# TRANSLATION ENDPOINT
# ============================================================================

@app.post("/translate", response_model=TranslateResponse, tags=["Speech & Translation"])
async def translate_text(request: TranslateRequest):
    """
    Translate text between languages
    
    **Supported Languages:**
    - English (en)
    - Hindi (hi), Bengali (bn), Telugu (te), Marathi (mr)
    - Tamil (ta), Gujarati (gu), Kannada (kn), Malayalam (ml)
    - Odia (or), Punjabi (pa)
    
    **Translation Modes:**
    - Auto-detect source language (set sourceLang='auto')
    - Bidirectional: Any supported language ↔ English
    - Uses culinary terminology table for food-specific accuracy
    
    **Example Request:**
    ```json
    {
        "text": "मुझे पनीर टिक्का की रेसिपी चाहिए",
        "sourceLang": "auto",
        "targetLang": "en"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "translatedText": "I want paneer tikka recipe",
        "detectedSourceLang": "hi",
        "confidence": 0.92
    }
    ```
    """
    if not translation_adapter:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Translation service is not available"
        )
    
    start_time = time.time()
    
    try:
        # Validate request
        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text is required and cannot be empty"
            )
        
        if len(request.text) > 5000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text too long (max 5000 characters)"
            )
        
        logger.info(
            "translation_request",
            text_length=len(request.text),
            source_lang=request.sourceLang,
            target_lang=request.targetLang
        )
        
        # Translate
        translated_text, detected_source = translation_adapter.translate(
            text=request.text,
            source_lang=request.sourceLang,
            target_lang=request.targetLang
        )
        
        duration_ms = (time.time() - start_time) * 1000
        
        logger.info(
            "translation_completed",
            detected_source=detected_source,
            output_length=len(translated_text),
            duration_ms=f"{duration_ms:.0f}"
        )
        
        return TranslateResponse(
            translatedText=translated_text,
            detectedSourceLang=detected_source,
            confidence=0.9  # Mock confidence for now
        )
        
    except ValueError as e:
        logger.warning("translation_validation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("translation_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )


# ============================================================================
# VOICE SEARCH ENDPOINT (STT → Translation → NLP → Search Pipeline)
# ============================================================================

@app.post("/voice-search", response_model=SearchResponse, tags=["Search"])
async def voice_search(request: STTRequest):
    """
    **End-to-end Voice Search Pipeline**
    
    Chains multiple AI services for multilingual voice recipe search:
    1. **STT**: Transcribe audio to text (Whisper)
    2. **Translation**: Translate to English if needed
    3. **NLP**: Parse constraints from query
    4. **Search**: Find matching recipes
    
    **Perfect for Indian users speaking in native languages!**
    
    **Workflow Example:**
    ```
    User speaks: "मुझे 30 मिनट में पनीर टिक्का बनाने की रेसिपी चाहिए"
    ↓ STT (Whisper)
    → Hindi transcript detected
    ↓ Translation
    → "I want paneer tikka recipe in 30 minutes"
    ↓ NLP
    → include=[paneer, tikka], maxCookMinutes=30
    ↓ Search
    → Returns matching recipes
    ```
    
    **Request:**
    ```json
    {
        "audio": "base64_encoded_webm_audio",
        "format": "webm"
    }
    ```
    
    **Response:** Same as /search endpoint
    """
    pipeline_start = time.time()
    
    try:
        logger.info("voice_search_started", audio_size=len(request.audio))
        
        # ============================================================
        # STEP 1: Speech-to-Text
        # ============================================================
        if not stt_adapter:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Speech-to-text service unavailable"
            )
        
        stt_start = time.time()
        transcript, stt_confidence, detected_lang = stt_adapter.transcribe(
            audio_base64=request.audio,
            format=request.format
        )
        stt_duration = (time.time() - stt_start) * 1000
        
        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not transcribe audio. Please try again."
            )
        
        logger.info(
            "voice_search_stt_complete",
            transcript=transcript,
            language=detected_lang,
            confidence=stt_confidence,
            duration_ms=stt_duration
        )
        
        print(f"🎤 STT: '{transcript}' (lang={detected_lang}, conf={stt_confidence:.2f})", flush=True)
        
        # ============================================================
        # STEP 2: Translation (if not English)
        # ============================================================
        search_text = transcript
        translated = False
        
        if detected_lang != 'en':
            if not translation_adapter:
                logger.warning("translation_unavailable", using_original=True)
                print(f"⚠️  Translation unavailable, using original text", flush=True)
            else:
                translate_start = time.time()
                try:
                    search_text, _ = translation_adapter.translate(
                        text=transcript,
                        source_lang=detected_lang,
                        target_lang='en'
                    )
                    translate_duration = (time.time() - translate_start) * 1000
                    translated = True
                    
                    logger.info(
                        "voice_search_translation_complete",
                        original=transcript,
                        translated=search_text,
                        duration_ms=translate_duration
                    )
                    
                    print(f"🌐 Translated: '{search_text}'", flush=True)
                except Exception as e:
                    logger.warning("translation_failed", error=str(e), using_original=True)
                    print(f"⚠️  Translation failed: {e}, using original", flush=True)
        
        # ============================================================
        # STEP 3: NLP Parsing
        # ============================================================
        nlp_start = time.time()
        constraints, nlp_confidence = parse_query(search_text, 'en')
        nlp_duration = (time.time() - nlp_start) * 1000
        
        logger.info(
            "voice_search_nlp_complete",
            constraints=constraints.model_dump(exclude_none=True),
            confidence=nlp_confidence,
            duration_ms=nlp_duration
        )
        
        print(f"🧠 NLP: include={constraints.include}, exclude={constraints.exclude}, "
              f"cuisine={constraints.cuisine}, diet={constraints.diet}", flush=True)
        
        # ============================================================
        # STEP 4: Search
        # ============================================================
        search_request = SearchRequest(
            query=UserQuery(
                text=search_text,
                lang='en',
                constraints=constraints
            )
        )
        
        # Reuse existing search endpoint logic
        search_result = await search(search_request)
        
        # Add voice search metadata to response
        pipeline_duration = (time.time() - pipeline_start) * 1000
        
        logger.info(
            "voice_search_complete",
            total_duration_ms=pipeline_duration,
            stt_ms=stt_duration,
            nlp_ms=nlp_duration,
            results_count=search_result.count,
            original_language=detected_lang,
            translated=translated
        )
        
        print(f"✅ Voice search complete: {search_result.count} results in {pipeline_duration:.0f}ms", flush=True)
        
        # Enhance response with original transcript for UI display
        search_result.translatedQuery = transcript if translated else None
        
        return search_result
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error("voice_search_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice search pipeline failed: {str(e)}"
        )


# ============================================================================
# NLU ENDPOINT
# ============================================================================

@app.post("/nlu/parse", response_model=NLUParseResponse, tags=["NLP"])
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
@app.post("/sparql/build", response_model=SPARQLBuildResponse, tags=["NLP"])
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


@app.post("/parse-query", response_model=NLUParseResponse, tags=["NLP"])
async def parse_query_endpoint(request: NLUParseRequest):
    """
    Parse natural language query into structured constraints using NLP
    
    Example:
        Input: "vegetarian paneer recipes without onion under 30 minutes"
        Output: Structured constraints with diet, include, exclude, time
    """
    try:
        from .nlu_parser import parse_query
        
        constraints, confidence = parse_query(request.text, request.lang)
        
        return NLUParseResponse(
            constraints=constraints,
            confidence=confidence,
            originalText=request.text
        )
    except Exception as e:
        logger.error("nlu_parse_failed", error=str(e), text=request.text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"NLU parsing failed: {str(e)}"
        )


# Main search endpoint - Using Food Graph API
@app.post("/search", response_model=SearchResponse, tags=["Search"])
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
        
        # Parse NLP constraints from query if not already provided
        from .nlu_parser import parse_query
        
        if query.constraints is None:
            print(f"🧠 Parsing NLP constraints from query...", flush=True)
            constraints, confidence = parse_query(search_text, query.lang)
            query.constraints = constraints
            print(f"✅ NLP Parsing (confidence: {confidence:.2f}):", flush=True)
            print(f"   - Include: {constraints.include}", flush=True)
            print(f"   - Exclude: {constraints.exclude}", flush=True)
            print(f"   - Cuisine: {constraints.cuisine}", flush=True)
            print(f"   - Diet: {constraints.diet}", flush=True)
            print(f"   - Course: {constraints.course}", flush=True)
            print(f"   - Max Cook Time: {constraints.maxCookMinutes}m", flush=True)
            logger.info("nlp_parsed", constraints=constraints.model_dump(exclude_none=True), confidence=confidence)
        
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
        
        # Intelligent filtering: match query against multiple fields + NLP constraints
        matched_recipes = []
        constraints = query.constraints
        
        for api_recipe in api_recipes:
            # Extract searchable text from recipe
            recipe_name = (api_recipe.get("name") or "").lower()
            recipe_cuisine = (api_recipe.get("cuisine") or "").lower()
            recipe_diet = (api_recipe.get("diet") or "").lower()
            recipe_course = (api_recipe.get("course") or "").lower()
            
            # Extract ingredient names from the structured data
            ingredient_names = []
            ingredient_desc = api_recipe.get("ingredient_description", [])
            if isinstance(ingredient_desc, list):
                for section in ingredient_desc:
                    if isinstance(section, dict) and "items" in section:
                        items = section["items"]
                        if isinstance(items, dict):
                            ingredient_names.extend([name.lower() for name in items.keys()])
            
            ingredient_text = " ".join(ingredient_names)
            
            # === NLP CONSTRAINT FILTERING ===
            
            # 1. Check cuisine constraint
            if constraints and constraints.cuisine:
                if not any(c.lower() in recipe_cuisine for c in constraints.cuisine):
                    continue  # Skip if cuisine doesn't match
            
            # 2. Check diet constraint
            if constraints and constraints.diet:
                if not any(d.lower() in recipe_diet for d in constraints.diet):
                    continue  # Skip if diet doesn't match
            
            # 3. Check course constraint
            if constraints and constraints.course:
                if not any(c.lower() in recipe_course for c in constraints.course):
                    continue  # Skip if course doesn't match
            
            # 4. Check excluded ingredients
            if constraints and constraints.exclude:
                has_excluded = False
                for excluded in constraints.exclude:
                    if any(excluded.lower() in ing for ing in ingredient_names):
                        has_excluded = True
                        break
                if has_excluded:
                    continue  # Skip if contains excluded ingredient
            
            # 5. Check included ingredients (at least one must match)
            if constraints and constraints.include:
                has_included = False
                for included in constraints.include:
                    if any(included.lower() in ing for ing in ingredient_names):
                        has_included = True
                        break
                if not has_included:
                    continue  # Skip if doesn't contain any required ingredient
            
            # 6. Check time constraints
            if constraints and constraints.maxCookMinutes:
                cook_time_str = api_recipe.get("cook_time", "")
                if cook_time_str:
                    import re
                    match = re.search(r'(\d+)', str(cook_time_str))
                    if match:
                        cook_minutes = int(match.group(1))
                        if cook_minutes > constraints.maxCookMinutes:
                            continue  # Skip if too long
            
            # === TEXT MATCHING (fallback for queries without constraints) ===
            # Combine all searchable text
            searchable = f"{recipe_name} {recipe_cuisine} {recipe_diet} {recipe_course} {ingredient_text}"
            
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
