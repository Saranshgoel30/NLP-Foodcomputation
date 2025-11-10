# 🔍 Complete Integration Analysis: MMFOOD with Existing APIs

## Executive Summary

After deep analysis of:
1. **GraphDB Access Guide** - SPARQL endpoint and ontology structure
2. **Food Graph API Documentation** (http://16.170.211.162:8002/)
3. **Food Graph API OpenAPI Spec** (http://16.170.211.162:8001/)

This document provides a complete integration strategy.

---

## 📊 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      MMFOOD APPLICATION                          │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │   Frontend   │→ │   Backend    │→ │  External Services  │   │
│  │  (Next.js)   │  │  (FastAPI)   │  │                     │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
        ┌──────────────────────────────────────────────┐
        │                                               │
        ↓                                               ↓
┌──────────────────┐                      ┌────────────────────────┐
│   GraphDB KG     │                      │  Food Graph API        │
│  16.170.211.162  │                      │  16.170.211.162:8001   │
│  Port: 7200      │                      │  (MongoDB-backed)      │
│                  │                      │                        │
│  • Recipes       │                      │  • Nutrition Data      │
│  • Ingredients   │                      │  • Ingredient Mapping  │
│  • Instructions  │                      │  • Unit Conversion     │
│  • Metadata      │                      │  • Autocomplete        │
└──────────────────┘                      └────────────────────────┘
```

---

## 🗄️ Data Source Analysis

### 1. GraphDB Knowledge Graph (Primary Recipe Source)

**Connection Details:**
- **URL**: http://16.170.211.162:7200/
- **Repository**: `mmfood_hackathon`
- **Named Graph**: `http://172.31.34.244/fkg`
- **Credentials**: 
  - Username: `mmfood25`
  - Password: `acm_hackathon`
- **SPARQL Endpoint**: `http://16.170.211.162:7200/repositories/mmfood_hackathon`

**Ontology Schema:**
```sparql
PREFIX : <http://172.31.34.244/fkg#>

Classes:
  - :FoodRecipes (main recipe class)

Properties:
  - :hasRecipeURL (string) - Recipe source URL
  - :hasCourse (string) - "Snack", "Main Course", "Breakfast", etc.
  - :hasCuisine (string) - "Indian", "Chinese", "South Indian", etc.
  - :hasDiet (string) - "Vegetarian", "Non-Vegetarian", "Jain", "Vegan"
  - :hasServings (integer) - Number of servings
  - :hasActualIngredients (string) - Individual ingredient (multi-valued)
  - :hasInstructions (string) - Cooking instructions text
  - :hasDifficulty (string) - "Easy", "Medium", "Hard" (optional)
  - :hasCookTime (string) - e.g., "30 minutes"
  - :hasPrepTime (string) - e.g., "15 minutes"
  - :hasTotalTime (string) - e.g., "45 minutes"
```

**Key Characteristics:**
- ✅ Read-only access (no write operations allowed)
- ✅ Supports complex SPARQL queries with FILTER, FILTER NOT EXISTS
- ✅ Contains 1000+ Indian recipes with rich metadata
- ✅ Natural language in recipe names (URI contains recipe name)
- ✅ Multi-valued ingredients (each ingredient is a separate triple)

**Sample Queries Provided:**
1. Basic recipe retrieval (all fields)
2. Ingredient-based search ("chicken", "brown rice")
3. Multi-ingredient search ("chicken", "carrot", "potato")
4. Exclusion queries ("walnuts" WITHOUT "banana")
5. Complex constraints (cuisine + ingredient + time)
6. Text pattern matching (recipe name contains "samosa")
7. Instruction-based search ("dum cook")

### 2. Food Graph API (Nutrition & Enrichment)

**Connection Details:**
- **Base URL**: http://16.170.211.162:8001
- **Documentation**: http://16.170.211.162:8002
- **Backend**: FastAPI + MongoDB
- **Auth**: API key required for admin/enrichment endpoints (Header: `x-api-key`)

**Available Endpoints:**

#### 🔓 Public Endpoints (No Auth)

1. **`GET /`** - Root endpoint with API information
   - Returns: API metadata, status

2. **`GET /recipes`** - Fetch all recipes from MongoDB
   - Returns: Array of recipe objects with full details
   - Schema:
     ```json
     {
       "uri": "recipe_001",
       "name": "Paneer Butter Masala",
       "slug": "paneer-butter-masala",
       "type": ["main-course", "vegetarian"],
       "id": "001",
       "url": "https://example.com/recipe",
       "prep_time": "15 mins",
       "cook_time": "30 mins",
       "total_time": "45 mins",
       "cuisine": "Indian",
       "course": "Main",
       "difficulty": "Medium",
       "diet": "Vegetarian",
       "servings": 4,
       "instructions": [
         {
           "heading": "Preparation",
           "instructions": "Step-by-step..."
         }
       ],
       "ingredient_description": [...],
       "ingredients": {
         "Paneer": {
           "category": "Dairy",
           "form": "cubed",
           "quantity": 200,
           "unit": "grams"
         }
       }
     }
     ```

3. **`GET /recipes/{recipe_id}`** - Fetch single recipe by MongoDB `_id`
   - Parameters: `recipe_id` (string, MongoDB ObjectId)
   - Returns: Single recipe object
   - Errors: 404 if not found

4. **`POST /api/nutrition`** - Get nutrition information for a dish
   - Request Body:
     ```json
     {
       "dish_name": "Paneer Butter Masala"
     }
     ```
   - Returns: Nutrition data (calories, protein, carbs, fat, etc.)

5. **`POST /api/ingredients`** - Get ingredient mapping for a dish
   - Request Body:
     ```json
     {
       "dish_name": "Chicken Biryani"
     }
     ```
   - Returns: Structured ingredient list with mappings

6. **`POST /api/autocomplete`** - Dish name suggestions with matching scores
   - Request Body:
     ```json
     {
       "query": "pane"
     }
     ```
   - Returns: Array of matching dish names with similarity scores

7. **`POST /api/agg_nutrition`** - Aggregated nutrition for multiple dishes
   - Request Body:
     ```json
     {
       "dishes": ["Dish 1", "Dish 2", "Dish 3"]
     }
     ```
   - Returns: Combined nutrition information

8. **`POST /api/fetch_nutrition`** - Fetch precalculated nutrition info
   - Request Body:
     ```json
     {
       "dish_name": "Dal Makhani"
     }
     ```
   - Returns: Pre-computed nutrition data if available

9. **`POST /api/nearest_ingredient`** - Find top-k closest matching ingredients
   - Query Params: `k` (integer, default=5)
   - Request Body:
     ```json
     {
       "ingredient_name": "panner"
     }
     ```
   - Returns: Array of closest matching ingredient names
   - Searches both `food_name` and `alternate_name` fields

10. **`POST /api/ingredient_nutrition`** - Nutrition for single ingredient
    - Request Body:
      ```json
      {
        "ingredient_name": "paneer"
      }
      ```
    - Returns: Nutrition values per 100g

11. **`POST /api/unit_and_ingredient_to_grams`** - Fuzzy unit matching & conversion
    - Request Body:
      ```json
      {
        "unit": "cup",
        "ingredient": "rice",
        "quantity": 1
      }
      ```
    - Returns: Matched unit, ingredient, conversion to grams

12. **`GET /api/unique_units`** - All available unit names
    - Returns: List of all units in the system

13. **`POST /api/nl_to_grams`** - Convert natural language ingredient to grams
    - Request Body:
      ```json
      {
        "ingredient_string": "2 cups of rice"
      }
      ```
    - Returns: Parsed ingredient, quantity in grams

14. **`GET /api/get_precalculated_sources`** - Unique sources from precalculated data
    - Returns: Array of data source names

15. **`GET /health`** - Health check endpoint
    - Returns: Service health status

#### 🔒 Admin Endpoints (Require API Key)

16. **`POST /admin/recipes`** - Create new recipe
    - Header: `x-api-key: <your-key>`
    - Request Body: Full recipe object
    - Returns: Created recipe with MongoDB `_id`

17. **`PUT /admin/recipes/{recipe_id}`** - Update existing recipe
    - Header: `x-api-key: <your-key>`
    - Parameters: `recipe_id` (MongoDB ObjectId)
    - Request Body: Updated recipe fields
    - Returns: Updated recipe object

18. **`DELETE /admin/recipes/{recipe_id}`** - Delete recipe
    - Header: `x-api-key: <your-key>`
    - Parameters: `recipe_id` (MongoDB ObjectId)
    - Returns: Deletion confirmation

19. **`POST /enrichment/run`** - Run enrichment pipeline
    - Header: `x-api-key: <your-key>`
    - Returns: Enrichment job status

---

## 🔗 Integration Strategy

### Phase 1: GraphDB Integration (Current Implementation)

**Status**: ✅ Already implemented in `app/api/graphdb_client.py`

**What's Working:**
```python
# app/api/graphdb_client.py
- execute_sparql() - Direct SPARQL execution
- search_recipes() - Recipe search with constraints
- parse_bindings_to_recipes() - Result parsing
```

**Enhancements Needed:**
1. Add GraphDB credentials to `.env`
2. Update endpoint URL to use `mmfood_hackathon` repository
3. Ensure all queries include `FROM <http://172.31.34.244/fkg>`

### Phase 2: Food Graph API Integration (NEW)

**Purpose**: Enhance recipe results with:
- Accurate nutrition data
- Ingredient standardization
- Unit conversions
- Autocomplete suggestions

**Implementation Plan:**

#### Step 1: Create Food Graph API Client

```python
# app/api/food_graph_client.py
import httpx
from typing import Dict, List, Any, Optional
import structlog

logger = structlog.get_logger()

class FoodGraphClient:
    """Client for Food Graph API (nutrition, ingredients, units)"""
    
    def __init__(self, base_url: str = "http://16.170.211.162:8001"):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)
    
    def get_nutrition(self, dish_name: str) -> Optional[Dict[str, Any]]:
        """Get nutrition information for a dish"""
        try:
            response = self.client.post(
                f"{self.base_url}/api/nutrition",
                json={"dish_name": dish_name}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning("nutrition_fetch_failed", dish=dish_name, error=str(e))
            return None
    
    def get_ingredient_nutrition(self, ingredient: str) -> Optional[Dict[str, Any]]:
        """Get nutrition per 100g for a single ingredient"""
        try:
            response = self.client.post(
                f"{self.base_url}/api/ingredient_nutrition",
                json={"ingredient_name": ingredient}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning("ingredient_nutrition_failed", ingredient=ingredient, error=str(e))
            return None
    
    def autocomplete_dish(self, query: str) -> List[Dict[str, Any]]:
        """Get dish name suggestions"""
        try:
            response = self.client.post(
                f"{self.base_url}/api/autocomplete",
                json={"query": query}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning("autocomplete_failed", query=query, error=str(e))
            return []
    
    def nearest_ingredient(self, ingredient: str, k: int = 5) -> List[str]:
        """Find closest matching ingredients (fuzzy match)"""
        try:
            response = self.client.post(
                f"{self.base_url}/api/nearest_ingredient",
                params={"k": k},
                json={"ingredient_name": ingredient}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning("nearest_ingredient_failed", ingredient=ingredient, error=str(e))
            return []
    
    def convert_to_grams(self, ingredient_string: str) -> Optional[Dict[str, Any]]:
        """Convert natural language ingredient to grams"""
        try:
            response = self.client.post(
                f"{self.base_url}/api/nl_to_grams",
                json={"ingredient_string": ingredient_string}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning("grams_conversion_failed", input=ingredient_string, error=str(e))
            return None
    
    def fetch_precalculated_nutrition(self, dish_name: str) -> Optional[Dict[str, Any]]:
        """Fetch pre-computed nutrition data (faster)"""
        try:
            response = self.client.post(
                f"{self.base_url}/api/fetch_nutrition",
                json={"dish_name": dish_name}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning("precalc_nutrition_failed", dish=dish_name, error=str(e))
            return None
    
    def health_check(self) -> bool:
        """Check if Food Graph API is healthy"""
        try:
            response = self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
```

#### Step 2: Enhance Recipe Model with Nutrition

```python
# app/api/models.py (additions)
from typing import Optional

class NutritionInfo(BaseModel):
    """Nutrition information per serving"""
    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    sodium_mg: Optional[float] = None
    sugar_g: Optional[float] = None
    # Add more fields as available from Food Graph API

class EnhancedIngredient(BaseModel):
    """Ingredient with nutrition data"""
    name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    grams: Optional[float] = None  # Converted to grams
    nutrition_per_100g: Optional[NutritionInfo] = None

class Recipe(BaseModel):
    """Enhanced recipe model"""
    # ... existing fields ...
    
    # NEW: Nutrition data
    nutrition: Optional[NutritionInfo] = None
    nutrition_source: Optional[str] = None  # "precalculated" or "computed"
    
    # NEW: Enhanced ingredients
    enhanced_ingredients: Optional[List[EnhancedIngredient]] = None
```

#### Step 3: Create Enrichment Service

```python
# app/api/enrichment.py
from typing import List
import structlog
from .models import Recipe, NutritionInfo, EnhancedIngredient
from .food_graph_client import FoodGraphClient

logger = structlog.get_logger()

class RecipeEnricher:
    """Enriches recipes with nutrition and ingredient data"""
    
    def __init__(self, food_graph_client: FoodGraphClient):
        self.fg_client = food_graph_client
    
    async def enrich_recipe(self, recipe: Recipe) -> Recipe:
        """Add nutrition and enhanced ingredient data to recipe"""
        
        # Step 1: Try to get precalculated nutrition (fastest)
        nutrition = self.fg_client.fetch_precalculated_nutrition(recipe.title)
        if nutrition:
            recipe.nutrition = NutritionInfo(**nutrition)
            recipe.nutrition_source = "precalculated"
            logger.info("nutrition_enriched", recipe=recipe.title, source="precalculated")
        
        # Step 2: Enhance ingredients with nutrition data
        if recipe.ingredients:
            enhanced = []
            for ing in recipe.ingredients:
                # Try to standardize ingredient name
                matches = self.fg_client.nearest_ingredient(ing, k=1)
                standardized_name = matches[0] if matches else ing
                
                # Get nutrition per 100g
                ing_nutrition = self.fg_client.get_ingredient_nutrition(standardized_name)
                
                enhanced_ing = EnhancedIngredient(
                    name=ing,
                    nutrition_per_100g=NutritionInfo(**ing_nutrition) if ing_nutrition else None
                )
                enhanced.append(enhanced_ing)
            
            recipe.enhanced_ingredients = enhanced
            logger.info("ingredients_enriched", recipe=recipe.title, count=len(enhanced))
        
        return recipe
    
    async def enrich_recipes(self, recipes: List[Recipe]) -> List[Recipe]:
        """Enrich multiple recipes"""
        enriched = []
        for recipe in recipes:
            try:
                enriched_recipe = await self.enrich_recipe(recipe)
                enriched.append(enriched_recipe)
            except Exception as e:
                logger.error("enrichment_failed", recipe=recipe.title, error=str(e))
                enriched.append(recipe)  # Return original if enrichment fails
        
        return enriched
```

#### Step 4: Update Search Endpoint

```python
# app/api/main.py (updates)
from .food_graph_client import FoodGraphClient
from .enrichment import RecipeEnricher

# Initialize clients
food_graph_client = FoodGraphClient(base_url="http://16.170.211.162:8001")
recipe_enricher = RecipeEnricher(food_graph_client)

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Enhanced search with nutrition data"""
    start = time.time()
    
    # Step 1: Parse NLU
    parsed = nlu_parser.parse_query(request.query.text, request.query.lang)
    
    # Step 2: Build SPARQL
    sparql = build_sparql_query(parsed["constraints"])
    
    # Step 3: Execute against GraphDB
    results = graphdb_client.search_recipes(sparql)
    
    # Step 4: Rank results
    ranked = rank_recipes(results, parsed["constraints"])
    
    # Step 5: ENRICH with nutrition (NEW!)
    enriched = await recipe_enricher.enrich_recipes(ranked)
    
    duration = (time.time() - start) * 1000
    
    return SearchResponse(
        results=enriched,
        count=len(enriched),
        durationMs=duration,
        sparql=sparql,
        parsedQuery=parsed
    )

# NEW: Autocomplete endpoint
@app.post("/autocomplete")
async def autocomplete(query: str):
    """Get dish name suggestions"""
    suggestions = food_graph_client.autocomplete_dish(query)
    return {"suggestions": suggestions}
```

#### Step 5: Update Health Check

```python
# app/api/main.py (update)
@app.get("/health")
async def health():
    """Enhanced health check"""
    graphdb_ok = graphdb_client.health_check()
    food_graph_ok = food_graph_client.health_check()
    
    return {
        "status": "healthy" if (graphdb_ok and food_graph_ok) else "degraded",
        "graphdb": "connected" if graphdb_ok else "unreachable",
        "food_graph_api": "connected" if food_graph_ok else "unreachable",
        "stt": "ready",
        "translation": "ready"
    }
```

### Phase 3: Frontend Enhancements

#### Update Recipe Card to Show Nutrition

```typescript
// app/web/src/components/RecipeCard.tsx (additions)
interface NutritionInfo {
  calories?: number;
  protein_g?: number;
  carbs_g?: number;
  fat_g?: number;
}

interface Recipe {
  // ... existing fields ...
  nutrition?: NutritionInfo;
  nutrition_source?: string;
}

export function RecipeCard({ recipe }: { recipe: Recipe }) {
  return (
    <div className="recipe-card">
      {/* ... existing content ... */}
      
      {/* NEW: Nutrition Badge */}
      {recipe.nutrition && (
        <div className="nutrition-summary">
          <span className="nutrition-item">
            🔥 {recipe.nutrition.calories?.toFixed(0)} cal
          </span>
          <span className="nutrition-item">
            💪 {recipe.nutrition.protein_g?.toFixed(1)}g protein
          </span>
          <span className="nutrition-item">
            🍚 {recipe.nutrition.carbs_g?.toFixed(1)}g carbs
          </span>
          <span className="nutrition-item">
            🧈 {recipe.nutrition.fat_g?.toFixed(1)}g fat
          </span>
        </div>
      )}
    </div>
  );
}
```

#### Add Autocomplete to Search Bar

```typescript
// app/web/src/components/SearchInterface.tsx (additions)
const [suggestions, setSuggestions] = useState<string[]>([]);
const [showSuggestions, setShowSuggestions] = useState(false);

const handleInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
  const query = e.target.value;
  setSearchQuery(query);
  
  if (query.length >= 3) {
    try {
      const response = await apiClient.autocomplete(query);
      setSuggestions(response.suggestions);
      setShowSuggestions(true);
    } catch (error) {
      console.error('Autocomplete failed:', error);
    }
  } else {
    setShowSuggestions(false);
  }
};

return (
  <div className="search-container">
    <input
      type="text"
      value={searchQuery}
      onChange={handleInputChange}
      placeholder="Search for recipes..."
    />
    
    {/* Autocomplete Dropdown */}
    {showSuggestions && suggestions.length > 0 && (
      <ul className="autocomplete-dropdown">
        {suggestions.map((suggestion, idx) => (
          <li
            key={idx}
            onClick={() => {
              setSearchQuery(suggestion);
              setShowSuggestions(false);
              handleSearch();
            }}
          >
            {suggestion}
          </li>
        ))}
      </ul>
    )}
  </div>
);
```

---

## 🎯 Implementation Priority

### High Priority (Week 1)
1. ✅ Update GraphDB credentials in `.env`
2. ✅ Test GraphDB connectivity with existing client
3. ✅ Create `food_graph_client.py`
4. ✅ Add nutrition enrichment to search pipeline
5. ✅ Update frontend to display nutrition info

### Medium Priority (Week 2)
1. ⭕ Implement autocomplete functionality
2. ⭕ Add ingredient standardization
3. ⭕ Create nutrition detail view in modal
4. ⭕ Add loading states for enrichment

### Low Priority (Week 3)
1. ⭕ Implement unit conversion for recipe scaling
2. ⭕ Add dietary filter based on nutrition thresholds
3. ⭕ Cache nutrition data in Redis
4. ⭕ Create admin panel for recipe management

---

## 🧪 Testing Strategy

### 1. GraphDB Integration Tests

```python
# app/api/tests/test_graphdb_integration.py
def test_graphdb_connection():
    """Test GraphDB is reachable"""
    client = GraphDBClient()
    assert client.health_check()

def test_basic_recipe_query():
    """Test basic SPARQL query execution"""
    client = GraphDBClient()
    sparql = """
    PREFIX : <http://172.31.34.244/fkg#>
    SELECT ?recipe
    FROM <http://172.31.34.244/fkg>
    WHERE {
      ?recipe a :FoodRecipes .
      ?recipe :hasActualIngredients "chicken" .
    }
    LIMIT 10
    """
    results = client.execute_sparql(sparql)
    assert len(results) > 0

def test_exclusion_query():
    """Test FILTER NOT EXISTS works correctly"""
    client = GraphDBClient()
    constraints = {
        "include": ["walnuts"],
        "exclude": ["banana"]
    }
    sparql = build_sparql_query(constraints)
    results = client.search_recipes(sparql)
    
    # Verify no results contain banana
    for recipe in results:
        assert "banana" not in [ing.lower() for ing in recipe.ingredients]
```

### 2. Food Graph API Integration Tests

```python
# app/api/tests/test_food_graph_integration.py
def test_food_graph_health():
    """Test Food Graph API is reachable"""
    client = FoodGraphClient()
    assert client.health_check()

def test_nutrition_fetch():
    """Test nutrition data retrieval"""
    client = FoodGraphClient()
    nutrition = client.get_nutrition("Paneer Butter Masala")
    assert nutrition is not None
    assert "calories" in nutrition

def test_ingredient_standardization():
    """Test ingredient fuzzy matching"""
    client = FoodGraphClient()
    matches = client.nearest_ingredient("panner", k=1)
    assert len(matches) > 0
    assert "paneer" in matches[0].lower()

def test_nl_to_grams_conversion():
    """Test natural language unit conversion"""
    client = FoodGraphClient()
    result = client.convert_to_grams("2 cups rice")
    assert result is not None
    assert result["grams"] > 0
```

### 3. End-to-End Tests

```python
# app/api/tests/test_e2e_search.py
async def test_enriched_search():
    """Test full search pipeline with enrichment"""
    request = SearchRequest(
        query=UserQuery(
            text="Chinese chicken under 30 minutes",
            lang="en"
        )
    )
    
    response = await search(request)
    
    assert response.count > 0
    assert response.results[0].nutrition is not None
    assert response.results[0].nutrition.calories > 0
```

---

## 📋 Configuration Updates

### Environment Variables (`.env`)

```bash
# GraphDB Configuration
GRAPHDB_URL=http://16.170.211.162:7200
GRAPHDB_REPOSITORY=mmfood_hackathon
GRAPHDB_NAMED_GRAPH=http://172.31.34.244/fkg
GRAPHDB_USERNAME=mmfood25
GRAPHDB_PASSWORD=acm_hackathon

# Food Graph API
FOOD_GRAPH_API_URL=http://16.170.211.162:8001
FOOD_GRAPH_API_KEY=  # Optional, only for admin endpoints

# Feature Flags
ENABLE_NUTRITION_ENRICHMENT=true
ENABLE_INGREDIENT_STANDARDIZATION=true
ENABLE_AUTOCOMPLETE=true

# Performance
NUTRITION_ENRICHMENT_TIMEOUT=5000  # ms
ENRICHMENT_BATCH_SIZE=10
```

### Update Config Class

```python
# app/api/config.py (additions)
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Food Graph API
    food_graph_api_url: str = "http://16.170.211.162:8001"
    food_graph_api_key: Optional[str] = None
    
    # Feature Flags
    enable_nutrition_enrichment: bool = True
    enable_ingredient_standardization: bool = True
    enable_autocomplete: bool = True
    
    # Performance
    nutrition_enrichment_timeout: int = 5000
    enrichment_batch_size: int = 10
```

---

## 🚀 Deployment Checklist

- [ ] Update `.env` with GraphDB credentials
- [ ] Test GraphDB connectivity
- [ ] Implement `food_graph_client.py`
- [ ] Create `enrichment.py` service
- [ ] Update `main.py` search endpoint
- [ ] Add nutrition models to `models.py`
- [ ] Update frontend RecipeCard component
- [ ] Add autocomplete to search bar
- [ ] Write integration tests
- [ ] Update health check endpoint
- [ ] Test full pipeline end-to-end
- [ ] Update documentation
- [ ] Performance testing with enrichment
- [ ] Monitor API rate limits

---

## ⚠️ Important Notes

1. **Rate Limiting**: Both GraphDB and Food Graph API may have rate limits. Implement:
   - Request throttling
   - Batch enrichment
   - Caching layer (Redis)

2. **Error Handling**: Enrichment should be optional:
   - If nutrition fetch fails, return recipe without nutrition
   - Log errors but don't fail the search
   - Implement circuit breaker for Food Graph API

3. **Performance**: Enrichment adds latency:
   - Use async/await for parallel requests
   - Consider background enrichment for large result sets
   - Cache frequently requested nutrition data

4. **Data Consistency**:
   - GraphDB recipe names may not exactly match Food Graph API dish names
   - Implement fuzzy matching for nutrition lookup
   - Log mismatches for manual review

5. **Security**:
   - Never expose GraphDB credentials in frontend
   - Keep Food Graph API key in backend only
   - Validate all user inputs before SPARQL query construction

---

## 📊 Expected Performance Metrics

| Operation | Without Enrichment | With Enrichment | Target |
|-----------|-------------------|----------------|--------|
| Simple search | 200-500ms | 800-1200ms | <1500ms |
| Complex search | 500-1000ms | 1200-2000ms | <2500ms |
| Autocomplete | N/A | 100-200ms | <300ms |
| Health check | 50ms | 100ms | <200ms |

---

## 🎉 Benefits of Integration

1. **Enhanced User Experience**:
   - Nutrition information helps dietary planning
   - Autocomplete speeds up recipe discovery
   - Ingredient standardization improves search accuracy

2. **Better Search Results**:
   - Fuzzy ingredient matching catches typos
   - Unit conversion enables precise recipe scaling
   - Multiple data sources increase coverage

3. **Future-Ready Architecture**:
   - Modular design allows easy addition of new APIs
   - Enrichment pipeline can be extended
   - Clean separation between data sources

---

## 📞 Support & Resources

- **GraphDB Workbench**: http://16.170.211.162:7200/
- **Food Graph API Docs**: http://16.170.211.162:8002/
- **Food Graph API Swagger**: http://16.170.211.162:8001/docs
- **SPARQL Tutorial**: https://www.w3.org/TR/sparql11-query/
- **GraphDB Documentation**: https://graphdb.ontotext.com/documentation

---

*Last Updated: 2025-01-10*
*Status: Ready for Implementation*
