import requests, json, uuid, sys
v = [0.01] * 768
pid = str(uuid.uuid4())
H = {'api-key': 'aios_qdrant_2026', 'Content-Type': 'application/json'}
r = requests.put('http://10.30.0.20:6333/collections/knowledge_chunks/points', headers=H, json={'points': [{'id': pid, 'vector': v, 'payload': {'text': 'test', 'source': '_test_'}}]}, timeout=10)
if r.json().get('status') != 'ok': print('upsert fail'); sys.exit(1)
s = requests.post('http://10.30.0.20:6333/collections/knowledge_chunks/points/search', headers=H, json={'vector': v, 'limit': 3}, timeout=10)
if not any(r.get('id') == pid for r in s.json().get('result', [])): print('search fail'); sys.exit(1)
requests.post('http://10.30.0.20:6333/collections/knowledge_chunks/points/delete', headers=H, json={'filter': {'must': [{'has_id': [pid]}]}}, timeout=10)
print('ok')
