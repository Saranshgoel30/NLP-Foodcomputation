import sys
import os
import argparse

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.search_client import SearchClient

def main():
    parser = argparse.ArgumentParser(description='Search recipes')
    parser.add_argument('query', type=str, help='Search query')
    parser.add_argument('--limit', type=int, default=5, help='Number of results')
    args = parser.parse_args()

    client = SearchClient()
    
    print(f"\nSearching for: '{args.query}'...\n")
    
    search_result = client.search(args.query, limit=args.limit)
    results = search_result['hits']
    
    for i, hit in enumerate(results):
        doc = hit['document']
        score = hit.get('vector_distance', 0) # Note: Typesense returns vector_distance (lower is better for distance, but search result usually sorted)
        # Actually Typesense hybrid search returns a text match score or vector distance.
        # Let's just print what we have.
        
        print(f"{i+1}. {doc['name']} (Score: {score})")
        print(f"   Cuisine: {doc['cuisine']} | Diet: {doc['diet']}")
        print(f"   Description: {doc['description'][:100]}...")
        print("-" * 50)

if __name__ == "__main__":
    main()
