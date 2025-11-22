import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.search_client import SearchClient

client = SearchClient()
print("Testing query autocomplete...")
results = client.autocomplete_query("chicken", limit=5)
print(f"Found {len(results)} results:")
for hit in results:
    print(f"- {hit['document']['query']}")
