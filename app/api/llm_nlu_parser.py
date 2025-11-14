"""
Advanced NLU Parser with LLM Integration
Supports Indian languages, intent recognition, and entity extraction
"""
import re
import json
from typing import Dict, List, Optional, Tuple, Any
import structlog
from models import QueryConstraints, Language

logger = structlog.get_logger()

# Indian language food vocabulary
INDIAN_FOOD_VOCAB = {
    'hi': {  # Hindi
        'ingredients': {
            'प्याज': 'onion', 'आलू': 'potato', 'टमाटर': 'tomato',
            'पनीर': 'paneer', 'दही': 'yogurt', 'घी': 'ghee',
            'मसाला': 'spice', 'मिर्च': 'chilli', 'धनिया': 'coriander',
            'लहसुन': 'garlic', 'अदरक': 'ginger', 'चावल': 'rice',
            'दाल': 'dal', 'रोटी': 'roti', 'सब्जी': 'vegetable'
        },
        'exclusions': ['बिना', 'के बिना', 'छोड़कर', 'नहीं'],
        'cuisines': ['भारतीय', 'पंजाबी', 'दक्षिण भारतीय', 'गुजराती'],
        'time_words': ['मिनट', 'घंटा', 'जल्दी', 'तेज़']
    },
    'mr': {  # Marathi
        'ingredients': {
            'कांदा': 'onion', 'बटाटा': 'potato', 'टोमॅटो': 'tomato',
            'पनीर': 'paneer', 'दही': 'yogurt', 'तूप': 'ghee',
            'मसाला': 'spice', 'मिरची': 'chilli', 'कोथिंबीर': 'coriander',
            'लसूण': 'garlic', 'आले': 'ginger', 'तांदूळ': 'rice',
            'डाळ': 'dal', 'भाकरी': 'roti', 'भाजी': 'vegetable'
        },
        'exclusions': ['शिवाय', 'नको', 'वगळा'],
        'cuisines': ['महाराष्ट्रियन', 'कोकणी'],
        'time_words': ['मिनिट', 'तास', 'लवकर']
    },
    'ta': {  # Tamil
        'ingredients': {
            'வெங்காயம்': 'onion', 'உருளைக்கிழங்கு': 'potato', 'தக்காளி': 'tomato',
            'பன்னீர்': 'paneer', 'தயிர்': 'yogurt', 'நெய்': 'ghee',
            'மசாலா': 'spice', 'மிளகாய்': 'chilli', 'கொத்தமல்லி': 'coriander',
            'பூண்டு': 'garlic', 'இஞ்சி': 'ginger', 'அரிசி': 'rice',
            'பருப்பு': 'dal', 'சப்பாத்தி': 'roti', 'காய்கறி': 'vegetable'
        },
        'exclusions': ['இல்லாமல்', 'தவிர', 'வேண்டாம்'],
        'cuisines': ['தமிழ்', 'செட்டிநாடு', 'தென்னிந்திய'],
        'time_words': ['நிமிடம்', 'மணி', 'விரைவாக']
    },
    'te': {  # Telugu
        'ingredients': {
            'ఉల్లి': 'onion', 'బంగాళాదుంప': 'potato', 'టమాటా': 'tomato',
            'పన్నీర్': 'paneer', 'పెరుగు': 'yogurt', 'నెయ్యి': 'ghee',
            'మసాలా': 'spice', 'మిర్చి': 'chilli', 'కొత్తిమీర': 'coriander',
            'వెల్లుల్లి': 'garlic', 'అల్లం': 'ginger', 'బియ్యం': 'rice',
            'పప్పు': 'dal', 'రోటీ': 'roti', 'కూర': 'vegetable'
        },
        'exclusions': ['లేకుండా', 'తప్ప', 'వద్దు'],
        'cuisines': ['తెలుగు', 'ఆంధ్ర', 'హైదరాబాద్'],
        'time_words': ['నిమిషం', 'గంట', 'త్వరగా']
    },
    'bn': {  # Bengali
        'ingredients': {
            'পেঁয়াজ': 'onion', 'আলু': 'potato', 'টমেটো': 'tomato',
            'পনির': 'paneer', 'দই': 'yogurt', 'ঘি': 'ghee',
            'মসলা': 'spice', 'মরিচ': 'chilli', 'ধনে': 'coriander',
            'রসুন': 'garlic', 'আদা': 'ginger', 'চাল': 'rice',
            'ডাল': 'dal', 'রুটি': 'roti', 'সবজি': 'vegetable'
        },
        'exclusions': ['ছাড়া', 'বাদে', 'নয়'],
        'cuisines': ['বাংলা', 'বাঙালি'],
        'time_words': ['মিনিট', 'ঘণ্টা', 'দ্রুত']
    },
    'gu': {  # Gujarati
        'ingredients': {
            'ડુંગળી': 'onion', 'બટાટા': 'potato', 'ટમેટા': 'tomato',
            'પનીર': 'paneer', 'દહીં': 'yogurt', 'ઘી': 'ghee',
            'મસાલો': 'spice', 'મરચું': 'chilli', 'કોથમીર': 'coriander',
            'લસણ': 'garlic', 'આદુ': 'ginger', 'ચોખા': 'rice',
            'દાળ': 'dal', 'રોટલી': 'roti', 'શાક': 'vegetable'
        },
        'exclusions': ['વગર', 'સિવાય', 'નહીં'],
        'cuisines': ['ગુજરાતી', 'કથિયાવાડી'],
        'time_words': ['મિનિટ', 'કલાક', 'ઝડપથી']
    }
}


