import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.search_client import SearchClient

client = SearchClient()
results = client.autocomplete_ingredient("pepper")
for hit in results:
    print(hit['document']['ingredient'])
