"""
Advanced Natural Language Query Parser for Recipe Search
Uses comprehensive pattern matching and ingredient aliases from JSON files
"""

import re
import json
import os
from typing import Dict, List, Tuple, Set

class QueryParser:
    """Advanced NLP parser with comprehensive ingredient understanding"""
    
    def __init__(self):
        """Load NLP data from JSON files"""
        self.nlp_data_dir = os.path.join(os.path.dirname(__file__), 'nlp_data')
        
        # Load ingredient aliases and patterns
        self.ingredient_data = self._load_json('ingredient_aliases.json')
        self.pattern_data = self._load_json('exclusion_patterns.json')
        self.context_data = self._load_json('dish_context.json')
        
        print(f"✅ Loaded {len(self.ingredient_data)} ingredient groups")
        print(f"✅ Loaded {len(self.pattern_data.get('explicit_exclusions', {}).get('regex_patterns', []))} exclusion patterns")
        
        # Build reverse lookup for ingredients (alias -> canonical)
        self.ingredient_lookup = {}
        self.exclusion_patterns_map = {}
        
        for canonical, data in self.ingredient_data.items():
            # Map all aliases to canonical name
            for alias in data.get('aliases', []):
                self.ingredient_lookup[alias.lower()] = canonical
            
            # Store exclusion patterns for this ingredient
            if 'exclusion_patterns' in data:
                self.exclusion_patterns_map[canonical] = data['exclusion_patterns']
        
        print(f"✅ Built lookup with {len(self.ingredient_lookup)} ingredient aliases")
        
        # Compile regex patterns from JSON
        exclusion_patterns = self.pattern_data.get('explicit_exclusions', {}).get('regex_patterns', [])
        requirement_patterns = self.pattern_data.get('requirement_patterns', {}).get('regex_patterns', [])
        
        self.exclusion_regex = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in exclusion_patterns
        ]
        
        self.requirement_regex = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in requirement_patterns
        ]
    
    def _load_json(self, filename: str) -> Dict:
        """Load JSON file from nlp_data directory"""
        try:
            filepath = os.path.join(self.nlp_data_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load {filename}: {e}")
            return {}
    
    def parse(self, query: str) -> Dict:
        """
        Parse a natural language query with advanced understanding
        Extracts:
        - Core search terms (cleaned query)
        - Excluded ingredients (with all variants)
        - Required ingredients (with all variants)
        - Time constraints
        """
        query_lower = query.lower()
        
        # Extract exclusions with comprehensive pattern matching
        excluded_ingredients = self._extract_exclusions(query_lower)
        
        # Extract requirements
        required_ingredients = self._extract_requirements(query_lower)
        
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
    
    def _extract_exclusions(self, query: str) -> List[str]:
        """Extract excluded ingredients using comprehensive patterns"""
        exclusions = set()
        
        # Try all exclusion regex patterns
        for pattern in self.exclusion_regex:
            matches = pattern.finditer(query)
            for match in matches:
                # Get the captured ingredient text
                ing_text = match.group(1).strip() if match.groups() else ""
                
                if ing_text:
                    # Split by delimiters
                    parts = re.split(r',|\s+and\s+|\s+or\s+', ing_text)
                    
                    for part in parts:
                        part = part.strip()
                        if part and len(part) > 1:
                            # Find canonical ingredient and add it
                            canonical = self._find_canonical_ingredient(part)
                            if canonical:
                                exclusions.add(canonical)
        
        return list(exclusions)
    
    def _extract_requirements(self, query: str) -> List[str]:
        """Extract required ingredients using comprehensive patterns"""
        requirements = set()
        
        # Try all requirement regex patterns
        for pattern in self.requirement_regex:
            matches = pattern.finditer(query)
            for match in matches:
                # Get the captured ingredient text
                ing_text = match.group(1).strip() if match.groups() else ""
                
                if ing_text:
                    # Split by delimiters
                    parts = re.split(r',|\s+and\s+|\s+or\s+', ing_text)
                    
                    for part in parts:
                        part = part.strip()
                        if part and len(part) > 1:
                            # Find canonical ingredient and add it
                            canonical = self._find_canonical_ingredient(part)
                            if canonical:
                                requirements.add(canonical)
        
        return list(requirements)
    
    def _find_canonical_ingredient(self, ingredient_text: str) -> str:
        """
        Find canonical ingredient name from any variant
        Uses comprehensive lookup including partial matches
        """
        ingredient_text = ingredient_text.strip().lower()
        
        # Direct lookup
        if ingredient_text in self.ingredient_lookup:
            return self.ingredient_lookup[ingredient_text]
        
        # Try partial matches (e.g., "potato" matches "potatoes")
        for alias, canonical in self.ingredient_lookup.items():
            # Check if the text contains or is contained in an alias
            if ingredient_text in alias or alias in ingredient_text:
                # Make sure it's not a false positive (e.g., "not" in "onion")
                if len(ingredient_text) >= 3:
                    return canonical
        
        # Return as-is if no match found (will still work for filtering)
        return ingredient_text
    
    def _extract_time_constraint(self, query: str) -> Dict:
        """Extract time-related constraints from patterns"""
        time_data = self.pattern_data.get('time_constraints', {})
        time_mappings = time_data.get('time_mappings', {})
        
        # Check for keyword time constraints (quick, fast, etc.)
        for keyword, minutes in time_mappings.items():
            if keyword in query.lower():
                return {'max_time': minutes}
        
        # Check for explicit time patterns
        for pattern in time_data.get('regex_patterns', []):
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                if match.groups():
                    # Extract numeric time value
                    time_val = int(match.group(1))
                    if 'under' in pattern or 'less' in pattern or 'within' in pattern:
                        return {'max_time': time_val}
                    elif 'in' in pattern or 'takes' in pattern:
                        # Allow some flexibility (±5 minutes)
                        return {'min_time': max(0, time_val - 5), 'max_time': time_val + 5}
        
        return {}
    
    def _clean_query(self, query: str, excluded: List[str], required: List[str]) -> str:
        """Remove constraint clauses from query to get clean search terms"""
        clean = query
        
        # Remove exclusion clauses using patterns from JSON
        for pattern in self.exclusion_regex:
            clean = pattern.sub(' ', clean)
        
        # Remove requirement clauses using patterns from JSON
        for pattern in self.requirement_regex:
            clean = pattern.sub(' ', clean)
        
        # Remove time constraint phrases
        time_data = self.pattern_data.get('time_constraints', {})
        for pattern_str in time_data.get('regex_patterns', []):
            try:
                clean = re.sub(pattern_str, ' ', clean, flags=re.IGNORECASE)
            except:
                pass
        
        # Clean up extra whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean
