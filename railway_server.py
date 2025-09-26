#!/usr/bin/env python3
"""
Railway Frontend Server
Serves the enhanced dashboard and static files
"""

import os
import http.server
import socketserver
from urllib.parse import urlparse

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Route requests
        if path == '/' or path == '/index.html':
            # Serve the main dashboard
            self.path = '/enhanced_dashboard.html'
        elif path == '/dashboard':
            # Alternative dashboard route
            self.path = '/enhanced_dashboard.html'
        elif path == '/health':
            # Health check endpoint
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'{"status": "healthy", "service": "frontend"}')
            return
        
        # Add CORS headers to all responses
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        
        # Call parent method
        super().do_GET()
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

if __name__ == '__main__':
    PORT = int(os.getenv('PORT', 8000))
    
    print(f"🚀 Starting Railway Frontend Server on port {PORT}")
    print(f"🌐 Dashboard will be available at: http://localhost:{PORT}/enhanced_dashboard.html")
    print(f"📊 Alternative route: http://localhost:{PORT}/dashboard")
    print(f"❤️ Health check: http://localhost:{PORT}/health")
    
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"✅ Server running on port {PORT}")
        httpd.serve_forever()
