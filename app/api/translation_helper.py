"""
Comprehensive Translation Helper for Indian Languages
Handles all major Indian languages with food-specific terminology and semantic understanding
"""

from typing import Dict, List, Optional, Tuple
import re

class IndianFoodTranslator:
    """Expert translator for Indian food queries across all major languages and dialects"""
    
    # Comprehensive ingredient mappings across Indian languages
    INGREDIENT_MAPPINGS = {
        # Onion variations
        "kanda": "onion", "कांदा": "onion", "kaanda": "onion",
        "pyaz": "onion", "प्याज": "onion", "pyaaz": "onion",
        "vengayam": "onion", "வெங்காயம்": "onion",
        "ullipaya": "onion", "ఉల్లిపాయ": "onion",
        "eerulli": "onion", "ಈರುಳ್ಳಿ": "onion",
        "ulli": "onion", "ഉള്ളി": "onion",
        "piyaj": "onion", "পিঁয়াজ": "onion",
        "dungri": "onion", "ડુંગરી": "onion",
        "piaja": "onion",
        
        # Garlic variations
        "lasun": "garlic", "लसून": "garlic", "lahsun": "garlic", "लहसुन": "garlic",
        "vellulli": "garlic", "వెల్లుల్లి": "garlic",
        "bellulli": "garlic", "ಬೆಳ್ಳುಳ್ಳಿ": "garlic",
        "veluthulli": "garlic", "വെളുത്തുള്ളി": "garlic",
        "poondu": "garlic", "பூண்டு": "garlic",
        "rasun": "garlic", "রসুন": "garlic",
        "lasan": "garlic", "લસણ": "garlic",
        
        # Potato variations
        "aloo": "potato", "आलू": "potato", "alu": "potato",
        "batata": "potato", "बटाटा": "potato", "bataata": "potato",
        "urulaikizhangu": "potato", "உருளைக்கிழங்கு": "potato",
        "bangaladumpa": "potato", "బంగాళాదుంప": "potato",
        "aalugadde": "potato", "ಆಲೂಗಡ್ಡೆ": "potato",
        "urulakizhangu": "potato", "ഉരുളക്കിഴങ്ങ്": "potato",
        "aalu": "potato", "আলু": "potato",
        "bataka": "potato", "બટાકા": "potato",
        
        # Tomato variations
        "tamatar": "tomato", "टमाटर": "tomato", "tamaatar": "tomato",
        "tomato": "tomato", "टोमॅटो": "tomato",
        "thakkali": "tomato", "தக்காளி": "tomato",
        "tamata": "tomato", "టమాట": "tomato",
        "tamota": "tomato",
        
        # Paneer/Cheese
        "paneer": "cottage cheese", "पनीर": "cottage cheese", "panir": "cottage cheese",
        "chenna": "cottage cheese", "ছানা": "cottage cheese",
        
        # Common vegetables
        "bhaji": "vegetable", "भाजी": "vegetable", "bhaji": "vegetable curry",
        "sabzi": "vegetable", "sabji": "vegetable", "सब्ज़ी": "vegetable",
        "curry": "curry", "कढी": "curry",
        "kuzhambu": "curry", "குழம்பு": "curry",
        "koora": "curry", "కూర": "curry",
        
        # Spices
        "mirch": "chili", "मिर्च": "chili", "mirchi": "chili",
        "mulagu": "chili", "மிளகாய்": "chili",
        "menasina": "chili", "ಮೆಣಸಿನ": "chili",
        "haldi": "turmeric", "हल्दी": "turmeric",
        "manjal": "turmeric", "மஞ்சள்": "turmeric",
        "jeera": "cumin", "जीरा": "cumin",
        "seeragam": "cumin", "சீரகம்": "cumin",
        "dhaniya": "coriander", "धनिया": "coriander",
        "kothmir": "coriander", "कोथिंबीर": "coriander",
        
        # Lentils/Dal
        "dal": "lentils", "daal": "lentils", "दाल": "lentils",
        "paruppu": "lentils", "பருப்பு": "lentils",
        "pappu": "lentils", "పప్పు": "lentils",
        
        # Rice variations
        "chawal": "rice", "चावल": "rice",
        "bhat": "rice", "भात": "rice",
        "arisi": "rice", "அரிசி": "rice",
        "annam": "rice", "అన్నం": "rice",
        
        # Bread variations
        "roti": "flatbread", "रोटी": "flatbread",
        "chapati": "flatbread", "चपाती": "flatbread",
        "phulka": "flatbread", "फुल्का": "flatbread",
        "paratha": "stuffed flatbread", "पराठा": "stuffed flatbread",
        "naan": "leavened bread", "नान": "leavened bread",
    }
    
    # Negation words across languages
    NEGATION_WORDS = {
        # Hindi/Urdu
        "bina": "without", "के बिना": "without", "nahi": "without", "nahī": "without",
        "mat": "without", "मत": "without",
        
        # Marathi
        "nahi": "without", "नाही": "without", "nashī": "without",
        "naslelī": "without", "नसलेली": "without", "naslela": "without", "नसलेला": "without",
        "shivaay": "without", "शिवाय": "without",
        
        # Tamil
        "illama": "without", "இல்லாமல்": "without", "illaamal": "without",
        "vendaam": "don't want", "வேண்டாம்": "don't want",
        
        # Telugu
        "lekunda": "without", "లేకుండా": "without", "lekundaa": "without",
        "vaddu": "don't want", "వద్దు": "don't want",
        
        # Kannada
        "illa": "without", "ಇಲ್ಲ": "without",
        "beda": "don't want", "ಬೇಡ": "don't want",
        
        # Malayalam
        "illaathe": "without", "ഇല്ലാതെ": "without",
        "venda": "don't want", "വേണ്ട": "don't want",
        
        # Bengali
        "chara": "without", "ছাড়া": "without", "chaara": "without",
        "na": "without", "না": "without",
        
        # Gujarati
        "vinaa": "without", "વિના": "without", "vina": "without",
        
        # Punjabi
        "baghair": "without", "ਬਗੈਰ": "without",
        
        # English
        "without": "without", "no": "without", "except": "without", "excluding": "without",
    }
    
    # Action/cooking verbs
    COOKING_VERBS = {
        "banana": "to make", "बनाना": "to make", "banavane": "to make",
        "pakana": "to cook", "पकाना": "to cook",
        "kadhne": "to prepare", "काढणे": "to prepare",
        "recipe": "recipe", "रेसिपी": "recipe", "विधी": "recipe",
        "kaise": "how to", "कैसे": "how to",
        "banaye": "make", "बनाये": "make",
        "tayar": "prepare", "तयार": "prepare",
    }
    
    # Common dish patterns
    DISH_PATTERNS = {
        "curry": ["curry", "bhaji", "sabzi", "kuzhambu", "koora"],
        "rice_dish": ["biryani", "pulao", "khichdi", "curd rice", "lemon rice"],
        "bread": ["roti", "chapati", "paratha", "naan", "puri", "bhakri"],
        "snack": ["pakora", "samosa", "vada", "bonda", "cutlet"],
        "sweet": ["halwa", "laddu", "barfi", "kheer", "payasam"],
    }
    
    # Dietary restrictions
    DIETARY_TERMS = {
        "jain": ["no onion", "no garlic", "no root vegetables"],
        "satvik": ["no onion", "no garlic", "pure vegetarian"],
        "vegetarian": ["no meat", "no fish", "no eggs"],
        "vegan": ["no dairy", "no eggs", "no honey"],
    }
    
    @classmethod
    def normalize_text(cls, text: str) -> str:
        """Normalize text for better matching"""
        # Convert to lowercase
        text = text.lower().strip()
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text
    
    @classmethod
    def detect_language(cls, text: str) -> str:
        """Detect the language of the input text"""
        # Check for Devanagari script (Hindi/Marathi)
        if re.search(r'[\u0900-\u097F]', text):
            # Marathi specific words
            if any(word in text for word in ['नाही', 'नसलेली', 'शिवाय', 'काढणे', 'बनवणे']):
                return "Marathi"
            return "Hindi"
        
        # Check for Tamil script
        if re.search(r'[\u0B80-\u0BFF]', text):
            return "Tamil"
        
        # Check for Telugu script
        if re.search(r'[\u0C00-\u0C7F]', text):
            return "Telugu"
        
        # Check for Kannada script
        if re.search(r'[\u0C80-\u0CFF]', text):
            return "Kannada"
        
        # Check for Malayalam script
        if re.search(r'[\u0D00-\u0D7F]', text):
            return "Malayalam"
        
        # Check for Bengali script
        if re.search(r'[\u0980-\u09FF]', text):
            return "Bengali"
        
        # Check for Gujarati script
        if re.search(r'[\u0A80-\u0AFF]', text):
            return "Gujarati"
        
        # Check for Gurmukhi/Punjabi script
        if re.search(r'[\u0A00-\u0A7F]', text):
            return "Punjabi"
        
        return "English"
    
    @classmethod
    def extract_negations(cls, text: str) -> List[Tuple[str, str]]:
        """Extract negated ingredients from text
        Returns: List of (negation_phrase, ingredient) tuples
        """
        negations = []
        normalized = cls.normalize_text(text)
        
        # Pattern: [negation word] [ingredient]
        for neg_word, neg_meaning in cls.NEGATION_WORDS.items():
            for ingredient_word, ingredient_meaning in cls.INGREDIENT_MAPPINGS.items():
                # Check for "negation + ingredient" pattern
                pattern1 = f"{neg_word}\\s+{ingredient_word}"
                pattern2 = f"{ingredient_word}\\s+{neg_word}"
                
                if re.search(pattern1, normalized) or re.search(pattern2, normalized):
                    negations.append((f"{neg_meaning} {ingredient_meaning}", ingredient_meaning))
        
        return negations
    
    @classmethod
    def translate_ingredients(cls, text: str) -> str:
        """Translate all ingredients in text to English"""
        translated = text
        normalized = cls.normalize_text(text)
        
        # Sort by length (longest first) to handle multi-word phrases
        sorted_ingredients = sorted(cls.INGREDIENT_MAPPINGS.items(), 
                                   key=lambda x: len(x[0]), 
                                   reverse=True)
        
        for local_term, english_term in sorted_ingredients:
            # Create pattern that matches word boundaries
            pattern = r'\b' + re.escape(local_term) + r'\b'
            translated = re.sub(pattern, english_term, translated, flags=re.IGNORECASE)
        
        return translated
    
    @classmethod
    def translate_negations(cls, text: str) -> str:
        """Translate negation words to English"""
        translated = text
        
        for neg_word, neg_meaning in cls.NEGATION_WORDS.items():
            pattern = r'\b' + re.escape(neg_word) + r'\b'
            translated = re.sub(pattern, neg_meaning, translated, flags=re.IGNORECASE)
        
        return translated
    
    @classmethod
    def semantic_translation(cls, query: str) -> Dict[str, any]:
        """
        Perform semantic translation with context understanding
        Returns structured data about the query
        """
        language = cls.detect_language(query)
        normalized = cls.normalize_text(query)
        
        # Step 1: Extract negations with context
        negations = cls.extract_negations(normalized)
        excluded_ingredients = [ing for _, ing in negations]
        
        # Step 2: Translate ingredients
        translated = cls.translate_ingredients(normalized)
        
        # Step 3: Translate negations
        translated = cls.translate_negations(translated)
        
        # Step 4: Translate cooking verbs
        for verb_word, verb_meaning in cls.COOKING_VERBS.items():
            pattern = r'\b' + re.escape(verb_word) + r'\b'
            translated = re.sub(pattern, verb_meaning, translated, flags=re.IGNORECASE)
        
        # Step 5: Clean up multiple spaces
        translated = re.sub(r'\s+', ' ', translated).strip()
        
        # Step 6: Extract dish type
        dish_type = None
        for category, patterns in cls.DISH_PATTERNS.items():
            if any(pattern in normalized for pattern in patterns):
                dish_type = category
                break
        
        # Step 7: Check dietary restrictions
        dietary_restrictions = []
        for diet, restrictions in cls.DIETARY_TERMS.items():
            if diet in normalized:
                dietary_restrictions.extend(restrictions)
                excluded_ingredients.extend(restrictions)
        
        return {
            "original_query": query,
            "detected_language": language,
            "translated_query": translated,
            "excluded_ingredients": list(set(excluded_ingredients)),
            "dish_type": dish_type,
            "dietary_restrictions": dietary_restrictions,
            "negation_phrases": negations
        }
    
    @classmethod
    def get_translation_prompt(cls, query: str) -> str:
        """
        Generate a comprehensive translation prompt for LLM
        with full context and examples
        """
        language = cls.detect_language(query)
        
        prompt = f"""You are translating a {language} recipe search query to clear, searchable English.

CRITICAL INSTRUCTIONS:
1. Preserve the EXACT meaning and context
2. Translate food terms accurately (use common English names)
3. Maintain negations ("without", "no", "excluding")
4. Keep dish names recognizable
5. Output ONLY the English translation, nothing else

LANGUAGE CONTEXT - {language}:
"""
        
        if language == "Marathi":
            prompt += """
Common Marathi food terms:
- कांदा (kanda) = onion
- बटाटा (batata) = potato
- भाजी (bhaji) = vegetable curry
- नाही/नसलेली (nahi/naslelī) = without/not having
- पनीर (paneer) = cottage cheese
- शिवाय (shivaay) = without/except

Example: "कांदा नसलेली पनीर भाजी" → "paneer vegetable curry without onion"
"""
        
        elif language == "Hindi":
            prompt += """
Common Hindi food terms:
- प्याज (pyaz) = onion
- आलू (aloo) = potato
- सब्ज़ी (sabzi) = vegetable
- के बिना (ke bina) = without
- टमाटर (tamatar) = tomato
- लहसुन (lahsun) = garlic

Example: "प्याज के बिना आलू की सब्जी" → "potato curry without onion"
"""
        
        elif language == "Tamil":
            prompt += """
Common Tamil food terms:
- வெங்காயம் (vengayam) = onion
- உருளைக்கிழங்கு (urulaikizhangu) = potato
- குழம்பு (kuzhambu) = curry
- இல்லாமல் (illama) = without

Example: "vengayam illama kuzhambu" → "curry without onion"
"""
        
        elif language == "Telugu":
            prompt += """
Common Telugu food terms:
- ఉల్లిపాయ (ullipaya) = onion
- బంగాళాదుంప (bangaladumpa) = potato
- కూర (koora) = curry
- లేకుండా (lekunda) = without

Example: "ullipaya lekunda koora" → "curry without onion"
"""
        
        else:  # English or other
            prompt += """
Handle mixed language queries (Hinglish, etc.):
- "pyaz ke bina" = "without onion"
- "bina lahsun" = "without garlic"
- "no aloo" = "no potato"
"""
        
        prompt += f"""

Now translate this query to searchable English:
Query: "{query}"

Translation:"""
        
        return prompt


# Export singleton instance
translator = IndianFoodTranslator()
