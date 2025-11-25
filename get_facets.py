import typesense

client = typesense.Client({
    'nodes': [{'host': 'localhost', 'port': '8108', 'protocol': 'http'}],
    'api_key': 'xyz'
})

result = client.collections['recipes'].documents.search({
    'q': '*',
    'query_by': 'name',
    'per_page': 0,
    'facet_by': 'cuisine,diet,course'
})

print("CUISINE VALUES (top 30):")
for f in result['facet_counts'][0]['counts'][:30]:
    print(f"  '{f['value']}' ({f['count']} recipes)")

print("\nDIET VALUES (top 20):")
for f in result['facet_counts'][1]['counts'][:20]:
    print(f"  '{f['value']}' ({f['count']} recipes)")

print("\nCOURSE VALUES (all):")
for f in result['facet_counts'][2]['counts']:
    print(f"  '{f['value']}' ({f['count']} recipes)")
