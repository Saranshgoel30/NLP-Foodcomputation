"""
Intelligent Query Enhancement Layer
Adds rule-based logic to detect semantic concepts and enhance search queries

This sits between LLM parsing and Typesense search:
User Query → LLM Parser → Query Enhancer → Typesense

Examples:
- "healthy paneer" → exclude fried foods, prefer grilled/steamed
- "low carb chicken" → exclude rice/bread/potato, prefer protein-rich
- "persian style biryani" → add cuisine filter, boost iranian keywords
- "quick breakfast" → time filter, breakfast course
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json
import os


@dataclass
class QueryEnhancement:
    """Enhanced query with additional search intelligence"""
    original_query: str
    enhanced_query: str  # Modified search query
    additional_inclusions: List[str]  # Extra ingredients to include
    additional_exclusions: List[str]  # Extra ingredients to exclude
    filters: Dict[str, str]  # Typesense filters (cuisine, diet, course)
    time_constraint: Optional[Dict[str, int]]  # Cooking time limits
    boost_terms: List[str]  # Terms to boost in search
    reasoning: List[str]  # Explanations of applied rules


class QueryEnhancer:
    """
    Rule-based query enhancement using semantic pattern matching
    
    Detects concepts like:
    - Health indicators (healthy, low-carb, light, nutritious)
    - Style/cuisine modifiers (persian-style, authentic, traditional)
    - Time constraints (quick, fast, instant)
    - Preparation methods (grilled, steamed, baked)
    """
    
    def __init__(self):
        """Load enhancement rules from JSON"""
        self.rules_dir = os.path.join(os.path.dirname(__file__), 'nlp_data')
        
        # Load enhancement rules
        self.enhancement_rules = self._load_json('query_enhancement_rules.json')
        
        # Build quick lookup maps
        self._build_lookup_maps()
        
        print("✅ Query Enhancer initialized")
        print(f"   Loaded {len(self.concept_patterns)} concept patterns")
        print(f"   Loaded {len(self.style_patterns)} style patterns")
    
    def _load_json(self, filename: str) -> Dict:
        """Load JSON configuration file"""
        try:
            filepath = os.path.join(self.rules_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Warning: {filename} not found, using empty rules")
            return self._get_default_rules()
        except Exception as e:
            print(f"⚠️  Error loading {filename}: {e}")
            return self._get_default_rules()
    
    def _get_default_rules(self) -> Dict:
        """Fallback rules if JSON file not found"""
        return {
            "health_concepts": {},
            "style_modifiers": {},
            "time_concepts": {},
            "preparation_methods": {}
        }
    
    def _build_lookup_maps(self):
        """Build efficient lookup structures from rules"""
        rules = self.enhancement_rules
        
        # Health concepts (healthy, low-carb, etc.)
        self.concept_patterns = {}
        for concept, data in rules.get('health_concepts', {}).items():
            patterns = data.get('patterns', [])
            self.concept_patterns[concept] = {
                'regex': [re.compile(p, re.IGNORECASE) for p in patterns],
                'exclude': data.get('exclude_ingredients', []),
                'include': data.get('prefer_ingredients', []),
                'filters': data.get('filters', {}),
                'description': data.get('description', '')
            }
        
        # Style modifiers (persian-style, traditional, etc.)
        self.style_patterns = {}
        for style, data in rules.get('style_modifiers', {}).items():
            patterns = data.get('patterns', [])
            self.style_patterns[style] = {
                'regex': [re.compile(p, re.IGNORECASE) for p in patterns],
                'filters': data.get('filters', {}),
                'boost_terms': data.get('boost_terms', []),
                'description': data.get('description', '')
            }
        
        # Time concepts (quick, fast, etc.)
        self.time_patterns = {}
        for concept, data in rules.get('time_concepts', {}).items():
            patterns = data.get('patterns', [])
            self.time_patterns[concept] = {
                'regex': [re.compile(p, re.IGNORECASE) for p in patterns],
                'max_time': data.get('max_time_minutes'),
                'description': data.get('description', '')
            }
        
        # Preparation methods (grilled, baked, etc.)
        self.prep_patterns = {}
        for method, data in rules.get('preparation_methods', {}).items():
            patterns = data.get('patterns', [])
            self.prep_patterns[method] = {
                'regex': [re.compile(p, re.IGNORECASE) for p in patterns],
                'boost_terms': data.get('boost_terms', []),
                'exclude': data.get('exclude_ingredients', []),
                'description': data.get('description', '')
            }
    
    def enhance_query(
        self, 
        query: str,
        existing_exclusions: List[str] = None,
        existing_filters: Dict[str, str] = None
    ) -> QueryEnhancement:
        """
        Enhance query with rule-based intelligence
        
        Args:
            query: Original search query
            existing_exclusions: Already detected exclusions from LLM
            existing_filters: Already applied filters
        
        Returns:
            QueryEnhancement with additional search intelligence
        """
        existing_exclusions = existing_exclusions or []
        existing_filters = existing_filters or {}
        
        # Initialize enhancement
        enhancement = QueryEnhancement(
            original_query=query,
            enhanced_query=query,
            additional_inclusions=[],
            additional_exclusions=[],
            filters=existing_filters.copy(),
            time_constraint=None,
            boost_terms=[],
            reasoning=[]
        )
        
        query_lower = query.lower()
        
        # Apply health concept rules
        self._apply_health_concepts(query_lower, enhancement, existing_exclusions)
        
        # Apply style modifier rules
        self._apply_style_modifiers(query_lower, enhancement)
        
        # Apply time constraint rules
        self._apply_time_constraints(query_lower, enhancement)
        
        # Apply preparation method rules
        self._apply_preparation_methods(query_lower, enhancement)
        
        # Clean enhanced query (remove modifier terms)
        enhancement.enhanced_query = self._clean_query(query, enhancement)
        
        return enhancement
    
    def _apply_health_concepts(
        self, 
        query: str, 
        enhancement: QueryEnhancement,
        existing_exclusions: List[str]
    ):
        """Detect and apply health-related concepts"""
        for concept, rules in self.concept_patterns.items():
            # Check if any pattern matches
            for regex in rules['regex']:
                if regex.search(query):
                    # Add exclusions (avoid duplicates)
                    new_exclusions = [
                        exc for exc in rules['exclude'] 
                        if exc not in existing_exclusions 
                        and exc not in enhancement.additional_exclusions
                    ]
                    enhancement.additional_exclusions.extend(new_exclusions)
                    
                    # Add inclusions
                    enhancement.additional_inclusions.extend(rules['include'])
                    
                    # Add filters
                    for key, value in rules['filters'].items():
                        if key not in enhancement.filters:
                            enhancement.filters[key] = value
                    
                    # Add reasoning
                    enhancement.reasoning.append(
                        f"🏥 {concept.upper()}: {rules['description']}"
                    )
                    
                    if new_exclusions:
                        enhancement.reasoning.append(
                            f"   → Excluding: {', '.join(new_exclusions[:5])}"
                        )
                    
                    break  # Only apply once per concept
    
    def _apply_style_modifiers(self, query: str, enhancement: QueryEnhancement):
        """Detect and apply style/cuisine modifiers"""
        for style, rules in self.style_patterns.items():
            for regex in rules['regex']:
                if regex.search(query):
                    # Add filters (don't override existing)
                    for key, value in rules['filters'].items():
                        if key not in enhancement.filters:
                            enhancement.filters[key] = value
                    
                    # Add boost terms
                    enhancement.boost_terms.extend(rules['boost_terms'])
                    
                    # Add reasoning
                    enhancement.reasoning.append(
                        f"🎨 {style.upper()}: {rules['description']}"
                    )
                    
                    if rules['boost_terms']:
                        enhancement.reasoning.append(
                            f"   → Boosting: {', '.join(rules['boost_terms'][:5])}"
                        )
                    
                    break
    
    def _apply_time_constraints(self, query: str, enhancement: QueryEnhancement):
        """Detect and apply time-related constraints"""
        for concept, rules in self.time_patterns.items():
            for regex in rules['regex']:
                if regex.search(query):
                    # Set time constraint (use minimum if multiple match)
                    max_time = rules['max_time']
                    if enhancement.time_constraint is None:
                        enhancement.time_constraint = {'max_time': max_time}
                    else:
                        # Use stricter constraint
                        existing_max = enhancement.time_constraint.get('max_time', 999)
                        enhancement.time_constraint['max_time'] = min(existing_max, max_time)
                    
                    # Add reasoning
                    enhancement.reasoning.append(
                        f"⏱️  {concept.upper()}: {rules['description']}"
                    )
                    
                    break
    
    def _apply_preparation_methods(self, query: str, enhancement: QueryEnhancement):
        """Detect and apply preparation method preferences"""
        for method, rules in self.prep_patterns.items():
            for regex in rules['regex']:
                if regex.search(query):
                    # Add boost terms
                    enhancement.boost_terms.extend(rules['boost_terms'])
                    
                    # Add exclusions
                    enhancement.additional_exclusions.extend(rules['exclude'])
                    
                    # Add reasoning
                    enhancement.reasoning.append(
                        f"🔥 {method.upper()}: {rules['description']}"
                    )
                    
                    break
    
    def _clean_query(self, query: str, enhancement: QueryEnhancement) -> str:
        """
        Remove modifier terms from query to get clean dish name
        
        For example:
        - "healthy paneer tikka" → "paneer tikka"
        - "quick persian style biryani" → "persian biryani" (keep style)
        - "low carb grilled chicken" → "grilled chicken" (keep method)
        """
        cleaned = query
        
        # Remove health concept keywords
        health_keywords = [
            'healthy', 'light', 'low carb', 'low-carb', 'low fat', 'low-fat',
            'diet', 'nutritious', 'wholesome', 'clean eating'
        ]
        
        for keyword in health_keywords:
            # Remove keyword (case-insensitive, whole word)
            cleaned = re.sub(r'\b' + re.escape(keyword) + r'\b', '', cleaned, flags=re.IGNORECASE)
        
        # Remove time keywords (but keep them if they're part of dish name)
        time_keywords = ['quick', 'fast', 'instant', 'easy']
        for keyword in time_keywords:
            # Only remove if not part of dish name (e.g., "quick pickles")
            if keyword.lower() not in ['pickles', 'bread']:
                cleaned = re.sub(r'\b' + re.escape(keyword) + r'\b', '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def get_search_params(self, enhancement: QueryEnhancement) -> Dict[str, Any]:
        """
        Convert enhancement to Typesense search parameters
        
        Returns dict with:
        - query: Enhanced search query
        - filters: Additional filters to apply
        - boost: Terms to boost in ranking
        """
        params = {
            'query': enhancement.enhanced_query,
            'additional_exclusions': enhancement.additional_exclusions,
            'additional_inclusions': enhancement.additional_inclusions,
            'filters': enhancement.filters,
            'time_constraint': enhancement.time_constraint,
            'boost_terms': enhancement.boost_terms
        }
        
        return params
    
    def print_enhancement_summary(self, enhancement: QueryEnhancement):
        """Print human-readable summary of enhancement"""
        print(f"\n🧠 Query Enhancement Summary:")
        print(f"   Original: '{enhancement.original_query}'")
        print(f"   Enhanced: '{enhancement.enhanced_query}'")
        
        if enhancement.additional_exclusions:
            print(f"   ❌ Exclude: {enhancement.additional_exclusions[:5]}")
        
        if enhancement.additional_inclusions:
            print(f"   ✅ Include: {enhancement.additional_inclusions[:5]}")
        
        if enhancement.filters:
            print(f"   🏷️  Filters: {enhancement.filters}")
        
        if enhancement.time_constraint:
            print(f"   ⏱️  Time: {enhancement.time_constraint}")
        
        if enhancement.boost_terms:
            print(f"   🚀 Boost: {enhancement.boost_terms}")
        
        if enhancement.reasoning:
            print(f"   📋 Rules Applied:")
            for reason in enhancement.reasoning:
                print(f"      {reason}")


# Global instance
query_enhancer = QueryEnhancer()
