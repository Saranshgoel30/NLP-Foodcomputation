"""
Professional Typesense Client for Recipe Search.
Mirrors the functionality of the reference 'searchClient.ts' but in Python.
"""

import typesense
import os
import re
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
# Lazy import for sentence_transformers to avoid DLL issues in some envs
# from sentence_transformers import SentenceTransformer
# import torch

# Configuration
TYPESENSE_HOST = os.getenv("TYPESENSE_HOST", "localhost")
TYPESENSE_PORT = os.getenv("TYPESENSE_PORT", "8108")
TYPESENSE_PROTOCOL = os.getenv("TYPESENSE_PROTOCOL", "http")
TYPESENSE_API_KEY = os.getenv("TYPESENSE_API_KEY", "xyz")
COLLECTION_NAME = "recipes"

# Schema Definition (Matching the reference 'upload.js' but enhanced)
SCHEMA = {
    'name': COLLECTION_NAME,
    'fields': [
        {'name': 'name', 'type': 'string'},
        {'name': 'description', 'type': 'string', 'optional': True},
        {'name': 'instructions', 'type': 'string[]', 'optional': True},
        {'name': 'ingredients', 'type': 'string[]', 'facet': True},
        {'name': 'cuisine', 'type': 'string', 'optional': True, 'facet': True},
        {'name': 'course', 'type': 'string', 'optional': True, 'facet': True},
        {'name': 'diet', 'type': 'string', 'optional': True, 'facet': True},
        {'name': 'difficulty', 'type': 'string', 'optional': True, 'facet': True},
        {'name': 'prep_time', 'type': 'int32', 'optional': True, 'facet': True},
        {'name': 'cook_time', 'type': 'int32', 'optional': True, 'facet': True},
        {'name': 'total_time', 'type': 'int32', 'optional': True, 'facet': True},
        {'name': 'servings', 'type': 'int32', 'optional': True},
        {'name': 'url', 'type': 'string', 'optional': True},
        
        # Embedding field for semantic search (768 dim for mpnet-base-v2)
        {
            'name': 'embedding', 
            'type': 'float[]', 
            'num_dim': 768
        }
    ]
}

