import sys
import os
import json
import typesense

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.search_client import SearchClient

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'comprehensive_queries.jsonl')

def load_queries(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def main():
    print("Initializing Search Client...")
    client = SearchClient()
    
    # Define schema for queries
    schema = {
        'name': 'queries',
        'fields': [
            {'name': 'query', 'type': 'string'},
            {'name': 'embedding', 'type': 'float[]', 'num_dim': 768, 'optional': True}
        ]
    }
    
    try:
        client.client.collections['queries'].retrieve()
        print("Collection 'queries' exists.")
    except:
        print("Creating collection 'queries'...")
        client.client.collections.create(schema)
        
    print(f"Reading from {DATA_FILE}...")
    
    batch = []
    count = 0
    
    for item in load_queries(DATA_FILE):
        # Generate embedding for the query text
        embedding = client.generate_embedding(item['query'])
        if embedding:
            item['embedding'] = embedding
        batch.append(item)
        
        if len(batch) >= 100:
            client.client.collections['queries'].documents.import_(batch, {'action': 'upsert'})
            count += len(batch)
            print(f"Indexed {count} queries...")
            batch = []
            
    if batch:
        client.client.collections['queries'].documents.import_(batch, {'action': 'upsert'})
        count += len(batch)
        
    print(f"Done! Total queries indexed: {count}")

if __name__ == "__main__":
    main()
