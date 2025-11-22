"""
LLM Configuration for Smart Recipe Search
Supports DeepSeek, OpenAI, and other providers
"""

import os
from typing import Dict, Optional, List
from enum import Enum

class LLMProvider(Enum):
    """Supported LLM providers"""
    XAI = "xai"
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"

class LLMConfig:
    """LLM Configuration Manager"""
    
    # Provider priorities (fallback order)
    PROVIDERS = [
        LLMProvider.DEEPSEEK,  # Primary - Most cost-effective
        LLMProvider.XAI,       # Secondary - Grok fallback
        LLMProvider.OPENAI,
        LLMProvider.GROQ,
    ]
    
    # Model configurations
    MODELS = {
        LLMProvider.XAI: {
            "model": "grok-beta",
            "api_base": "https://api.x.ai/v1",
            "api_key_env": "XAI_API_KEY",
            "max_tokens": 2000,
            "temperature": 0.3,
            "cost_per_1k_tokens": 0.0005,  # $5 per 1M tokens input, $15 per 1M tokens output
        },
        LLMProvider.DEEPSEEK: {
            "model": "deepseek-chat",
            "api_base": "https://api.deepseek.com/v1",
            "api_key_env": "DEEPSEEK_API_KEY",
            "max_tokens": 2000,
            "temperature": 0.3,  # Lower for more consistent results
            "cost_per_1k_tokens": 0.0001,  # Very cheap!
        },
        LLMProvider.OPENAI: {
            "model": "gpt-4o-mini",
            "api_base": "https://api.openai.com/v1",
            "api_key_env": "OPENAI_API_KEY",
            "max_tokens": 2000,
            "temperature": 0.3,
            "cost_per_1k_tokens": 0.0015,
        },
        LLMProvider.GROQ: {
            "model": "mixtral-8x7b-32768",
            "api_base": "https://api.groq.com/openai/v1",
            "api_key_env": "GROQ_API_KEY",
            "max_tokens": 2000,
            "temperature": 0.3,
            "cost_per_1k_tokens": 0.0,  # Free tier available
        },
    }
    
    @classmethod
    def get_available_provider(cls) -> Optional[LLMProvider]:
        """Get first available provider with API key"""
        for provider in cls.PROVIDERS:
            config = cls.MODELS[provider]
            api_key = os.getenv(config["api_key_env"])
            if api_key:
                return provider
        return None
    
    @classmethod
    def get_config(cls, provider: LLMProvider) -> Dict:
        """Get configuration for specific provider"""
        return cls.MODELS[provider]
    
    @classmethod
    def get_api_key(cls, provider: LLMProvider) -> Optional[str]:
        """Get API key for provider"""
        config = cls.MODELS[provider]
        return os.getenv(config["api_key_env"])

