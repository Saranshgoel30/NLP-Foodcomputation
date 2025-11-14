"""
Pydantic models mirroring TypeScript types
for contract consistency across frontend/backend
"""
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict


Language = Literal['en', 'hi', 'mr', 'ta', 'te', 'bn', 'gu', 'kn', 'ml', 'or', 'pa', 'auto']


class QueryConstraints(BaseModel):
    """Structured constraints extracted from user query"""
    include: Optional[List[str]] = Field(None, description="Ingredients to include")
    exclude: Optional[List[str]] = Field(None, description="Ingredients to exclude")
    cuisine: Optional[List[str]] = Field(None, description="Cuisine types")
    diet: Optional[List[str]] = Field(None, description="Dietary restrictions")
    maxCookMinutes: Optional[int] = Field(None, description="Max cooking time in minutes")
    maxTotalMinutes: Optional[int] = Field(None, description="Max total time in minutes")
    course: Optional[List[str]] = Field(None, description="Course types")
    keywords: Optional[List[str]] = Field(None, description="Technique keywords")


class UserQuery(BaseModel):
    """User's search query"""
    text: str = Field(..., description="Raw query text", min_length=1, max_length=500)
    lang: Language = Field(default='en', description="Source language")
    constraints: Optional[QueryConstraints] = None


class NutritionInfo(BaseModel):
    """Nutrition information per serving"""
    calories: Optional[float] = Field(None, description="Energy in kcal")
    protein_g: Optional[float] = Field(None, description="Protein in grams")
    carbs_g: Optional[float] = Field(None, description="Carbohydrates in grams")
    fat_g: Optional[float] = Field(None, description="Total fat in grams")
    fiber_g: Optional[float] = Field(None, description="Dietary fiber in grams")
    sodium_mg: Optional[float] = Field(None, description="Sodium in milligrams")
    sugar_g: Optional[float] = Field(None, description="Total sugars in grams")


class EnhancedIngredient(BaseModel):
    """Ingredient with enrichment data"""
    name: str = Field(..., description="Original ingredient name from GraphDB")
    standardized_name: Optional[str] = Field(None, description="Standardized name after fuzzy matching")
    quantity: Optional[float] = Field(None, description="Quantity if parsed")
    unit: Optional[str] = Field(None, description="Unit if parsed")
    grams: Optional[float] = Field(None, description="Converted to grams")
    nutrition_per_100g: Optional[NutritionInfo] = Field(None, description="Nutrition per 100g")


class Recipe(BaseModel):
    """Recipe result from GraphDB with optional enrichment"""
    model_config = ConfigDict(extra='allow')
    
    iri: str = Field(..., description="Recipe URI from GraphDB")
    title: Optional[str] = None
    url: Optional[str] = None
    course: Optional[str] = None
    cuisine: Optional[str] = None
    diet: Optional[str] = None
    servings: Optional[str | int] = None
    ingredients: Optional[List[str]] = None
    instructions: Optional[str | List[str]] = None  # Accept both string and list from GraphDB
    difficulty: Optional[str] = None
    cookTime: Optional[str] = None
    totalTime: Optional[str] = None
    prepTime: Optional[str] = None  # Added prepTime field
    score: Optional[float] = None
    nutrition: Optional[Dict[str, Any]] = None  # Added nutrition dict
    
    # Enrichment fields (added by Food Graph API integration)
    nutrition: Optional[NutritionInfo] = Field(None, description="Nutrition data from Food Graph API")
    nutrition_source: Optional[str] = Field(None, description="Source of nutrition data")
    enhanced_ingredients: Optional[List[EnhancedIngredient]] = Field(None, description="Ingredients with nutrition")


class SearchRequest(BaseModel):
    """Search endpoint request"""
    query: UserQuery


class SearchResponse(BaseModel):
    """Search endpoint response"""
    results: List[Recipe]
    query: UserQuery
    translatedQuery: Optional[str] = None
    count: int
    durationMs: float


class STTRequest(BaseModel):
    """Speech-to-text request"""
    audio: str = Field(..., description="Base64 encoded audio data")
    format: Optional[str] = Field('webm', description="Audio format (webm, wav, mp3, ogg, m4a)")


class STTResponse(BaseModel):
    """Speech-to-text response"""
    transcript: str = Field(..., description="Transcribed text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    detectedLanguage: str = Field(..., description="Detected language code")


class TranslateRequest(BaseModel):
    """Translation request"""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to translate")
    sourceLang: Language = Field(default='auto', description="Source language (auto for detection)")
    targetLang: Language = Field(..., description="Target language")


class TranslateResponse(BaseModel):
    """Translation response"""
    translatedText: str = Field(..., description="Translated text")
    detectedSourceLang: Language = Field(..., description="Detected source language")
    confidence: float = Field(default=0.9, ge=0.0, le=1.0, description="Translation confidence")


class NLUParseRequest(BaseModel):
    """NLU parsing request"""
    text: str = Field(..., min_length=1, max_length=500)
    lang: Language = Field(default='en')


class NLUParseResponse(BaseModel):
    """NLU parsing response"""
    constraints: QueryConstraints
    confidence: float = Field(..., ge=0.0, le=1.0)
    originalText: str


class SPARQLBuildRequest(BaseModel):
    """SPARQL builder request"""
    constraints: QueryConstraints


class SPARQLBuildResponse(BaseModel):
    """SPARQL builder response"""
    sparql: str
    params: Optional[Dict[str, Any]] = None


class APIError(BaseModel):
    """Standard error response"""
    error: str
    message: str
    code: Optional[str] = None
    details: Optional[Any] = None
