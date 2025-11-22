import sys
import os
import json
import typesense

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.search_client import SearchClient

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'ingredients.jsonl')

def load_ingredients(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def main():
    print("Initializing Search Client...")
    client = SearchClient()
    
    # Define schema for ingredients
    schema = {
        'name': 'ingredients',
        'fields': [
            {'name': 'ingredient', 'type': 'string'},
            {'name': 'synonym', 'type': 'string[]', 'optional': True},
            {'name': 'replacements', 'type': 'string[]', 'optional': True},
            {'name': 'embedding', 'type': 'float[]', 'num_dim': 768, 'optional': True}
        ]
    }
    
    try:
        client.client.collections['ingredients'].retrieve()
        print("Collection 'ingredients' exists.")
    except:
        print("Creating collection 'ingredients'...")
        client.client.collections.create(schema)
        
    print(f"Reading from {DATA_FILE}...")
    
    batch = []
    count = 0
    
    for item in load_ingredients(DATA_FILE):
        # Generate embedding for the ingredient name
        embedding = client.generate_embedding(item['ingredient'])
        item['embedding'] = embedding
        batch.append(item)
        
        if len(batch) >= 100:
            client.client.collections['ingredients'].documents.import_(batch, {'action': 'upsert'})
            count += len(batch)
            print(f"Indexed {count} ingredients...")
            batch = []
            
    if batch:
        client.client.collections['ingredients'].documents.import_(batch, {'action': 'upsert'})
        count += len(batch)
        
    print(f"Done! Total ingredients indexed: {count}")

if __name__ == "__main__":
    main()