class LLMNLUParser:
    """
    Advanced NLU Parser with LLM integration for better understanding
    Supports Indian languages and complex query understanding
    """
    
    def __init__(self, use_llm: bool = True, llm_api_key: Optional[str] = None):
        self.use_llm = use_llm
        self.llm_api_key = llm_api_key
        self.llm_client = None
        
        if use_llm and llm_api_key:
            self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize LLM client (OpenAI, Anthropic, or local model)"""
        try:
            # Try OpenAI first
            import openai
            self.llm_client = openai.OpenAI(api_key=self.llm_api_key)
            self.llm_provider = 'openai'
            logger.info("llm_initialized", provider="openai")
        except Exception as e:
            logger.warning("llm_initialization_failed", error=str(e))
            self.use_llm = False
    
    def parse_with_llm(self, text: str, lang: Language = 'en') -> Dict[str, Any]:
        """
        Use LLM to parse natural language query into structured constraints
        
        Args:
            text: User query in any language
            lang: Language code
            
        Returns:
            Dict with extracted constraints
        """
        if not self.use_llm or not self.llm_client:
            logger.debug("llm_not_available", falling_back="rule_based")
            return self._rule_based_parse(text, lang)
        
        try:
            # Create prompt for LLM
            prompt = self._create_llm_prompt(text, lang)
            
            # Call LLM
            response = self.llm_client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cost-effective
                messages=[
                    {
                        "role": "system",
                        "content": """You are a food query parser. Extract structured information from user queries about recipes.
                        
Return JSON with these fields:
- include: List of ingredients to include
- exclude: List of ingredients to exclude  
- cuisine: List of cuisine types
- diet: List of dietary restrictions
- maxCookMinutes: Maximum cooking time in minutes (integer or null)
- maxTotalMinutes: Maximum total time in minutes (integer or null)
- course: List of meal courses
- keywords: List of cooking techniques or keywords
- intent: User's intent (search, filter, recommend)
- confidence: Your confidence 0.0-1.0

