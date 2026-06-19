#!/usr/bin/env python3
"""Exhaustive auth tests from frigate container."""
import subprocess

tests = [
    # wget with auth-no-challenge
    "wget --user=admin --password=Lahore*999 --auth-no-challenge -q -O /tmp/wget_test.jpg http://10.0.0.51/cgi-bin/snapshot.cgi 2>&1; ls -la /tmp/wget_test.jpg 2>&1; echo '---'",
    # curl with --anyauth
    "curl -s --anyauth -u admin:Lahore*999 -o /tmp/curl_test.jpg -w '%{http_code}' http://10.0.0.51/cgi-bin/snapshot.cgi; ls -la /tmp/curl_test.jpg 2>&1; echo '---'",
    # curl with --basic
    "curl -s --basic -u admin:Lahore*999 -o /tmp/curl_basic.jpg -w '%{http_code}' http://10.0.0.51/cgi-bin/snapshot.cgi; ls -la /tmp/curl_basic.jpg 2>&1; echo '---'",
    # curl with --ntlm
    "curl -s --ntlm -u admin:Lahore*999 -o /tmp/curl_ntlm.jpg -w '%{http_code}' http://10.0.0.51/cgi-bin/snapshot.cgi; ls -la /tmp/curl_ntlm.jpg 2>&1; echo '---'",
    # Actually do an OPTIONS request first to see server response
    "curl -s -v -u admin:Lahore*999 http://10.0.0.51/cgi-bin/snapshot.cgi -o /tmp/curl_verbose.txt 2>&1 | head -30; echo '---'",
    # Check if we need to send a session/login first
    "curl -s -c /tmp/cookies.txt -b /tmp/cookies.txt -X POST -d 'username=admin&password=Lahore*999' http://10.0.0.51/cgi-bin/login.cgi 2>&1 | head -5; echo '---'",
]

for i, cmd in enumerate(tests):
    print(f"\n=== Test {i+1} ===")
    try:
        result = subprocess.run(
            ["docker", "exec", "aios-frigate", "sh", "-c", cmd],
            capture_output=True, text=True, timeout=10
        )
        out = (result.stdout or "")[:300] + (result.stderr or "")[:100]
        print(out)
    except Exception as e:
        print(f"Error: {e}")
