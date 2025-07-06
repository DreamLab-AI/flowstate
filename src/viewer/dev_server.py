#!/usr/bin/env python3
"""
Development server for testing the FlowState 3D viewer locally.
This server allows testing the visualization before deploying to GitHub Pages.
"""

import http.server
import socketserver
import json
import os
import sys
from pathlib import Path
from functools import partial
import argparse
import webbrowser
import time
from typing import Optional, Dict, Any
import threading


class FlowStateDevHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for the development server with CORS support and enhanced features."""

    def end_headers(self):
        """Add CORS headers to allow cross-origin requests."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        """Handle preflight CORS requests."""
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        """Custom logging with timestamp."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")


class DevelopmentServer:
    """Development server for testing FlowState viewer locally."""

    def __init__(self, port: int = 8080, directory: Optional[Path] = None):
        self.port = port
        self.directory = directory or Path.cwd()
        self.server = None
        self.server_thread = None

    def generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample pose data for testing if no real data is available."""
        import random
        
        # Generate sample pose landmarks for 60 frames (2 seconds at 30fps)
        num_frames = 60
        num_joints = 33  # MediaPipe pose landmarks
        
        pose_landmarks = []
        for frame in range(num_frames):
            frame_landmarks = []
            for joint in range(num_joints):
                # Create smooth movement using sine waves
                t = frame / num_frames * 2 * 3.14159
                x = random.uniform(-1, 1) + 0.2 * float(f"{0.2 * (1 + joint / num_joints) * (-1 if joint % 2 else 1):.3f}")
                y = random.uniform(0, 2) + 0.3 * float(f"{0.3 * (1 + 0.5 * (joint % 5 / 5)):.3f}")
                z = 0.1 * float(f"{0.1 * (0.5 + 0.5 * (joint % 3 / 3)):.3f}")
                
                frame_landmarks.append({
                    "x": x,
                    "y": y,
                    "z": z,
                    "visibility": random.uniform(0.8, 1.0)
                })
            pose_landmarks.append(frame_landmarks)
        
        return {
            "poseData": {
                "pose_landmarks": pose_landmarks,
                "overall_scores": {
                    "flow": random.uniform(70, 95),
                    "balance": random.uniform(65, 90),
                    "smoothness": random.uniform(75, 98),
                    "energy": random.uniform(60, 85)
                }
            },
            "videoInfo": {
                "title": "Sample Dance Video (Dev Mode)",
                "uploader": "FlowState Developer",
                "uploadDate": time.strftime("%Y-%m-%d"),
                "thumbnail": "",
                "webpageUrl": "#"
            },
            "settings": {
                "quality": "high",
                "theme": "dark",
                "enableParticles": True,
                "enableShadows": True
            }
        }

    def create_test_data_file(self):
        """Create a test data.js file if it doesn't exist."""
        data_file = self.directory / "data.js"
        if not data_file.exists():
            print("No data.js found. Creating sample data for testing...")
            sample_data = self.generate_sample_data()
            with open(data_file, 'w', encoding='utf-8') as f:
                f.write(f"const flowStateData = {json.dumps(sample_data, indent=2)};")
            print(f"Created sample data file: {data_file}")

    def start(self):
        """Start the development server."""
        # Ensure we have test data
        self.create_test_data_file()
        
        # Create the server
        handler = partial(FlowStateDevHandler, directory=str(self.directory))
        self.server = socketserver.TCPServer(("", self.port), handler)
        
        # Start server in a separate thread
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        print(f"\nFlowState Development Server")
        print(f"{'='*40}")
        print(f"Serving directory: {self.directory}")
        print(f"Server running at: http://localhost:{self.port}")
        print(f"{'='*40}")
        print("\nPress Ctrl+C to stop the server\n")

    def open_browser(self):
        """Open the viewer in the default web browser."""
        time.sleep(0.5)  # Give server time to start
        url = f"http://localhost:{self.port}"
        webbrowser.open(url)

    def stop(self):
        """Stop the development server."""
        if self.server:
            print("\nShutting down server...")
            self.server.shutdown()
            self.server_thread.join()
            print("Server stopped.")


def main():
    """Main entry point for the development server."""
    parser = argparse.ArgumentParser(
        description="FlowState 3D Viewer Development Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start server on default port (8080)
  python dev_server.py

  # Start server on custom port
  python dev_server.py --port 3000

  # Start server without opening browser
  python dev_server.py --no-browser

  # Serve a specific directory
  python dev_server.py --directory ../output/viewer
        """
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8080,
        help='Port to run the server on (default: 8080)'
    )
    
    parser.add_argument(
        '--directory', '-d',
        type=Path,
        help='Directory to serve (default: current directory)'
    )
    
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help="Don't open the browser automatically"
    )
    
    args = parser.parse_args()
    
    # Determine directory to serve
    if args.directory:
        serve_dir = args.directory.resolve()
    else:
        # If no directory specified, try to find template directory
        template_dir = Path(__file__).parent / "template"
        if template_dir.exists():
            serve_dir = template_dir
        else:
            serve_dir = Path.cwd()
    
    if not serve_dir.exists():
        print(f"Error: Directory {serve_dir} does not exist!")
        sys.exit(1)
    
    # Create and start server
    server = DevelopmentServer(port=args.port, directory=serve_dir)
    
    try:
        server.start()
        
        # Open browser if requested
        if not args.no_browser:
            server.open_browser()
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nReceived interrupt signal...")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        server.stop()


if __name__ == "__main__":
    main()