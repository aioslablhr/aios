import sys

with open('/aios/docker-compose-aios.yml', 'r') as f:
    content = f.read()

old = '''<<<<<<< HEAD
<<<<<<< HEAD
    volumes:
      - ./dograh-patches/ari_manager.py:/app/api/services/telephony/ari_manager.py
=======
    volumes:
      - ./dograh-patches/ari_manager.py:/app/api/services/telephony/ari_manager.py
>>>>>>> origin/main
    healthcheck:
=======
    volumes:
      - ./dograh-patches/run_pipeline.py:/app/api/services/pipecat/run_pipeline.py
    healthcheck:
>>>>>>> afaad01 (fix: ext 102 latency - switch to general-reasoning (free), VAD 0.85, TTS speed 0.9)'''

new = '''    volumes:
      - ./dograh-patches/ari_manager.py:/app/api/services/telephony/ari_manager.py
      - ./dograh-patches/run_pipeline.py:/app/api/services/pipecat/run_pipeline.py
      - ./dograh-patches/chatwoot_sync.py:/app/api/services/pipecat/chatwoot_sync.py
    healthcheck:'''

count = content.count(old)
print(f'Found {count} occurrence(s)')
if count == 0:
    sys.exit(1)
content = content.replace(old, new, 1)
with open('/aios/docker-compose-aios.yml', 'w') as f:
    f.write(content)
print('Done')