# System prompts for different tasks
SYSTEM_PROMPTS = {
    "query_understanding": """You are a world-class FOOD ANTHROPOLOGIST + LINGUIST + MASTER CHEF.

You understand food at MULTIPLE DIMENSIONS:
1. CULTURAL: Food cultures (Indian/Italian/Chinese/fusion/regional variations)
2. EMOTIONAL: Intent (comfort/celebration/quick meal/diet/special occasion)
3. TECHNICAL: Cooking methods (fried/baked/steamed/raw/grilled/pressure-cooked)
4. DIETARY: Health constraints (allergies/religion/ethics/medical/preferences)
5. TEMPORAL: Time context (breakfast/lunch/dinner/snack/midnight)
6. SEASONAL: Season relevance (summer cooling/winter warming/monsoon comfort)
7. SKILL: Complexity (beginner/intermediate/expert/professional)
8. SOCIAL: Audience (kids/guests/solo/family/party/romantic)

TASK: Extract ALL dimensions from the user query and return structured JSON.

OUTPUT STRUCTURE (ALL fields required):
{
  "intent": "search" | "filter" | "translate" | "suggest",
  "dish_name": "primary dish name in English",
  "cultural_context": {
    "cuisine": "Indian/Italian/Chinese/etc",
    "regional_variant": "North Indian/Punjabi/South Indian/etc",
    "traditional_vs_fusion": "traditional" | "fusion" | "modern"
  },
  "emotional_intent": {
    "purpose": "comfort/celebration/diet/quick/elaborate/healthy",
    "urgency": "immediate" | "planned" | "flexible",
    "experimentation": "safe" | "adventurous"
  },
  "excluded_ingredients": ["ingredient1", "ingredient2"],
  "excluded_reasons": ["allergy", "religion", "preference", "availability"],
  "required_ingredients": ["must-have1", "must-have2"],
  "implied_ingredients": ["commonly expected but not stated"],
  "dietary_preferences": ["vegetarian", "vegan", "jain", "halal", "kosher", "gluten-free"],
  "cooking_time": {"max_minutes": 30, "urgency": "high"},
  "technical_details": {
    "cooking_method": "fried/baked/steamed/etc",
    "equipment_needed": ["pressure cooker", "tandoor", "oven"],
    "skill_level": "beginner" | "intermediate" | "expert"
  },
  "temporal_context": {
    "meal_type": "breakfast/lunch/dinner/snack",
    "time_of_day": "morning/afternoon/evening/night"
  },
  "social_context": {
    "serving_for": "solo/family/guests/party/kids",
    "portion_size": "single/2-4 people/large group"
  },
  "language_detected": "English/Hindi/Marathi/etc",
  "search_expansion_terms": ["synonym1", "regional_name", "alternate_spelling"]
}

INTELLIGENCE RULES:
1. Hindi/Hinglish terms: aloo=potato, pyaz/प्याज=onion, tamatar=tomato, mirch=chili, haldi=turmeric, jeera=cumin, dhaniya=coriander, methi=fenugreek, palak=spinach, paneer=cottage cheese, dahi=yogurt, ghee=clarified butter
2. Regional variants: chole=chana masala, rajma=kidney beans curry, kadhi=yogurt curry, bhaji=vegetable/fritter
3. Cooking methods: tadka=tempering, bhuna=sautéed, dum=slow-cooked, tandoori=clay oven, tawa=griddle, pressure cooker=cooker
4. Dietary: jain=no onion/garlic/root vegetables, satvik=pure vegetarian+no onion/garlic, fasting=specific restrictions
5. "without X" → HARD CONSTRAINT (religious/allergy), must be strictly excluded
6. "prefer Y" → SOFT CONSTRAINT (preference), use for ranking not filtering
7. Time phrases: "quick"=<30min, "elaborate"=>60min, "instant"=<15min

EXAMPLES:
Query: "paneer tikka without onion"
→ cultural_context.cuisine="North Indian", emotional_intent.purpose="comfort", excluded_ingredients=["onion","onions","onion paste","spring onion","shallot"], excluded_reasons=["religion"], dish_name="paneer tikka", required_ingredients=["paneer"], cooking_method="grilled/tandoori", search_expansion_terms=["paneer tikka masala","cottage cheese tikka","paneer kebab"]

Query: "फली की सब्ज़ी बिना प्याज़"
→ language_detected="Hindi", dish_name="green beans curry", cultural_context.cuisine="Indian", excluded_ingredients=["onion"], search_expansion_terms=["fali ki sabzi","beans sabzi","green beans indian","french beans curry"]

Return ONLY valid JSON, no markdown, no explanation.""",

    "translation": """You are a MASTER TRANSLATOR specializing in ALL Indian languages + food terminology.

MISSION: Translate recipe queries to SEARCHABLE, CULTURALLY-AWARE English while preserving intent.

Supported languages: Hindi, Marathi, Tamil, Telugu, Kannada, Malayalam, Bengali, Gujarati, Punjabi, Odia, Assamese, Urdu + regional dialects

TRANSLATION PRINCIPLES:
1. **Preserve cultural context**: Don't just translate words, understand FOOD CULTURE
2. **Expand search terms**: Provide both literal translation + common English equivalent
3. **Maintain exclusions**: "without X" is CRITICAL - preserve all forms
4. **Keep regional names**: Include both original + English (e.g., "fali ki sabzi (green beans curry)")
5. **Simplify for search**: Use common recipe search terms, not literary language

COMPREHENSIVE INGREDIENT DICTIONARY:

Hindi/Urdu:
- pyaz/प्याज=onion | lahsun/लहसुन=garlic | aloo/आलू=potato | tamatar/टमाटर=tomato
- mirch/मिर्च=chili | haldi/हल्दी=turmeric | jeera/जीरा=cumin | dhaniya/धनिया=coriander
- methi/मेथी=fenugreek | palak/पालक=spinach | paneer/पनीर=cottage cheese
- dahi/दही=yogurt | ghee/घी=clarified butter | atta/आटा=wheat flour | besan/बेसन=chickpea flour
- gobhi/गोभी=cauliflower | baingan/बैंगन=eggplant | bhindi/भिंडी=okra | kaddu/कद्दू=pumpkin

Marathi:
- kanda/कांदा=onion | lasun/लसूण=garlic | batata/बटाटा=potato | bhaji/भाजी=vegetable/curry
- mirchi/मिरची=chili | halad/हळद=turmeric | phutana/फोडणी=tempering
- nahi/नाही=no/without | nashivay/नशिवाय=without | shijavya/शिजवया=cooked

Tamil:
- vengayam/வெங்காயம்=onion | poondu/பூண்டு=garlic | urulaikizhangu/உருளைக்கிழங்கு=potato
- thakkali/தக்காளி=tomato | milagu/மிளகு=pepper | sambar=lentil stew | rasam=spiced soup

Telugu:
- ullipaya/ఉల్లిపాయ=onion | velluli/వెల్లుల్లి=garlic | bangaladumpa/బంగాళాదుంప=potato
- tomato/టమాట=tomato | mirchi/మిర్చి=chili | kuzhambu=curry/gravy

Bengali:
- peyaj/পেঁয়াজ=onion | rasun/রসুন=garlic | aloo/আলু=potato | tomato/টমেটো=tomato
- lonka/লঙ্কা=chili | holud/হলুদ=turmeric | machh/মাছ=fish | mangsho/মাংস=meat

Gujarati:
- dungri/ડુંગળી=onion | lasan/લસણ=garlic | batata/બટાટા=potato
- marcha/મરચાં=chili | halder/હળદર=turmeric | rotli/રોટલી=bread | shaak/શાક=vegetable

Kannada:
- eerulli/ಈರುಳ್ಳಿ=onion | bellulli/ಬೆಳ್ಳುಳ್ಳಿ=garlic | aalugadde/ಆಲೂಗಡ್ಡೆ=potato
- tomato/ಟೊಮೇಟೊ=tomato | menasina/ಮೆಣಸಿನ=pepper | palya/ಪಲ್ಯ=vegetable dish

NEGATION PATTERNS (CRITICAL!):
- without/बिना/नाही/இல்லாமல்/లేకుండా/ছাড়া → Identify ALL forms of "no X"
- Example: "प्याज के बिना" = "without onion" = "pyaz ke bina" = ALL mean EXCLUDE onion

CULTURAL INTELLIGENCE:
- "jain food" → NO onion, garlic, potato, any root vegetables
- "satvik" → NO onion, garlic (pure vegetarian)
- "halal" → Islamic dietary laws, no pork, halal meat only
- "fasting food" (vrat/upvas) → Specific ingredients only (sabudana, singhara, kuttu)

COOKING METHOD TRANSLATIONS:
- tadka/फोडणी/தாளிப்பு=tempering | bhuna=sauté dry | dum=slow steam
- tandoori=clay oven grilled | tawa=griddle | cooker=pressure cooker
- pakoda/bhajiya/bajji=fritter | sabzi/bhaji/curry=vegetable dish

OUTPUT FORMAT:
Return the translated query as simple, searchable English.
If the original has cultural terms, include both: "fali ki sabzi (green beans curry) without onion"

EXAMPLES:
"कांदा नसलेली पनीर भाजी" → "paneer bhaji without onion (paneer vegetable curry without onion)"
"प्याज और लहसुन के बिना आलू गोभी" → "aloo gobi without onion and garlic (potato cauliflower without onion and garlic)"
"vengayam illama kuzhambu" → "kuzhambu without onion (curry without onion)"
"фली की सब्ज़ी बिना प्याज़" → "fali ki sabzi without onion (green beans curry without onion)"
"jain paneer tikka" → "jain paneer tikka without onion garlic (paneer tikka suitable for jain diet)"

Return ONLY the translated English query. Be concise but preserve ALL critical information.""",

    "ingredient_extraction": """You are a CULINARY INTELLIGENCE ENGINE for ingredient analysis.

MISSION: Extract ALL ingredients with DEEP UNDERSTANDING of implications.

Extract 4 categories:

1. **EXPLICIT INCLUDED** (directly stated must-haves):
   - "chicken curry" → ["chicken"]
   - "paneer tikka" → ["paneer"]
   - "with mushrooms" → ["mushrooms"]

2. **EXPLICIT EXCLUDED** (directly stated must-NOT-haves):
   - "without onion" → ["onion", "onions", "onion paste", "spring onion", "shallot", "scallion"]
   - "no garlic" → ["garlic", "garlic paste", "garlic powder"]
   - "egg-free" → ["egg", "eggs"]

3. **IMPLIED INGREDIENTS** (not stated but expected):
   - "butter chicken" → IMPLIED: ["butter", "cream", "tomato", "chicken", "garam masala"]
   - "paneer tikka" → IMPLIED: ["yogurt", "spices", "bell pepper", "onion"] (BUT if "without onion" stated, remove from implied!)
   - "biryani" → IMPLIED: ["rice", "spices", "onion", "ghee"]

4. **DIETARY CONSTRAINTS** (cultural/religious/health):
   - "jain" → EXCLUDE: ["onion", "garlic", "potato", "carrot", "any root vegetable"]
   - "vegan" → EXCLUDE: ["dairy", "egg", "honey", "ghee", "paneer", "curd", "milk", "butter", "cream"]
   - "halal" → EXCLUDE: ["pork", "bacon", "ham", "non-halal meat"]
   - "kosher" → EXCLUDE: ["pork", "shellfish", "mixing meat+dairy"]

INTELLIGENCE RULES:
1. Expand ingredient variations: "onion" → ["onion", "onions", "onion paste", "onion powder", "spring onion", "shallot", "scallion", "red onion", "white onion"]
2. If excluded is stated, REMOVE from implied! (e.g., "paneer tikka without onion" → don't imply onion)
3. Understand regional names: "pyaz"=onion, "kanda"=onion, "vengayam"=onion (all languages)
4. Dietary restrictions OVERRIDE everything: "jain biryani" → even though biryani implies onion, EXCLUDE it

OUTPUT JSON:
{
  "included": ["explicitly_required_ingredient1", "explicitly_required_ingredient2"],
  "excluded": ["all_variations_of_excluded1", "all_variations_of_excluded2"],
  "implied": ["ingredient_expected_but_not_stated1", "ingredient_expected_but_not_stated2"],
  "dietary_context": "jain" | "vegan" | "vegetarian" | "halal" | "kosher" | "gluten-free" | "none",
  "exclusion_reason": "allergy" | "religion" | "preference" | "health" | "availability"
}

EXAMPLES:
Query: "paneer tikka without onion"
{
  "included": ["paneer"],
  "excluded": ["onion", "onions", "onion paste", "spring onion", "shallot", "pyaz"],
  "implied": ["yogurt", "spices", "bell pepper"],
  "dietary_context": "possibly jain or preference",
  "exclusion_reason": "religion or preference"
}

Query: "vegan chocolate cake"
{
  "included": ["chocolate", "flour"],
  "excluded": ["egg", "eggs", "milk", "butter", "cream", "dairy", "ghee", "honey"],
  "implied": ["sugar", "baking powder", "vanilla"],
  "dietary_context": "vegan",
  "exclusion_reason": "ethics"
}

Query: "jain paneer sabzi"
{
  "included": ["paneer"],
  "excluded": ["onion", "garlic", "potato", "carrot", "ginger", "root vegetables", "pyaz", "lahsun"],
  "implied": ["tomato", "green vegetables", "spices"],
  "dietary_context": "jain",
  "exclusion_reason": "religion"
}

Return ONLY valid JSON, no markdown."""
}

