"""
Ingredient Synonym Service
Loads synonyms from ingredients.jsonl and expands search queries
"""

import json
import os
from typing import Dict, List, Set, Optional
from pathlib import Path


class IngredientSynonymService:
    """
    Loads ingredient synonyms from ingredients.jsonl and provides
    query expansion for search.
    
    Example: "paneer" -> ["paneer", "indian cottage cheese", "cottage cheese", "panir"]
    """
    
    def __init__(self, jsonl_path: Optional[str] = None):
        # Default path relative to this file
        if jsonl_path is None:
            base_dir = Path(__file__).parent.parent.parent
            jsonl_path = base_dir / "data" / "ingredients.jsonl"
        
        self.jsonl_path = str(jsonl_path)
        
        # ingredient -> set of all synonyms (bidirectional)
        self.synonym_map: Dict[str, Set[str]] = {}
        
        # All known ingredients (for quick lookup)
        self.all_ingredients: Set[str] = set()
        
        # Load synonyms
        self._load_synonyms()
        
        print(f"🧂 Ingredient Synonym Service initialized")
        print(f"   Loaded {len(self.all_ingredients)} ingredients")
        print(f"   Synonym groups: {len(self.synonym_map)}")
    
    def _load_synonyms(self):
        """Load and index synonyms from ingredients.jsonl"""
        try:
            if not os.path.exists(self.jsonl_path):
                print(f"⚠️ Ingredients file not found: {self.jsonl_path}")
                return
            
            with open(self.jsonl_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        ingredient = data.get("ingredient", "").strip().lower()
                        synonyms = data.get("synonym", [])
                        replacements = data.get("replacements", [])
                        
                        if not ingredient:
                            continue
                        
                        self.all_ingredients.add(ingredient)
                        
                        # Build synonym group: ingredient + actual synonyms ONLY
                        # (NOT replacements - those are alternatives, not the same thing)
                        synonym_group = {ingredient}
                        
                        for syn in synonyms:
                            if isinstance(syn, str) and syn.strip():
                                clean_syn = syn.strip().lower()
                                synonym_group.add(clean_syn)
                                self.all_ingredients.add(clean_syn)
                        
                        # Track replacements separately (for future use, not for synonym expansion)
                        for rep in replacements:
                            if isinstance(rep, str) and rep.strip():
                                clean_rep = rep.strip().lower()
                                self.all_ingredients.add(clean_rep)  # Still track as known ingredient
                        
                        # Store bidirectional mappings for TRUE synonyms only
                        for term in synonym_group:
                            if term not in self.synonym_map:
                                self.synonym_map[term] = set()
                            self.synonym_map[term].update(synonym_group)
                    
                    except json.JSONDecodeError:
                        continue
            
            print(f"   ✅ Loaded synonyms from {self.jsonl_path}")
            
        except Exception as e:
            print(f"❌ Error loading synonyms: {e}")
    
    def get_synonyms(self, ingredient: str) -> List[str]:
        """
        Get all synonyms for an ingredient.
        
        Args:
            ingredient: The ingredient to look up
            
        Returns:
            List of synonyms (including the original term)
        """
        ingredient = ingredient.strip().lower()
        
        if ingredient in self.synonym_map:
            return list(self.synonym_map[ingredient])
        
        # Try partial matching for compound ingredients
        for known in self.synonym_map:
            if ingredient in known or known in ingredient:
                return list(self.synonym_map[known])
        
        return [ingredient]
    
    def expand_query(self, query: str) -> str:
        """
        Expand a search query by adding ingredient synonyms.
        
        Example: "paneer curry" -> "paneer OR cottage cheese OR indian cottage cheese curry"
        
        Args:
            query: Original search query
            
        Returns:
            Expanded query with OR clauses for synonyms
        """
        words = query.lower().split()
        expanded_parts = []
        i = 0
        
        while i < len(words):
            # Try to match multi-word ingredients (longest match first)
            matched = False
            
            for length in range(min(4, len(words) - i), 0, -1):
                phrase = " ".join(words[i:i + length])
                
                if phrase in self.synonym_map:
                    synonyms = self.synonym_map[phrase]
                    if len(synonyms) > 1:
                        # Create OR clause for synonyms
                        synonym_list = list(synonyms)[:5]  # Limit to 5 synonyms
                        or_clause = " OR ".join(f'"{s}"' for s in synonym_list)
                        expanded_parts.append(f"({or_clause})")
                    else:
                        expanded_parts.append(phrase)
                    i += length
                    matched = True
                    break
            
            if not matched:
                expanded_parts.append(words[i])
                i += 1
        
        return " ".join(expanded_parts)
    
    def get_all_synonyms_for_terms(self, terms: List[str]) -> Dict[str, List[str]]:
        """
        Get synonyms for multiple terms.
        
        Args:
            terms: List of ingredient terms
            
        Returns:
            Dict mapping each term to its synonyms
        """
        result = {}
        for term in terms:
            result[term] = self.get_synonyms(term)
        return result
    
    def extract_ingredients_from_query(self, query: str) -> List[str]:
        """
        Extract known ingredients from a query.
        
        Args:
            query: Search query
            
        Returns:
            List of identified ingredients
        """
        query_lower = query.lower()
        found = []
        
        # Check for known ingredients (prioritize longer matches)
        sorted_ingredients = sorted(self.all_ingredients, key=len, reverse=True)
        
        for ingredient in sorted_ingredients:
            if ingredient in query_lower:
                # Avoid overlapping matches
                already_covered = any(
                    ingredient in existing or existing in ingredient 
                    for existing in found
                )
                if not already_covered:
                    found.append(ingredient)
        
        return found


# Singleton instance
_synonym_service: Optional[IngredientSynonymService] = None


def get_synonym_service() -> IngredientSynonymService:
    """Get or create the singleton synonym service"""
    global _synonym_service
    if _synonym_service is None:
        _synonym_service = IngredientSynonymService()
    return _synonym_service
