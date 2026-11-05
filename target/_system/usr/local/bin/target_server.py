#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone
from threading import Thread, Lock
from socketserver import ThreadingTCPServer, BaseRequestHandler
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LOG = Path("/home/ubuntu/scan-lab/connections.log")
LOCK = Lock()
PORTS = range(9001, 9009)

class ConnectionHandler(BaseRequestHandler):
    def handle(self):
        event = {
            "time": datetime.now(timezone.utc).isoformat(),
            "source_ip": self.client_address[0],
            "destination_port": self.server.server_address[1]
        }
        with LOCK:
            with LOG.open("a") as f:
                f.write(json.dumps(event) + "\n")
        try:
            self.request.sendall(b"PORT_OPEN\n")
        except OSError:
            pass

class PortServer(ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

class API(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            result = {"status": "TARGET_READY"}
        elif self.path == "/events":
            if self.client_address[0] != "172.29.111.30":
                self.send_error(403)
                return
            with LOCK:
                lines = LOG.read_text().splitlines() if LOG.exists() else []
            result = {"events": [json.loads(x) for x in lines]}
        else:
            self.send_error(404)
            return

        data = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass

for port in PORTS:
    server = PortServer(("0.0.0.0", port), ConnectionHandler)
    Thread(target=server.serve_forever, daemon=True).start()

print("TARGET_READY: TCP 9001-9008, HTTP 8080", flush=True)
ThreadingHTTPServer(("0.0.0.0", 8080), API).serve_forever()
