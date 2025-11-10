# 🚀 Quick Start: Food Graph API Integration

This guide will help you quickly integrate nutrition data into your MMFOOD application.

---

## ⚡ 5-Minute Setup

### Step 1: Update Environment Variables

```powershell
cd app\api
notepad .env
```

Add these credentials:

```bash
# GraphDB Credentials (REQUIRED)
GRAPHDB_USERNAME=mmfood25
GRAPHDB_PASSWORD=acm_hackathon

# Food Graph API (REQUIRED)
FOOD_GRAPH_API_URL=http://16.170.211.162:8001

# Enable Enrichment Features
ENABLE_NUTRITION_ENRICHMENT=true
ENABLE_INGREDIENT_STANDARDIZATION=true
ENABLE_AUTOCOMPLETE=true
```

### Step 2: Test Connection

```powershell
# Activate environment
.\.venv\Scripts\Activate.ps1

# Test Food Graph API connectivity
python -c "from food_graph_client import FoodGraphClient; client = FoodGraphClient(); print('Health Check:', client.health_check())"

# Expected output: Health Check: True
```

### Step 3: Run Tests

```powershell
# Run integration tests
pytest tests/test_food_graph_integration.py -v

# Expected: All tests pass or skip gracefully
```

---

## 🔧 Update Main Application

### Modify `app/api/main.py`

Add these imports at the top:

```python
from .food_graph_client import get_food_graph_client
from .enrichment import get_recipe_enricher
```

Add initialization in startup event:

```python
# Add these global variables at module level
food_graph_client = None
recipe_enricher = None

@app.on_event("startup")
async def startup():
    """Initialize services on startup"""
    global food_graph_client, recipe_enricher
    
    # Existing GraphDB initialization...
    
    # NEW: Initialize Food Graph API client
    food_graph_client = get_food_graph_client()
    recipe_enricher = get_recipe_enricher(food_graph_client)
    
    logger.info(
        "services_initialized",
        graphdb=graphdb_client is not None,
        food_graph=food_graph_client is not None
    )
```

Update the search endpoint:

```python
@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Enhanced search with nutrition enrichment"""
    start = time.time()
    
    # Step 1: Parse NLU (existing code)
    parsed = nlu_parser.parse_query(request.query.text, request.query.lang)
    
    # Step 2: Build SPARQL (existing code)
    sparql = build_sparql_query(parsed["constraints"])
    
    # Step 3: Execute GraphDB query (existing code)
    results = graphdb_client.search_recipes(sparql)
    
    # Step 4: Rank recipes (existing code)
    ranked = rank_recipes(results, parsed["constraints"])
    
    # Step 5: ENRICH with nutrition (NEW!)
    if settings.enable_nutrition_enrichment and recipe_enricher:
        try:
            ranked = await recipe_enricher.enrich_recipes(ranked)
            logger.info("recipes_enriched", count=len(ranked))
        except Exception as e:
            logger.warning("enrichment_failed", error=str(e))
            # Continue without enrichment on error
    
    duration = (time.time() - start) * 1000
    
    return SearchResponse(
        results=ranked,
        query=request.query,
        count=len(ranked),
        durationMs=duration
    )
```

Add autocomplete endpoint:

```python
@app.post("/autocomplete")
async def autocomplete(query: str = Query(..., min_length=1)):
    """Get dish name suggestions"""
    if not settings.enable_autocomplete or not recipe_enricher:
        return {"suggestions": []}
    
    try:
        suggestions = recipe_enricher.enrich_with_autocomplete(query, top_k=5)
        return {"suggestions": suggestions}
    except Exception as e:
        logger.error("autocomplete_error", query=query, error=str(e))
        return {"suggestions": []}
```

Update health check:

