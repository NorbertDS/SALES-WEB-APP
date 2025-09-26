#!/usr/bin/env python3
"""
CORS Proxy Server for local development
This server acts as a proxy to bypass CORS issues during development
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json

class CORSProxyHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        self.handle_request()
    
    def do_POST(self):
        self.handle_request()
    
    def handle_request(self):
        try:
            # Extract the target URL from the path
            if self.path.startswith('/proxy/'):
                target_url = self.path[7:]  # Remove '/proxy/' prefix
                if not target_url.startswith('http'):
                    target_url = 'https://data-analytics-master.up.railway.app' + target_url
            else:
                target_url = 'https://data-analytics-master.up.railway.app' + self.path
            
            print(f"🔄 Proxying request to: {target_url}")
            
            # Make the request to the target server
            req = urllib.request.Request(target_url)
            req.add_header('User-Agent', 'CORS-Proxy/1.0')
            
            # Forward request headers
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'connection']:
                    req.add_header(header, value)
            
            # Handle POST data
            if self.command == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length)
                    req.data = post_data
                    req.add_header('Content-Length', str(len(post_data)))
            
            # Make the request
            with urllib.request.urlopen(req) as response:
                # Send response
                self.send_response(response.status)
                self.send_cors_headers()
                
                # Forward response headers
                for header, value in response.headers.items():
                    if header.lower() not in ['content-encoding', 'transfer-encoding']:
                        self.send_header(header, value)
                
                self.end_headers()
                
                # Forward response body
                self.wfile.write(response.read())
                
        except Exception as e:
            print(f"❌ Proxy error: {e}")
            self.send_response(500)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Allow-Credentials', 'true')
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

if __name__ == '__main__':
    PORT = 8080
    print(f"🚀 Starting CORS Proxy Server on port {PORT}")
    print(f"🌐 Proxy URL: http://localhost:{PORT}")
    print(f"🔗 Use: http://localhost:{PORT}/proxy/health")
    print(f"📡 Target: https://data-analytics-master.up.railway.app")
    
    server = HTTPServer(('localhost', PORT), CORSProxyHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Proxy server stopped")
        server.shutdown()
