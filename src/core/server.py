"""
Web server module for hosting FlowState visualizations.
Provides a fallback option when GitHub Pages deployment is not available.
"""

import http.server
import socketserver
import json
import os
import sys
from pathlib import Path
from functools import partial
import argparse
import threading
import time
from typing import Optional, Dict, Any
import logging

from ..core.config import settings


class FlowStateHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with CORS support for FlowState viewer."""

    def end_headers(self):
        """Add CORS and cache headers."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        """Handle preflight CORS requests."""
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        """Custom logging with timestamp."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        logging.info(f"[{timestamp}] {format % args}")


class FlowStateServer:
    """Production web server for hosting FlowState visualizations."""

    def __init__(self, port: int = 8080, directory: Optional[Path] = None, host: str = '0.0.0.0'):
        self.port = port
        self.host = host
        self.directory = directory or Path(settings.output_dir) / "viewer"
        self.server = None
        self.server_thread = None
        self.logger = logging.getLogger(__name__)

    def validate_directory(self) -> bool:
        """Validate that the viewer directory exists and contains required files."""
        required_files = ['index.html', 'data.js']
        
        if not self.directory.exists():
            self.logger.error(f"Viewer directory does not exist: {self.directory}")
            return False
        
        for file in required_files:
            if not (self.directory / file).exists():
                self.logger.error(f"Required file missing: {file}")
                return False
        
        return True

    def start(self, daemon: bool = False) -> bool:
        """
        Start the web server.
        
        Args:
            daemon: Run server as daemon thread
            
        Returns:
            True if server started successfully
        """
        if not self.validate_directory():
            return False
        
        try:
            # Create the server
            handler = partial(FlowStateHandler, directory=str(self.directory))
            self.server = socketserver.TCPServer((self.host, self.port), handler)
            self.server.allow_reuse_address = True
            
            # Start server in a separate thread
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = daemon
            self.server_thread.start()
            
            self.logger.info(f"FlowState Web Server started")
            self.logger.info(f"Serving directory: {self.directory}")
            self.logger.info(f"Server running at: http://{self.host}:{self.port}")
            
            # If not daemon mode, provide access URLs
            if not daemon:
                if self.host == '0.0.0.0':
                    import socket
                    hostname = socket.gethostname()
                    local_ip = socket.gethostbyname(hostname)
                    self.logger.info(f"Local access: http://localhost:{self.port}")
                    self.logger.info(f"Network access: http://{local_ip}:{self.port}")
                
            return True
            
        except OSError as e:
            if e.errno == 98:  # Address already in use
                self.logger.error(f"Port {self.port} is already in use")
            else:
                self.logger.error(f"Failed to start server: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error starting server: {e}")
            return False

    def stop(self):
        """Stop the web server gracefully."""
        if self.server:
            self.logger.info("Shutting down FlowState Web Server...")
            self.server.shutdown()
            if self.server_thread:
                self.server_thread.join(timeout=5)
            self.server.server_close()
            self.logger.info("Server stopped.")

    def wait(self):
        """Wait for the server thread to complete (blocking)."""
        if self.server_thread and self.server_thread.is_alive():
            try:
                self.server_thread.join()
            except KeyboardInterrupt:
                self.stop()


def run_server(port: int = 8080, directory: Optional[str] = None, host: str = '0.0.0.0') -> None:
    """
    Run the FlowState web server.
    
    Args:
        port: Port to bind to
        directory: Directory to serve (defaults to output viewer directory)
        host: Host to bind to (0.0.0.0 for all interfaces)
    """
    server_dir = Path(directory) if directory else None
    server = FlowStateServer(port=port, directory=server_dir, host=host)
    
    if server.start(daemon=False):
        print(f"\nPress Ctrl+C to stop the server\n")
        try:
            server.wait()
        except KeyboardInterrupt:
            print("\nReceived interrupt signal...")
        finally:
            server.stop()
    else:
        sys.exit(1)


if __name__ == "__main__":
    # Simple test mode
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        (test_dir / "index.html").write_text("<h1>FlowState Test</h1>")
        (test_dir / "data.js").write_text("const flowStateData = {};")
        
        server = FlowStateServer(port=8888, directory=test_dir)
        if server.start():
            print("Test server running for 5 seconds...")
            time.sleep(5)
            server.stop()