from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"""
        <html>
        <body>
            <h1>Movie Catalog</h1>
            <p>Desktop application for managing movie catalog.</p>
            <p>Run locally: <code>python main.py</code></p>
        </body>
        </html>
        """)