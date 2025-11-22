"""
Professional Typesense Client for Recipe Search.
Mirrors the functionality of the reference 'searchClient.ts' but in Python.
"""

import typesense
import os
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

    def search(self, query: str, limit: int = 10, filters: Dict[str, str] = None):
        search_params = {
            'q': query,
            'query_by': 'name,description,ingredients',
            'per_page': limit,
            'collection': COLLECTION_NAME,
            'facet_by': 'cuisine,diet,course'
        }
        
        if filters:
            filter_str = []
            for key, value in filters.items():
                if value and value != "All":
                    filter_str.append(f"{key}:={value}")
            if filter_str:
                search_params['filter_by'] = ' && '.join(filter_str)
        
        if self.use_external_embeddings and query:
            vector = self.generate_embedding(query)
            search_params['vector_query'] = f"embedding:([{','.join(map(str, vector))}], k:50)"

        # Use multi_search to avoid URL length limits with vectors
        results = self.client.multi_search.perform({'searches': [search_params]}, {})
        return results['results'][0]

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
