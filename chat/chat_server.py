import http.server
import urllib.request
import urllib.error
import json
import os

DOGRAH_API = "http://10.50.0.30:8000"
API_KEY = "dgr_JxFoGXkzncAlJM2aUhPhFOZ_GCQKgBHpajfgH15V0Bc"
WORKFLOW_ID = 1

KNOWLEDGE_MSG = "Here is our company information for reference: SHIN Travels, 123 High Street, London, E1 1AA. Family-run since 1998. We book Pakistan (Lahore from 379), India (Delhi from 380), Dubai (from 479), Saudi/Umrah (from 449), Qatar, Japan, Oman, USA. Umrah packages include flights, visa, hotels near Haram."

class ChatHandler(http.server.SimpleHTTPRequestHandler):
    def translate(self, path):
        path = path.replace('/api/sessions', f'/api/v1/workflow/{WORKFLOW_ID}/text-chat/sessions', 1)
        return f"{DOGRAH_API}{path}"

    def do_GET(self):
        if self.path == '/' or self.path == '/chat':
            self.path = '/index.html'
        if self.path.startswith('/api/'):
            try:
                target = self.translate(self.path)
                req = urllib.request.Request(target, headers={"X-API-Key": API_KEY})
                with urllib.request.urlopen(req, timeout=30) as r:
                    self.send_response(r.status)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(r.read())
            except urllib.error.HTTPError as e:
                self.send_response(e.code)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(e.read())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/'):
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length) if length else b'{}'
            try:
                target = self.translate(self.path)
                # Inject knowledge into new sessions
                if self.path == '/api/sessions':
                    req = urllib.request.Request(target, data=body,
                        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
                        method='POST')
                    with urllib.request.urlopen(req, timeout=60) as r:
                        resp_data = r.read()
                        session = json.loads(resp_data)
                        sid = session.get("workflow_run_id")
                        if sid:
                            msg_body = json.dumps({"text": KNOWLEDGE_MSG}).encode()
                            msg_url = target + "/" + str(sid) + "/messages"
                            msg_req = urllib.request.Request(msg_url, data=msg_body,
                                headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
                                method='POST')
                            urllib.request.urlopen(msg_req, timeout=60)
                        self.send_response(r.status)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(resp_data)
                else:
                    req = urllib.request.Request(target, data=body,
                        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
                        method='POST')
                    with urllib.request.urlopen(req, timeout=60) as r:
                        self.send_response(r.status)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(r.read())
            except urllib.error.HTTPError as e:
                self.send_response(e.code)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(e.read())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    port = int(os.getenv('PORT', '8081'))
    server = http.server.HTTPServer(("0.0.0.0", port), ChatHandler)
    print(f"Emma Chat Server running at http://0.0.0.0:{port}")
    server.serve_forever()