```python
@app.get("/health")
async def health():
    """Enhanced health check with all services"""
    graphdb_ok = graphdb_client.health_check() if graphdb_client else False
    food_graph_ok = food_graph_client.health_check() if food_graph_client else False
    
    return {
        "status": "healthy" if (graphdb_ok and food_graph_ok) else "degraded",
        "services": {
            "graphdb": "connected" if graphdb_ok else "unreachable",
            "food_graph_api": "connected" if food_graph_ok else "unreachable",
            "stt": "ready",
            "translation": "ready"
        },
        "enrichment": {
            "enabled": settings.enable_nutrition_enrichment,
            "batch_size": settings.enrichment_batch_size
        }
    }
```

---

## 🎨 Update Frontend

### Add Nutrition Display to `RecipeCard.tsx`

```typescript
interface NutritionInfo {
  calories?: number;
  protein_g?: number;
  carbs_g?: number;
  fat_g?: number;
  fiber_g?: number;
  sodium_mg?: number;
  sugar_g?: number;
}

interface Recipe {
  // ... existing fields ...
  nutrition?: NutritionInfo;
  nutrition_source?: string;
}

export function RecipeCard({ recipe }: { recipe: Recipe }) {
  return (
    <div className="recipe-card border rounded-lg p-4 hover:shadow-lg transition">
      {/* Existing content: title, cuisine, diet, etc. */}
      
      {/* NEW: Nutrition Information */}
      {recipe.nutrition && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="flex flex-wrap gap-2 text-sm">
            {recipe.nutrition.calories && (
              <span className="px-2 py-1 bg-red-50 text-red-700 rounded">
                🔥 {recipe.nutrition.calories.toFixed(0)} cal
              </span>
            )}
            {recipe.nutrition.protein_g && (
              <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded">
                💪 {recipe.nutrition.protein_g.toFixed(1)}g protein
              </span>
            )}
            {recipe.nutrition.carbs_g && (
              <span className="px-2 py-1 bg-yellow-50 text-yellow-700 rounded">
                🍚 {recipe.nutrition.carbs_g.toFixed(1)}g carbs
              </span>
            )}
            {recipe.nutrition.fat_g && (
              <span className="px-2 py-1 bg-purple-50 text-purple-700 rounded">
                🧈 {recipe.nutrition.fat_g.toFixed(1)}g fat
              </span>
            )}
          </div>
          {recipe.nutrition_source && (
            <p className="text-xs text-gray-500 mt-1">
              Nutrition from {recipe.nutrition_source}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
```

### Add Autocomplete to `SearchInterface.tsx`

```typescript
const [suggestions, setSuggestions] = useState<any[]>([]);
const [showSuggestions, setShowSuggestions] = useState(false);

const handleInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
  const query = e.target.value;
  setSearchQuery(query);
  
  // Fetch autocomplete suggestions
  if (query.length >= 3) {
    try {
      const response = await fetch(
        `http://localhost:8000/autocomplete?query=${encodeURIComponent(query)}`,
        { method: 'POST' }
      );
      const data = await response.json();
      setSuggestions(data.suggestions || []);
      setShowSuggestions(true);
    } catch (error) {
      console.error('Autocomplete failed:', error);
    }
  } else {
    setShowSuggestions(false);
  }
};

const selectSuggestion = (suggestion: any) => {
  const dishName = suggestion.name || suggestion.dish_name;
  setSearchQuery(dishName);
  setShowSuggestions(false);
  handleSearch();
};

