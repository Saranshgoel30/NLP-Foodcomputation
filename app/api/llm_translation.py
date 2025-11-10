"""
LLM-Powered Translation with Indian Language Focus
Context-aware translation preserving culinary terminology
"""
import json
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import structlog
from .models import Language

logger = structlog.get_logger()


class TranslationProvider(str, Enum):
    """Available translation providers"""
    OPENAI = "openai"
    GOOGLE = "google"
    AZURE = "azure"
    LOCAL = "local"


# Culinary terms that should be preserved across translations
PRESERVE_TERMS = {
    'indian': [
        'paneer', 'ghee', 'masala', 'biryani', 'tikka', 'tandoor',
        'dal', 'roti', 'naan', 'paratha', 'dosa', 'idli', 'sambar',
        'curry', 'chutney', 'raita', 'kheer', 'gulab jamun', 'jalebi',
        'dum', 'tadka', 'tempering', 'dhokla', 'vada', 'uttapam',
        'halwa', 'laddu', 'barfi', 'kulfi', 'lassi', 'chai'
    ],
    'cooking': [
        'sauté', 'braise', 'blanch', 'julienne', 'brunoise',
        'reduction', 'emulsion', 'caramelization', 'sear', 'roast'
    ]
}

# Language-specific culinary vocabulary
CULINARY_VOCAB = {
    'hi': {  # Hindi
        'dishes': ['बिरयानी', 'टिक्का', 'करी', 'समोसा', 'पकोड़ा', 'खीर', 'हलवा'],
        'techniques': ['तड़का', 'दम', 'भूनना', 'तलना', 'उबालना'],
        'spices': ['मसाला', 'हल्दी', 'धनिया', 'जीरा', 'गरम मसाला', 'मिर्च']
    },
    'ta': {  # Tamil
        'dishes': ['பிரியாணி', 'சாம்பார்', 'டோசை', 'இட்லி', 'வடை', 'பாயசம்'],
        'techniques': ['தாளிக்க', 'வேகவைக்க', 'பொரிக்க', 'வறுக்க'],
        'spices': ['மசாலா', 'மஞ்சள்', 'கொத்தமல்லி', 'சீரகம்', 'மிளகாய்']
    },
    'te': {  # Telugu
        'dishes': ['బిర్యానీ', 'సాంబార్', 'దోస', 'ఇడ్లీ', 'వడ', 'పాయసం'],
        'techniques': ['తాళింపు', 'ఉడికించు', 'వేయించు', 'కాల్చు'],
        'spices': ['మసాలా', 'పసుపు', 'కొత్తిమీర', 'జీలకర్ర', 'మిర్చి']
    },
    'bn': {  # Bengali
        'dishes': ['বিরিয়ানি', 'মাছের ঝোল', 'রসগোল্লা', 'সন্দেশ', 'চপ'],
        'techniques': ['ফোড়ন', 'সেদ্ধ', 'ভাজা', 'ঝোল'],
        'spices': ['মসলা', 'হলুদ', 'ধনে', 'জিরা', 'গরম মসলা']
    },
    'gu': {  # Gujarati
        'dishes': ['ધોકળા', 'થેપલા', 'ખાંડવી', 'ફાફડા', 'ઉંધિયું'],
        'techniques': ['તડકો', 'બાફવું', 'તળવું', 'શેકવું'],
        'spices': ['મસાલો', 'હળદર', 'ધાણા', 'જીરું', 'મરચું']
    },
    'mr': {  # Marathi
        'dishes': ['वडापाव', 'पोहे', 'भेळ', 'मोदक', 'पुरण पोळी'],
        'techniques': ['फोडणी', 'शिजवणे', 'तळणे', 'भाजणे'],
        'spices': ['मसाला', 'हळद', 'धने', 'जिरे', 'मिरची']
    }
}


