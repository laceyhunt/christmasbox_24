import threading
import http.server
import socketserver
import urllib
from pygame import time

# Global variable to hold the state value and server running flag
state_value = None
running = True

# Custom HTTP request handler
class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global state_value

        # Parse query parameters
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        state = query_components.get("state", [""])[0]
        
        # Update the state value
        state_value = state
        response_text=bytes(str(state_value),'utf-8')

        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(response_text)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

# Start HTTP server in a separate thread
def start_server():
    global running
    with ThreadedTCPServer(("", 8000), CustomHandler) as httpd:
        print("Serving at port", 8000)
        while running:
            httpd.handle_request()
        print("Server closed")

# Start the server thread
server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

# Pygame loop
clock = time.Clock()
try:
    while True:
        # Run at 30 FPS
        clock.tick(30)

        # Check the state value
        if state_value is not None:
            print("State value received:", state_value)
            # Reset state_value or perform your actions here
            state_value = None
except KeyboardInterrupt:
    print("Pygame loop interrupted")
finally:
    print("Cleaning up...")
    # Signal the server thread to stop
    running = False
    server_thread.join()