return (
  <div className="relative">
    <input
      type="text"
      value={searchQuery}
      onChange={handleInputChange}
      placeholder="Search for recipes..."
      className="w-full px-4 py-2 border rounded-lg"
    />
    
    {/* Autocomplete Dropdown */}
    {showSuggestions && suggestions.length > 0 && (
      <ul className="absolute z-10 w-full bg-white border rounded-lg shadow-lg mt-1 max-h-60 overflow-y-auto">
        {suggestions.map((suggestion, idx) => (
          <li
            key={idx}
            onClick={() => selectSuggestion(suggestion)}
            className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
          >
            {suggestion.name || suggestion.dish_name}
            {suggestion.score && (
              <span className="text-xs text-gray-500 ml-2">
                ({(suggestion.score * 100).toFixed(0)}% match)
              </span>
            )}
          </li>
        ))}
      </ul>
    )}
  </div>
);
```

---

## ✅ Verification Checklist

### Backend

- [ ] `.env` file updated with credentials
- [ ] Food Graph API client imports successfully
- [ ] Health check shows both GraphDB and Food Graph API connected
- [ ] Integration tests pass (or skip gracefully if API is down)
- [ ] Search endpoint returns enriched recipes with nutrition
- [ ] Autocomplete endpoint returns suggestions

### Frontend

- [ ] Recipe cards show nutrition badges when available
- [ ] Autocomplete dropdown appears when typing 3+ characters
- [ ] Clicking suggestion populates search and executes query
- [ ] No console errors related to nutrition data

### Testing Queries

Try these to verify enrichment:

```
1. "Paneer Butter Masala" - Should show nutrition
2. "Dal Makhani" - Should show nutrition
3. "Chicken Biryani" - Should show nutrition
4. Type "pane" - Should suggest "Paneer..." dishes
5. "walnuts without banana" - Should work with exclusions
```

---

## 🐛 Troubleshooting

### "Health Check: False"

**Problem**: Food Graph API not reachable

**Solution**:
```powershell
# Test connectivity
curl http://16.170.211.162:8001/health

# Check environment variable
python -c "from config import settings; print(settings.food_graph_api_url)"
```

### No Nutrition Data Showing

**Problem**: Enrichment not enabled or failing

**Solution**:
```bash
# Check feature flag
ENABLE_NUTRITION_ENRICHMENT=true

# Check logs for errors
grep "enrichment" logs/app.log
```

### Autocomplete Not Working

**Problem**: Endpoint not responding

**Solution**:
```powershell
# Test endpoint directly
Invoke-WebRequest -Method POST -Uri "http://localhost:8000/autocomplete?query=pane"

# Check feature flag
ENABLE_AUTOCOMPLETE=true
```

### Slow Search Performance

**Problem**: Enrichment adding too much latency

**Solution**:
```bash
# Reduce batch size
ENRICHMENT_BATCH_SIZE=5  # Default is 10

# Or disable enrichment temporarily
ENABLE_NUTRITION_ENRICHMENT=false
```

---

## 📊 Performance Monitoring

Add these log queries to monitor performance:

```python
# Check enrichment timing
grep "recipes_enriched" logs/app.log | jq '.durationMs'

# Check nutrition fetch success rate
grep "nutrition_fetched\|nutrition_not_found" logs/app.log | wc -l

# Check autocomplete usage
grep "autocomplete" logs/app.log | wc -l
```

---

## 🎓 Next Steps

1. **Short Term** (Today):
   - [ ] Test all endpoints manually
   - [ ] Verify nutrition appears in frontend
   - [ ] Test autocomplete suggestions

2. **Medium Term** (This Week):
   - [ ] Add more nutrition fields to display
   - [ ] Implement nutrition-based filtering (e.g., "low calorie recipes")
   - [ ] Add caching for frequently requested nutrition data

3. **Long Term** (Next Sprint):
   - [ ] Track nutrition enrichment coverage (% of recipes with data)
   - [ ] Implement fallback nutrition calculation from ingredients
   - [ ] Add user feedback for incorrect nutrition data

---

## 📚 Documentation References

- **Integration Analysis**: `INTEGRATION_ANALYSIS.md` (400+ lines)
- **Food Graph Client**: `app/api/food_graph_client.py` (350+ lines)
- **Enrichment Service**: `app/api/enrichment.py` (250+ lines)
- **Integration Tests**: `app/api/tests/test_food_graph_integration.py` (300+ lines)
- **Complete Summary**: `INTEGRATION_COMPLETE.md`

---

## 🆘 Support

If you encounter issues:

1. Check logs: `logs/app.log`
2. Run tests: `pytest tests/test_food_graph_integration.py -v`
3. Verify API health: `curl http://16.170.211.162:8001/health`
4. Review error logs for specific endpoint failures

---

**Happy Cooking! 🍳**

*Last Updated: 2025-01-10*
