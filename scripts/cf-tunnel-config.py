#!/usr/bin/env python3
"""Write cloudflared config to server."""
import os

config = """tunnel: 710998a2-2ffd-49ac-84e6-5a563ea5a93a
credentials-file: /home/ai/.cloudflared/710998a2-2ffd-49ac-84e6-5a563ea5a93a.json

ingress:
  - hostname: socialbeesai.com
    service: https://10.10.0.10:443
    originRequest:
      noTLSVerify: true
  - hostname: '*.socialbeesai.com'
    service: https://10.10.0.10:443
    originRequest:
      noTLSVerify: true
  - service: http_status:404
"""

with open("/home/ai/.cloudflared/config.yml", "w") as f:
    f.write(config)
print("Config written OK")
