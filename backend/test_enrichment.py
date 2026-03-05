from app import app
import json

client = app.test_client()

# Test enrichment
print('='*80)
print('TEST: Enriched prompt via /generate endpoint')
print('='*80)

response = client.post('/generate', json={'prompt': 'Marseille verte avec innovation technologique'})
data = response.json

print(f'Status: {response.status_code}')
print(f'Original: {data.get("original_prompt")}')
print(f'\nEnriched Prompt:')
print(data.get('prompt'))
print('\n' + '='*80)