class LLMTranslator:
    """
    LLM-powered translation with culinary context preservation
    Optimized for Indian languages and food terminology
    """
    
    def __init__(
        self,
        provider: TranslationProvider = TranslationProvider.OPENAI,
        api_key: Optional[str] = None,
        preserve_culinary_terms: bool = True
    ):
        self.provider = provider
        self.api_key = api_key
        self.preserve_culinary = preserve_culinary_terms
        self.client = None
        
        if api_key:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize translation client"""
        if self.provider == TranslationProvider.OPENAI:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info("translation_client_initialized", provider="openai")
            except Exception as e:
                logger.error("client_initialization_failed", error=str(e))
        
        elif self.provider == TranslationProvider.GOOGLE:
            try:
                from google.cloud import translate_v2 as translate
                self.client = translate.Client()
                logger.info("translation_client_initialized", provider="google")
            except Exception as e:
                logger.error("client_initialization_failed", error=str(e))
    
    def translate(
        self,
        text: str,
        source_lang: Language,
        target_lang: Language,
        context: Optional[str] = None
    ) -> Tuple[str, float]:
        """
        Translate text with culinary context preservation
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            context: Additional context (e.g., "recipe instructions", "ingredient list")
            
        Returns:
            (translated_text, confidence_score)
        """
        if source_lang == target_lang:
            return text, 1.0
        
        if not self.client:
            logger.warning("translation_client_not_initialized", falling_back="passthrough")
            return text, 0.5
        
        try:
            if self.provider == TranslationProvider.OPENAI:
                return self._translate_with_openai(text, source_lang, target_lang, context)
            
            elif self.provider == TranslationProvider.GOOGLE:
                return self._translate_with_google(text, source_lang, target_lang)
            
            else:
                logger.warning("provider_not_supported", provider=self.provider)
                return text, 0.5
                
        except Exception as e:
            logger.error("translation_failed", error=str(e))
            return text, 0.3
    
    def _translate_with_openai(
        self,
        text: str,
        source_lang: Language,
        target_lang: Language,
        context: Optional[str]
    ) -> Tuple[str, float]:
        """Translate using OpenAI GPT models"""
        
        # Get language names
        lang_names = {
            'en': 'English', 'hi': 'Hindi', 'mr': 'Marathi',
            'ta': 'Tamil', 'te': 'Telugu', 'bn': 'Bengali',
            'gu': 'Gujarati', 'kn': 'Kannada', 'ml': 'Malayalam',
            'pa': 'Punjabi', 'or': 'Odia'
        }
        
        source_name = lang_names.get(source_lang, source_lang)
        target_name = lang_names.get(target_lang, target_lang)
        
        # Build system prompt with culinary preservation instructions
        system_prompt = f"""You are an expert culinary translator specializing in {source_name} to {target_name} translation.

CRITICAL RULES:
1. Preserve authentic culinary terms (e.g., paneer, biryani, tandoor, masala, ghee, dal)
2. Keep dish names in their original form
3. Maintain cooking technique terms that are culturally specific
4. Translate only generic cooking instructions
5. Preserve measurements and quantities exactly
6. Keep ingredient names recognizable

Context: {context or 'Food recipe translation'}