Be liberal with ingredient extraction but conservative with exclusions."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Low temperature for consistency
                response_format={"type": "json_object"}
            )
            
            # Parse LLM response
            result = json.loads(response.choices[0].message.content)
            logger.info("llm_parsed_query", input_length=len(text), confidence=result.get('confidence', 0.0))
            
            return result
            
        except Exception as e:
            logger.error("llm_parsing_failed", error=str(e))
            return self._rule_based_parse(text, lang)
    
    def _create_llm_prompt(self, text: str, lang: Language) -> str:
        """Create optimized prompt for LLM"""
        lang_name = {
            'en': 'English', 'hi': 'Hindi', 'mr': 'Marathi', 
            'ta': 'Tamil', 'te': 'Telugu', 'bn': 'Bengali',
            'gu': 'Gujarati', 'kn': 'Kannada', 'ml': 'Malayalam'
        }.get(lang, 'English')
        
        return f"""Parse this {lang_name} recipe query and extract information:

Query: "{text}"

Extract:
1. Ingredients to INCLUDE (be generous, include main ingredients)
2. Ingredients to EXCLUDE (only if explicitly mentioned with "without", "no", "except")
3. Cuisine type (Indian, Chinese, Italian, etc.)
4. Diet restrictions (vegetarian, vegan, jain, etc.)
5. Time constraints (cooking time or total time in minutes)
6. Course (breakfast, lunch, dinner, snack, etc.)
7. Cooking techniques (dum cook, tandoor, grill, etc.)

Return as JSON."""
    
    def _rule_based_parse(self, text: str, lang: Language) -> Dict[str, Any]:
        """Fallback rule-based parsing"""
        text_lower = text.lower()
        
        # Translate Indian language terms to English
        if lang != 'en' and lang in INDIAN_FOOD_VOCAB:
            text_lower = self._translate_food_terms(text_lower, lang)
        
        return {
            'include': self._extract_ingredients(text_lower),
            'exclude': self._extract_exclusions(text_lower),
            'cuisine': self._extract_cuisines(text_lower),
            'diet': self._extract_diets(text_lower),
            'maxCookMinutes': self._extract_time(text_lower, 'cook'),
            'maxTotalMinutes': self._extract_time(text_lower, 'total'),
            'course': self._extract_courses(text_lower),
            'keywords': self._extract_keywords(text_lower),
            'intent': 'search',
            'confidence': 0.7
        }
    
    def _translate_food_terms(self, text: str, lang: Language) -> str:
        """Translate Indian language food terms to English"""
        vocab = INDIAN_FOOD_VOCAB.get(lang, {})
        ingredients = vocab.get('ingredients', {})
        
        # Replace Indian language terms with English equivalents
        for native_term, english_term in ingredients.items():
            text = text.replace(native_term, english_term)
        
        return text
    
    def _extract_ingredients(self, text: str) -> List[str]:
        """Extract ingredient names from text"""
        # Common ingredients in Indian cooking
        common_ingredients = [
            'chicken', 'paneer', 'potato', 'tomato', 'onion', 'rice', 'dal',
            'spinach', 'cauliflower', 'peas', 'carrot', 'beans', 'mushroom',
            'lentil', 'chickpea', 'butter', 'cream', 'yogurt', 'milk',
            'garlic', 'ginger', 'cumin', 'coriander', 'turmeric', 'chilli'
        ]
        
        found = []
        for ingredient in common_ingredients:
            if ingredient in text:
                found.append(ingredient)
        
        return found
    
    def _extract_exclusions(self, text: str) -> List[str]:
        """Extract excluded ingredients"""
        exclusions = []
        patterns = [
            r'without\s+(\w+(?:\s+\w+)?)',
            r'no\s+(\w+(?:\s+\w+)?)',
            r'except\s+(\w+(?:\s+\w+)?)',
            r'excluding\s+(\w+(?:\s+\w+)?)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                ingredient = match.group(1).strip()
                if ingredient not in ['time', 'problem', 'issue']:
                    exclusions.append(ingredient)
        
        return exclusions
    
    def _extract_cuisines(self, text: str) -> List[str]:
        """Extract cuisine types"""
        cuisines = [
            'indian', 'chinese', 'italian', 'mexican', 'thai',
            'punjabi', 'south indian', 'north indian', 'gujarati',
            'bengali', 'maharashtrian', 'goan', 'kashmiri'
        ]
        
        found = []
        for cuisine in cuisines:
            if cuisine in text:
                found.append(cuisine)
        
        return found
    
    def _extract_diets(self, text: str) -> List[str]:
        """Extract dietary restrictions"""
        diets = [
            'vegetarian', 'vegan', 'jain', 'non-vegetarian',
            'gluten-free', 'dairy-free', 'egg-free'
        ]
        
        found = []
        for diet in diets:
            if diet in text or diet.replace('-', ' ') in text:
                found.append(diet)
        
        return found
    
    def _extract_time(self, text: str, time_type: str) -> Optional[int]:
        """Extract time constraints in minutes"""
        patterns = [
            r'(?:under|less than|below|<=|<)\s*(\d+)\s*(?:min|minute|minutes)',
            r'(\d+)\s*(?:min|minute|minutes)\s*or\s*less',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_courses(self, text: str) -> List[str]:
        """Extract meal courses"""
        courses = [
            'breakfast', 'lunch', 'dinner', 'snack', 'appetizer',
            'main course', 'dessert', 'beverage', 'side dish'
        ]
        
        found = []
        for course in courses:
            if course in text:
                found.append(course)
        
        return found
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract cooking technique keywords"""
        keywords = [
            'dum cook', 'tandoor', 'tadka', 'tempering', 'roast',
            'grill', 'steam', 'bake', 'fry', 'pressure cook'
        ]
        
        found = []
        for keyword in keywords:
            if keyword in text:
                found.append(keyword)
        
        return found
    
    def parse(self, text: str, lang: Language = 'en') -> Tuple[QueryConstraints, float]:
        """
        Main parsing method
        
        Args:
            text: User query
            lang: Language code
            
        Returns:
            (QueryConstraints object, confidence score)
        """
        # Try LLM parsing first
        result = self.parse_with_llm(text, lang)
        
        # Convert to QueryConstraints
        constraints = QueryConstraints(
            include=result.get('include'),
            exclude=result.get('exclude'),
            cuisine=result.get('cuisine'),
            diet=result.get('diet'),
            maxCookMinutes=result.get('maxCookMinutes'),
            maxTotalMinutes=result.get('maxTotalMinutes'),
            course=result.get('course'),
            keywords=result.get('keywords')
        )
        
        confidence = result.get('confidence', 0.7)
        
        logger.info(
            "query_parsed",
            input_text=text[:50],
            lang=lang,
            confidence=confidence,
            include_count=len(constraints.include or []),
            exclude_count=len(constraints.exclude or [])
        )
        
        return constraints, confidence


# Singleton instance
_llm_parser: Optional[LLMNLUParser] = None


def get_llm_parser(use_llm: bool = True, api_key: Optional[str] = None) -> LLMNLUParser:
    """Get or create singleton LLM parser"""
    global _llm_parser
    if _llm_parser is None:
        _llm_parser = LLMNLUParser(use_llm=use_llm, llm_api_key=api_key)
    return _llm_parser