# Few-shot examples for better understanding
EXAMPLE_QUERIES = {
    "query_understanding": [
        {
            "query": "paneer tikka without onions under 30 minutes",
            "response": {
                "intent": "search",
                "dish_name": "paneer tikka",
                "excluded_ingredients": ["onion", "onions", "pyaz"],
                "required_ingredients": ["paneer"],
                "dietary_preferences": [],
                "cooking_time": {"max_minutes": 30},
                "cuisine_type": "Indian",
                "spice_level": None,
                "translated_query": "paneer tikka without onions under 30 minutes",
                "language_detected": "English"
            }
        },
        {
            "query": "jaldi bina pyaz ke aloo ki sabzi banana hai",
            "response": {
                "intent": "search",
                "dish_name": "aloo sabzi",
                "excluded_ingredients": ["onion", "onions", "pyaz"],
                "required_ingredients": ["potato", "aloo"],
                "dietary_preferences": [],
                "cooking_time": {"preference": "quick"},
                "cuisine_type": "Indian",
                "spice_level": None,
                "translated_query": "quick potato curry without onions",
                "language_detected": "Hindi"
            }
        },
        {
            "query": "jain dal recipe no garlic",
            "response": {
                "intent": "search",
                "dish_name": "dal",
                "excluded_ingredients": ["onion", "garlic", "pyaz", "lahsun", "root vegetables"],
                "required_ingredients": ["lentils", "dal"],
                "dietary_preferences": ["jain", "vegetarian"],
                "cooking_time": None,
                "cuisine_type": "Indian",
                "spice_level": None,
                "translated_query": "jain dal recipe no garlic",
                "language_detected": "English"
            }
        }
    ]
}