Return ONLY the translation, no explanations."""
        
        # Add examples of terms to preserve
        if self.preserve_culinary:
            preserve_list = PRESERVE_TERMS['indian'][:10]
            system_prompt += f"\n\nPreserve these terms: {', '.join(preserve_list)}"
        
        # Call OpenAI
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Translate from {source_name} to {target_name}:\n\n{text}"}
            ],
            temperature=0.3,  # Low temperature for consistency
            max_tokens=1000
        )
        
        translation = response.choices[0].message.content.strip()
        confidence = 0.9  # High confidence for GPT-4
        
        logger.info(
            "translation_completed",
            source_lang=source_lang,
            target_lang=target_lang,
            source_length=len(text),
            target_length=len(translation),
            confidence=confidence
        )
        
        return translation, confidence
    
    def _translate_with_google(
        self,
        text: str,
        source_lang: Language,
        target_lang: Language
    ) -> Tuple[str, float]:
        """Translate using Google Cloud Translation API"""
        
        result = self.client.translate(
            text,
            source_language=source_lang,
            target_language=target_lang
        )
        
        translation = result['translatedText']
        confidence = 0.85  # Google doesn't provide confidence scores
        
        logger.info(
            "google_translation_completed",
            source_lang=source_lang,
            target_lang=target_lang
        )
        
        return translation, confidence
    
    def translate_batch(
        self,
        texts: List[str],
        source_lang: Language,
        target_lang: Language,
        context: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """
        Translate multiple texts efficiently
        
        Args:
            texts: List of texts to translate
            source_lang: Source language
            target_lang: Target language
            context: Translation context
            
        Returns:
            List of (translated_text, confidence) tuples
        """
        results = []
        
        for text in texts:
            translation, confidence = self.translate(text, source_lang, target_lang, context)
            results.append((translation, confidence))
        
        return results
    
    def translate_recipe(
        self,
        recipe_data: Dict[str, Any],
        target_lang: Language,
        source_lang: Language = 'en'
    ) -> Dict[str, Any]:
        """
        Translate entire recipe with field-aware context
        
        Args:
            recipe_data: Recipe dictionary with title, ingredients, instructions, etc.
            target_lang: Target language
            source_lang: Source language
            
        Returns:
            Translated recipe dictionary
        """
        translated = recipe_data.copy()
        
        # Translate title
        if 'title' in recipe_data:
            translated['title'], _ = self.translate(
                recipe_data['title'],
                source_lang,
                target_lang,
                context="recipe title"
            )
        
        # Translate description
        if 'description' in recipe_data:
            translated['description'], _ = self.translate(
                recipe_data['description'],
                source_lang,
                target_lang,
                context="recipe description"
            )
        
        # Translate ingredients (preserve ingredient names)
        if 'ingredients' in recipe_data:
            translated_ingredients = []
            for ingredient in recipe_data['ingredients']:
                trans_ing, _ = self.translate(
                    ingredient,
                    source_lang,
                    target_lang,
                    context="ingredient with measurement"
                )
                translated_ingredients.append(trans_ing)
            translated['ingredients'] = translated_ingredients
        
        # Translate instructions
        if 'instructions' in recipe_data:
            if isinstance(recipe_data['instructions'], list):
                translated_instructions = []
                for step in recipe_data['instructions']:
                    trans_step, _ = self.translate(
                        step,
                        source_lang,
                        target_lang,
                        context="cooking instruction"
                    )
                    translated_instructions.append(trans_step)
                translated['instructions'] = translated_instructions
            else:
                translated['instructions'], _ = self.translate(
                    recipe_data['instructions'],
                    source_lang,
                    target_lang,
                    context="cooking instructions"
                )
        
        # Translate tags/keywords
        if 'tags' in recipe_data:
            translated_tags = []
            for tag in recipe_data['tags']:
                trans_tag, _ = self.translate(
                    tag,
                    source_lang,
                    target_lang,
                    context="recipe tag"
                )
                translated_tags.append(trans_tag)
            translated['tags'] = translated_tags
        
        logger.info(
            "recipe_translated",
            source_lang=source_lang,
            target_lang=target_lang,
            title=recipe_data.get('title', 'Unknown')
        )
        
        return translated
    
    def detect_culinary_terms(self, text: str, lang: Language) -> List[str]:
        """
        Detect culinary-specific terms in text
        
        Args:
            text: Text to analyze
            lang: Language code
            
        Returns:
            List of detected culinary terms
        """
        detected = []
        text_lower = text.lower()
        
        # Check Indian culinary terms
        for term in PRESERVE_TERMS['indian']:
            if term in text_lower:
                detected.append(term)
        
        # Check cooking terms
        for term in PRESERVE_TERMS['cooking']:
            if term in text_lower:
                detected.append(term)
        
        # Check language-specific vocabulary
        if lang in CULINARY_VOCAB:
            vocab = CULINARY_VOCAB[lang]
            for category in ['dishes', 'techniques', 'spices']:
                for term in vocab.get(category, []):
                    if term in text:
                        detected.append(term)
        
        return detected


class MultilingualRecipeAdapter:
    """
    Adapts recipes for different linguistic and cultural contexts
    """
    
    def __init__(self, translator: LLMTranslator):
        self.translator = translator
    
    def adapt_recipe(
        self,
        recipe: Dict[str, Any],
        target_lang: Language,
        cultural_adaptation: bool = False
    ) -> Dict[str, Any]:
        """
        Adapt recipe for target language and optionally culture
        
        Args:
            recipe: Source recipe
            target_lang: Target language
            cultural_adaptation: Whether to suggest cultural substitutions
            
        Returns:
            Adapted recipe
        """
        # First translate
        adapted = self.translator.translate_recipe(recipe, target_lang)
        
        # Add cultural notes if requested
        if cultural_adaptation:
            adapted['cultural_notes'] = self._generate_cultural_notes(
                recipe,
                target_lang
            )
        
        return adapted
    
    def _generate_cultural_notes(
        self,
        recipe: Dict[str, Any],
        target_lang: Language
    ) -> List[str]:
        """Generate cultural adaptation suggestions"""
        notes = []
        
        # Example: Suggest ghee instead of butter for Indian adaptation
        if target_lang in ['hi', 'mr', 'ta', 'te', 'bn', 'gu']:
            ingredients_text = str(recipe.get('ingredients', ''))
            if 'butter' in ingredients_text.lower() and 'ghee' not in ingredients_text.lower():
                notes.append("Consider using ghee instead of butter for authentic flavor")
        
        return notes


# Singleton instance
_translator: Optional[LLMTranslator] = None


def get_translator(
    provider: TranslationProvider = TranslationProvider.OPENAI,
    api_key: Optional[str] = None
) -> LLMTranslator:
    """Get or create singleton translator"""
    global _translator
    if _translator is None:
        _translator = LLMTranslator(provider=provider, api_key=api_key)
    return _translator
