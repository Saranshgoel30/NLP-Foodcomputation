"""
Natural Language Query Parser for Recipe Search
Understands patterns like "without X", "no Y", "exclude Z", etc.
"""

import re
from typing import Dict, List, Tuple

class QueryParser:
    """Parse natural language queries to extract intent and constraints"""
    
    # Patterns to identify exclusions
    EXCLUSION_PATTERNS = [
        r'\bwithout\s+([a-z\s,]+?)(?:\s+and\s+|\s+or\s+|$)',
        r'\bno\s+([a-z\s,]+?)(?:\s+and\s+|\s+or\s+|$)',
        r'\bexclude\s+([a-z\s,]+?)(?:\s+and\s+|\s+or\s+|$)',
        r'\bminus\s+([a-z\s,]+?)(?:\s+and\s+|\s+or\s+|$)',
        r'\bdoesn\'?t?\s+have\s+([a-z\s,]+?)(?:\s+and\s+|\s+or\s+|$)',
        r'\bfree\s+from\s+([a-z\s,]+?)(?:\s+and\s+|\s+or\s+|$)',
    ]
    
    # Patterns to identify requirements
    REQUIREMENT_PATTERNS = [
        r'\bwith\s+([a-z\s,]+?)(?:\s+and\s+|\s+or\s+|$)',
        r'\bcontaining\s+([a-z\s,]+?)(?:\s+and\s+|\s+or\s+|$)',
        r'\bhaving\s+([a-z\s,]+?)(?:\s+and\s+|\s+or\s+|$)',
        r'\bmust\s+have\s+([a-z\s,]+?)(?:\s+and\s+|\s+or\s+|$)',
        r'\bneeds\s+([a-z\s,]+?)(?:\s+and\s+|\s+or\s+|$)',
    ]
    
    # Time-related patterns
    TIME_PATTERNS = [
        (r'\bunder\s+(\d+)\s*min(?:ute)?s?', 'max_time'),
        (r'\bless\s+than\s+(\d+)\s*min(?:ute)?s?', 'max_time'),
        (r'\bquick(?:\s+and\s+easy)?', 30),  # Quick = under 30 mins
        (r'\bfast', 20),  # Fast = under 20 mins
        (r'\bin\s+(\d+)\s*min(?:ute)?s?', 'exact_time'),
    ]
    
    # Common ingredient aliases
    INGREDIENT_ALIASES = {
        'onions': ['onion', 'onions', 'pyaz'],
        'tomatoes': ['tomato', 'tomatoes', 'tamatar'],
        'garlic': ['garlic', 'lahsun'],
        'ginger': ['ginger', 'adrak'],
        'chili': ['chili', 'chilli', 'mirch', 'pepper'],
        'oil': ['oil', 'tel'],
        'butter': ['butter', 'makkhan'],
        'cheese': ['cheese', 'paneer'],
        'milk': ['milk', 'doodh'],
    }
    
    def parse(self, query: str) -> Dict:
        """
        Parse a natural language query and extract:
        - Core search terms (cleaned query)
        - Excluded ingredients
        - Required ingredients
        - Time constraints
        """
        query_lower = query.lower()
        
        # Extract exclusions
        excluded_ingredients = self._extract_ingredients(query_lower, self.EXCLUSION_PATTERNS)
        
        # Extract requirements
        required_ingredients = self._extract_ingredients(query_lower, self.REQUIREMENT_PATTERNS)
        
        # Extract time constraints
        time_constraint = self._extract_time_constraint(query_lower)
        
        # Clean the query by removing constraint clauses
        clean_query = self._clean_query(query, excluded_ingredients, required_ingredients)
        
        return {
            'clean_query': clean_query,
            'excluded_ingredients': excluded_ingredients,
            'required_ingredients': required_ingredients,
            'time_constraint': time_constraint,
            'original_query': query
        }
    
    def _extract_ingredients(self, query: str, patterns: List[str]) -> List[str]:
        """Extract ingredients from query using regex patterns"""
        ingredients = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, query, re.IGNORECASE)
            for match in matches:
                # Get the captured group (ingredients text)
                ing_text = match.group(1).strip()
                
                # Split by common delimiters
                parts = re.split(r',|\s+and\s+|\s+or\s+', ing_text)
                
                # Clean and add each ingredient
                for part in parts:
                    part = part.strip()
                    if part and len(part) > 1:
                        # Normalize using aliases
                        normalized = self._normalize_ingredient(part)
                        if normalized not in ingredients:
                            ingredients.append(normalized)
        
        return ingredients
    
    def _normalize_ingredient(self, ingredient: str) -> str:
        """Normalize ingredient name using aliases"""
        ingredient = ingredient.strip().lower()
        
        # Check if it matches any alias group
        for canonical, aliases in self.INGREDIENT_ALIASES.items():
            if ingredient in aliases:
                return canonical
        
        return ingredient
    
    def _extract_time_constraint(self, query: str) -> Dict:
        """Extract time-related constraints"""
        for pattern, constraint_type in self.TIME_PATTERNS:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                if isinstance(constraint_type, int):
                    # Fixed time value (like "quick" = 30 mins)
                    return {'max_time': constraint_type}
                elif constraint_type == 'max_time':
                    return {'max_time': int(match.group(1))}
                elif constraint_type == 'exact_time':
                    time_val = int(match.group(1))
                    # Allow some flexibility (±5 minutes)
                    return {'min_time': time_val - 5, 'max_time': time_val + 5}
        
        return {}
    
    def _clean_query(self, query: str, excluded: List[str], required: List[str]) -> str:
        """Remove constraint clauses from query to get clean search terms"""
        clean = query
        
        # Remove exclusion clauses
        for pattern in self.EXCLUSION_PATTERNS:
            clean = re.sub(pattern, ' ', clean, flags=re.IGNORECASE)
        
        # Remove requirement clauses (but keep "with" if it's part of dish name)
        # Be careful not to remove "with" from phrases like "rice with"
        
        # Remove time constraint phrases
        for pattern, _ in self.TIME_PATTERNS:
            clean = re.sub(pattern, ' ', clean, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean

# Global instance
query_parser = QueryParser()