class SearchClient:
    def __init__(self, use_external_embeddings: bool = True):
        self.client = typesense.Client({
            'nodes': [{
                'host': TYPESENSE_HOST,
                'port': TYPESENSE_PORT,
                'protocol': TYPESENSE_PROTOCOL
            }],
            'api_key': TYPESENSE_API_KEY,
            'connection_timeout_seconds': 10
        })
        
        self.use_external_embeddings = use_external_embeddings
        self.model = None
        
        if self.use_external_embeddings:
            try:
                print("Loading embedding model (paraphrase-multilingual-mpnet-base-v2)...")
                from sentence_transformers import SentenceTransformer
                import torch
                self.torch = torch
                device = 'cuda' if torch.cuda.is_available() else 'cpu'
                self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2', device=device)
            except Exception as e:
                print(f"Warning: Failed to load embedding model: {e}")
                print("Falling back to text-only search.")
                self.use_external_embeddings = False
                self.model = None

    def ensure_collection(self):
        try:
            self.client.collections[COLLECTION_NAME].retrieve()
            print(f"Collection '{COLLECTION_NAME}' exists.")
        except typesense.exceptions.ObjectNotFound:
            print(f"Creating collection '{COLLECTION_NAME}'...")
            self.client.collections.create(SCHEMA)

    def generate_embedding(self, text: str) -> List[float]:
        if not self.model:
            return []
        with self.torch.no_grad():
            return self.model.encode(text, normalize_embeddings=True).tolist()

    def index_documents(self, documents: List[Dict[str, Any]], batch_size: int = 100):
        # Generate embeddings if missing
        if self.use_external_embeddings:
            docs_to_embed = [d for d in documents if 'embedding' not in d]
            if docs_to_embed:
                print(f"Generating embeddings for {len(docs_to_embed)} documents...")
                for doc in docs_to_embed:
                    # Create rich text representation
                    text = f"{doc.get('name', '')} {doc.get('description', '')} {doc.get('cuisine', '')} {' '.join(doc.get('ingredients', [])[:10])}"
                    doc['embedding'] = self.generate_embedding(text)

        # Import
        try:
            self.client.collections[COLLECTION_NAME].documents.import_(documents, {'action': 'upsert'})
            print(f"Indexed {len(documents)} documents.")
        except Exception as e:
            print(f"Indexing failed: {e}")

    def search(self, query: str, limit: int = 10, filters: Dict[str, str] = None, 
               excluded_ingredients: list = None, required_ingredients: list = None,
               time_constraint: dict = None):
        # Typesense has a max of 250 results per page - always fetch max for comprehensive results
        per_page = 250
        
        search_params = {
            'q': query,
            'query_by': 'name,description,ingredients',
            'per_page': per_page,
            'collection': COLLECTION_NAME,
            'facet_by': 'cuisine,diet,course',
            # OPTIMIZATION: Exhaustive search for comprehensive results
            'exhaustive_search': 'true',
            # OPTIMIZATION: Consider 100 prefix/typo variations (default is only 4!)
            'max_candidates': 100,
            # OPTIMIZATION: Don't drop query words too early
            'drop_tokens_threshold': 10,
            # OPTIMIZATION: Be strict with typos initially (only after 100 results)
            'typo_tokens_threshold': 100,
            # OPTIMIZATION: Sum scores across fields for better ranking
            'text_match_type': 'sum_score',
            # OPTIMIZATION: Prioritize recipes matching more fields
            'prioritize_num_matching_fields': 'true',
            # OPTIMIZATION: Exact matches get highest priority
            'prioritize_exact_match': 'true'
        }
        
        if filters:
            filter_str = []
            for key, value in filters.items():
                if value and value != "All":
                    filter_str.append(f"{key}:={value}")
            if filter_str:
                search_params['filter_by'] = ' && '.join(filter_str)
        
        # Add time constraint to filters
        if time_constraint:
            time_filters = []
            if 'max_time' in time_constraint:
                time_filters.append(f"total_time:<={time_constraint['max_time']}")
            if 'min_time' in time_constraint:
                time_filters.append(f"total_time:>={time_constraint['min_time']}")
            
            if time_filters:
                time_filter_str = ' && '.join(time_filters)
                if 'filter_by' in search_params:
                    search_params['filter_by'] += f" && {time_filter_str}"
                else:
                    search_params['filter_by'] = time_filter_str
        
        if self.use_external_embeddings and query:
            vector = self.generate_embedding(query)
            search_params['vector_query'] = f"embedding:([{','.join(map(str, vector))}], k:50)"

        # Use multi_search to avoid URL length limits with vectors
        try:
            results = self.client.multi_search.perform({'searches': [search_params]}, {})
            result = results['results'][0]
            
            # Validate result structure - check for Typesense errors
            if 'error' in result:
                print(f"❌ Typesense error: {result.get('error', 'Unknown error')}")
                print(f"   Error code: {result.get('code', 'N/A')}")
                return {
                    'hits': [],
                    'found': 0,
                    'out_of': 0,
                    'page': 1,
                    'search_time_ms': 0
                }
            
            if 'hits' not in result:
                print(f"⚠️  Typesense returned unexpected structure: {result.keys()}")
                print(f"   Result: {result}")
                return {
                    'hits': [],
                    'found': 0,
                    'out_of': 0,
                    'page': 1,
                    'search_time_ms': 0
                }
        except Exception as e:
            print(f"❌ Typesense search error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'hits': [],
                'found': 0,
                'out_of': 0,
                'page': 1,
                'search_time_ms': 0
            }
        
        # Post-process to filter by ingredients
        if excluded_ingredients or required_ingredients:
            filtered_hits = self._filter_by_ingredients(
                result.get('hits', []), 
                excluded_ingredients or [], 
                required_ingredients or []
            )
            
            # If filtering removes ALL results, show original results with warning
            if len(filtered_hits) == 0 and len(result.get('hits', [])) > 0:
                print(f"⚠️  No recipes found matching exclusions: {excluded_ingredients}")
                print(f"   Showing all {len(result['hits'])} results (may contain excluded ingredients)")
                result['hits'] = result['hits'][:limit]
                result['found'] = len(result['hits'])
                result['excluded_applied'] = False  # Mark that exclusions weren't applied
            else:
                result['hits'] = filtered_hits[:limit]
                result['found'] = len(filtered_hits)
                result['excluded_applied'] = True
        else:
            result['hits'] = result.get('hits', [])[:limit]
        
        return result
    
    def _filter_by_ingredients(self, hits: list, excluded: list, required: list) -> list:
        """
        Filter recipe hits based on ingredient constraints
        Uses comprehensive pattern matching for better accuracy
        """
        import json
        import os
        
        # Load ingredient patterns for comprehensive matching
        nlp_data_dir = os.path.join(os.path.dirname(__file__), 'nlp_data')
        ingredient_patterns = {}
        
        try:
            with open(os.path.join(nlp_data_dir, 'ingredient_aliases.json'), 'r', encoding='utf-8') as f:
                ingredient_data = json.load(f)
                # Build pattern map for each canonical ingredient
                for canonical, data in ingredient_data.items():
                    ingredient_patterns[canonical] = {
                        'aliases': [alias.lower() for alias in data.get('aliases', [])],
                        'patterns': data.get('exclusion_patterns', [])
                    }
        except Exception as e:
            print(f"Warning: Could not load ingredient patterns: {e}")
        
        filtered = []
        
        for hit in hits:
            # Get recipe data for comprehensive checking
            ingredients = hit['document'].get('ingredients', [])
            recipe_name = hit['document'].get('name', '').lower()
            description = hit['document'].get('description', '').lower()
            
            # Convert to lowercase for comparison
            ingredients_lower = [ing.lower() for ing in ingredients]
            
            # Create comprehensive searchable text (title + ingredients + description)
            searchable_text = f"{recipe_name} {' '.join(ingredients_lower)} {description}"
            
            # Check exclusions with comprehensive matching
            has_excluded = False
            for excluded_canonical in excluded:
                # Get all patterns for this ingredient
                patterns_data = ingredient_patterns.get(excluded_canonical, {})
                aliases = patterns_data.get('aliases', [excluded_canonical])
                regex_patterns = patterns_data.get('patterns', [])
                
                # Method 1: Check title for obvious exclusions
                for alias in aliases:
                    if alias in recipe_name:
                        has_excluded = True
                        print(f"   ❌ Excluded '{recipe_name}' - found '{alias}' in title")
                        break
                
                if has_excluded:
                    break
                
                # Method 2: Check each ingredient in the recipe
                for recipe_ing in ingredients_lower:
                    # Check if any alias appears in ingredient
                    for alias in aliases:
                        if alias in recipe_ing:
                            has_excluded = True
                            break
                    
                    # Use regex patterns if available
                    if not has_excluded and regex_patterns:
                        for pattern in regex_patterns:
                            try:
                                if re.search(pattern, recipe_ing, re.IGNORECASE):
                                    has_excluded = True
                                    break
                            except:
                                pass
                    
                    if has_excluded:
                        break
                
                if has_excluded:
                    break
                
                # Method 3: Check description as final catch-all
                if not has_excluded:
                    for alias in aliases:
                        # Only check for whole word matches in description to avoid false positives
                        if re.search(r'\b' + re.escape(alias) + r'\b', description):
                            has_excluded = True
                            print(f"   ❌ Excluded '{recipe_name}' - found '{alias}' in description")
                            break
                
                if has_excluded:
                    break
            
            if has_excluded:
                continue
            
            # Check requirements with comprehensive matching (title + ingredients + description)
            has_all_required = True
            for required_canonical in required:
                # Get all patterns for this ingredient
                patterns_data = ingredient_patterns.get(required_canonical, {})
                aliases = patterns_data.get('aliases', [required_canonical])
                
                # Check in multiple places: title first, then ingredients, then description
                found = False
                
                # 1. Check title
                for alias in aliases:
                    if alias in recipe_name:
                        found = True
                        break
                
                # 2. Check ingredients
                if not found:
                    for recipe_ing in ingredients_lower:
                        for alias in aliases:
                            if alias in recipe_ing:
                                found = True
                                break
                        if found:
                            break
                
                # 3. Check description as fallback
                if not found:
                    for alias in aliases:
                        if re.search(r'\b' + re.escape(alias) + r'\b', description):
                            found = True
                            break
                
                if not found:
                    has_all_required = False
                    break
            
            if not has_all_required:
                continue
            
            filtered.append(hit)
        
        return filtered

    def autocomplete_ingredient(self, query: str, limit: int = 5):
        """
        Search for ingredients matching the query.
        """
        search_params = {
            'q': query,
            'query_by': 'ingredient,synonym',
            'per_page': limit,
            'collection': 'ingredients'
        }
        try:
            results = self.client.multi_search.perform({'searches': [search_params]}, {})
            return results['results'][0]['hits']
        except Exception as e:
            print(f"Autocomplete failed: {e}")
            return []

    def autocomplete_query(self, query: str, limit: int = 5):
        """
        Search for queries matching the input.
        """
        search_params = {
            'q': query,
            'query_by': 'query',
            'per_page': limit,
            'collection': 'queries'
        }
        try:
            results = self.client.multi_search.perform({'searches': [search_params]}, {})
            return results['results'][0]['hits']
        except Exception as e:
            print(f"Query autocomplete failed: {e}")
            return []
